import logging
import datetime
import wrapt
from revenium_middleware import client, run_async_in_thread, shutdown_event
import time

logger = logging.getLogger("revenium_middleware.extension")

# Ensure debug logging is enabled when REVENIUM_DEBUG is set
import os
if os.getenv("REVENIUM_DEBUG", "").lower() in ("true", "1", "yes"):
    logger.setLevel(logging.DEBUG)
    # Also ensure the handler is configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('DEBUG - %(name)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)


def extract_usage_metadata_and_timing(kwargs: dict, operation_name: str = "operation"):
    """
    Extract usage metadata from kwargs.
    Provides robust error handling for malformed metadata structures.

    Args:
        kwargs: The kwargs dict to extract from (will be modified)
        operation_name: Name of operation for logging (e.g., "create", "stream")

    Returns:
        tuple: (usage_metadata, request_time, request_time_dt)
    """
    # Extract usage_metadata from kwargs
    usage_metadata = kwargs.pop("usage_metadata", {})

    # Validate and sanitize usage_metadata
    if not isinstance(usage_metadata, dict):
        logger.warning(f"usage_metadata for {operation_name} should be a dict, got {type(usage_metadata)}. Using empty dict.")
        usage_metadata = {}

    # Sanitize metadata structure (defensive programming)
    usage_metadata = _sanitize_metadata(usage_metadata, operation_name)

    # Create request timestamp
    request_time_dt = datetime.datetime.now(datetime.timezone.utc)
    request_time = request_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Debug logging
    logger.debug(f"Usage metadata for {operation_name}: %s", usage_metadata)

    return usage_metadata, request_time, request_time_dt


def _sanitize_metadata(metadata: dict, operation_name: str, max_depth: int = 5, current_depth: int = 0) -> dict:
    """
    Sanitize metadata structure to prevent issues with deeply nested objects
    or problematic data types that could break metering calls.

    Args:
        metadata: The metadata dict to sanitize
        operation_name: Operation name for logging
        max_depth: Maximum allowed nesting depth
        current_depth: Current recursion depth

    Returns:
        dict: Sanitized metadata
    """
    if current_depth > max_depth:
        logger.warning(f"Metadata for {operation_name} exceeds maximum depth {max_depth}. Truncating.")
        return {}

    if not isinstance(metadata, dict):
        return {}

    sanitized = {}
    for key, value in metadata.items():
        # Ensure key is a string
        if not isinstance(key, str):
            key = str(key)

        # Sanitize value based on type
        if isinstance(value, dict):
            sanitized[key] = _sanitize_metadata(value, operation_name, max_depth, current_depth + 1)
        elif isinstance(value, (list, tuple)):
            # Convert lists/tuples to strings to avoid complex nested structures
            sanitized[key] = str(value)
        elif isinstance(value, (str, int, float, bool)):
            sanitized[key] = value
        elif value is None:
            sanitized[key] = None
        else:
            # Convert other types to string
            sanitized[key] = str(value)

    return sanitized


