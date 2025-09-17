"""
TokenRouter SDK - OpenAI Responses API Compatible Client

A Python SDK for the TokenRouter API that provides intelligent routing
to multiple LLM providers with the OpenAI Responses API interface.
"""

from .client import TokenRouter, AsyncTokenRouter
from .models import (
    Response,
    ResponseStreamEvent,
    InputItemsList,
    Usage,
    OutputItem,
    OutputContent,
    ContentItem,
    InputItem,
    Tool,
    ToolCall,
    ResponseFormat,
    TextConfig,
    ResponseDelta,
)
from .exceptions import (
    TokenRouterError,
    AuthenticationError,
    RateLimitError,
    InvalidRequestError,
    APIConnectionError,
    APIStatusError,
    TimeoutError,
    QuotaExceededError,
)

__version__ = "1.0.14"

__all__ = [
    # Client classes
    "TokenRouter",
    "AsyncTokenRouter",
    # Response models
    "Response",
    "ResponseStreamEvent",
    "InputItemsList",
    "Usage",
    "OutputItem",
    "OutputContent",
    "ContentItem",
    "InputItem",
    "Tool",
    "ToolCall",
    "ResponseFormat",
    "TextConfig",
    "ResponseDelta",
    # Exceptions
    "TokenRouterError",
    "AuthenticationError",
    "RateLimitError",
    "InvalidRequestError",
    "APIConnectionError",
    "APIStatusError",
    "TimeoutError",
    "QuotaExceededError",
]

# Default export for OpenAI-like usage
def create_client(*args, **kwargs):
    """Create a TokenRouter client"""
    return TokenRouter(*args, **kwargs)