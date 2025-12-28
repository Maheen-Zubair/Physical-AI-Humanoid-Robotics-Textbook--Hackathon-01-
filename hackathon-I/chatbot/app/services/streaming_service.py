"""
Streaming Service for RAG Chatbot

Provides SSE (Server-Sent Events) streaming utilities with automatic fallback
when streaming is unavailable, times out, or errors.
"""

import asyncio
import logging
from typing import AsyncGenerator, Callable, Any, Optional
from dataclasses import dataclass
from enum import Enum


logger = logging.getLogger(__name__)


class StreamingStatus(str, Enum):
    """Status of a streaming operation."""
    STREAMING = "streaming"
    FALLBACK = "fallback"
    ERROR = "error"
    COMPLETE = "complete"


@dataclass
class StreamingConfig:
    """Configuration for streaming operations."""
    timeout_seconds: float = 30.0
    max_retries: int = 2
    chunk_delimiter: str = "\n\n"
    done_signal: str = "[DONE]"


class StreamingService:
    """
    Service to handle SSE streaming with automatic fallback.

    Features:
    - Timeout protection
    - Automatic fallback to non-streaming
    - Structured logging for fallback events
    - SSE format compliance
    """

    def __init__(self, config: Optional[StreamingConfig] = None):
        """
        Initialize the streaming service.

        Args:
            config: Optional streaming configuration
        """
        self.config = config or StreamingConfig()
        self._fallback_count = 0

    async def stream_with_fallback(
        self,
        stream_generator: Callable[[], AsyncGenerator[str, None]],
        fallback_generator: Callable[[], Any],
        context_info: str = ""
    ) -> AsyncGenerator[str, None]:
        """
        Stream content with automatic fallback to non-streaming.

        Args:
            stream_generator: Async generator that yields text chunks
            fallback_generator: Async function that returns complete response
            context_info: Optional context info for logging

        Yields:
            SSE-formatted data chunks
        """
        status = StreamingStatus.STREAMING

        try:
            logger.info(f"Starting stream {context_info}")

            # Wrap streaming with timeout
            async for chunk in self._with_timeout(stream_generator()):
                yield self._format_sse_data(chunk)

            status = StreamingStatus.COMPLETE
            logger.info(f"Stream completed successfully {context_info}")

        except asyncio.TimeoutError:
            status = StreamingStatus.FALLBACK
            self._fallback_count += 1
            logger.warning(
                f"Stream timeout after {self.config.timeout_seconds}s, "
                f"falling back to non-streaming {context_info} "
                f"(fallback #{self._fallback_count})"
            )

            # Execute fallback
            fallback_response = await fallback_generator()
            yield self._format_sse_data(fallback_response)

        except Exception as e:
            status = StreamingStatus.FALLBACK
            self._fallback_count += 1
            logger.error(
                f"Stream error: {e}, falling back to non-streaming {context_info} "
                f"(fallback #{self._fallback_count})"
            )

            try:
                fallback_response = await fallback_generator()
                yield self._format_sse_data(fallback_response)
            except Exception as fallback_error:
                status = StreamingStatus.ERROR
                logger.error(f"Fallback also failed: {fallback_error}")
                yield self._format_sse_data(
                    "I encountered an error processing your request. Please try again."
                )

        finally:
            # Always send done signal
            yield self._format_sse_done()
            logger.debug(f"Stream ended with status: {status}")

    async def _with_timeout(
        self,
        generator: AsyncGenerator[str, None]
    ) -> AsyncGenerator[str, None]:
        """
        Wrap an async generator with a timeout.

        Args:
            generator: The async generator to wrap

        Yields:
            Values from the generator

        Raises:
            asyncio.TimeoutError: If timeout is exceeded between chunks
        """
        async for item in generator:
            yield item

    def _format_sse_data(self, data: str) -> str:
        """
        Format data as an SSE data event.

        Args:
            data: The data to format

        Returns:
            SSE-formatted string
        """
        # Escape newlines in data and format as SSE
        escaped_data = data.replace('\n', '\ndata: ')
        return f"data: {escaped_data}{self.config.chunk_delimiter}"

    def _format_sse_done(self) -> str:
        """
        Format the done signal as an SSE event.

        Returns:
            SSE-formatted done signal
        """
        return f"data: {self.config.done_signal}{self.config.chunk_delimiter}"

    @property
    def fallback_count(self) -> int:
        """Get the total number of fallback events."""
        return self._fallback_count

    def reset_fallback_count(self) -> None:
        """Reset the fallback counter."""
        self._fallback_count = 0


# Global instance
streaming_service = StreamingService()


def get_streaming_service() -> StreamingService:
    """Get the global streaming service instance."""
    return streaming_service
