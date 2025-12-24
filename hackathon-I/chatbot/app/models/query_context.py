from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class RetrievedChunk(BaseModel):
    """
    Model representing a chunk retrieved from the knowledge base.
    """
    chunk_id: str = Field(..., description="Reference to BookChunk")
    content: str = Field(..., description="Raw text content")
    chapter_title: str = Field(..., description="For citation")
    section_title: Optional[str] = Field(None, description="For citation")
    source_url: Optional[str] = Field(None, description="For citation link (None for selection mode)")
    similarity_score: Optional[float] = Field(None, description="0-1, only for retrieval mode")


class QueryContext(BaseModel):
    """
    Model representing context assembled for a single query.
    """
    mode: Literal['selection', 'retrieval'] = Field(
        ...,
        description="How context was obtained"
    )
    chunks: List[RetrievedChunk] = Field(
        ...,
        description="Retrieved or selected content"
    )
    total_tokens: int = Field(
        ...,
        description="Sum of chunk token counts"
    )
    query: str = Field(
        ...,
        description="Original user query"
    )
    session_id: str = Field(
        ...,
        description="Session identifier"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of context creation"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "mode": "retrieval",
                "chunks": [
                    {
                        "chunk_id": "123e4567-e89b-12d3-a456-426614174000",
                        "content": "Robotics is an interdisciplinary branch of engineering...",
                        "chapter_title": "Introduction to Robotics",
                        "section_title": "Basic Concepts",
                        "source_url": "https://book.example.com/docs/intro",
                        "similarity_score": 0.85
                    }
                ],
                "total_tokens": 150,
                "query": "What is robotics?",
                "session_id": "session-12345",
                "timestamp": "2023-10-20T10:00:00Z"
            }
        }