@wrapt.patch_function_wrapper('anthropic.resources.messages.messages', 'Messages.create')
def create_wrapper(wrapped, _, args, kwargs):
    """
    Wraps the anthropic.ChatCompletion.create method to log token usage.
    """
    logger.debug("REVENIUM MIDDLEWARE: Intercepted client.messages.create call - wrapper active")

    # Extract usage metadata and timing using shared handler
    usage_metadata, request_time, request_time_dt = extract_usage_metadata_and_timing(kwargs, "create")

    logger.debug("REVENIUM MIDDLEWARE: Calling client.messages.create with args: %s, kwargs: %s", args, kwargs)

    response = wrapped(*args, **kwargs)
    logger.debug("REVENIUM MIDDLEWARE: Received response from client.messages.create: %s", response.id)
    logger.debug(
        "Anthropic client.messages.create response: %s",
        response)
    response_time_dt = datetime.datetime.now(datetime.timezone.utc)
    response_time = response_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    request_duration = (response_time_dt - request_time_dt).total_seconds() * 1000
    response_id = response.id

    prompt_tokens = response.usage.input_tokens
    completion_tokens = response.usage.output_tokens
    cache_creation_input_tokens = response.usage.cache_creation_input_tokens
    cache_read_input_tokens = response.usage.cache_read_input_tokens

    logger.debug(
        "Anthropic client.ai.create_completion token usage - prompt: %d, completion: %d, "
        "cache_creation_input_tokens: %d,cache_read_input_tokens: %d",
        prompt_tokens, completion_tokens, cache_creation_input_tokens, cache_read_input_tokens
    )

    anthropic_finish_reason = None
    if response.stop_reason:
        anthropic_finish_reason = response.stop_reason

    finish_reason_map = {
        "end_turn": "END",
        "tool_use": "END_SEQUENCE",
        "max_tokens": "TOKEN_LIMIT",
        "content_filter": "ERROR"
    }
    stop_reason = finish_reason_map.get(anthropic_finish_reason, "end_turn")  # type: ignore

    async def metering_call():
        try:
            if shutdown_event.is_set():
                logger.warning("Skipping metering call during shutdown")
                return
            logger.debug("Metering call to Revenium for completion %s with usage_metadata: %s", response_id,
                         usage_metadata)
            
            # Create subscriber object from usage metadata
            subscriber = {}
            
            # Handle nested subscriber object
            if "subscriber" in usage_metadata and isinstance(usage_metadata["subscriber"], dict):
                nested_subscriber = usage_metadata["subscriber"]
                
                if nested_subscriber.get("id"):
                    subscriber["id"] = nested_subscriber["id"]
                if nested_subscriber.get("email"):
                    subscriber["email"] = nested_subscriber["email"]
                if nested_subscriber.get("credential") and isinstance(nested_subscriber["credential"], dict):
                    # Maintain nested credential structure
                    subscriber["credential"] = {
                        "name": nested_subscriber["credential"].get("name"),
                        "value": nested_subscriber["credential"].get("value")
                    }
            
            result = client.ai.create_completion(
                cache_creation_token_count=cache_creation_input_tokens,
                cache_read_token_count=cache_read_input_tokens,
                input_token_cost=None,
                output_token_cost=None,
                total_cost=None,
                output_token_count=completion_tokens,
                cost_type="AI",
                model=response.model,
                input_token_count=prompt_tokens,
                provider="ANTHROPIC",
                model_source="ANTHROPIC",
                reasoning_token_count=0,
                request_time=request_time,
                response_time=response_time,
                completion_start_time=response_time,
                request_duration=int(request_duration),
                time_to_first_token=int(request_duration),  # For non-streaming, use the full request duration
                stop_reason=stop_reason,
                total_token_count=prompt_tokens + completion_tokens,
                transaction_id=response_id,
                trace_id=usage_metadata.get("trace_id"),
                task_type=usage_metadata.get("task_type"),
                subscriber=subscriber if subscriber else None,
                organization_id=usage_metadata.get("organization_id"),
                subscription_id=usage_metadata.get("subscription_id"),
                product_id=usage_metadata.get("product_id"),
                agent=usage_metadata.get("agent"),
                response_quality_score=usage_metadata.get("response_quality_score"),
                is_streamed=False,
                operation_type="CHAT",
                middleware_source="PYTHON"
            )
            logger.debug("Metering call result: %s", result)
            # Treat any successful resource response as success; only warn on explicit failure
            success = False
            try:
                if result is None:
                    success = False
                elif hasattr(result, 'status_code'):
                    status_code = int(getattr(result, 'status_code', 0) or 0)
                    success = 200 <= status_code < 300
                elif hasattr(result, 'resource_type') or hasattr(result, 'resourceType') or hasattr(result, 'id'):
                    # Revenium SDK returns a resource object on success (e.g., MeteringResponseResource)
                    success = True
                else:
                    # Unknown shape but non-empty result; assume success
                    success = True
            except Exception:
                success = False

            if success:
                logger.debug("✅ REVENIUM SUCCESS: Metering call successful for transaction %s", response_id)
            else:
                logger.warning("❌ REVENIUM ERROR: Metering call did not return success for transaction %s: %s", response_id, result)
        except Exception as e:
            if not shutdown_event.is_set():
                logger.warning(f"Error in metering call: {str(e)}")
                # Log the full traceback for better debugging
                import traceback
                logger.warning(f"Traceback: {traceback.format_exc()}")

    thread = run_async_in_thread(metering_call())
    logger.debug("Metering thread started: %s", thread)
    return response


