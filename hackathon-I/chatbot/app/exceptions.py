"""
Custom exceptions for the RAG Chatbot application.
Provides structured error handling with user-friendly messages.
"""

from enum import Enum
from typing import Optional


class ErrorCode(str, Enum):
    """Error codes for different failure types."""
    RATE_LIMIT_COHERE = "RATE_LIMIT_COHERE"
    RATE_LIMIT_GEMINI = "RATE_LIMIT_GEMINI"
    EMBEDDING_FAILED = "EMBEDDING_FAILED"
    VECTOR_SEARCH_FAILED = "VECTOR_SEARCH_FAILED"
    DATABASE_ERROR = "DATABASE_ERROR"
    LLM_ERROR = "LLM_ERROR"
    CONTEXT_OVERFLOW = "CONTEXT_OVERFLOW"
    AUTH_ERROR = "AUTH_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class ChatbotException(Exception):
    """Base exception for chatbot errors."""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        user_message: str,
        details: Optional[str] = None,
        recoverable: bool = False
    ):
        super().__init__(message)
        self.error_code = error_code
        self.user_message = user_message
        self.details = details
        self.recoverable = recoverable


class RateLimitError(ChatbotException):
    """Raised when an API rate limit is hit."""

    def __init__(
        self,
        provider: str,
        message: str = "Rate limit exceeded",
        details: Optional[str] = None
    ):
        error_code = ErrorCode.RATE_LIMIT_COHERE if provider == "cohere" else ErrorCode.RATE_LIMIT_GEMINI
        user_message = (
            f"The {provider.title()} API rate limit has been reached. "
            "This is a temporary issue. Please try again in a few minutes, "
            "or select text from the book and ask a question about it (selection mode works without embeddings)."
        )
        super().__init__(
            message=message,
            error_code=error_code,
            user_message=user_message,
            details=details,
            recoverable=True
        )
        self.provider = provider


class EmbeddingError(ChatbotException):
    """Raised when embedding generation fails."""

    def __init__(self, message: str = "Failed to generate embeddings", details: Optional[str] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.EMBEDDING_FAILED,
            user_message="Unable to process your question. Please try selecting text from the book and asking about it instead.",
            details=details,
            recoverable=True
        )


class VectorSearchError(ChatbotException):
    """Raised when vector search fails."""

    def __init__(self, message: str = "Vector search failed", details: Optional[str] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.VECTOR_SEARCH_FAILED,
            user_message="Unable to search the book content. Please try again.",
            details=details,
            recoverable=True
        )


class DatabaseError(ChatbotException):
    """Raised when database operations fail."""

    def __init__(self, message: str = "Database error", details: Optional[str] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_ERROR,
            user_message="A database error occurred. Please try again.",
            details=details,
            recoverable=True
        )


class LLMError(ChatbotException):
    """Raised when LLM generation fails."""

    def __init__(self, message: str = "LLM generation failed", details: Optional[str] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.LLM_ERROR,
            user_message="Unable to generate a response. Please try again.",
            details=details,
            recoverable=True
        )


class ContextOverflowError(ChatbotException):
    """Raised when context exceeds token limits."""

    def __init__(self, message: str = "Context overflow", details: Optional[str] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.CONTEXT_OVERFLOW,
            user_message="Your question or selected text is too long. Please try a shorter query.",
            details=details,
            recoverable=True
        )
