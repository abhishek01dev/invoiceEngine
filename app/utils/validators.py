import re
from typing import Tuple
from app.config import settings


def validate_file(filename: str, file_size: int) -> Tuple[bool, str]:
    """
    Validate uploaded file

    Args:
        filename: Name of uploaded file
        file_size: Size of file in bytes

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check extension
    extension = filename.lower().split('.')[-1]
    allowed = [ext.strip().lower() for ext in settings.ALLOWED_EXTENSIONS.split(',')]
    if extension not in allowed:
        return False, f"Invalid file type. Allowed: {settings.ALLOWED_EXTENSIONS}"

    # Check file size
    max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size_bytes:
        return False, f"File too large. Max size: {settings.MAX_FILE_SIZE_MB}MB"

    return True, ""


def clean_text(text: str) -> str:
    """Clean extracted text while preserving line structure for field extraction"""
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        # Collapse multiple spaces within each line
        cleaned = ' '.join(line.split())
        if cleaned:
            cleaned_lines.append(cleaned)
    return '\n'.join(cleaned_lines)