@wrapt.patch_function_wrapper('anthropic.resources.messages.messages', 'Messages.stream')
def stream_wrapper(wrapped, _, args, kwargs):
    """
    Wraps the anthropic.resources.messages.Messages.stream method to log token usage.
    Extracts usage data from the final message of the stream.
    """
    logger.debug("REVENIUM MIDDLEWARE: Intercepted client.messages.stream call - wrapper active")

    # Extract usage metadata and timing using shared handler
    usage_metadata, request_time, request_time_dt = extract_usage_metadata_and_timing(kwargs, "stream")

    logger.debug("REVENIUM MIDDLEWARE: Calling client.messages.stream with args: %s, kwargs: %s", args, kwargs)

    stream = wrapped(*args, **kwargs)
    logger.debug("REVENIUM MIDDLEWARE: Received stream from client.messages.stream")

    # Create a wrapper for the stream that will capture the final message
    class StreamWrapper:
        def __init__(self, stream):
            self.stream = stream
            self.response_time_dt = None
            self.response_id = None
            self.collected_content = []
            self.final_message = None
            self.first_token_time = None
            self.request_start_time = time.time() * 1000  # Convert to milliseconds

        def __enter__(self):
            self.stream_context = self.stream.__enter__()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            result = self.stream.__exit__(exc_type, exc_val, exc_tb)

            # Get the final message with usage information
            try:
                self.final_message = self.stream_context.get_final_message()
                self.response_time_dt = datetime.datetime.now(datetime.timezone.utc)
                self.response_time = self.response_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                request_duration = (self.response_time_dt - request_time_dt).total_seconds() * 1000

                self.response_id = self.final_message.id

                prompt_tokens = self.final_message.usage.input_tokens
                completion_tokens = self.final_message.usage.output_tokens
                cache_creation_input_tokens = self.final_message.usage.cache_creation_input_tokens
                cache_read_input_tokens = self.final_message.usage.cache_read_input_tokens

                logger.debug(
                    "Anthropic client.messages.stream token usage - prompt: %d, completion: %d, "
                    "cache_creation_input_tokens: %d, cache_read_input_tokens: %d",
                    prompt_tokens, completion_tokens, cache_creation_input_tokens, cache_read_input_tokens
                )

                anthropic_finish_reason = None
                if self.final_message.stop_reason:
                    anthropic_finish_reason = self.final_message.stop_reason

                finish_reason_map = {
                    "end_turn": "END",
                    "tool_use": "END_SEQUENCE",
                    "max_tokens": "TOKEN_LIMIT",
                    "content_filter": "ERROR"
                }
                stop_reason = finish_reason_map.get(anthropic_finish_reason, "end_turn")  # type: ignore

                async def metering_call():
                    try:
                        if shutdown_event.is_set():
                            logger.warning("Skipping metering call during shutdown")
                            return
                        logger.debug("Metering call to Revenium for stream completion %s", self.response_id)
                        
                        # Create subscriber object from usage metadata
                        subscriber = {}
                        
                        # Handle nested subscriber object
                        if "subscriber" in usage_metadata and isinstance(usage_metadata["subscriber"], dict):
                            nested_subscriber = usage_metadata["subscriber"]
                            
                            if nested_subscriber.get("id"):
                                subscriber["id"] = nested_subscriber["id"]
                            if nested_subscriber.get("email"):
                                subscriber["email"] = nested_subscriber["email"]
                            if nested_subscriber.get("credential") and isinstance(nested_subscriber["credential"], dict):
                                # Maintain nested credential structure
                                subscriber["credential"] = {
                                    "name": nested_subscriber["credential"].get("name"),
                                    "value": nested_subscriber["credential"].get("value")
                                }
                        
                        result = client.ai.create_completion(
                            cache_creation_token_count=cache_creation_input_tokens,
                            cache_read_token_count=cache_read_input_tokens,
                            input_token_cost=None,
                            output_token_cost=None,
                            total_cost=None,
                            output_token_count=completion_tokens,
                            cost_type="AI",
                            model=self.final_message.model,
                            input_token_count=prompt_tokens,
                            provider="ANTHROPIC",
                            model_source="ANTHROPIC",
                            reasoning_token_count=0,
                            request_time=request_time,
                            response_time=self.response_time,
                            completion_start_time=self.response_time,
                            request_duration=int(request_duration),
                            time_to_first_token=int(
                                self.first_token_time - self.request_start_time) if self.first_token_time else 0,
                            stop_reason=stop_reason,
                            total_token_count=prompt_tokens + completion_tokens,
                            transaction_id=self.response_id,
                            trace_id=usage_metadata.get("trace_id"),
                            task_type=usage_metadata.get("task_type"),
                            subscriber=subscriber if subscriber else None,
                            organization_id=usage_metadata.get("organization_id"),
                            subscription_id=usage_metadata.get("subscription_id"),
                            product_id=usage_metadata.get("product_id"),
                            agent=usage_metadata.get("agent"),
                            is_streamed=True,
                            operation_type="CHAT",
                            response_quality_score=usage_metadata.get("response_quality_score"),
                            middleware_source="PYTHON"
                        )
                        logger.debug("Metering call result for stream: %s", result)
                        # Treat any successful resource response as success; only warn on explicit failure
                        success = False
                        try:
                            if result is None:
                                success = False
                            elif hasattr(result, 'status_code'):
                                status_code = int(getattr(result, 'status_code', 0) or 0)
                                success = 200 <= status_code < 300
                            elif hasattr(result, 'resource_type') or hasattr(result, 'resourceType') or hasattr(result, 'id'):
                                success = True
                            else:
                                success = True
                        except Exception:
                            success = False

                        if success:
                            logger.debug("✅ REVENIUM SUCCESS: Streaming metering call successful for transaction %s", self.response_id)
                        else:
                            logger.warning("❌ REVENIUM ERROR: Streaming metering call did not return success for transaction %s: %s", self.response_id, result)
                    except Exception as e:
                        if not shutdown_event.is_set():
                            logger.warning(f"Error in metering call for stream: {str(e)}")
                            # Log the full traceback for better debugging
                            import traceback
                            logger.warning(f"Traceback: {traceback.format_exc()}")

                thread = run_async_in_thread(metering_call())
                logger.debug("Metering thread started for stream: %s", thread)

            except Exception as e:
                logger.warning(f"Error processing final message from stream: {str(e)}")
                import traceback
                logger.warning(f"Traceback: {traceback.format_exc()}")

            return result

        @property
        def text_stream(self):
            # Create a wrapper for the text_stream that doesn't consume it
            original_text_stream = self.stream_context.text_stream
            wrapper_self = self

            class TextStreamWrapper:
                def __iter__(self):
                    return self

                def __next__(self):
                    try:
                        chunk = next(original_text_stream)
                        # Record the time of the first token
                        if wrapper_self.first_token_time is None and chunk:
                            wrapper_self.first_token_time = time.time() * 1000  # Convert to milliseconds
                        return chunk
                    except StopIteration:
                        raise

            return TextStreamWrapper()

        def get_final_message(self):
            if self.final_message:
                return self.final_message
            return self.stream_context.get_final_message()

        def __iter__(self):
            return iter(self.stream_context)

        def __getattr__(self, name):
            return getattr(self.stream_context, name)

    return StreamWrapper(stream)


# Log middleware initialization
logger.debug("REVENIUM MIDDLEWARE: Anthropic middleware loaded and wrappers registered")
