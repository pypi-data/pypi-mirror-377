"""SyInfo Exceptions - Simplified

Essential exceptions for the SyInfo library without over-engineering.
"""


class SyInfoException(Exception):
    """Base exception for all SyInfo errors.

    Accepts arbitrary keyword arguments for compatibility with callers that
    provide structured context (e.g., details, resource_path, required_privilege).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        # Attach any keyword context as attributes for downstream use
        for key, value in kwargs.items():
            try:
                setattr(self, key, value)
            except Exception:
                # Avoid failing exception construction on attribute set
                pass
        # Also keep a copy on a common attribute
        self.context = kwargs or {}


class DataCollectionError(SyInfoException):
    """Raised when data collection fails."""

    pass


class SystemAccessError(SyInfoException):
    """Raised when system access is denied or insufficient privileges."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ValidationError(SyInfoException):
    """Raised when input validation fails."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


__all__ = [
    "SyInfoException",
    "DataCollectionError", 
    "SystemAccessError",
    "ValidationError",
]
