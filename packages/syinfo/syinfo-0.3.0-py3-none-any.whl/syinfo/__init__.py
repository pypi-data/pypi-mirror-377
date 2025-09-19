"""SyInfo - System Information Library

A modern, well-designed Python library for gathering system information using
a clean Builder pattern API.

Features:
- Hardware Information: CPU, memory, disk, GPU details
- Network Information: Interfaces, connectivity, device discovery
- Software Information: OS details, kernel info, Python environment
- System Monitoring: Performance monitoring capabilities
- Export Capabilities: JSON, CSV, YAML formats
- CLI Tools: Simple command-line interface

Usage:
    Builder Pattern API (Primary - Recommended):
    >>> import syinfo
    >>> system = (syinfo.InfoBuilder()
    ...     .include_hardware()
    ...     .include_network(timeout=10)
    ...     .enable_caching()
    ...     .build())
    >>> data = await system.collect_async("all")

    Quick presets:
    >>> basic = syinfo.InfoBuilder.basic_system().build()
    >>> full = syinfo.InfoBuilder.full_system().build()
    
    Direct core access (Advanced):
    >>> from syinfo import DeviceInfo, SystemInfo
    >>> device_data = DeviceInfo.get_all()
    >>> system_data = SystemInfo.get_all()
"""

import logging
from typing import Any, Dict, List, Optional

# Version information
from ._version import __author__, __email__, __license__, __version__, __version_info__

# Configure logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Import core functionality
from .core.device_info import DeviceInfo
from .core.system_info import SystemInfo, print_brief_sys_info
from .exceptions import (
    DataCollectionError,
    SyInfoException,
    SystemAccessError,
    ValidationError,
)

# Import network features (full installation required)
from .core.network_info import NetworkInfo
from .core.search_network import search_devices_on_network

# Analysis classes (logs, packages)
from .analysis.logs import LogAnalyzer, LogAnalysisConfig, LogEntry
from .analysis.packages import PackageManager, PackageManagerType, PackageInfo

# Monitoring classes
from .resource_monitor.system_monitor import SystemMonitor
from .resource_monitor.process_monitoring import ProcessMonitor

# Utility classes
from .utils.logger import Logger, LoggerConfig
from .utils.formatters import HumanReadable
from .utils.system import Execute
from .utils.export import export_data

# Builder Pattern API (Primary - Modern)
from .builder import InfoBuilder, SyInfoSystem, SyInfoConfiguration


# Module exports
__all__ = [
    # Version information
    "__version__",
    "__version_info__",
    "__author__",
    "__email__",
    "__license__",
    # Builder Pattern API (Primary - Modern)
    "InfoBuilder",
    "SyInfoSystem", 
    "SyInfoConfiguration",
    # Core classes (for advanced usage)
    "DeviceInfo",
    "SystemInfo", 
    # Network classes (for advanced usage)
    "NetworkInfo",
    "search_devices_on_network",
    # Analysis classes (logs, packages)
    "LogAnalyzer",
    "LogAnalysisConfig",
    "LogEntry",
    "PackageManager",
    "PackageManagerType",
    "PackageInfo",
    # Monitoring classes
    "SystemMonitor",
    "ProcessMonitor",
    # Utility classes
    "Logger",
    "LoggerConfig",
    "HumanReadable",
    "Execute",
    "export_data",
    # Exceptions
    "SyInfoException",
    "DataCollectionError",
    "SystemAccessError",
    "ValidationError",
    # Legacy compatibility
    "print_brief_sys_info",
]