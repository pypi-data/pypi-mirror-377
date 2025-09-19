"""Agentic Blocks - Building blocks for agentic systems."""

from .mcp_client import MCPClient, MCPEndpointError
from .messages import Messages
from .llm import call_llm, call_llm_stream, call_llm_stream_basic, LLMResponse, LLMError

# Structured LLM functions (optional, requires instructor)
try:
    from .llm_structured import (
        call_llm as call_llm_structured,
        call_llm_async as call_llm_structured_async,
        call_llm_stream as call_llm_structured_stream,
        call_llm_stream_async as call_llm_structured_stream_async,
        StructuredLLMClient,
        StructuredLLMError,
        # Example models for documentation
        ExamplePersonInfo,
        ExampleMathResult,
        ExampleSearchQuery,
    )
    STRUCTURED_AVAILABLE = True
except ImportError:
    # Instructor not installed, structured functions not available
    STRUCTURED_AVAILABLE = False

# Get version from package metadata
try:
    from importlib.metadata import version

    __version__ = version("agentic-blocks")
except Exception:
    __version__ = "unknown"

__all__ = [
    "MCPClient",
    "MCPEndpointError",
    "Messages",
    "call_llm",
    "call_llm_stream",
    "call_llm_stream_basic",
    "LLMResponse",
    "LLMError",
    "STRUCTURED_AVAILABLE",
]

# Add structured functions to __all__ if available
if STRUCTURED_AVAILABLE:
    __all__.extend([
        "call_llm_structured",
        "call_llm_structured_async",
        "call_llm_structured_stream",
        "call_llm_structured_stream_async",
        "StructuredLLMClient",
        "StructuredLLMError",
        "ExamplePersonInfo",
        "ExampleMathResult",
        "ExampleSearchQuery",
    ])
