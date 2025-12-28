from pydantic import BaseModel, Field


class Source(BaseModel):
    """
    Model representing a source citation in the chat response.
    """
    title: str = Field(..., description="Title of the source (e.g., chapter or section name)")
    url: str = Field(..., description="URL to the source in the book")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Chapter 5: Kinematics",
                "url": "https://book.example.com/docs/kinematics"
            }
        }