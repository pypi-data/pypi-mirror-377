"""Analysis: Log discovery, parsing, and querying.

Linux-first implementation that scans common syslog-style locations with
conservative defaults, supports gzip-rotated files, and provides structured
results for downstream use (CLI/JSON export).
"""

from __future__ import annotations

import concurrent.futures
import gzip
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Pattern, Tuple, Union

from syinfo.utils import Logger

# Get logger instance
logger = Logger.get_logger()


@dataclass
class LogEntry:
    """Structured representation of a log entry."""

    timestamp: Optional[datetime] = None
    level: Optional[str] = None
    process: Optional[str] = None
    pid: Optional[int] = None
    message: str = ""
    raw_line: str = ""
    file_path: str = ""
    line_number: int = 0


@dataclass
class LogAnalysisConfig:
    """Configuration for log analysis operations."""

    log_paths: List[str] = field(
        default_factory=lambda: [
            "/var/log/syslog*",
            "/var/log/messages*",
            "/var/log/kern.log*",
            "/var/log/auth.log*",
        ]
    )
    include_rotated: bool = True
    max_files_per_pattern: int = 10
    max_file_size_mb: int = 100
    default_limit: int = 100
    date_format_patterns: List[str] = field(
        default_factory=lambda: [
            r"(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})",  # Oct 15 14:30:45
            r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})",  # 2023-10-15T14:30:45
            r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})",  # 2023-10-15 14:30:45
        ]
    )


