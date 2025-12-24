import re
from typing import List, Tuple, Dict, Any
import tiktoken


class Chunker:
    """
    Class to handle chunking of content based on headers with token fallback.
    """

    def __init__(self, max_tokens: int = 2000, min_tokens: int = 100, overlap_tokens: int = 50):
        """
        Initialize the chunker with token limits.

        Args:
            max_tokens: Maximum tokens per chunk (default 2000 for Gemini embedding limit)
            min_tokens: Minimum tokens to avoid fragments (default 100)
            overlap_tokens: Overlap between chunks for context continuity (default 50)
        """
        self.max_tokens = max_tokens
        self.min_tokens = min_tokens
        self.overlap_tokens = overlap_tokens
        self.encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")  # Close enough for token estimation

    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text.

        Args:
            text: Input text

        Returns:
            Number of tokens
        """
        return len(self.encoder.encode(text))

    def split_by_headers(self, content: str, primary_split: str = "##", secondary_split: str = "###") -> List[str]:
        """
        Split content by headers, preserving header structure.

        Args:
            content: Content to split
            primary_split: Primary header level to split on (default "##" for H2)
            secondary_split: Secondary header level to split on if section is too large (default "###" for H3)

        Returns:
            List of content chunks
        """
        # First, split by primary headers
        if primary_split in content:
            sections = re.split(f'(^.*?{re.escape(primary_split)} .+?)(?=\n{re.escape(primary_split)} |\n*$)',
                               content, flags=re.MULTILINE | re.DOTALL)
            # Filter out empty sections and reassemble with headers
            sections = [sec.strip() for sec in sections if sec.strip()]

            # Process sections that are too large
            processed_sections = []
            for section in sections:
                if self.count_tokens(section) > self.max_tokens and secondary_split in section:
                    # Split this section by secondary headers
                    sub_sections = re.split(f'(^.*?{re.escape(secondary_split)} .+?)(?=\n{re.escape(secondary_split)} |\n*$)',
                                           section, flags=re.MULTILINE | re.DOTALL)
                    sub_sections = [sub_sec.strip() for sub_sec in sub_sections if sub_sec.strip()]
                    processed_sections.extend(sub_sections)
                else:
                    processed_sections.append(section)

            return [sec for sec in processed_sections if sec.strip()]
        else:
            # If no primary headers, return the whole content as one chunk
            return [content] if content.strip() else []

    def split_by_sentences(self, content: str) -> List[str]:
        """
        Split content by sentences as a fallback method.

        Args:
            content: Content to split

        Returns:
            List of sentence chunks
        """
        # Split by sentences, preserving sentence boundaries
        sentences = re.split(r'(?<=[.!?]) +', content)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence

            if self.count_tokens(test_chunk) <= self.max_tokens:
                current_chunk = test_chunk
            else:
                if current_chunk and self.count_tokens(current_chunk) >= self.min_tokens:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    # Current chunk is too small, force add it and start new
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def chunk_content(self, content: str, chapter_title: str, source_url: str) -> List[Dict[str, Any]]:
        """
        Main method to chunk content with various strategies.

        Args:
            content: Content to chunk
            chapter_title: Title of the chapter this content belongs to
            source_url: URL where the content is located

        Returns:
            List of chunk dictionaries with content, metadata, and token counts
        """
        # First try header-based splitting
        header_chunks = self.split_by_headers(content)

        final_chunks = []
        chunk_index = 0

        for chunk_content in header_chunks:
            if self.count_tokens(chunk_content) <= self.max_tokens:
                # Chunk is within size limits
                final_chunks.append({
                    "content": chunk_content,
                    "chapter_title": chapter_title,
                    "source_url": source_url,
                    "chunk_index": chunk_index,
                    "token_count": self.count_tokens(chunk_content)
                })
                chunk_index += 1
            else:
                # Chunk is too large, fall back to sentence splitting
                sentence_chunks = self.split_by_sentences(chunk_content)

                for sent_chunk in sentence_chunks:
                    if self.count_tokens(sent_chunk) <= self.max_tokens:
                        final_chunks.append({
                            "content": sent_chunk,
                            "chapter_title": chapter_title,
                            "source_url": source_url,
                            "chunk_index": chunk_index,
                            "token_count": self.count_tokens(sent_chunk)
                        })
                        chunk_index += 1
                    else:
                        # Still too large, force split by token count
                        token_chunks = self.force_chunk_by_tokens(sent_chunk, chapter_title, source_url)
                        for token_chunk in token_chunks:
                            final_chunks.append({
                                "content": token_chunk,
                                "chapter_title": chapter_title,
                                "source_url": source_url,
                                "chunk_index": chunk_index,
                                "token_count": self.count_tokens(token_chunk)
                            })
                            chunk_index += 1

        return final_chunks

    def force_chunk_by_tokens(self, content: str, chapter_title: str, source_url: str) -> List[str]:
        """
        Force split content by token count when other methods fail.

        Args:
            content: Content to chunk
            chapter_title: Title of the chapter
            source_url: Source URL

        Returns:
            List of content chunks
        """
        tokens = self.encoder.encode(content)
        chunks = []

        start_idx = 0
        while start_idx < len(tokens):
            end_idx = start_idx + self.max_tokens
            if end_idx > len(tokens):
                end_idx = len(tokens)

            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = self.encoder.decode(chunk_tokens)
            chunks.append(chunk_text)

            start_idx = end_idx

        return chunks


# Global instance
chunker = Chunker()