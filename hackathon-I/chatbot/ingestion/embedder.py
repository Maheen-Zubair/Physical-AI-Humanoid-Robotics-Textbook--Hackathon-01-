import cohere
from typing import List, Union
import asyncio
import time
import logging
import sys
import os

# Add parent dir to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.config import get_settings


logger = logging.getLogger(__name__)


class Embedder:
    """
    Class to handle text embedding using Cohere API.
    """

    def __init__(self):
        """
        Initialize the embedder with API configuration.
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
        """
        try:
            if isinstance(text, str):
                # Single text embedding
                response = self.client.embed(
                    texts=[text],
                    model=self.model,
                    input_type="search_document"  # Using search_document for document chunks
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
            logger.error(f"Error generating embedding with Cohere: {e}")
            raise

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


# Global instance
embedder = Embedder()