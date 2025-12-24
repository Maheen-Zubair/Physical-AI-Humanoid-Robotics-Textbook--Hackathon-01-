from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """
    Enum for message roles in the conversation.
    """
    USER = "user"
    ASSISTANT = "assistant"


class ContextMode(str, Enum):
    """
    Enum for context modes used in messages.
    """
    SELECTION = "selection"
    RETRIEVAL = "retrieval"


class ChatMessage(BaseModel):
    """
    Model representing a single message in the conversation.
    """
    role: MessageRole = Field(..., description="Message author")
    content: str = Field(..., description="Message text")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message time")
    context_mode: Optional[ContextMode] = Field(
        None,
        description="How context was obtained (user messages only)"
    )


class ChatSession(BaseModel):
    """
    Model representing an in-memory chat session.
    """
    session_id: str = Field(..., description="UUID generated client-side")
    messages: List[ChatMessage] = Field(
        default=[],
        description="Conversation history"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Session start time"
    )
    last_activity: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last interaction time"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session-12345",
                "messages": [
                    {
                        "role": "user",
                        "content": "What is inverse kinematics?",
                        "timestamp": "2023-10-20T10:00:00Z",
                        "context_mode": "retrieval"
                    },
                    {
                        "role": "assistant",
                        "content": "Inverse kinematics is the process of determining...",
                        "timestamp": "2023-10-20T10:00:05Z"
                    }
                ],
                "created_at": "2023-10-20T10:00:00Z",
                "last_activity": "2023-10-20T10:00:05Z"
            }
        }

    def add_message(self, message: ChatMessage):
        """
        Add a message to the session and update last activity.
        """
        self.messages.append(message)
        self.last_activity = datetime.utcnow()

    def trim_history(self, max_messages: int = 10):
        """
        Trim the message history to the most recent messages.
        """
        if len(self.messages) > max_messages:
            self.messages = self.messages[-max_messages:]