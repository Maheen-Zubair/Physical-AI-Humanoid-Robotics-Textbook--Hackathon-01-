import re
from typing import List, Tuple
from ..models.source import Source
from ..models.query_context import QueryContext
import logging


logger = logging.getLogger(__name__)


class CitationService:
    """
    Service to handle citation validation and enforcement.
    """

    def __init__(self):
        """
        Initialize the citation service.
        """
        # Pattern to match [Source: Title](URL) format
        self.citation_pattern = r'\[Source:\s*([^\]]+)\]\(([^)]+)\)'

    def validate_citations(self, response: str, context: QueryContext) -> Tuple[str, bool]:
        """
        Validate citations in the response and add fallback if needed.

        Args:
            response: The response text to validate
            context: The query context for fallback citation generation

        Returns:
            Tuple of (processed_response, citation_valid)
        """
        # Check if response contains any citations
        has_citations = bool(re.search(self.citation_pattern, response))

        # If no citations and we're in retrieval mode, add fallback
        if not has_citations and context.mode == "retrieval" and context.chunks:
            # Add fallback citation from the first chunk
            first_chunk = context.chunks[0]
            if first_chunk.source_url:
                # Append fallback citation
                fallback_citation = f"\n\n[Source: {first_chunk.chapter_title}]({first_chunk.source_url})"
                response += fallback_citation
                logger.warning("Added fallback citation - LLM did not include one")
                return response, False  # Citation was added, so original wasn't valid

        # If no citations and in selection mode, that's acceptable
        if not has_citations and context.mode == "selection":
            # No citations expected in selection mode
            return response, True

        return response, has_citations

    def extract_citations(self, response: str) -> List[Source]:
        """
        Extract all citations from a response.

        Args:
            response: The response text to extract citations from

        Returns:
            List of Source objects
        """
        matches = re.findall(self.citation_pattern, response)
        sources = []

        for title, url in matches:
            sources.append(Source(title=title.strip(), url=url.strip()))

        return sources

    def format_citation(self, title: str, url: str) -> str:
        """
        Format a citation in the required format.

        Args:
            title: The title of the source
            url: The URL of the source

        Returns:
            Formatted citation string
        """
        return f"[Source: {title}]({url})"

    def append_citations(self, response: str, sources: List[Source]) -> str:
        """
        Append citations to a response if they're not already present.

        Args:
            response: The response text
            sources: List of sources to cite

        Returns:
            Response with citations appended
        """
        # Check if response already has citations
        has_citations = bool(re.search(self.citation_pattern, response))

        if not has_citations and sources:
            # Append all sources as citations
            citation_texts = [self.format_citation(source.title, source.url) for source in sources]
            citations_str = " " + " ".join(citation_texts)
            return response + citations_str

        return response

    def validate_citation_format(self, text: str) -> bool:
        """
        Validate that all citations in text follow the correct format.

        Args:
            text: Text to validate

        Returns:
            True if all citations are properly formatted, False otherwise
        """
        citations = re.findall(self.citation_pattern, text)
        # If we found citations with the pattern, they're properly formatted
        return len(citations) > 0


# Global instance
citation_service = CitationService()