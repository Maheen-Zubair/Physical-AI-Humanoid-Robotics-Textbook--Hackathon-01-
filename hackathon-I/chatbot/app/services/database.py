import asyncpg
import os
from typing import Optional
from contextlib import asynccontextmanager
from ..config import get_settings


class DatabaseConnection:
    """
    Singleton class to manage Neon Postgres connection pool.
    """
    _instance: Optional['DatabaseConnection'] = None
    _pool: Optional[asyncpg.Pool] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def initialize(self):
        """
        Initialize the database connection pool.
        """
        settings = get_settings()
        self._pool = await asyncpg.create_pool(
            dsn=settings.database_url,
            min_size=2,
            max_size=10,
            command_timeout=60,
            ssl='require' if 'sslmode=require' in settings.database_url else None
        )

    @property
    def pool(self) -> asyncpg.Pool:
        """
        Get the connection pool.
        """
        if self._pool is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._pool

    @asynccontextmanager
    async def get_connection(self):
        """
        Get a connection from the pool.
        """
        if self._pool is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        async with self._pool.acquire() as connection:
            yield connection

    async def close(self):
        """
        Close the connection pool.
        """
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()


# Global instance
db_connection = DatabaseConnection()


async def get_db_connection():
    """
    Dependency to get database connection.
    """
    return db_connection