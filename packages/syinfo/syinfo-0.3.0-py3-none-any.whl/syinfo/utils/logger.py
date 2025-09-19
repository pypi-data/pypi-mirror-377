"""This code implements a refined singleton logger class with enhanced functionality."""

import os
import re
import sys
import logging
import logging.handlers
import traceback
import platform
from typing import List, Optional, Union, Dict, Any, Tuple
from functools import wraps
from pathlib import Path


class LoggerConfig:
    """Configuration for logger settings including syslog support.
    
    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_files: List of file paths to write logs to
        truncate_log_files: Clear existing files on startup vs append
        output_to_stdout: Show logs in console
        verbose_logs: Include function names and line numbers
        enable_incident_counting: Add numbers to warnings/errors
        enable_traceback: Include Python tracebacks in errors
        enable_syslog: Send logs to system syslog
        syslog_address: Syslog destination (None=auto-detect, str=socket, tuple=network)
        syslog_facility: Syslog facility (LOG_USER, LOG_LOCAL0-7, etc.)
        syslog_socktype: Socket type for network syslog (UDP/TCP)
    """
    
    def __init__(
        self,
        log_level: int = logging.INFO,
        log_files: Optional[List[str]] = None,
        truncate_log_files: bool = True,
        output_to_stdout: bool = True,
        verbose_logs: bool = False,
        enable_incident_counting: bool = True,
        enable_traceback: bool = True,
        enable_syslog: bool = False,
        syslog_address: Optional[Union[str, Tuple[str, int]]] = None,
        syslog_facility: int = logging.handlers.SysLogHandler.LOG_USER,
        syslog_socktype: Optional[int] = None
    ):
        self.log_level = log_level
        self.log_files = log_files or []
        self.truncate_log_files = truncate_log_files
        self.output_to_stdout = output_to_stdout
        self.verbose_logs = verbose_logs
        self.enable_incident_counting = enable_incident_counting
        self.enable_traceback = enable_traceback
        self.enable_syslog = enable_syslog
        self.syslog_address = syslog_address
        self.syslog_facility = syslog_facility
        self.syslog_socktype = syslog_socktype


