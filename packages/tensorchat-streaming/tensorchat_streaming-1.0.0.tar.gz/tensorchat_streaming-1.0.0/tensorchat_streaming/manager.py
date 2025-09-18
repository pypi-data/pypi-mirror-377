"""
Tensorchat Streaming Manager

Framework-agnostic streaming manager for Python applications.
"""

import asyncio
from typing import Optional

from .client import TensorchatStreaming
from .types import StreamRequest, StreamCallbacks, TensorchatConfig


class TensorchatStreamingManager:
    """
    Framework-agnostic Tensorchat streaming client manager.
    
    This replaces React hooks with a generic class-based approach
    suitable for any Python application.
    """

    def __init__(self, config: TensorchatConfig):
        """
        Initialize the streaming manager.
        
        Args:
            config: Configuration for the Tensorchat client
        """
        self.config = config
        self._client: Optional[TensorchatStreaming] = None
        self._initialized = False

    async def _ensure_initialized(self):
        """Ensure the client is initialized."""
        if not self._initialized or self._client is None:
            await self._initialize()

    async def _initialize(self):
        """Initialize or reinitialize the client."""
        if self._client:
            await self._client.destroy()
        
        self._client = TensorchatStreaming(self.config)
        await self._client._ensure_session()
        self._initialized = True

    async def update_config(self, new_config: TensorchatConfig):
        """
        Update configuration and reinitialize client.
        
        Args:
            new_config: New configuration to apply
        """
        self.config = new_config
        await self._initialize()

    async def stream_process(
        self,
        request: StreamRequest,
        callbacks: Optional[StreamCallbacks] = None
    ) -> None:
        """
        Stream process tensors with real-time callbacks.
        
        Args:
            request: The streaming request
            callbacks: Optional callback functions for stream events
        """
        await self._ensure_initialized()
        
        if not self._client:
            raise RuntimeError("Tensorchat client not initialized")
            
        await self._client.stream_process(request, callbacks)

    async def process_single(self, request: StreamRequest):
        """
        Process a single tensor (non-streaming).
        
        Args:
            request: The request to process
            
        Returns:
            The response data
        """
        await self._ensure_initialized()
        
        if not self._client:
            raise RuntimeError("Tensorchat client not initialized")
            
        return await self._client.process_single(request)

    def get_client(self) -> Optional[TensorchatStreaming]:
        """
        Get the underlying client instance.
        
        Returns:
            The TensorchatStreaming client or None if not initialized
        """
        return self._client

    async def destroy(self):
        """Clean up resources."""
        if self._client:
            await self._client.destroy()
            self._client = None
        self._initialized = False

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_initialized()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.destroy()


def create_streaming_manager(config: TensorchatConfig) -> TensorchatStreamingManager:
    """
    Factory function for creating a Tensorchat streaming manager.
    
    Args:
        config: Configuration for the Tensorchat client
        
    Returns:
        A new TensorchatStreamingManager instance
    """
    return TensorchatStreamingManager(config)