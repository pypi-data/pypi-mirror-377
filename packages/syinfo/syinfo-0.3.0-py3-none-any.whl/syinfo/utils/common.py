"""Common utilities, decorators, and formatting functions for SyInfo.

This module provides shared functionality used across the package including:
- Error handling decorators with exception translation
- Text formatting and display utilities with ANSI color support

The utilities here are designed to be lightweight, stateless, and reusable
across different modules without creating dependencies.
"""

from typing import Tuple

from syinfo.exceptions import SystemAccessError, ValidationError
from .logger import Logger

# Get logger instance
logger = Logger.get_logger()


def handle_system_error(func):
    """Simple decorator for system error handling."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PermissionError as e:
            raise SystemAccessError(f"Insufficient permissions: {e!s}")
        except Exception as e:
            raise SystemAccessError(f"Error in {func.__name__}: {e!s}")

    return wrapper


def create_highlighted_heading(
    msg: str, 
    line_symbol: str = "━", 
    total_length: int = 100, 
    prefix_suffix: str = "#",
    center_highlighter: Tuple[str, str] = (" ◄◂◀ ", " ▶▸► ")
) -> str:
    """Create a center aligned message with highlighters.
    
    Args:
        msg: The message to highlight
        line_symbol: Character used for the line
        total_length: Total length of the heading
        prefix_suffix: Prefix/suffix characters
        center_highlighter: Tuple of left and right highlighter strings
        
    Returns:
        Formatted heading string with ANSI color codes
        
    Raises:
        ValidationError: If parameters are invalid
    """
    if not isinstance(msg, str):
        raise ValidationError("Message must be a string", details={"field_name": "msg", "expected_type": str.__name__})
    if total_length < 20:
        raise ValidationError("Total length must be at least 20", details={"field_name": "total_length"})
    
    msg = f" {msg} "
    msg_len = len(msg)
    msg = "\033[1m" + msg + "\033[0m"
    
    start, end = (
        (f"{prefix_suffix} ", f" {prefix_suffix}")
        if len(prefix_suffix) > 0 else
        ("", "")
    )
    
    lt_sep_cnt = (
        int(total_length / 2) - len(center_highlighter[0]) - len(start) -
        (int(msg_len / 2) if msg_len % 2 == 0 else int((msg_len + 1) / 2))
    )
    rt_sep_cnt = (
        int(total_length / 2) - len(center_highlighter[1]) - len(end) -
        (int(msg_len / 2) if msg_len % 2 == 0 else int((msg_len - 1) / 2))
    )
    
    _msg = f"{start}{line_symbol*lt_sep_cnt}{center_highlighter[0]}{msg}{center_highlighter[1]}{line_symbol*rt_sep_cnt}{end}"
    return _msg


__all__ = [
    "handle_system_error",
    "create_highlighted_heading",
]
