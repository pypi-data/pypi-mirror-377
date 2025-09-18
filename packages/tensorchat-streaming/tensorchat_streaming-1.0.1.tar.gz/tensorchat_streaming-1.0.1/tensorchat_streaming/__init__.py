"""
Tensorchat Streaming Python Client

Framework-agnostic Python client for Tensorchat.io streaming API.
Process multiple LLM prompts concurrently with real-time streaming responses.
"""

from .client import TensorchatStreaming
from .manager import TensorchatStreamingManager, create_streaming_manager
from .types import (
    TensorConfig,
    StreamRequest,
    StreamEventData,
    StreamCallbacks,
    TensorchatConfig,
    EventType
)

__version__ = "1.0.0"
__author__ = "Tensorchat.io"
__email__ = "support@tensorchat.io"

__all__ = [
    "TensorchatStreaming",
    "TensorchatStreamingManager", 
    "create_streaming_manager",
    "TensorConfig",
    "StreamRequest",
    "StreamEventData",
    "StreamCallbacks",
    "TensorchatConfig",
    "EventType",
]