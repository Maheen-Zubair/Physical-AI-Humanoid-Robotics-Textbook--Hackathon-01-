from typing import List, Optional
from ..services.database import db_connection
from ..models.book_chunk import BookChunk
from ..models.query_context import RetrievedChunk
import logging
import asyncpg


logger = logging.getLogger(__name__)


class MetadataService:
    """
    Service to handle metadata lookup from Neon Postgres.
    """

    async def get_chunk_by_id(self, chunk_id: str) -> Optional[BookChunk]:
        """
        Retrieve a single chunk by its ID from Neon Postgres.

        Args:
            chunk_id: The ID of the chunk to retrieve

        Returns:
            BookChunk object or None if not found
        """
        try:
            async with db_connection.get_connection() as conn:
                query = """
                SELECT chunk_id, chapter_title, section_title, content, source_url,
                       chunk_index, token_count, created_at, updated_at
                FROM book_chunks
                WHERE chunk_id = $1
                """
                row = await conn.fetchrow(query, chunk_id)

                if row:
                    return BookChunk(
                        chunk_id=str(row['chunk_id']),
                        chapter_title=row['chapter_title'],
                        section_title=row['section_title'],
                        content=row['content'],
                        source_url=row['source_url'],
                        chunk_index=row['chunk_index'],
                        token_count=row['token_count'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    )
                return None

        except Exception as e:
            logger.error(f"Error retrieving chunk {chunk_id}: {e}")

            # Graceful degradation: return None instead of raising error
            logger.warning(f"Neon is unavailable, returning None for chunk {chunk_id}")
            return None

    async def get_chunks_by_ids(self, chunk_ids: List[str]) -> List[BookChunk]:
        """
        Retrieve multiple chunks by their IDs from Neon Postgres.

        Args:
            chunk_ids: List of chunk IDs to retrieve

        Returns:
            List of BookChunk objects
        """
        if not chunk_ids:
            return []

        try:
            async with db_connection.get_connection() as conn:
                # Create placeholders for the query (e.g., ($1), ($2), ...)
                placeholders = ','.join([f'${i+1}' for i in range(len(chunk_ids))])
                query = f"""
                SELECT chunk_id, chapter_title, section_title, content, source_url,
                       chunk_index, token_count, created_at, updated_at
                FROM book_chunks
                WHERE chunk_id = ANY(ARRAY[{placeholders}]::uuid[])
                """
                rows = await conn.fetch(query, *chunk_ids)

                chunks = []
                for row in rows:
                    chunks.append(BookChunk(
                        chunk_id=str(row['chunk_id']),
                        chapter_title=row['chapter_title'],
                        section_title=row['section_title'],
                        content=row['content'],
                        source_url=row['source_url'],
                        chunk_index=row['chunk_index'],
                        token_count=row['token_count'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ))

                logger.info(f"Retrieved {len(chunks)} chunks by IDs")
                return chunks

        except Exception as e:
            logger.error(f"Error retrieving chunks by IDs: {e}")

            # Graceful degradation: return empty list instead of raising error
            logger.warning("Neon is unavailable, returning empty results for chunk retrieval")
            return []

    async def get_chunks_by_chapter(self, chapter_title: str, limit: int = 100) -> List[BookChunk]:
        """
        Retrieve chunks by chapter title from Neon Postgres.

        Args:
            chapter_title: The chapter title to search for
            limit: Maximum number of chunks to return

        Returns:
            List of BookChunk objects
        """
        try:
            async with db_connection.get_connection() as conn:
                query = """
                SELECT chunk_id, chapter_title, section_title, content, source_url,
                       chunk_index, token_count, created_at, updated_at
                FROM book_chunks
                WHERE chapter_title = $1
                ORDER BY chunk_index
                LIMIT $2
                """
                rows = await conn.fetch(query, chapter_title, limit)

                chunks = []
                for row in rows:
                    chunks.append(BookChunk(
                        chunk_id=str(row['chunk_id']),
                        chapter_title=row['chapter_title'],
                        section_title=row['section_title'],
                        content=row['content'],
                        source_url=row['source_url'],
                        chunk_index=row['chunk_index'],
                        token_count=row['token_count'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ))

                logger.info(f"Retrieved {len(chunks)} chunks for chapter '{chapter_title}'")
                return chunks

        except Exception as e:
            logger.error(f"Error retrieving chunks by chapter '{chapter_title}': {e}")

            # Graceful degradation: return empty list instead of raising error
            logger.warning(f"Neon is unavailable, returning empty results for chapter '{chapter_title}'")
            return []


# Global instance
metadata_service = MetadataService()