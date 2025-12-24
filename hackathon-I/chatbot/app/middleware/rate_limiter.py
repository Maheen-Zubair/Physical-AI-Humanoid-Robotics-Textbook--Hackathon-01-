import time
from typing import Dict, Optional
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging


logger = logging.getLogger(__name__)


class RateLimitEntry:
    """
    Runtime model for tracking rate limit entries per IP.
    """
    def __init__(self):
        self.minute_count = 0
        self.daily_count = 0
        self.minute_reset = datetime.utcnow() + timedelta(minutes=1)
        self.daily_reset = datetime.utcnow() + timedelta(days=1)


class RateLimiter:
    """
    IP-based rate limiter for the chatbot API.
    """

    def __init__(self, per_minute: int = 30, per_day: int = 500):
        """
        Initialize the rate limiter.

        Args:
            per_minute: Maximum requests per minute per IP
            per_day: Maximum requests per day per IP
        """
        self.per_minute = per_minute
        self.per_day = per_day
        self.entries: Dict[str, RateLimitEntry] = {}

    def _get_or_create_entry(self, ip_address: str) -> RateLimitEntry:
        """
        Get or create a rate limit entry for the given IP address.

        Args:
            ip_address: The IP address to get/create entry for

        Returns:
            RateLimitEntry for the IP address
        """
        if ip_address not in self.entries:
            self.entries[ip_address] = RateLimitEntry()

        entry = self.entries[ip_address]

        # Check if we need to reset counters
        now = datetime.utcnow()
        if now >= entry.minute_reset:
            entry.minute_count = 0
            entry.minute_reset = now + timedelta(minutes=1)

        if now >= entry.daily_reset:
            entry.daily_count = 0
            entry.daily_reset = now + timedelta(days=1)

        return entry

    def check_rate_limit(self, ip_address: str) -> tuple[bool, Optional[str], Optional[int]]:
        """
        Check if the IP address has exceeded rate limits.

        Args:
            ip_address: The IP address to check

        Returns:
            Tuple of (is_allowed, error_message_if_any, retry_after_seconds_if_any)
        """
        entry = self._get_or_create_entry(ip_address)

        # Check minute limit
        if entry.minute_count >= self.per_minute:
            secs_remaining = int((entry.minute_reset - datetime.utcnow()).total_seconds())
            if secs_remaining <= 0:
                secs_remaining = 60  # Fallback to 60 seconds
            error_msg = f"Rate limit exceeded: {self.per_minute}/minute. Please wait {secs_remaining}s."
            return False, error_msg, secs_remaining

        # Check daily limit
        if entry.daily_count >= self.per_day:
            secs_remaining = int((entry.daily_reset - datetime.utcnow()).total_seconds())
            if secs_remaining <= 0:
                secs_remaining = 86400  # Fallback to 24 hours (86400 seconds)
            error_msg = f"Rate limit exceeded: {self.per_day}/day. Please try again in {secs_remaining // 3600}h {(secs_remaining % 3600) // 60}m."
            return False, error_msg, secs_remaining

        # Update counters
        entry.minute_count += 1
        entry.daily_count += 1

        return True, None, None


# Global instance
rate_limiter = RateLimiter()