class LogAnalyzer:
    """Advanced log file analyzer with filtering, parsing, and analysis capabilities."""

    def __init__(self, config: Optional[LogAnalysisConfig] = None) -> None:
        # Base config
        self.config = config or LogAnalysisConfig()
        # Allow environment overrides for performance/tuning
        # SYINFO_LOG_PATHS: colon-separated list of globs
        # SYINFO_LOG_MAX_FILES: int
        # SYINFO_LOG_MAX_SIZE_MB: int
        # SYINFO_LOG_DEFAULT_LIMIT: int
        try:
            paths = os.environ.get("SYINFO_LOG_PATHS")
            if paths:
                self.config.log_paths = [p for p in paths.split(":") if p]
            max_files = os.environ.get("SYINFO_LOG_MAX_FILES")
            if max_files:
                self.config.max_files_per_pattern = int(max_files)
            max_size = os.environ.get("SYINFO_LOG_MAX_SIZE_MB")
            if max_size:
                self.config.max_file_size_mb = int(max_size)
            default_limit = os.environ.get("SYINFO_LOG_DEFAULT_LIMIT")
            if default_limit:
                self.config.default_limit = int(default_limit)
        except Exception:
            # Ignore bad overrides; keep safe defaults
            pass

    def discover_log_files(self, patterns: Optional[List[str]] = None) -> List[str]:
        """Discover available log files matching patterns.

        Returns a list of paths sorted by modification time (newest first),
        limited by `max_files_per_pattern` and `max_file_size_mb`.
        """
        patterns = patterns or self.config.log_paths
        discovered_files: List[str] = []

        for pattern in patterns:
            try:
                # glob manually to avoid importing glob here (std lib glob acceptable)
                import glob as _glob

                files = _glob.glob(pattern)
                files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                files = files[: self.config.max_files_per_pattern]

                for file_path in files:
                    if not os.path.exists(file_path):
                        continue
                    size_mb = os.path.getsize(file_path) / (1024 * 1024)
                    if size_mb <= self.config.max_file_size_mb:
                        discovered_files.append(file_path)
                    else:
                        logger.debug(
                            "Skipping large file %s (%.1fMB)", file_path, size_mb
                        )
            except Exception as exc:
                logger.debug("Error discovering files for %s: %s", pattern, exc)

        logger.debug("Discovered %d log files", len(discovered_files))
        return discovered_files

    def _parse_timestamp(self, line: str) -> Optional[datetime]:
        for pattern in self.config.date_format_patterns:
            match = re.search(pattern, line)
            if not match:
                continue
            date_str = match.group(1)
            for fmt in ["%b %d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
                try:
                    if fmt == "%b %d %H:%M:%S":
                        year = datetime.now().year
                        return datetime.strptime(f"{year} {date_str}", f"%Y {fmt}")
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
        return None

    def parse_log_entry(self, line: str, file_path: str, line_number: int) -> LogEntry:
        entry = LogEntry(raw_line=line.strip(), file_path=file_path, line_number=line_number)

        entry.timestamp = self._parse_timestamp(line)

        proc = re.search(r"(\w+)\[(\d+)\]:", line)
        if proc:
            entry.process = proc.group(1)
            try:
                entry.pid = int(proc.group(2))
            except Exception:
                entry.pid = None

        for level in [
            "EMERGENCY",
            "ALERT",
            "CRITICAL",
            "ERROR",
            "WARNING",
            "NOTICE",
            "INFO",
            "DEBUG",
        ]:
            if level in line.upper():
                entry.level = level
                break

        msg_match = re.search(r":\s*(.+)$", line)
        entry.message = msg_match.group(1).strip() if msg_match else line.strip()
        return entry

    def _read_file_lines(self, file_path: str) -> Iterator[str]:
        try:
            if file_path.endswith(".gz"):
                with gzip.open(file_path, "rt", encoding="utf-8", errors="ignore") as f:
                    yield from f
            else:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    yield from f
        except Exception as exc:
            logger.debug("Failed to read %s: %s", file_path, exc)
            return

    def query_logs(
        self,
        text_filter: str = "",
        level_filter: Optional[Union[str, List[str]]] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None,
        process_filter: str = "",
        regex_pattern: Optional[str] = None,
        file_patterns: Optional[List[str]] = None,
        limit: Optional[int] = None,
        reverse_order: bool = True,
    ) -> List[LogEntry]:
        """Query log entries with advanced filtering and search capabilities.

        This method provides comprehensive log analysis functionality, allowing you to
        search, filter, and retrieve log entries based on multiple criteria. It supports
        text searching, log level filtering, time range queries, process filtering,
        regex pattern matching, and file-specific searches.

        Args:
            text_filter (str, optional): Case-insensitive text to search for in log messages.
                Searches in the main log message content. Defaults to "" (no text filter).
            
            level_filter (str | List[str], optional): Filter by log levels. Can be a single
                level string (e.g., "ERROR") or a list of levels (e.g., ["ERROR", "WARN"]).
                Common levels: DEBUG, INFO, WARN, WARNING, ERROR, CRITICAL, FATAL.
                Defaults to None (all levels included).
            
            time_range (Tuple[datetime, datetime], optional): Filter logs within a specific
                time range. Tuple of (start_time, end_time) as datetime objects.
                Only logs with timestamps within this range will be included.
                Defaults to None (no time filtering).
            
            process_filter (str, optional): Filter by process name or PID. Searches for
                the specified text in process information fields. Case-insensitive.
                Defaults to "" (no process filter).
            
            regex_pattern (str, optional): Regular expression pattern to match against
                log messages. Uses case-insensitive matching. If the pattern is invalid,
                it will be ignored. Defaults to None (no regex filtering).
            
            file_patterns (List[str], optional): List of file patterns to search in.
                Supports glob patterns like "*.log", "/var/log/app*.log", etc.
                If not specified, searches in all discovered log files.
                Defaults to None (search all files).
            
            limit (int, optional): Maximum number of log entries to return.
                If not specified, uses the default limit from configuration.
                Defaults to None (use config default).
            
            reverse_order (bool, optional): Whether to return results in reverse
                chronological order (newest first). When True, returns most recent
                entries first. Defaults to True.

        Returns:
            List[LogEntry]: List of LogEntry objects matching the specified criteria.
                Each LogEntry contains parsed log information including timestamp,
                level, message, process info, and source file.

        Examples:
            Basic text search:
            >>> analyzer = LogAnalyzer()
            >>> errors = analyzer.query_logs(text_filter="connection failed")
            
            Filter by log level:
            >>> critical_logs = analyzer.query_logs(level_filter="ERROR")
            >>> multi_level = analyzer.query_logs(level_filter=["ERROR", "CRITICAL"])
            
            Time range query:
            >>> from datetime import datetime, timedelta
            >>> end_time = datetime.now()
            >>> start_time = end_time - timedelta(hours=1)
            >>> recent_logs = analyzer.query_logs(time_range=(start_time, end_time))
            
            Process-specific logs:
            >>> app_logs = analyzer.query_logs(process_filter="nginx")
            
            Regex pattern matching:
            >>> ip_logs = analyzer.query_logs(regex_pattern=r"\\d+\\.\\d+\\.\\d+\\.\\d+")
            
            File-specific search:
            >>> app_logs = analyzer.query_logs(file_patterns=["/var/log/app*.log"])
            
            Combined filtering:
            >>> complex_query = analyzer.query_logs(
            ...     text_filter="database",
            ...     level_filter=["ERROR", "WARN"],
            ...     time_range=(start_time, end_time),
            ...     limit=50
            ... )

        Note:
            - All text-based filters (text_filter, process_filter) are case-insensitive
            - Multiple filters are combined with AND logic (all must match)
            - Invalid regex patterns are silently ignored
            - The method automatically discovers log files if file_patterns is not specified
            - Results are sorted by timestamp, with reverse_order controlling the direction
        """

        limit = limit or self.config.default_limit
        results: List[LogEntry] = []

        if isinstance(level_filter, str):
            level_filter = [level_filter.upper()]
        elif level_filter:
            level_filter = [lvl.upper() for lvl in level_filter]

        regex_compiled: Optional[Pattern[str]] = None
        if regex_pattern:
            try:
                regex_compiled = re.compile(regex_pattern, re.IGNORECASE)
            except re.error:
                regex_compiled = None

        log_files = self.discover_log_files(file_patterns)

        def process_file(file_path: str) -> List[LogEntry]:
            file_results: List[LogEntry] = []
            for line_number, line in enumerate(self._read_file_lines(file_path) or [], start=1):
                if text_filter and text_filter.lower() not in line.lower():
                    continue
                if regex_compiled and not regex_compiled.search(line):
                    continue

                entry = self.parse_log_entry(line, file_path, line_number)

                if level_filter and (not entry.level or entry.level not in level_filter):
                    continue
                if process_filter and (not entry.process or process_filter.lower() not in entry.process.lower()):
                    continue
                if time_range and entry.timestamp:
                    start_time, end_time = time_range
                    if not (start_time <= entry.timestamp <= end_time):
                        continue
                file_results.append(entry)
            return file_results

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_file = {executor.submit(process_file, p): p for p in log_files}
            for future in concurrent.futures.as_completed(future_to_file):
                try:
                    results.extend(future.result())
                except Exception:
                    # ignore file-level failures, return best-effort results
                    continue

        results.sort(key=lambda x: x.timestamp or datetime.min, reverse=reverse_order)
        return results[:limit]

    def get_log_statistics(self, entries: List[LogEntry]) -> Dict[str, Any]:
        """Generate basic statistics for a collection of log entries.

        Args:
            entries: List of LogEntry objects to analyze.

        Returns:
            Dictionary containing statistics including total_entries, date_range,
            level_distribution, process_distribution, file_distribution, and
            hourly_distribution. Returns empty dict if no entries provided.
        """
        if not entries:
            return {}

        stats: Dict[str, Any] = {
            "total_entries": len(entries),
            "date_range": {},
            "level_distribution": {},
            "process_distribution": {},
            "file_distribution": {},
            "hourly_distribution": {},
        }

        timestamps = [e.timestamp for e in entries if e.timestamp]
        if timestamps:
            earliest = min(timestamps)
            latest = max(timestamps)
            stats["date_range"] = {
                "earliest": earliest,
                "latest": latest,
                "span_hours": (latest - earliest).total_seconds() / 3600,
            }

        for e in entries:
            if e.level:
                stats["level_distribution"][e.level] = stats["level_distribution"].get(e.level, 0) + 1
            if e.process:
                stats["process_distribution"][e.process] = stats["process_distribution"].get(e.process, 0) + 1
            file_name = Path(e.file_path).name if e.file_path else ""
            if file_name:
                stats["file_distribution"][file_name] = stats["file_distribution"].get(file_name, 0) + 1
            if e.timestamp:
                hour = e.timestamp.hour
                stats["hourly_distribution"][hour] = stats["hourly_distribution"].get(hour, 0) + 1

        return stats