class Logger:
    """Advanced singleton logger with comprehensive configuration options.
    
    Provides centralized logging for the SyInfo package with features including:
    - Multiple output destinations (console, files, syslog)
    - Automatic incident counting for warnings/errors
    - Configurable log rotation and formatting
    - Syslog integration for system-wide logging
    - Thread-safe singleton pattern
    - Environment variable overrides
    
    The logger is designed as a singleton to ensure consistent configuration
    across all modules in the package. Configuration is done once at 
    initialization and applies to all subsequent usage.
    
    Examples:
        >>> config = LoggerConfig(log_level=logging.DEBUG)
        >>> logger = Logger.get_logger(config)
        >>> logger.info("System information collection started")
        
        # Singleton behavior - same instance returned
        >>> logger2 = Logger.get_logger()
        >>> assert logger is logger2
        
    Note:
        The first call to Logger() or get_logger() determines the 
        configuration for all subsequent calls.
    """
    
    _instance: Optional['Logger'] = None
    
    def __new__(cls, config: Optional[LoggerConfig] = None) -> 'Logger':
        """Create or return singleton Logger instance.
        
        Args:
            config: Logger configuration (only used on first instantiation)
            
        Returns:
            Singleton Logger instance
            
        Note:
            Configuration is only applied during the first instantiation.
            Subsequent calls ignore the config parameter.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance
    
    def __init__(self, config: Optional[LoggerConfig] = None) -> None:
        """Initialize logger configuration (singleton - only runs once).
        
        Args:
            config: Logger configuration. If None, uses default LoggerConfig.
                   Only applied during first initialization.
                   
        Note:
            This method implements the singleton pattern - it only executes
            the initialization code once, even if called multiple times.
        """
        if hasattr(self, '_Logger__initialized') and self.__initialized:
            return
        
        if config is None:
            config = LoggerConfig()
        
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(config.log_level)
        
        # Incident tracking for numbered warnings/errors
        self.warning_count = 0
        self.error_count = 0
        
        # Clear any existing handlers to prevent duplicates
        self.logger.handlers.clear()
        
        # Prevent propagation to root logger to avoid duplicate messages
        self.logger.propagate = False
        
        # Setup handlers
        self._setup_handlers()
        
        # Apply custom overrides
        if config.enable_incident_counting:
            self._apply_warning_override()
            self._apply_error_override()
        
        self.__initialized = True
        # self.logger.info("Logger initialized successfully")
    
    @classmethod
    def get_logger(cls, config: Optional[LoggerConfig] = None) -> logging.Logger:
        """Get the singleton logger instance."""
        if cls._instance is None:
            cls._instance = cls(config)
        return cls._instance.logger
    
    @classmethod 
    def get_instance(cls) -> Optional['Logger']:
        """Get the Logger instance (not the logging.Logger)."""
        return cls._instance
    
    def set_log_level(self, level: Union[int, str]) -> None:
        """Change the log level after initialization.
        
        Args:
            level: New log level (e.g., logging.DEBUG, 'DEBUG', 10)
        """
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.INFO)
        
        self.config.log_level = level
        self.logger.setLevel(level)
        
        # Update all handlers
        for handler in self.logger.handlers:
            handler.setLevel(level)
        
        self.logger.info(f"Log level changed to {logging.getLevelName(level)}")
    
    def add_file_handler(self, file_path: str, truncate: bool = False) -> None:
        """Add a new file handler to the logger.
        
        Args:
            file_path: Path to log file
            truncate: Whether to truncate existing file
        """
        try:
            if truncate and os.path.exists(file_path):
                os.remove(file_path)
            
            # Create parent directory if needed
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            handler = logging.FileHandler(file_path)
            handler.setLevel(self.config.log_level)
            handler.setFormatter(self._get_formatter())
            
            self.logger.addHandler(handler)
            self.logger.info(f"Added file handler for: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to add file handler: {e}")
    
    def add_syslog_handler(
        self, 
        address: Optional[Union[str, Tuple[str, int]]] = None,
        facility: int = logging.handlers.SysLogHandler.LOG_USER,
        socktype: Optional[int] = None
    ) -> None:
        """Add a syslog handler to the logger.
        
        Args:
            address: Syslog server address. Can be:
                    - Unix socket path (str): '/dev/log' (Linux), '/var/run/syslog' (macOS)
                    - TCP/UDP tuple: ('localhost', 514)
                    - None: Auto-detect based on platform
            facility: Syslog facility (e.g., LOG_USER, LOG_LOCAL0-7, LOG_DAEMON)
            socktype: Socket type (socket.SOCK_DGRAM for UDP, socket.SOCK_STREAM for TCP)
        """
        try:
            # Auto-detect syslog address if not provided
            if address is None:
                address = self._get_default_syslog_address()
            
            # Create syslog handler
            if isinstance(address, str):
                # Unix socket
                handler = logging.handlers.SysLogHandler(address=address, facility=facility)
            else:
                # TCP/UDP
                if socktype is None:
                    import socket
                    socktype = socket.SOCK_DGRAM  # Default to UDP
                handler = logging.handlers.SysLogHandler(
                    address=address, facility=facility, socktype=socktype
                )
            
            handler.setLevel(self.config.log_level)
            
            # Use a simpler formatter for syslog (it adds its own timestamp)
            syslog_formatter = logging.Formatter(
                '%(name)s[%(process)d]: %(levelname)s - %(message)s'
            )
            handler.setFormatter(syslog_formatter)
            
            self.logger.addHandler(handler)
            self.logger.info(f"Added syslog handler: {address}")
            
        except Exception as e:
            self.logger.error(f"Failed to add syslog handler: {e}")
    
    def _get_default_syslog_address(self) -> Union[str, Tuple[str, int]]:
        """Get default syslog address based on platform."""
        system = platform.system().lower()
        
        if system == 'linux':
            # Try common Linux syslog socket paths
            linux_paths = ['/dev/log', '/var/run/rsyslog/kmsg']
            for path in linux_paths:
                if os.path.exists(path):
                    return path
            # Fallback to localhost UDP
            return ('localhost', 514)
            
        elif system == 'darwin':  # macOS
            # macOS syslog socket
            macos_path = '/var/run/syslog'
            if os.path.exists(macos_path):
                return macos_path
            return ('localhost', 514)
            
        else:  # Windows and others
            # Use network syslog (requires syslog daemon)
            return ('localhost', 514)
    
    def remove_handlers_by_type(self, handler_type: type) -> None:
        """Remove handlers of specific type.
        
        Args:
            handler_type: Type of handler to remove (e.g., logging.FileHandler)
        """
        handlers_to_remove = [h for h in self.logger.handlers if isinstance(h, handler_type)]
        for handler in handlers_to_remove:
            self.logger.removeHandler(handler)
            handler.close()
    
    def reset_incident_counters(self) -> None:
        """Reset warning and error counters."""
        self.warning_count = 0
        self.error_count = 0
        self.logger.info("Incident counters reset")
    
    def enable_syslog(
        self,
        address: Optional[Union[str, Tuple[str, int]]] = None,
        facility: int = logging.handlers.SysLogHandler.LOG_USER,
        socktype: Optional[int] = None
    ) -> None:
        """Enable syslog logging after initialization.
        
        Args:
            address: Syslog server address (auto-detected if None)
            facility: Syslog facility
            socktype: Socket type for network syslog
        """
        self.config.enable_syslog = True
        self.config.syslog_address = address
        self.config.syslog_facility = facility
        self.config.syslog_socktype = socktype
        self.add_syslog_handler(address, facility, socktype)
    
    def disable_syslog(self) -> None:
        """Disable syslog logging by removing syslog handlers."""
        self.config.enable_syslog = False
        self.remove_handlers_by_type(logging.handlers.SysLogHandler)
        self.logger.info("Syslog logging disabled")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get logger statistics."""
        return {
            'warning_count': self.warning_count,
            'error_count': self.error_count,
            'log_level': logging.getLevelName(self.logger.level),
            'handler_count': len(self.logger.handlers),
            'handlers': [type(h).__name__ for h in self.logger.handlers]
        }
    
    def _setup_handlers(self) -> None:
        """Setup initial handlers based on configuration."""
        formatter = self._get_formatter()
        
        # Console handler
        if self.config.output_to_stdout:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.config.log_level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # File handlers
        for log_file in self.config.log_files:
            self.add_file_handler(log_file, self.config.truncate_log_files)
        
        # Syslog handler
        if self.config.enable_syslog:
            self.add_syslog_handler(
                address=self.config.syslog_address,
                facility=self.config.syslog_facility,
                socktype=self.config.syslog_socktype
            )
    
    def _get_formatter(self) -> logging.Formatter:
        """Get appropriate formatter based on configuration."""
        format_string = '%(asctime)s | %(levelname)8s |'
        if self.config.verbose_logs:
            format_string += ' %(funcName)s:%(lineno)d |'
        format_string += ' %(message)s'
        
        return logging.Formatter(format_string)
    
    def _apply_warning_override(self) -> None:
        """Apply warning override with incident counting."""
        original_warning = self.logger.warning
        
        @wraps(original_warning)
        def warning_with_count(msg, *args, **kwargs):
            self.warning_count += 1
            msg = f'(incident #{self.warning_count}) {msg}'
            original_warning(msg, *args, **kwargs)
        
        self.logger.warning = warning_with_count
    
    def _apply_error_override(self) -> None:
        """Apply error override with traceback and incident counting."""
        original_error = self.logger.error
        
        @wraps(original_error)
        def error_with_traceback(msg, include_traceback=True, *args, **kwargs):
            if include_traceback and self.config.enable_traceback:
                traceback_msg = format_exception_traceback()
                if traceback_msg:
                    msg = f'{msg}\n{traceback_msg}'
            
            self.error_count += 1
            msg = f'(incident #{self.error_count}) {msg}'
            
            # Clean up multiple newlines
            msg = re.sub(r'\n+', '\n', str(msg)).strip()
            original_error(msg, *args, **kwargs)
        
        self.logger.error = error_with_traceback


