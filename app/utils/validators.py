"""Input validation utilities."""
import re
from typing import Optional


def validate_time_format(time_str: str) -> bool:
    """
    Validate HH:MM 24-hour time format.
    
    Args:
        time_str: Time string to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^([01]?[0-9]|2[0-3]):([0-5][0-9])$'
    return bool(re.match(pattern, time_str))


def sanitize_text(text: str) -> str:
    """
    Sanitize text to prevent Markdown injection in Telegram.
    
    Args:
        text: Raw text to sanitize
        
    Returns:
        Sanitized text safe for Telegram HTML mode
    """
    if not text:
        return ""
    # Escape HTML special characters
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


def validate_channel_username(username: str) -> bool:
    """
    Validate Telegram channel username format.
    
    Args:
        username: Channel username (with or without @)
        
    Returns:
        True if valid format
    """
    username = username.lstrip("@")
    pattern = r'^[a-zA-Z][a-zA-Z0-9_]{4,31}$'
    return bool(re.match(pattern, username))


def validate_invite_threshold(value: int) -> bool:
    """
    Validate invite threshold is between 1 and 100.
    
    Args:
        value: Threshold value
        
    Returns:
        True if valid
    """
    return 1 <= value <= 100


def truncate_text(text: str, max_length: int = 4000) -> str:
    """
    Truncate text to max length for Telegram messages.
    
    Args:
        text: Text to truncate
        max_length: Maximum allowed length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
