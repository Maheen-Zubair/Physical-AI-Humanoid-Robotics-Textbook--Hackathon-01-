from pydantic import BaseModel, Field
from typing import Optional


class ErrorResponse(BaseModel):
    """
    Model representing an error response from the backend.
    """
    error: str = Field(..., description="Error message describing what went wrong")
    error_code: Optional[str] = Field(None, description="Specific error code for client handling")
    details: Optional[str] = Field(None, description="Additional details about the error")
    timestamp: str = Field(..., description="Timestamp of when the error occurred")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Rate limit exceeded",
                "error_code": "RATE_LIMIT",
                "details": "You have exceeded the rate limit of 30 requests per minute",
                "timestamp": "2023-10-20T10:00:00Z"
            }
        }