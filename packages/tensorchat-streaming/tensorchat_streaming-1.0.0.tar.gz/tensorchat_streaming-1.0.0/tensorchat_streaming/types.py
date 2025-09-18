"""
Type definitions for Tensorchat Streaming Python client.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Union, Callable, Any, Literal
from enum import Enum


class EventType(str, Enum):
    """Stream event types."""
    START = "start"
    PROGRESS = "progress"
    SEARCH_PROGRESS = "search_progress"
    SEARCH_COMPLETE = "search_complete"
    TENSOR_CHUNK = "tensor_chunk"
    TENSOR_COMPLETE = "tensor_complete"
    TENSOR_ERROR = "tensor_error"
    COMPLETE = "complete"
    ERROR = "error"
    FATAL_ERROR = "fatal_error"


@dataclass
class TensorConfig:
    """Configuration for a single tensor."""
    messages: str
    concise: Optional[bool] = None
    model: Optional[str] = None
    search: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {"messages": self.messages}
        if self.concise is not None:
            result["concise"] = self.concise
        if self.model is not None:
            result["model"] = self.model
        if self.search is not None:
            result["search"] = self.search
        return result


@dataclass
class StreamRequest:
    """Request structure for streaming operations."""
    context: str
    model: str
    tensors: List[TensorConfig]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "context": self.context,
            "model": self.model,
            "tensors": [tensor.to_dict() for tensor in self.tensors]
        }


@dataclass
class StreamEventData:
    """Data structure for streaming events."""
    type: EventType
    index: Optional[int] = None
    chunk: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    details: Optional[str] = None
    total_tensors: Optional[int] = None
    model: Optional[str] = None
    search_applied: Optional[bool] = None
    tensors: Optional[List[Any]] = None
    stream_buffers: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StreamEventData":
        """Create from dictionary."""
        return cls(
            type=EventType(data["type"]),
            index=data.get("index"),
            chunk=data.get("chunk"),
            result=data.get("result"),
            error=data.get("error"),
            details=data.get("details"),
            total_tensors=data.get("totalTensors"),
            model=data.get("model"),
            search_applied=data.get("searchApplied"),
            tensors=data.get("tensors"),
            stream_buffers=data.get("streamBuffers")
        )


@dataclass
class TensorchatConfig:
    """Configuration for Tensorchat client."""
    api_key: str
    base_url: Optional[str] = None
    throttle_ms: Optional[int] = None

    def __post_init__(self):
        """Set default values after initialization."""
        if self.base_url is None:
            self.base_url = "https://api.tensorchat.io"
        if self.throttle_ms is None:
            self.throttle_ms = 50


# Callback type definitions
OnStartCallback = Callable[[StreamEventData], None]
OnProgressCallback = Callable[[StreamEventData], None]
OnSearchProgressCallback = Callable[[StreamEventData], None]
OnSearchCompleteCallback = Callable[[StreamEventData], None]
OnTensorChunkCallback = Callable[[StreamEventData], None]
OnTensorCompleteCallback = Callable[[StreamEventData], None]
OnTensorErrorCallback = Callable[[StreamEventData], None]
OnCompleteCallback = Callable[[StreamEventData], None]
OnErrorCallback = Callable[[Exception], None]


@dataclass
class StreamCallbacks:
    """Callback functions for streaming events."""
    on_start: Optional[OnStartCallback] = None
    on_progress: Optional[OnProgressCallback] = None
    on_search_progress: Optional[OnSearchProgressCallback] = None
    on_search_complete: Optional[OnSearchCompleteCallback] = None
    on_tensor_chunk: Optional[OnTensorChunkCallback] = None
    on_tensor_complete: Optional[OnTensorCompleteCallback] = None
    on_tensor_error: Optional[OnTensorErrorCallback] = None
    on_complete: Optional[OnCompleteCallback] = None
    on_error: Optional[OnErrorCallback] = None