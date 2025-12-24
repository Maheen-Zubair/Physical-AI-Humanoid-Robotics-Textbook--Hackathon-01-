import argparse
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any
import sys
import os

# Add the parent directory to sys.path so we can import from app
chatbot_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, chatbot_dir)

# Load environment variables before any imports that need them
from dotenv import load_dotenv
load_dotenv(os.path.join(chatbot_dir, '.env'))

from ingestion.parser import parse_markdown_content, get_all_markdown_files
from ingestion.chunker import chunker
from ingestion.url_mapper import file_path_to_url
from ingestion.writer import dual_store_writer
from app.config import get_settings


logger = logging.getLogger(__name__)


async def process_file(file_path: str, base_url: str, chapter_title_override: str = None) -> List[Dict[str, Any]]:
    """
    Process a single markdown file: parse, chunk, and prepare for storage.

    Args:
        file_path: Path to the markdown file
        base_url: Base URL for generating source URLs
        chapter_title_override: Optional chapter title to override the one from file

    Returns:
        List of chunk dictionaries ready for storage
    """
    logger.info(f"Processing file: {file_path}")

    try:
        # Parse the markdown file
        parsed_data = parse_markdown_content(file_path)

        # Generate the source URL
        source_url = file_path_to_url(file_path, base_url)

        # Use provided chapter title or extract from file
        chapter_title = chapter_title_override or parsed_data['chapter_title']

        # Chunk the content
        chunks = chunker.chunk_content(
            content=parsed_data['content'],
            chapter_title=chapter_title,
            source_url=source_url
        )

        logger.info(f"File {file_path} chunked into {len(chunks)} chunks")

        return chunks

    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        return []


async def process_file_with_retry(file_path: str, base_url: str, chapter_title_override: str = None, max_retries: int = 3) -> List[Dict[str, Any]]:
    """
    Process a single markdown file with retry logic.

    Args:
        file_path: Path to the markdown file
        base_url: Base URL for generating source URLs
        chapter_title_override: Optional chapter title to override the one from file
        max_retries: Maximum number of retry attempts

    Returns:
        List of chunk dictionaries ready for storage, or empty list if all retries failed
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"Processing file: {file_path} (attempt {attempt + 1}/{max_retries})")

            # Parse the markdown file
            parsed_data = parse_markdown_content(file_path)

            # Generate the source URL
            source_url = file_path_to_url(file_path, base_url)

            # Use provided chapter title or extract from file
            chapter_title = chapter_title_override or parsed_data['chapter_title']

            # Chunk the content
            chunks = chunker.chunk_content(
                content=parsed_data['content'],
                chapter_title=chapter_title,
                source_url=source_url
            )

            logger.info(f"File {file_path} chunked into {len(chunks)} chunks")

            return chunks

        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed for file {file_path}: {e}")
            if attempt == max_retries - 1:
                # Last attempt failed
                logger.error(f"All {max_retries} attempts failed for file {file_path}. Skipping.")
                return []
            else:
                # Wait before retry with exponential backoff
                import asyncio
                wait_time = 2 ** attempt  # 1s, 2s, 4s, etc.
                logger.info(f"Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)

    # This should not be reached, but included for completeness
    return []


async def ingest_files(file_paths: List[str], base_url: str, clear_first: bool = False):
    """
    Ingest multiple files into the knowledge base.

    Args:
        file_paths: List of paths to markdown files
        base_url: Base URL for generating source URLs
        clear_first: Whether to clear existing data before ingesting
    """
    logger.info(f"Starting ingestion of {len(file_paths)} files")

    # Initialize database connection
    from app.services.database import db_connection
    from app.services.vector_store import vector_store

    await db_connection.initialize()
    logger.info("Database connection initialized")

    vector_store.initialize()
    logger.info("Vector store initialized")

    # Initialize the database tables
    await dual_store_writer.initialize_tables()

    # Process all files
    all_chunks = []
    for file_path in file_paths:
        chunks = await process_file(file_path, base_url)
        all_chunks.extend(chunks)

    logger.info(f"Total chunks generated: {len(all_chunks)}")

    if all_chunks:
        # Write chunks in smaller batches with rate limiting
        batch_size = 20  # Small batch to avoid Cohere rate limits
        total_ingested = 0

        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i + batch_size]
            try:
                chunk_ids = await dual_store_writer.write_chunks_transaction(batch)
                total_ingested += len(chunk_ids)
                logger.info(f"Batch {i//batch_size + 1}: Ingested {len(chunk_ids)} chunks (total: {total_ingested}/{len(all_chunks)})")

                # Rate limit: Wait between batches to stay under Cohere limits
                if i + batch_size < len(all_chunks):
                    import asyncio
                    await asyncio.sleep(15)  # 15 second pause between batches
            except Exception as e:
                logger.error(f"Error in batch {i//batch_size + 1}: {e}")
                logger.info("Waiting 60 seconds before retrying...")
                import asyncio
                await asyncio.sleep(60)
                # Retry the failed batch
                try:
                    chunk_ids = await dual_store_writer.write_chunks_transaction(batch)
                    total_ingested += len(chunk_ids)
                    logger.info(f"Retry succeeded for batch {i//batch_size + 1}")
                except Exception as retry_error:
                    logger.error(f"Retry failed for batch {i//batch_size + 1}: {retry_error}")
                    continue

        logger.info(f"Successfully ingested {total_ingested} of {len(all_chunks)} chunks")
    else:
        logger.warning("No chunks were generated from the provided files")


async def main():
    """
    Main function to run the ingestion script with CLI interface.
    """
    parser = argparse.ArgumentParser(description="Ingest book content into RAG system")
    parser.add_argument("--source", required=True, help="Source directory containing markdown files")
    parser.add_argument("--base-url", required=True, help="Base URL for the deployed book")
    parser.add_argument("--clear", action="store_true", help="Clear existing content before ingesting")
    parser.add_argument("--chapter-title", help="Override chapter title for all files")

    args = parser.parse_args()

    # Validate inputs
    if not Path(args.source).exists():
        print(f"Error: Source directory does not exist: {args.source}")
        sys.exit(1)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Get all markdown files
    markdown_files = get_all_markdown_files(args.source)
    logger.info(f"Found {len(markdown_files)} markdown files in {args.source}")

    if not markdown_files:
        print("No markdown files found in the specified source directory.")
        sys.exit(0)

    # Run ingestion
    await ingest_files(markdown_files, args.base_url, args.clear)

    print(f"Ingestion completed successfully! Processed {len(markdown_files)} files.")


if __name__ == "__main__":
    asyncio.run(main())