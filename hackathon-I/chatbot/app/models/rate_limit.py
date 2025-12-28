from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RateLimitEntry(BaseModel):
    """
    Model representing a rate limit entry in memory.
    """
    ip_address: str
    minute_count: int = 0
    daily_count: int = 0
    minute_reset: datetime
    daily_reset: datetime
    created_at: datetime
    last_updated: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "ip_address": "192.168.1.1",
                "minute_count": 15,
                "daily_count": 120,
                "minute_reset": "2023-10-20T10:01:00Z",
                "daily_reset": "2023-10-21T00:00:00Z",
                "created_at": "2023-10-20T10:00:00Z",
                "last_updated": "2023-10-20T10:00:30Z"
            }
        }