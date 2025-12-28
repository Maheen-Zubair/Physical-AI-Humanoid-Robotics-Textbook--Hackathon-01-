from pydantic import BaseModel, Field
from typing import List, Optional
from .source import Source
from datetime import datetime


class ChatResponse(BaseModel):
    """
    Model representing a chat response from the backend.
    """
    response: str = Field(..., description="The chatbot's response to the user's query")
    sources: List[Source] = Field(default=[], description="List of sources cited in the response")
    session_id: str = Field(..., description="Session identifier for conversation context")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the response")
    out_of_scope: Optional[bool] = Field(
        default=False,
        description="Indicates if the question was out of scope for the book content"
    )
    selection_mode: Optional[bool] = Field(
        default=False,
        description="Indicates if the response was generated using only selected text"
    )
    selection_ignored: Optional[bool] = Field(
        default=False,
        description="Indicates if user selection was empty/whitespace and was ignored"
    )
    error_code: Optional[str] = Field(
        default=None,
        description="Error code if an error occurred (e.g., RATE_LIMIT_COHERE, EMBEDDING_FAILED)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "response": "Inverse kinematics is the process of determining joint angles...",
                "sources": [
                    {
                        "title": "Chapter 5: Kinematics",
                        "url": "https://book.example.com/docs/kinematics"
                    }
                ],
                "session_id": "session-12345",
                "timestamp": "2023-10-20T10:00:00Z",
                "out_of_scope": False,
                "selection_mode": False,
                "selection_ignored": False
            }
        }