from typing import List, Dict, Any, Optional, Tuple
from qdrant_client.http import models
from ..services.vector_store import vector_store
from ..models.query_context import RetrievedChunk
import logging


logger = logging.getLogger(__name__)


class SearchService:
    """
    Service to handle similarity search in the Qdrant vector store.
    """

    def __init__(self, similarity_threshold: float = 0.65):
        """
        Initialize the search service.

        Args:
            similarity_threshold: Threshold below which questions are considered out-of-scope
        """
        self.vs = vector_store
        self.similarity_threshold = similarity_threshold

    async def search_similar_chunks(
        self,
        query_embedding: List[float],
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedChunk]:
        """
        Search for similar chunks based on the query embedding.

        Args:
            query_embedding: The embedding vector for the query
            limit: Maximum number of results to return
            filters: Optional filters to apply to the search

        Returns:
            List of RetrievedChunk objects with similarity scores
        """
        try:
            # Perform the search in Qdrant
            results = await self.vs.search_embeddings(
                query_vector=query_embedding,
                limit=limit,
                filters=filters
            )

            # Convert results to RetrievedChunk objects
            retrieved_chunks = []
            for result in results:
                payload = result.get('payload', {})
                retrieved_chunks.append(RetrievedChunk(
                    chunk_id=result['id'],
                    content="",  # Content will be retrieved from Neon separately
                    chapter_title=payload.get('chapter_title', ''),
                    section_title=payload.get('section_title', ''),
                    source_url=payload.get('source_url', ''),
                    similarity_score=result.get('score', 0.0)
                ))

            logger.info(f"Found {len(retrieved_chunks)} similar chunks for query")
            return retrieved_chunks

        except Exception as e:
            logger.error(f"Error during similarity search: {e}")

            # Graceful degradation: return empty list instead of raising error
            logger.warning("Qdrant is unavailable, returning empty results for similarity search")
            return []

    async def search_similar_chunks_with_content(
        self,
        query_embedding: List[float],
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedChunk]:
        """
        Search for similar chunks and retrieve their content from Neon.

        Args:
            query_embedding: The embedding vector for the query
            limit: Maximum number of results to return
            filters: Optional filters to apply to the search

        Returns:
            List of RetrievedChunk objects with content and similarity scores
        """
        # First, get the similar chunk IDs from Qdrant
        similar_chunks = await self.search_similar_chunks(
            query_embedding=query_embedding,
            limit=limit,
            filters=filters
        )

        # Then, retrieve the content for these chunks from Neon
        from .metadata_service import metadata_service
        chunk_ids = [chunk.chunk_id for chunk in similar_chunks]

        # Retrieve content from Neon
        chunks_with_content = await metadata_service.get_chunks_by_ids(chunk_ids)

        # Update the similarity scores from the Qdrant search
        chunk_map = {chunk.chunk_id: chunk for chunk in chunks_with_content}
        for similar_chunk in similar_chunks:
            if similar_chunk.chunk_id in chunk_map:
                existing_chunk = chunk_map[similar_chunk.chunk_id]
                # Create a new RetrievedChunk with both content and similarity score
                similar_chunk.content = existing_chunk.content
                similar_chunk.chapter_title = existing_chunk.chapter_title
                similar_chunk.section_title = existing_chunk.section_title
                similar_chunk.source_url = existing_chunk.source_url

        return similar_chunks

    def detect_out_of_scope(
        self,
        chunks: List[RetrievedChunk]
    ) -> Tuple[bool, float]:
        """
        Detect if a query is out-of-scope based on similarity scores.

        Args:
            chunks: List of retrieved chunks with similarity scores

        Returns:
            Tuple of (is_out_of_scope, highest_similarity_score)
        """
        if not chunks:
            return True, 0.0

        # Get the highest similarity score
        highest_score = max((chunk.similarity_score or 0.0 for chunk in chunks), default=0.0)

        # Check if highest score is below threshold
        is_out_of_scope = highest_score < self.similarity_threshold

        return is_out_of_scope, highest_score


# Global instance
search_service = SearchService()