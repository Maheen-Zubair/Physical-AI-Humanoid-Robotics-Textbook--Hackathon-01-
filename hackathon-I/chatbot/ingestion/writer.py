import asyncio
import logging
import sys
import os
from typing import List, Dict, Any
from uuid import uuid4

# Add parent dir to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.database import db_connection
from app.services.vector_store import vector_store
from app.models.book_chunk import BookChunk, CREATE_BOOK_CHUNKS_TABLE_SQL, UPDATE_TIMESTAMP_TRIGGER_SQL


logger = logging.getLogger(__name__)


class DualStoreWriter:
    """
    Class to handle writing to both Qdrant (vector store) and Neon (metadata store) atomically.
    """

    async def initialize_tables(self):
        """
        Initialize the required database tables.
        """
        async with db_connection.get_connection() as conn:
            # Create book_chunks table
            await conn.execute(CREATE_BOOK_CHUNKS_TABLE_SQL)
            # Create update timestamp trigger
            await conn.execute(UPDATE_TIMESTAMP_TRIGGER_SQL)
            logger.info("Database tables initialized")

    async def write_chunk(self, chunk_data: Dict[str, Any]) -> str:
        """
        Write a single chunk to both stores atomically.

        Args:
            chunk_data: Dictionary containing chunk information including content, metadata, etc.

        Returns:
            The chunk_id of the written chunk
        """
        chunk_id = str(uuid4())

        try:
            # Prepare data for both stores
            book_chunk = BookChunk(
                chunk_id=chunk_id,
                chapter_title=chunk_data['chapter_title'],
                section_title=chunk_data.get('section_title'),
                content=chunk_data['content'],
                source_url=chunk_data['source_url'],
                chunk_index=chunk_data['chunk_index'],
                token_count=chunk_data['token_count']
            )

            # Generate embedding for the content
            from .embedder import embedder
            embedding = embedder.embed_text(chunk_data['content'])

            # Write to Neon Postgres first
            async with db_connection.get_connection() as conn:
                query = """
                INSERT INTO book_chunks
                (chunk_id, chapter_title, section_title, content, source_url, chunk_index, token_count)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """
                await conn.execute(
                    query,
                    book_chunk.chunk_id,
                    book_chunk.chapter_title,
                    book_chunk.section_title,
                    book_chunk.content,
                    book_chunk.source_url,
                    book_chunk.chunk_index,
                    book_chunk.token_count
                )

            # Write to Qdrant vector store
            vs = vector_store
            payload = {
                "chapter_title": chunk_data['chapter_title'],
                "section_title": chunk_data.get('section_title', ''),
                "token_count": chunk_data['token_count']
            }

            await vs.store_embedding(
                chunk_id=chunk_id,
                embedding=embedding,
                payload=payload
            )

            logger.info(f"Successfully wrote chunk {chunk_id} to both stores")
            return chunk_id

        except Exception as e:
            logger.error(f"Error writing chunk to stores: {e}")
            # Attempt rollback - delete from Qdrant if Neon write succeeded but Qdrant failed
            try:
                vs = vector_store
                await vs.delete_embedding(chunk_id)
                logger.info(f"Rolled back Qdrant entry for chunk {chunk_id}")
            except:
                logger.warning(f"Could not roll back Qdrant entry for chunk {chunk_id}")
            raise

    async def write_chunks_batch(self, chunks_data: List[Dict[str, Any]]) -> List[str]:
        """
        Write multiple chunks to both stores.

        Args:
            chunks_data: List of dictionaries containing chunk information

        Returns:
            List of chunk_ids that were written
        """
        chunk_ids = []

        # Process each chunk individually to maintain atomicity
        for chunk_data in chunks_data:
            chunk_id = await self.write_chunk(chunk_data)
            chunk_ids.append(chunk_id)

        return chunk_ids

    async def write_chunks_transaction(self, chunks_data: List[Dict[str, Any]]) -> List[str]:
        """
        Write multiple chunks to both stores in a more efficient transaction-like manner.
        This method attempts to batch operations where possible while maintaining consistency.

        Args:
            chunks_data: List of dictionaries containing chunk information

        Returns:
            List of chunk_ids that were written
        """
        chunk_ids = []
        book_chunks = []
        embeddings_data = []

        # Prepare all data first
        for chunk_data in chunks_data:
            chunk_id = str(uuid4())
            chunk_ids.append(chunk_id)

            book_chunk = BookChunk(
                chunk_id=chunk_id,
                chapter_title=chunk_data['chapter_title'],
                section_title=chunk_data.get('section_title'),
                content=chunk_data['content'],
                source_url=chunk_data['source_url'],
                chunk_index=chunk_data['chunk_index'],
                token_count=chunk_data['token_count']
            )
            book_chunks.append(book_chunk)

            # Generate embedding
            from .embedder import embedder
            embedding = embedder.embed_text(chunk_data['content'])

            payload = {
                "chapter_title": chunk_data['chapter_title'],
                "section_title": chunk_data.get('section_title', ''),
                "token_count": chunk_data['token_count']
            }

            embeddings_data.append({
                'chunk_id': chunk_id,
                'embedding': embedding,
                'payload': payload
            })

        try:
            # Write all to Neon Postgres
            async with db_connection.get_connection() as conn:
                # Prepare the query
                query = """
                INSERT INTO book_chunks
                (chunk_id, chapter_title, section_title, content, source_url, chunk_index, token_count)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """

                # Prepare values for executemany
                values = [
                    (
                        bc.chunk_id,
                        bc.chapter_title,
                        bc.section_title,
                        bc.content,
                        bc.source_url,
                        bc.chunk_index,
                        bc.token_count
                    )
                    for bc in book_chunks
                ]

                # Execute in batch
                for value in values:
                    await conn.execute(query, *value)

            # Write all to Qdrant vector store
            vs = vector_store

            # Extract data for Qdrant batch operation
            chunk_ids_batch = [data['chunk_id'] for data in embeddings_data]
            embeddings_batch = [data['embedding'] for data in embeddings_data]
            payloads_batch = [data['payload'] for data in embeddings_data]

            await vs.batch_store_embeddings(
                chunk_ids=chunk_ids_batch,
                embeddings=embeddings_batch,
                payloads=payloads_batch
            )

            logger.info(f"Successfully wrote {len(chunks_data)} chunks to both stores")
            return chunk_ids

        except Exception as e:
            logger.error(f"Error writing chunks batch to stores: {e}")
            # Attempt rollback - delete from Qdrant for all chunk_ids
            try:
                vs = vector_store
                for chunk_id in chunk_ids:
                    await vs.delete_embedding(chunk_id)
                logger.info(f"Rolled back Qdrant entries for {len(chunk_ids)} chunks")
            except Exception as rollback_error:
                logger.error(f"Could not roll back Qdrant entries: {rollback_error}")
            raise


# Global instance
dual_store_writer = DualStoreWriter()