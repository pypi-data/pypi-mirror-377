"""
Configuration management for SyInfo Builder Pattern.

This module defines configuration dataclasses that store all settings
without touching any base code functionality.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path


@dataclass
class NetworkConfig:
    """Network scanning configuration."""
    enabled: bool = False
    timeout: int = 10
    include_vendor_info: bool = True
    include_wifi_scan: bool = False
    max_devices: int = 255
    async_scanning: bool = True  # Use async for network operations


@dataclass
class MonitoringConfig:
    """System monitoring configuration."""
    enabled: bool = False
    interval: int = 60
    duration: Optional[int] = None
    output_path: Optional[Path] = None
    keep_in_memory: bool = True
    rotate_max_lines: Optional[int] = None
    rotate_max_bytes: Optional[int] = None
    summary_on_stop: bool = True
    callback: Optional[Callable[[Dict[str, Any]], None]] = None


@dataclass
class ProcessMonitoringConfig:
    """Process monitoring configuration."""
    enabled: bool = False
    filters: List[str] = field(default_factory=list)
    match_fields: List[str] = field(default_factory=lambda: ['name', 'cmdline'])
    case_sensitive: bool = False
    use_regex: bool = False
    include_children: bool = False
    interval: int = 30


@dataclass
class LogAnalysisConfig:
    """Log analysis configuration."""
    enabled: bool = False
    log_paths: List[str] = field(default_factory=lambda: [
        "/var/log/syslog*", "/var/log/messages*", "/var/log/kern.log*"
    ])
    include_rotated: bool = True
    max_files_per_pattern: int = 10
    max_file_size_mb: int = 100
    time_range: Optional[tuple] = None
    level_filter: Optional[List[str]] = None
    text_filter: str = ""
    regex_pattern: Optional[str] = None
    limit: int = 100


@dataclass
class PackageAnalysisConfig:
    """Package analysis configuration."""
    enabled: bool = False
    manager_types: List[str] = field(default_factory=list)  # apt, yum, pip, conda, etc.
    name_filter: str = ""
    include_versions: bool = True
    include_descriptions: bool = False


@dataclass
class ExportConfig:
    """Export configuration."""
    format: str = "json"
    output_file: Optional[Path] = None
    include_sensitive: bool = False
    pretty_print: bool = True


@dataclass
class SyInfoConfiguration:
    """Complete SyInfo configuration for the Builder pattern."""
    
    # Core settings
    cache_enabled: bool = False
    cache_ttl: int = 300  # 5 minutes
    log_level: str = "INFO"
    timeout: int = 30
    
    # Hardware settings
    include_hardware: bool = True
    include_gpu: bool = True
    include_disk: bool = True
    
    # Feature configurations
    network: NetworkConfig = field(default_factory=NetworkConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    process_monitoring: ProcessMonitoringConfig = field(default_factory=ProcessMonitoringConfig)
    log_analysis: LogAnalysisConfig = field(default_factory=LogAnalysisConfig)
    package_analysis: PackageAnalysisConfig = field(default_factory=PackageAnalysisConfig)
    export: ExportConfig = field(default_factory=ExportConfig)
    
    def validate(self) -> None:
        """Validate configuration settings."""
        # Allow 0 to disable active scanning while still enabling network info
        if self.network.timeout < 0:
            raise ValueError("Network timeout must be non-negative")
        if self.monitoring.interval <= 0:
            raise ValueError("Monitoring interval must be positive")
        if self.cache_ttl <= 0:
            raise ValueError("Cache TTL must be positive")
        if self.timeout <= 0:
            raise ValueError("Global timeout must be positive")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        # This could be useful for serialization/debugging
        result = {}
        for field_name, field_value in self.__dict__.items():
            if hasattr(field_value, '__dict__'):  # Nested dataclass
                result[field_name] = field_value.__dict__
            else:
                result[field_name] = field_value
        return result
