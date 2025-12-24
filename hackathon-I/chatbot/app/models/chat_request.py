from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ChatRequest(BaseModel):
    """
    Model representing a chat request from the frontend.
    """
    query: str = Field(..., description="The user's question or query")
    session_id: Optional[str] = Field(None, description="Session identifier for conversation context")
    context_selection: Optional[str] = Field(
        None,
        description="User-selected text that should be used as exclusive context (when present, no vector search is performed)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is inverse kinematics?",
                "session_id": "session-12345",
                "context_selection": "Inverse kinematics is the mathematical process of determining..."
            }
        }


class SelectedTextRequest(BaseModel):
    """
    Model representing a request that REQUIRES selected text context.
    This endpoint enforces selection-only mode and never performs vector search.
    """
    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The user's question about the selected text"
    )
    context_selection: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Required: User-selected text to use as exclusive context"
    )
    session_id: Optional[str] = Field(
        None,
        description="Session identifier for conversation context"
    )

    @field_validator('context_selection')
    @classmethod
    def validate_context_selection(cls, v: str) -> str:
        """Validate that context_selection is not empty or whitespace-only."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("context_selection cannot be empty or whitespace-only")
        return stripped

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Explain this in simpler terms",
                "context_selection": "Inverse kinematics (IK) is the mathematical process of calculating the joint parameters needed to place the end of a kinematic chain in a desired position and orientation.",
                "session_id": "session-12345"
            }
        }