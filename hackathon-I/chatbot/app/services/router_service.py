from typing import Optional
from ..models.chat_request import ChatRequest
from enum import Enum
import logging
import tiktoken


logger = logging.getLogger(__name__)


class ContextMode(str, Enum):
    """
    Enum for different context modes.
    """
    SELECTION = "selection"
    RETRIEVAL = "retrieval"
    SELECTION_TRUNCATED = "selection_truncated"


class QueryRouter:
    """
    Service to route queries to the correct processing path based on context mode.
    """

    def __init__(self):
        """
        Initialize the query router.
        """
        self.encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")
        self.max_selection_tokens = 4000  # Maximum tokens for user selection

    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text.

        Args:
            text: Input text

        Returns:
            Number of tokens
        """
        return len(self.encoder.encode(text))

    def determine_context_mode(self, request: ChatRequest) -> ContextMode:
        """
        Determine the context mode based on the request.

        Args:
            request: The chat request

        Returns:
            ContextMode indicating how to process the request
        """
        if request.context_selection:
            # Check if the selection is empty or whitespace-only
            stripped_selection = request.context_selection.strip()
            if not stripped_selection:
                logger.info("Empty/whitespace selection detected, routing to retrieval mode")
                # According to spec, empty selection should be treated as no selection
                return ContextMode.RETRIEVAL

            # Check token count
            token_count = self.count_tokens(request.context_selection)
            if token_count > self.max_selection_tokens:
                logger.warning(f"Selection too long ({token_count} tokens), truncating")
                return ContextMode.SELECTION_TRUNCATED

            logger.info(f"Valid selection detected ({token_count} tokens), routing to selection mode")
            return ContextMode.SELECTION

        # No context selection provided, use retrieval mode
        logger.info("No selection provided, routing to retrieval mode")
        return ContextMode.RETRIEVAL

    def route_request(self, request: ChatRequest) -> dict:
        """
        Route the request to the appropriate processing path.

        Args:
            request: The chat request

        Returns:
            Dictionary with routing information
        """
        mode = self.determine_context_mode(request)

        result = {
            "mode": mode,
            "process_selection": mode in [ContextMode.SELECTION, ContextMode.SELECTION_TRUNCATED],
            "perform_search": mode == ContextMode.RETRIEVAL,
            "request": request
        }

        logger.info(f"Request routed to {mode.value} mode")
        return result

    def validate_selection(self, selection: Optional[str]) -> tuple[bool, str]:
        """
        Validate the user's text selection.

        Args:
            selection: The selected text

        Returns:
            Tuple of (is_valid, message)
        """
        if not selection:
            return True, "No selection provided, using retrieval mode"

        stripped_selection = selection.strip()
        if not stripped_selection:
            return True, "Selection was empty/whitespace, using retrieval mode"

        token_count = self.count_tokens(selection)
        if token_count > self.max_selection_tokens:
            return False, f"Selection too long ({token_count} tokens, max {self.max_selection_tokens})"

        return True, "Selection is valid"


# Global instance
router_service = QueryRouter()