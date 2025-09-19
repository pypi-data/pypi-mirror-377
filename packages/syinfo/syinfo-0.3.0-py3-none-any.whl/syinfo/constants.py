"""Constants used throughout the SyInfo package."""

from typing import Final

# Display constants for missing or unavailable data
UNKNOWN: Final[str] = "unknown"
NEED_SUDO: Final[str] = "sudo needed"

# Time constants (in seconds)
DAY_IN_SECONDS: Final[int] = 24 * 3600
HOUR_IN_SECONDS: Final[int] = 3600
MINUTE_IN_SECONDS: Final[int] = 60

# Size conversion constants
BYTES_IN_KB: Final[int] = 1024
BYTES_IN_MB: Final[int] = 1024 * 1024
BYTES_IN_GB: Final[int] = 1024 * 1024 * 1024
BYTES_IN_TB: Final[int] = 1024 * 1024 * 1024 * 1024
