from typing import Tuple, List
from ..models.query_context import RetrievedChunk
from .search_service import search_service
import logging


logger = logging.getLogger(__name__)


class ScopeService:
    """
    Service to handle out-of-scope question detection using both similarity thresholds and LLM analysis.
    """

    def __init__(self, similarity_threshold: float = 0.65):
        """
        Initialize the scope service.

        Args:
            similarity_threshold: Threshold below which questions are considered out-of-scope based on similarity
        """
        self.similarity_threshold = similarity_threshold

    def detect_out_of_scope(
        self,
        chunks: List[RetrievedChunk],
        llm_response: str = None,
        llm_indicates_out_of_scope: bool = False
    ) -> Tuple[bool, str, float]:
        """
        Detect if a question is out-of-scope using both similarity and LLM analysis.

        Args:
            chunks: List of retrieved chunks with similarity scores
            llm_response: The response from the LLM (optional)
            llm_indicates_out_of_scope: Whether the LLM indicated the question was out of scope

        Returns:
            Tuple of (is_out_of_scope, reason, confidence_score)
        """
        # Check similarity-based out-of-scope detection
        similarity_out_of_scope, highest_similarity = search_service.detect_out_of_scope(chunks)

        # If no chunks were found, it's definitely out of scope
        if not chunks:
            return True, "No relevant content found in the book", 1.0

        # If similarity is below threshold, consider it out of scope
        if similarity_out_of_scope and llm_indicates_out_of_scope:
            # Both indicators agree - high confidence
            confidence = (self.similarity_threshold - highest_similarity) / self.similarity_threshold
            confidence = min(confidence + 0.2, 1.0)  # Boost for LLM agreement
            return True, f"Low similarity ({highest_similarity:.2f}) and LLM uncertainty", confidence
        elif similarity_out_of_scope:
            # Only similarity indicates out of scope
            confidence = (self.similarity_threshold - highest_similarity) / self.similarity_threshold
            return True, f"Low similarity ({highest_similarity:.2f})", confidence
        elif llm_indicates_out_of_scope:
            # Only LLM indicates out of scope
            return True, "LLM indicated insufficient context", 0.7
        else:
            # Both indicators suggest it's in scope
            return False, "Relevant content found", highest_similarity

    def suggest_related_topics(
        self,
        query: str,
        chunks: List[RetrievedChunk],
        max_suggestions: int = 3
    ) -> List[str]:
        """
        Suggest related topics when a question is out-of-scope.

        Args:
            query: The original query
            chunks: Retrieved chunks that might contain related information
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of suggested topics/chapters
        """
        suggestions = set()

        # Extract chapter and section titles from retrieved chunks
        for chunk in chunks:
            if chunk.chapter_title:
                suggestions.add(chunk.chapter_title)
            if chunk.section_title:
                suggestions.add(chunk.section_title)

        # Limit to max suggestions
        suggestions_list = list(suggestions)[:max_suggestions]
        return suggestions_list


# Global instance
scope_service = ScopeService()