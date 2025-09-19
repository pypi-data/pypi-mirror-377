"""
SyInfo Builder - Keras-style fluent API for system information collection.

This module provides a clean, discoverable interface for configuring and collecting
system information using the Builder pattern, while preserving all existing
functionality in the core modules.
"""

from .config import SyInfoConfiguration
from .facade import InfoBuilder, SyInfoSystem

__all__ = [
    "InfoBuilder",
    "SyInfoSystem", 
    "SyInfoConfiguration",
]
