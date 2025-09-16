"""iFlow Python SDK - AI Agent Integration for iFlow CLI.

A powerful SDK for interacting with iFlow using the Agent Communication Protocol (ACP).
Provides both simple query functions and full bidirectional client for complex interactions.
"""

# Error types (private module)
from ._errors import (
    IFlowError,
    ConnectionError,
    ProtocolError,
    AuthenticationError,
    TimeoutError,
    InterruptError,
    ToolCallError,
    ValidationError,
    TransportError,
    JSONDecodeError,
)

# Main client
from .client import IFlowClient

# Raw data client for advanced users
from .raw_client import RawDataClient, RawMessage, ProtocolDebugger

# Convenience functions
from .query import query, query_stream, query_sync

# Type definitions
from .types import (
    # Protocol version
    PROTOCOL_VERSION,
    # Enums
    ToolCallStatus,
    ToolCallConfirmationOutcome,
    PermissionMode,
    # Message chunks
    UserMessageChunk,
    AssistantMessageChunk,
    # Tool call types
    ToolCallConfirmation,
    ToolCallContent,
    ToolCallLocation,
    Icon,
    # Messages
    Message,
    UserMessage,
    AssistantMessage,
    ToolCallMessage,
    PlanMessage,
    PlanEntry,
    TaskFinishMessage,
    ErrorMessage,
    # Configuration
    IFlowOptions,
)


__version__ = "1.0.0"

__all__ = [
    # Main exports
    "IFlowClient",
    "RawDataClient",
    "RawMessage",
    "ProtocolDebugger",
    "query",
    "query_stream",
    "query_sync",
    # Configuration
    "IFlowOptions",
    # Enums
    "PermissionMode",
    "ToolCallStatus",
    "ToolCallConfirmationOutcome",
    # Messages
    "Message",
    "UserMessage",
    "AssistantMessage",
    "ToolCallMessage",
    "PlanMessage",
    "PlanEntry",
    "TaskFinishMessage",
    "ErrorMessage",
    # Message chunks
    "UserMessageChunk",
    "AssistantMessageChunk",
    # Tool call types
    "ToolCallConfirmation",
    "ToolCallContent",
    "ToolCallLocation",
    "Icon",
    # Errors
    "IFlowError",
    "ConnectionError",
    "ProtocolError",
    "AuthenticationError",
    "TimeoutError",
    "InterruptError",
    "ToolCallError",
    "ValidationError",
    "TransportError",
    "JSONDecodeError",
    # Version info
    "PROTOCOL_VERSION",
    "__version__",
]
