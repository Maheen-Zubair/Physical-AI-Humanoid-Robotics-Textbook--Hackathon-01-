import re
import frontmatter  # This will need to be added to requirements.txt
from typing import Dict, List, Tuple, Optional
from pathlib import Path


def parse_markdown_file(file_path: str) -> Tuple[Dict, str]:
    """
    Parse a markdown file and extract frontmatter and content.

    Args:
        file_path: Path to the markdown file

    Returns:
        A tuple containing (frontmatter dict, content string)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)
        metadata = post.metadata
        content = post.content

    return metadata, content


def extract_headers(content: str) -> List[Tuple[str, str, int]]:
    """
    Extract headers from markdown content.

    Args:
        content: The markdown content string

    Returns:
        A list of tuples containing (header_level, header_text, start_position)
    """
    headers = []
    lines = content.split('\n')

    for i, line in enumerate(lines):
        # Match markdown headers: ## Header text
        header_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
        if header_match:
            header_level = len(header_match.group(1))
            header_text = header_match.group(2).strip()
            # Calculate the position in the original content
            position = sum(len(line) + 1 for line in lines[:i])
            headers.append((f'H{header_level}', header_text, position))

    return headers


def extract_chapter_info(file_path: str, content: str) -> Dict:
    """
    Extract chapter/section information from file path and content.

    Args:
        file_path: Path to the markdown file
        content: Content of the markdown file

    Returns:
        A dictionary with chapter information
    """
    path = Path(file_path)

    # Extract chapter title from filename or first H1 if available
    chapter_title = path.stem.replace('-', ' ').replace('_', ' ').title()

    # Look for first H1 in content as chapter title if it exists
    first_h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if first_h1_match:
        chapter_title = first_h1_match.group(1).strip()

    # Extract first H2 as section title if it exists
    first_h2_match = re.search(r'^##\s+(.+)$', content, re.MULTILINE)
    section_title = None
    if first_h2_match:
        section_title = first_h2_match.group(1).strip()

    return {
        'chapter_title': chapter_title,
        'section_title': section_title,
        'file_path': str(path),
        'file_name': path.name
    }


def parse_markdown_content(file_path: str) -> Dict:
    """
    Parse markdown content completely, extracting all relevant information.

    Args:
        file_path: Path to the markdown file

    Returns:
        A dictionary with all extracted information
    """
    metadata, content = parse_markdown_file(file_path)
    headers = extract_headers(content)
    chapter_info = extract_chapter_info(file_path, content)

    return {
        'metadata': metadata,
        'content': content,
        'headers': headers,
        'chapter_title': chapter_info['chapter_title'],
        'section_title': chapter_info['section_title'],
        'file_path': chapter_info['file_path'],
        'file_name': chapter_info['file_name']
    }


def get_all_markdown_files(source_dir: str) -> List[str]:
    """
    Recursively find all markdown files in a directory.

    Args:
        source_dir: Directory to search for markdown files

    Returns:
        List of paths to markdown files
    """
    source_path = Path(source_dir)
    markdown_files = []

    for md_file in source_path.rglob('*.md'):
        if md_file.is_file():
            markdown_files.append(str(md_file))

    return sorted(markdown_files)  # Sort for consistent processing order