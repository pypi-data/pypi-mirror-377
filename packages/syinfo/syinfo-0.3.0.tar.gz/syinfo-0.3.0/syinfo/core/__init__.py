"""Core module for SyInfo.

This module provides the core functionality for system information gathering,
including device information, system information, and network information.

Classes:
- DeviceInfo: Hardware and device information collection
- SystemInfo: Complete system information with optional network data
- NetworkInfo: Network interface and connectivity information
"""

from .device_info import DeviceInfo
from .system_info import SystemInfo, print_brief_sys_info
from .network_info import NetworkInfo
from .search_network import search_devices_on_network

__all__ = [
    # Core classes
    "DeviceInfo",
    "SystemInfo", 
    "NetworkInfo",
    # Network functions
    "search_devices_on_network",
    # Utility functions
    "print_brief_sys_info",
]