"""Analysis module for SyInfo.

This module provides log analysis, package management analysis,
and system health analysis capabilities.

Classes:
- LogAnalyzer: Advanced log file analysis and filtering
- LogAnalysisConfig: Configuration for log analysis operations
- LogEntry: Structured representation of log entries
- PackageManager: Cross-platform package inventory helpers  
- PackageManagerType: Enum for supported package managers
- PackageInfo: Package information data structure
"""

from .logs import LogAnalyzer, LogAnalysisConfig, LogEntry
from .packages import PackageManager, PackageManagerType, PackageInfo

__all__ = [
    # Log analysis
    "LogAnalyzer",
    "LogAnalysisConfig", 
    "LogEntry",
    # Package analysis
    "PackageManager",
    "PackageManagerType",
    "PackageInfo",
]
