from typing import List, Optional
from ..models.query_context import QueryContext, RetrievedChunk
from ..models.chat_session import ChatMessage, MessageRole
from .session_service import session_service
import logging
import tiktoken


logger = logging.getLogger(__name__)


class ContextService:
    """
    Service to handle context assembly for queries, combining chunks and respecting token budgets.
    """

    def __init__(self):
        """
        Initialize the context service.
        """
        self.encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")  # Close enough for token estimation
        self.max_context_tokens = 4000  # Maximum context window
        self.max_query_tokens = 2000    # Maximum for query context (leaving room for response)

    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text.

        Args:
            text: Input text

        Returns:
            Number of tokens
        """
        return len(self.encoder.encode(text))

    def assemble_context(
        self,
        query: str,
        retrieved_chunks: List[RetrievedChunk],
        session_id: Optional[str] = None,
        max_tokens: int = 2000
    ) -> QueryContext:
        """
        Assemble context for a query from retrieved chunks, respecting token budget.

        Args:
            query: The user's query
            retrieved_chunks: List of retrieved chunks with content
            session_id: Session ID for conversation context
            max_tokens: Maximum tokens for the assembled context

        Returns:
            QueryContext object with assembled context
        """
        # Start with the query tokens
        query_tokens = self.count_tokens(query)
        current_tokens = query_tokens

        # Get conversation history if session_id is provided
        conversation_context = ""
        if session_id:
            session = session_service.get_session(session_id)
            if session and session.messages:
                # Get the last few exchanges to stay within token limits
                conversation_messages = []
                for msg in reversed(session.messages[-4:]):  # Last 4 messages (2 exchanges)
                    msg_text = f"{msg.role.value}: {msg.content}"
                    msg_tokens = self.count_tokens(msg_text)
                    if current_tokens + msg_tokens > max_tokens:
                        break
                    conversation_messages.insert(0, msg_text)  # Maintain order
                    current_tokens += msg_tokens

                if conversation_messages:
                    conversation_context = "Previous conversation:\n" + "\n".join(conversation_messages) + "\n\n"

        # Add retrieved chunks until we reach the token limit
        selected_chunks = []
        context_text = conversation_context

        for chunk in retrieved_chunks:
            chunk_text = f"Source: {chunk.chapter_title} - {chunk.section_title}\n{chunk.content}\n\n"
            chunk_tokens = self.count_tokens(chunk_text)

            if current_tokens + chunk_tokens <= max_tokens:
                selected_chunks.append(chunk)
                context_text += chunk_text
                current_tokens += chunk_tokens
            else:
                # If adding this chunk would exceed the limit, stop
                break

        # Calculate total tokens
        total_tokens = self.count_tokens(context_text)

        return QueryContext(
            mode="retrieval",
            chunks=selected_chunks,
            total_tokens=total_tokens,
            query=query,
            session_id=session_id or ""
        )

    def assemble_selection_context(
        self,
        query: str,
        selected_text: str,
        session_id: Optional[str] = None
    ) -> QueryContext:
        """
        Assemble context for a query when user has selected text.

        Args:
            query: The user's query
            selected_text: Text selected by the user
            session_id: Session ID for conversation context

        Returns:
            QueryContext object with selected text as context
        """
        # Get conversation history if session_id is provided
        conversation_context = ""
        if session_id:
            session = session_service.get_session(session_id)
            if session and session.messages:
                # Get the last few exchanges
                conversation_messages = []
                for msg in reversed(session.messages[-4:]):  # Last 4 messages (2 exchanges)
                    conversation_messages.insert(0, f"{msg.role.value}: {msg.content}")

                if conversation_messages:
                    conversation_context = "Previous conversation:\n" + "\n".join(conversation_messages) + "\n\n"

        # Combine conversation context with selected text
        full_context = conversation_context + selected_text
        total_tokens = self.count_tokens(full_context)

        # Create a RetrievedChunk for the selected text
        selected_chunk = RetrievedChunk(
            chunk_id="user_selection",
            content=selected_text,
            chapter_title="User Selection",
            section_title="",
            source_url="",  # Empty string for selection mode (no external source)
            similarity_score=0.0
        )

        return QueryContext(
            mode="selection",
            chunks=[selected_chunk],
            total_tokens=total_tokens,
            query=query,
            session_id=session_id or ""
        )

    def validate_context_size(self, context: QueryContext, max_tokens: int = 4000) -> bool:
        """
        Validate that the context size is within acceptable limits.

        Args:
            context: QueryContext to validate
            max_tokens: Maximum allowed tokens

        Returns:
            True if context is within limits, False otherwise
        """
        return context.total_tokens <= max_tokens

    def truncate_context_if_needed(self, context: QueryContext, max_tokens: int = 4000) -> QueryContext:
        """
        Truncate context if it exceeds the maximum token limit.

        Args:
            context: QueryContext to potentially truncate
            max_tokens: Maximum allowed tokens

        Returns:
            QueryContext that respects the token limit
        """
        if context.total_tokens <= max_tokens:
            return context

        # If it exceeds the limit, we need to reduce the chunks
        # Start by removing the lowest scoring chunks (for retrieval mode)
        if context.mode == "retrieval":
            # Sort chunks by similarity score (descending) and keep the highest scoring ones
            sorted_chunks = sorted(
                context.chunks,
                key=lambda x: x.similarity_score or 0,
                reverse=True
            )

            # Rebuild context with fewer chunks
            truncated_chunks = []
            current_tokens = self.count_tokens(context.query)

            for chunk in sorted_chunks:
                chunk_tokens = self.count_tokens(chunk.content)
                if current_tokens + chunk_tokens <= max_tokens:
                    truncated_chunks.append(chunk)
                    current_tokens += chunk_tokens
                else:
                    break

            # Calculate new total tokens
            new_total_tokens = current_tokens

            return QueryContext(
                mode=context.mode,
                chunks=truncated_chunks,
                total_tokens=new_total_tokens,
                query=context.query,
                session_id=context.session_id,
                timestamp=context.timestamp
            )

        # For selection mode, we can't really truncate the selected text meaningfully
        # so we'll just return the original context (which will exceed the limit)
        # The calling code should handle this appropriately
        return context


# Global instance
context_service = ContextService()