import os
import json
from typing import List, Optional
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """
    Application settings loaded from environment variables.
    """
    # Qdrant Cloud
    qdrant_url: str = Field(..., description="Qdrant Cloud URL")
    qdrant_api_key: str = Field(..., description="Qdrant API key")

    # Neon Postgres
    database_url: str = Field(..., description="Neon Postgres database URL")

    # Cohere API (Embeddings)
    cohere_api_key: str = Field(..., description="Cohere API key for embeddings")

    # Gemini API (Response generation)
    gemini_api_key: str = Field(..., description="Google Gemini API key")

    # Application Config
    book_base_url: str = Field(..., description="Base URL for the book")
    cors_origins: List[str] = Field(default=["https://username.github.io"], description="CORS allowed origins")
    rate_limit_per_minute: int = Field(default=30, description="Rate limit per minute")
    rate_limit_per_day: int = Field(default=500, description="Rate limit per day")

    class Config:
        env_file = ".env"
        case_sensitive = True


def parse_cors_origins(cors_string: str) -> List[str]:
    """Parse CORS origins from environment variable string."""
    try:
        # Try to parse as JSON array
        origins = json.loads(cors_string)
        if isinstance(origins, list):
            return origins
        return [str(origins)]
    except (json.JSONDecodeError, TypeError):
        # If not valid JSON, treat as comma-separated list
        return [origin.strip() for origin in cors_string.split(",")]


def get_settings() -> Settings:
    """
    Get application settings from environment variables.
    """
    # Validate required environment variables
    required_env = [
        "QDRANT_URL",
        "QDRANT_API_KEY",
        "DATABASE_URL",
        "COHERE_API_KEY",
        "GEMINI_API_KEY",
        "BOOK_BASE_URL"
    ]

    missing = [var for var in required_env if not os.getenv(var)]
    if missing:
        raise EnvironmentError(f"Missing required env vars: {missing}")

    # Parse CORS origins from environment
    cors_origins_str = os.getenv("CORS_ORIGINS", '["https://username.github.io"]')
    cors_origins = parse_cors_origins(cors_origins_str)

    return Settings(
        qdrant_url=os.getenv("QDRANT_URL"),
        qdrant_api_key=os.getenv("QDRANT_API_KEY"),
        database_url=os.getenv("DATABASE_URL"),
        cohere_api_key=os.getenv("COHERE_API_KEY"),
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        book_base_url=os.getenv("BOOK_BASE_URL"),
        cors_origins=cors_origins,
        rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "30")),
        rate_limit_per_day=int(os.getenv("RATE_LIMIT_PER_DAY", "500"))
    )