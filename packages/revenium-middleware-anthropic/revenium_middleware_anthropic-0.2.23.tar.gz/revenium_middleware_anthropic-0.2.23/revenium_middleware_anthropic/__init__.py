"""
When you install and import this library, it will automatically hook
anthropic.resources.messages.create using wrapt, and log token usage after
each request. You can customize or extend this logging logic later
to add user or organization metadata for metering purposes.
"""
# Import the middleware module to ensure the wrapt decorators are executed
from . import middleware
from .middleware import create_wrapper