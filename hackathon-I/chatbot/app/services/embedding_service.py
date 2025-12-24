import cohere
from cohere.core.api_error import ApiError
from typing import List, Union
from ..config import get_settings
from ..exceptions import RateLimitError, EmbeddingError
import logging
import time
import asyncio


logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service to handle text embedding using Cohere API for query and document embedding.
    """

    def __init__(self):
        """
        Initialize the embedding service with API configuration.
        """
        settings = get_settings()
        self.client = cohere.Client(api_key=settings.cohere_api_key)
        # Using embed-english-v3.0 as specified in the requirements
        self.model = "embed-english-v3.0"
        self.settings = settings

    def embed_text(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings for text(s) using Cohere.

        Args:
            text: Single text string or list of text strings to embed

        Returns:
            Single embedding vector or list of embedding vectors

        Raises:
            RateLimitError: When Cohere API rate limit is exceeded
            EmbeddingError: For other embedding failures
        """
        try:
            if isinstance(text, str):
                # Single text embedding
                response = self.client.embed(
                    texts=[text],
                    model=self.model,
                    input_type="search_query"  # Using search_query for individual queries
                )
                return response.embeddings[0]
            else:
                # Multiple texts embedding
                response = self.client.embed(
                    texts=text,
                    model=self.model,
                    input_type="search_document"  # Using search_document for document chunks
                )
                return response.embeddings
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error generating embedding with Cohere: {e}")

            # Check for rate limit error (HTTP 429)
            if "429" in error_str or "rate limit" in error_str.lower() or "Too Many Requests" in error_str:
                logger.warning("Cohere API rate limit exceeded - Trial tier limit reached")
                raise RateLimitError(
                    provider="cohere",
                    message="Cohere embedding API rate limit exceeded",
                    details="Trial API key limited to 1000 calls/month. Select text to use selection mode instead."
                )

            # Check for authentication errors
            if "401" in error_str or "403" in error_str or "unauthorized" in error_str.lower():
                raise EmbeddingError(
                    message="Cohere API authentication failed",
                    details="Invalid or expired API key"
                )

            # Generic embedding error
            raise EmbeddingError(
                message=f"Failed to generate embeddings: {error_str}",
                details=str(e)
            )

    async def embed_text_async(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Async version of embed_text to handle rate limiting.
        """
        # Implement basic rate limiting to respect free tier limits
        # Add a small delay to avoid hitting rate limits
        await asyncio.sleep(0.1)  # 100ms delay to stay under rate limit

        return self.embed_text(text)

    def embed_batch(self, texts: List[str], batch_size: int = 96) -> List[List[float]]:
        """
        Embed a batch of texts with rate limiting.
        Cohere free tier allows up to 100 texts per request for embeddings.

        Args:
            texts: List of text strings to embed
            batch_size: Number of texts to process in each batch (max 96 to stay under limit)

        Returns:
            List of embedding vectors
        """
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            try:
                # Process batch with Cohere
                response = self.client.embed(
                    texts=batch,
                    model=self.model,
                    input_type="search_document"
                )

                # Add batch results to embeddings list
                embeddings.extend(response.embeddings)

                # Small delay between batches to respect rate limits
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error processing batch {i//batch_size + 1}: {e}")
                # Log failed items and continue with the rest
                continue

        return embeddings


    async def ping(self) -> bool:
        """
        Test Cohere API connectivity with a minimal request.

        Returns:
            True if the API is reachable and functional, False otherwise
        """
        try:
            # Use a minimal embed request to test connectivity
            response = self.client.embed(
                texts=["test"],
                model=self.model,
                input_type="search_query"
            )
            # Check if we got a valid response with embeddings
            return response.embeddings is not None and len(response.embeddings) > 0
        except Exception as e:
            logger.error(f"Cohere API ping failed: {e}")
            return False


# Global instance
embedding_service = EmbeddingService()