"""
Tensorchat Streaming Client

Main streaming client for Tensorchat.io API.
"""

import asyncio
import json
import logging
from typing import Dict, Optional, Any
from dataclasses import asdict

import aiohttp

from .types import (
    StreamRequest,
    StreamEventData,
    StreamCallbacks,
    TensorchatConfig,
    EventType
)


logger = logging.getLogger(__name__)


class TensorchatStreaming:
    """
    Async streaming client for Tensorchat.io API.
    
    Handles real-time streaming of tensor processing with throttling
    and proper async/await patterns.
    """

    def __init__(self, config: TensorchatConfig):
        """
        Initialize the streaming client.
        
        Args:
            config: Configuration including API key, base URL, and throttle settings
        """
        self.api_key = config.api_key
        self.base_url = config.base_url or "https://api.tensorchat.ai"
        self.throttle_ms = config.throttle_ms or 50
        self._throttle_tasks: Dict[str, asyncio.Task] = {}
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.destroy()

    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()

    async def _throttle(self, key: str, callback, *args, **kwargs):
        """
        Throttle callback execution to prevent flooding.
        
        Args:
            key: Unique key for the throttled operation
            callback: Function to call after throttle delay
            *args, **kwargs: Arguments to pass to callback
        """
        # Cancel existing throttled task if it exists
        if key in self._throttle_tasks:
            self._throttle_tasks[key].cancel()

        async def throttled_execution():
            await asyncio.sleep(self.throttle_ms / 1000.0)
            if callback:
                callback(*args, **kwargs)
            if key in self._throttle_tasks:
                del self._throttle_tasks[key]

        task = asyncio.create_task(throttled_execution())
        self._throttle_tasks[key] = task

    async def stream_process(
        self,
        request: StreamRequest,
        callbacks: Optional[StreamCallbacks] = None
    ) -> None:
        """
        Stream process tensors with real-time callbacks.
        
        Args:
            request: The streaming request containing context, model, and tensors
            callbacks: Optional callback functions for various stream events
        """
        if callbacks is None:
            callbacks = StreamCallbacks()

        await self._ensure_session()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "x-api-key": self.api_key,
        }

        try:
            async with self._session.post(
                f"{self.base_url}/streamProcess",
                headers=headers,
                json=request.to_dict()
            ) as response:
                
                if not response.ok:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")

                buffer = ""
                
                async for chunk in response.content.iter_chunked(1024):
                    buffer += chunk.decode('utf-8')
                    
                    # Process complete lines
                    while "\n\n" in buffer:
                        line_end = buffer.index("\n\n")
                        line = buffer[:line_end]
                        buffer = buffer[line_end + 2:]
                        
                        if line.startswith("data: "):
                            try:
                                data_dict = json.loads(line[6:])
                                data = StreamEventData.from_dict(data_dict)
                                
                                await self._handle_stream_event(data, callbacks)
                                
                                if data.type == EventType.COMPLETE:
                                    return
                                    
                            except json.JSONDecodeError as e:
                                logger.warning(f"Failed to parse streaming data: {line}, error: {e}")
                            except Exception as e:
                                logger.error(f"Error handling stream event: {e}")
                                if callbacks.on_error:
                                    callbacks.on_error(e)

        except Exception as error:
            logger.error(f"Streaming error: {error}")
            if callbacks.on_error:
                callbacks.on_error(error)

    async def _handle_stream_event(self, data: StreamEventData, callbacks: StreamCallbacks):
        """
        Handle individual stream events and call appropriate callbacks.
        
        Args:
            data: The stream event data
            callbacks: Callback functions to invoke
        """
        if data.type == EventType.START:
            logger.info(f"🚀 Starting {data.total_tensors} tensors with {data.model}")
            if callbacks.on_start:
                callbacks.on_start(data)
                
        elif data.type == EventType.PROGRESS:
            logger.info(f"⏳ Processing tensor {data.index}...")
            if callbacks.on_progress:
                callbacks.on_progress(data)
                
        elif data.type == EventType.SEARCH_PROGRESS:
            logger.info(f"🔍 Searching for tensor {data.index}...")
            if callbacks.on_search_progress:
                callbacks.on_search_progress(data)
                
        elif data.type == EventType.SEARCH_COMPLETE:
            logger.info(f"✅ Search completed for tensor {data.index}")
            if callbacks.on_search_complete:
                callbacks.on_search_complete(data)
                
        elif data.type == EventType.TENSOR_CHUNK:
            logger.debug(f"📝 Tensor {data.index} chunk received")
            # Throttle chunk updates to prevent UI flooding
            if callbacks.on_tensor_chunk and data.index is not None:
                await self._throttle(f"chunk-{data.index}", callbacks.on_tensor_chunk, data)
                
        elif data.type == EventType.TENSOR_COMPLETE:
            logger.info(f"✅ Tensor {data.index} completed")
            if callbacks.on_tensor_complete:
                callbacks.on_tensor_complete(data)
                
        elif data.type == EventType.TENSOR_ERROR:
            error_msg = data.result.get("error", "Unknown error") if data.result else "Unknown error"
            logger.warning(f"❌ Tensor {data.index} failed: {error_msg}")
            if callbacks.on_tensor_error:
                callbacks.on_tensor_error(data)
                
        elif data.type == EventType.COMPLETE:
            logger.info("🎉 All tensors completed!")
            if callbacks.on_complete:
                callbacks.on_complete(data)
                
        elif data.type in (EventType.ERROR, EventType.FATAL_ERROR):
            error_msg = data.error or data.details or "Streaming error"
            error = Exception(error_msg)
            logger.error(f"Stream error: {error_msg}")
            if callbacks.on_error:
                callbacks.on_error(error)

    async def process_single(self, request: StreamRequest) -> Any:
        """
        Process a single tensor (non-streaming).
        
        Args:
            request: The request containing context, model, and tensors
            
        Returns:
            The response data
        """
        await self._ensure_session()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "x-api-key": self.api_key,
        }

        async with self._session.post(
            f"{self.base_url}/process",
            headers=headers,
            json=request.to_dict()
        ) as response:
            
            if not response.ok:
                error_text = await response.text()
                raise Exception(f"HTTP {response.status}: {error_text}")
                
            return await response.json()

    async def destroy(self):
        """
        Clean up resources and cancel pending operations.
        """
        # Cancel all throttled tasks
        for task in self._throttle_tasks.values():
            task.cancel()
        self._throttle_tasks.clear()

        # Close aiohttp session
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None