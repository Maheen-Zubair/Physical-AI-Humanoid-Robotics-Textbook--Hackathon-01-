from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class BookChunk(BaseModel):
    """
    Model representing a chunk of book content stored in Neon Postgres.
    """
    chunk_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the chunk")
    chapter_title: str = Field(..., max_length=255, description="Human-readable chapter name")
    section_title: Optional[str] = Field(None, max_length=255, description="Section within chapter (H2/H3 header)")
    content: str = Field(..., description="Raw markdown/text content of chunk")
    source_url: str = Field(..., max_length=512, description="Full URL to the book page")
    chunk_index: int = Field(..., description="Order within the chapter")
    token_count: int = Field(..., description="Approximate token count for context budgeting")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Ingestion timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last modification timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "chunk_id": "123e4567-e89b-12d3-a456-426614174000",
                "chapter_title": "Introduction to Robotics",
                "section_title": "Basic Concepts",
                "content": "Robotics is an interdisciplinary branch of engineering...",
                "source_url": "https://book.example.com/docs/intro",
                "chunk_index": 1,
                "token_count": 150
            }
        }


class BookChunkCreate(BaseModel):
    """
    Model for creating a new book chunk.
    """
    chapter_title: str = Field(..., max_length=255, description="Human-readable chapter name")
    section_title: Optional[str] = Field(None, max_length=255, description="Section within chapter (H2/H3 header)")
    content: str = Field(..., description="Raw markdown/text content of chunk")
    source_url: str = Field(..., max_length=512, description="Full URL to the book page")
    chunk_index: int = Field(..., description="Order within the chapter")
    token_count: int = Field(..., description="Approximate token count for context budgeting")


class BookChunkUpdate(BaseModel):
    """
    Model for updating an existing book chunk.
    """
    chapter_title: Optional[str] = Field(None, max_length=255)
    section_title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = Field(None)
    source_url: Optional[str] = Field(None, max_length=512)
    chunk_index: Optional[int] = Field(None)
    token_count: Optional[int] = Field(None)


# SQL for creating the table
CREATE_BOOK_CHUNKS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS book_chunks (
    chunk_id UUID PRIMARY KEY,
    chapter_title VARCHAR(255) NOT NULL,
    section_title VARCHAR(255),
    content TEXT NOT NULL,
    source_url VARCHAR(512) NOT NULL,
    chunk_index INTEGER NOT NULL,
    token_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_chunk_chapter ON book_chunks(chapter_title);
CREATE INDEX IF NOT EXISTS idx_chunk_url ON book_chunks(source_url);
"""

# SQL for updating the updated_at timestamp
UPDATE_TIMESTAMP_TRIGGER_SQL = """
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_book_chunks_updated_at ON book_chunks;
CREATE TRIGGER update_book_chunks_updated_at
    BEFORE UPDATE ON book_chunks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
"""