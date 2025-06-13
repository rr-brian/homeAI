"""Utility functions for search operations."""
import logging
import re
from typing import Dict, Optional

logger = logging.getLogger(__name__)

def clean_query(query: str) -> str:
    """Clean and normalize a search query."""
    # Remove special characters
    cleaned = re.sub(r'[^\w\s]', '', query)
    # Normalize whitespace
    cleaned = ' '.join(cleaned.split())
    return cleaned

def safe_str(value: Optional[str]) -> str:
    """Safely convert a value to string."""
    if value is None:
        return ''
    return str(value)

def safe_float(value: Optional[float]) -> float:
    """Safely convert a value to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

def extract_field(item: Dict, field_names: list[str], default: str = '') -> str:
    """Extract a field value from multiple possible field names."""
    for name in field_names:
        value = item.get(name)
        if value:
            return safe_str(value)
    return default

def truncate_text(text: str, max_length: int = 200, suffix: str = '...') -> str:
    """Truncate text to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + suffix
