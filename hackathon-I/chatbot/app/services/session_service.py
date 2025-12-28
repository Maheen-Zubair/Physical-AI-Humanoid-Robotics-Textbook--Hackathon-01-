from typing import Dict, Optional, List
from ..models.chat_session import ChatSession, ChatMessage, MessageRole, ContextMode
from datetime import datetime, timedelta
import logging
import asyncio
import threading


logger = logging.getLogger(__name__)


class SessionService:
    """
    Service to handle conversation session management with in-memory storage and TTL.
    """

    def __init__(self, default_ttl_minutes: int = 30):
        """
        Initialize the session service.

        Args:
            default_ttl_minutes: Default time-to-live for sessions in minutes
        """
        self.sessions: Dict[str, ChatSession] = {}
        self.default_ttl = timedelta(minutes=default_ttl_minutes)
        self.lock = threading.Lock()  # Thread-safe access to sessions
        self._start_cleanup_task()

    def _start_cleanup_task(self):
        """
        Start a background task to clean up expired sessions.
        """
        def cleanup_expired_sessions():
            while True:
                try:
                    current_time = datetime.utcnow()
                    expired_session_ids = []

                    # Find expired sessions
                    with self.lock:
                        for session_id, session in self.sessions.items():
                            if current_time - session.last_activity > self.default_ttl:
                                expired_session_ids.append(session_id)

                    # Remove expired sessions
                    for session_id in expired_session_ids:
                        with self.lock:
                            if session_id in self.sessions:
                                del self.sessions[session_id]
                        logger.info(f"Removed expired session: {session_id}")

                    # Sleep for 5 minutes before next cleanup
                    import time
                    time.sleep(300)  # 5 minutes
                except Exception as e:
                    logger.error(f"Error in session cleanup task: {e}")

        # Start cleanup thread
        cleanup_thread = threading.Thread(target=cleanup_expired_sessions, daemon=True)
        cleanup_thread.start()

    def create_session(self, session_id: str) -> ChatSession:
        """
        Create a new chat session.

        Args:
            session_id: Unique identifier for the session

        Returns:
            Created ChatSession object
        """
        with self.lock:
            session = ChatSession(
                session_id=session_id,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )
            self.sessions[session_id] = session
            logger.info(f"Created new session: {session_id}")
            return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Get an existing session by ID.

        Args:
            session_id: ID of the session to retrieve

        Returns:
            ChatSession object or None if not found
        """
        with self.lock:
            session = self.sessions.get(session_id)
            if session:
                # Update last activity time
                session.last_activity = datetime.utcnow()
            return session

    def add_message_to_session(self, session_id: str, message: ChatMessage) -> ChatSession:
        """
        Add a message to a session and update activity time.

        Args:
            session_id: ID of the session
            message: Message to add

        Returns:
            Updated ChatSession object
        """
        with self.lock:
            session = self.sessions.get(session_id)
            if not session:
                session = self.create_session(session_id)

            session.add_message(message)
            # Trim history to last 10 messages (5 Q&A pairs) to prevent memory issues
            session.trim_history(max_messages=10)
            session.last_activity = datetime.utcnow()

            logger.debug(f"Added message to session {session_id}, now has {len(session.messages)} messages")
            return session

    def get_conversation_context(self, session_id: str, max_messages: int = 4) -> List[ChatMessage]:
        """
        Get the recent conversation context from a session.

        Args:
            session_id: ID of the session
            max_messages: Maximum number of messages to return

        Returns:
            List of recent ChatMessage objects
        """
        session = self.get_session(session_id)
        if not session:
            return []

        # Return the most recent messages, up to the limit
        return session.messages[-max_messages:]

    def clear_session(self, session_id: str):
        """
        Clear all messages from a session but keep the session.

        Args:
            session_id: ID of the session to clear
        """
        with self.lock:
            session = self.sessions.get(session_id)
            if session:
                session.messages = []
                session.last_activity = datetime.utcnow()
                logger.info(f"Cleared messages from session: {session_id}")

    def delete_session(self, session_id: str):
        """
        Delete a session completely.

        Args:
            session_id: ID of the session to delete
        """
        with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                logger.info(f"Deleted session: {session_id}")


# Global instance
session_service = SessionService()