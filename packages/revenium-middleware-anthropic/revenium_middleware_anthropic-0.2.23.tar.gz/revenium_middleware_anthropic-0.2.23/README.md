#  Revenium Middleware for Anthropic

[![PyPI version](https://img.shields.io/pypi/v/revenium-middleware-anthropic.svg)](https://pypi.org/project/revenium-middleware-anthropic/)
[![Python Versions](https://img.shields.io/pypi/pyversions/revenium-middleware-anthropic.svg)](https://pypi.org/project/revenium-middleware-anthropic/)
[![Documentation](https://img.shields.io/badge/docs-revenium.io-blue)](https://docs.revenium.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A middleware library for metering and monitoring Anthropic API usage in Python applications.


A middleware library for metering and monitoring Anthropic API usage in Python applications. 

##  Features

- ** Precise Usage Tracking**: Monitor tokens, costs, and request counts across all Anthropic API endpoints
- ** Seamless Integration**: Drop-in middleware that works with minimal code changes
- **️ Flexible Configuration**: Customize metering behavior to suit your application needs

##  Installation


```bash
pip install revenium-middleware-anthropic
```

##  Usage

### Zero-Config Integration

Simply export your REVENIUM_METERING_API_KEY and import the middleware.
Your Anthropic calls will be metered automatically:

```python
import anthropic
import revenium_middleware_anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=20000,
    temperature=1,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                     "text": "What is the meaning of life, the universe and everything?",
                }
            ]
        }
    ]
)
print(message.content)
```

The middleware automatically intercepts Anthropic API calls and sends metering data to Revenium without requiring any
changes to your existing code. Make sure to set the `REVENIUM_METERING_API_KEY` environment variable for authentication
with the Revenium service.

### Enhanced Tracking with Metadata

For more granular usage tracking and detailed reporting, add the `usage_metadata` parameter:

```python
import anthropic
import revenium_middleware_anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=20000,
    temperature=1,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What is the meaning of life, the universe and everything?",
                }
            ]
        }
    ],
    usage_metadata={
         "trace_id": "conv-28a7e9d4",
         "task_type": "summarize-customer-issue",
         "subscriber": {
             "id": "subscriberid-1234567890",
             "email": "user@example.com",
             "credential": {
                 "name": "engineering-api-key",
                 "value": "sk-ant-api03-..."
             }
         },
         "organization_id": "acme-corp",
         "subscription_id": "startup-plan-Q1",
         "product_id": "saas-app-gold-tier",
         "agent": "support-agent",
    }
)
print(message.content)
```

### Streaming Support

The middleware also supports Anthropic's streaming API. For streaming responses, use the `usage_metadata` parameter to provide metadata for analytics. The middleware will automatically track token usage and send metering data when the stream completes. 

### Example Code

View the [examples](./examples) directory for more code samples for both streaming and non-streaming AI calls.

#### ️ Metadata Fields

The `usage_metadata` parameter supports the following fields:

| Field                        | Description                                               | Use Case                                                          |
|------------------------------|-----------------------------------------------------------|-------------------------------------------------------------------|
| `trace_id`                   | Unique identifier for a conversation or session           | Group multi-turn conversations into single event for performance & cost tracking                           |
| `task_type`                  | Classification of the AI operation by type of work        | Track cost & performance by purpose (e.g., classification, summarization)                                  |
| `subscriber`                 | Object containing subscriber information                   | Track cost & performance by individual users and their credentials                                          |
| `subscriber.id`              | The id of the subscriber from non-Revenium systems        | Track cost & performance by individual users (if customers are anonymous or tracking by emails is not desired)   |
| `subscriber.email`           | The email address of the subscriber                       | Track cost & performance by individual users (if customer e-mail addresses are known)                      |
| `subscriber.credential`      | Object containing credential information                   | Track cost & performance by API keys and credentials                                                       |
| `subscriber.credential.name` | An alias for an API key used by one or more users         | Track cost & performance by individual API keys                                                            |
| `subscriber.credential.value`| The key value associated with the subscriber (i.e an API key)     | Track cost & performance by API key value (normally used when the only identifier for a user is an API key) |
| `organization_id`            | Customer or department ID from non-Revenium systems       | Track cost & performance by customers or business units                                                    |
| `subscription_id`            | Reference to a billing plan in non-Revenium systems       | Track cost & performance by a specific subscription                                                        |
| `product_id`                 | Your product or feature making the AI call                | Track cost & performance across different products                                                         |
| `agent`                      | Identifier for the specific AI agent                      | Track cost & performance performance by AI agent                                                           |
| `response_quality_score`     | The quality of the AI response (0..1)                     | Track AI response quality                                                                                  |

**All metadata fields are optional**. Adding them enables more detailed reporting and analytics in Revenium.


##  Compatibility

-  Python 3.8+
-  Anthropic Python SDK

##  Logging

This module uses Python's standard logging system. You can control the log level by setting the `REVENIUM_LOG_LEVEL` environment variable:

```bash
# Enable debug logging
export REVENIUM_LOG_LEVEL=DEBUG

# Or when running your script
REVENIUM_LOG_LEVEL=DEBUG python your_script.py
```

Available log levels:
- `DEBUG`: Detailed debugging information
- `INFO`: General information (default)
- `WARNING`: Warning messages only
- `ERROR`: Error messages only
- `CRITICAL`: Critical error messages only

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md)

## Security

See [SECURITY.md](./SECURITY.md)

##  License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

##  Acknowledgments

-  Built by the Revenium team