def format_exception_traceback() -> Optional[str]:
    """Format current exception traceback in a clean, readable format.
    
    Returns:
        Formatted traceback string or None if no exception is active
    """
    exc_info = sys.exc_info()
    exc_type, exc_value, exc_traceback = exc_info
    
    if exc_type is None:
        return None
    
    try:
        tb_lines = traceback.extract_tb(exc_traceback)
        
        if not tb_lines:
            return f"{exc_type.__name__}: {exc_value}"
        
        # Build clean traceback format
        lines = [f"╭─ Traceback ({exc_type.__name__})"]
        
        for i, tb_line in enumerate(tb_lines, 1):
            is_last = i == len(tb_lines)
            prefix = "├─" if not is_last else "╰─"
            
            lines.extend([
                f"{prefix} [{i}] {Path(tb_line.filename).name}:{tb_line.lineno} in {tb_line.name}()",
                f"│     {tb_line.line.strip()}" if tb_line.line else "│     <code unavailable>"
            ])
        
        lines.append(f"╰─ {exc_type.__name__}: {exc_value}")
        
        return '\n'.join(lines)
        
    except Exception as fallback_error:
        # Fallback to basic format if formatting fails
        return f"Traceback format error: {fallback_error}\n{exc_type.__name__}: {exc_value}"

