from pathlib import Path
from typing import Optional


def file_path_to_url(file_path: str, base_url: str) -> str:
    """
    Map local file path to deployed Docusaurus URL.

    Args:
        file_path: Local file path (e.g., docs/intro.md, docs/chapter-1/index.md)
        base_url: Base URL for the deployed book (e.g., https://site.io/docs)

    Returns:
        Full URL to the deployed page

    Examples:
        - docs/intro.md → https://site.io/docs/intro
        - docs/chapter-1/index.md → https://site.io/docs/chapter-1
        - docs/chapter-1/section-1-1.md → https://site.io/docs/chapter-1/section-1-1
    """
    # Convert to Path object for easier manipulation
    path = Path(file_path)

    # Remove .md extension
    path_str = str(path.with_suffix(''))

    # Handle index files - if the filename is 'index', remove it from the path
    if path_str.endswith('/index') or path_str.endswith('\\index') or path.name == 'index':
        path_str = str(path.parent)

    # Remove docs/ prefix if present
    if path_str.startswith('docs/'):
        path_str = path_str[5:]
    elif path_str.startswith('docs\\'):
        path_str = path_str[5:]

    # Construct the full URL
    if path_str:
        return f"{base_url}/{path_str}"
    else:
        return base_url


def validate_url(url: str) -> bool:
    """
    Basic URL validation.

    Args:
        url: URL to validate

    Returns:
        True if URL appears valid, False otherwise
    """
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None


def normalize_file_path(file_path: str) -> str:
    """
    Normalize file path to ensure consistent format for URL mapping.

    Args:
        file_path: File path to normalize

    Returns:
        Normalized file path
    """
    # Convert to Path object and back to string to normalize separators
    path = Path(file_path)
    path_str = str(path.as_posix())  # Use forward slashes consistently

    # Ensure it starts with docs/ if it's meant to be in the docs directory
    if not path_str.startswith('docs/'):
        # If it's clearly a doc file, prepend 'docs/'
        if path_str.endswith('.md') and not any(path_str.startswith(prefix) for prefix in ['src/', 'chatbot/', 'node_modules/']):
            path_str = 'docs/' + path_str

    return path_str