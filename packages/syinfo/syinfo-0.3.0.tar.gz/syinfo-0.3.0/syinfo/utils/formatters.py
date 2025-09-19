"""Data formatting and conversion utilities."""

from functools import lru_cache
from typing import Dict, Union

from syinfo.constants import (
    BYTES_IN_KB, 
    BYTES_IN_MB, 
    BYTES_IN_GB, 
    BYTES_IN_TB,
    DAY_IN_SECONDS,
    HOUR_IN_SECONDS,
    MINUTE_IN_SECONDS
)
from syinfo.exceptions import ValidationError


class HumanReadable:
    """Convert various data formats to human-readable representations.
    
    This class provides static methods for converting bytes to human-readable sizes,
    time durations to readable formats, and other data conversions.
    Methods are cached for performance optimization.
    """

    @staticmethod
    @lru_cache(maxsize=128)
    def size_to_bytes(size: Union[str, int, float]) -> int:
        """Convert size with units to number of bytes.
        
        Args:
            size: Size string with unit (e.g., "32 MB", "100 kB") or numeric value
            
        Returns:
            Number of bytes as integer
            
        Raises:
            ValidationError: If size format is invalid
            
        Examples:
            >>> HumanReadable.size_to_bytes("32 MB")
            33554432
            >>> HumanReadable.size_to_bytes("1 GB")
            1073741824
        """
        multipliers: Dict[str, int] = {
            "kb": BYTES_IN_KB,
            "mb": BYTES_IN_MB,
            "gb": BYTES_IN_GB,
            "tb": BYTES_IN_TB,
        }
        
        if isinstance(size, (int, float)):
            return int(size)
            
        size_str = str(size).strip().lower()
        
        # Remove spaces between number and unit
        size_str = size_str.replace(" ", "")
        
        # Check for unit multipliers
        for suffix, multiplier in multipliers.items():
            if size_str.endswith(suffix):
                try:
                    value = float(size_str[:-len(suffix)])
                    return int(value * multiplier)
                except ValueError:
                    raise ValidationError(
                        f"Invalid numeric value in size: {size}",
                        details={"field_name": "size", "field_value": str(size)}
                    )
        
        # Handle bytes suffix
        if size_str.endswith("b"):
            try:
                return int(float(size_str[:-1]))
            except ValueError:
                raise ValidationError(
                    f"Invalid numeric value in size: {size}",
                    details={"field_name": "size", "field_value": str(size)}
                )
        
        # Plain number
        try:
            return int(float(size_str))
        except ValueError:
            raise ValidationError(
                f"Invalid size format: {size}. Expected format like '1GB', '512MB', or plain number",
                details={"field_name": "size", "field_value": str(size)}
            )

    @staticmethod
    @lru_cache(maxsize=128)
    def bytes_to_size(num_bytes: Union[int, float], suffix: str = "B") -> str:
        """Convert bytes to a human-readable format.
        
        Args:
            num_bytes: Number of bytes to convert
            suffix: Suffix to append to the unit
            
        Returns:
            Human-readable size string
            
        Examples:
            >>> HumanReadable.bytes_to_size(1073741824)
            '1.0 GB'
            >>> HumanReadable.bytes_to_size(1536)
            '1.5 KB'
        """
        if not isinstance(num_bytes, (int, float)):
            raise ValidationError(
                "num_bytes must be numeric",
                details={"field_name": "num_bytes", "expected_type": "int or float"}
            )
            
        if num_bytes < 0:
            return f"-{HumanReadable.bytes_to_size(-num_bytes, suffix)}"
            
        units = ["", "K", "M", "G", "T", "P", "E", "Z"]
        
        for unit in units:
            if abs(num_bytes) < 1024.0:
                return f"{num_bytes:3.1f} {unit}{suffix}"
            num_bytes /= 1024.0
        
        return f"{num_bytes:.1f} Yi{suffix}"

    @staticmethod
    @lru_cache(maxsize=64)
    def time_spend(time_in_sec: Union[int, float]) -> str:
        """Convert time in seconds to human readable format.
        
        Args:
            time_in_sec: Time duration in seconds
            
        Returns:
            Human readable time string
            
        Raises:
            ValidationError: If time_in_sec is not numeric
            
        Examples:
            >>> HumanReadable.time_spend(3661)
            '1 hr, 1 min, 1 sec, 0.0 ms'
            >>> HumanReadable.time_spend(90)
            '1 min, 30 sec, 0.0 ms'
        """
        if not isinstance(time_in_sec, (int, float)):
            raise ValidationError(
                "time_in_sec must be numeric",
                details={"field_name": "time_in_sec", "expected_type": "int or float"}
            )
            
        if time_in_sec < 0:
            return f"negative time: {time_in_sec}"
        
        day = int(time_in_sec // DAY_IN_SECONDS)
        time_in_sec = time_in_sec % DAY_IN_SECONDS
        hour = int(time_in_sec // HOUR_IN_SECONDS)
        time_in_sec %= HOUR_IN_SECONDS
        minutes = int(time_in_sec // MINUTE_IN_SECONDS)
        time_in_sec %= MINUTE_IN_SECONDS
        seconds = int(time_in_sec)
        msec = round((time_in_sec % 1) * 1000, 2)

        if day != 0:
            return f"{day} day, {hour} hr, {minutes} min, {seconds} sec, {msec} ms"
        elif hour != 0:
            return f"{hour} hr, {minutes} min, {seconds} sec, {msec} ms"
        elif minutes != 0:
            return f"{minutes} min, {seconds} sec, {msec} ms"
        else:
            return f"{seconds} sec, {msec} ms"


__all__ = ["HumanReadable"]
