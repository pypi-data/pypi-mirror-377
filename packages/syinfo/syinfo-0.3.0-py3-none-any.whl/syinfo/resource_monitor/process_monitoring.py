"""Process monitor with string-based filtering and optional on-disk persistence.

Monitors processes matching specified string patterns (name, cmdline, or exe path).
Supports crash-safe persistence with JSONL format and optional rotation.
"""

import json
import os
import re
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import psutil

from syinfo.exceptions import DataCollectionError
from syinfo.utils import HumanReadable, Logger

# Get logger instance
logger = Logger.get_logger()


class ProcessMonitor:
    """Process monitoring with string-based filtering and optional persistence.

    Monitors processes that match specified string patterns in their name,
    command line, or executable path. Data can be persisted to JSONL files
    with optional rotation by lines or bytes.
    """

    def __init__(
        self,
        filters: Optional[Union[str, List[str]]] = None,
        match_fields: Optional[List[str]] = None,
        case_sensitive: bool = False,
        use_regex: bool = False,
        interval: int = 30,
        output_path: Optional[str] = None,
        rotate_max_lines: Optional[int] = None,
        rotate_max_bytes: Optional[int] = None,
        keep_in_memory: bool = True,
        summary_on_stop: bool = True,
        include_children: bool = False,
    ):
        """Initialize process monitor.

        Args:
            filters: String or list of strings to match against processes
            match_fields: Fields to match against ('name', 'cmdline', 'exe'). Default: ['name', 'cmdline']
            case_sensitive: Whether string matching is case sensitive
            use_regex: Whether filters are treated as regex patterns
            interval: Monitoring interval in seconds
            output_path: Optional path (file or directory) to persist data (JSONL)
            rotate_max_lines: Rotate file after this many lines (optional)
            rotate_max_bytes: Rotate file after this many bytes (optional)
            keep_in_memory: Keep collected data points in memory (default True)
            summary_on_stop: Write summary JSON on stop (when output_path is set)
            include_children: Include child process information
        """
        # Filter configuration
        if filters is None:
            self.filters = []
        elif isinstance(filters, str):
            self.filters = [filters]
        else:
            self.filters = list(filters)

        self.match_fields = match_fields or ['name', 'cmdline']
        self.case_sensitive = case_sensitive
        self.use_regex = use_regex
        self.include_children = include_children

        # Compile regex patterns if needed
        self._compiled_patterns: List[re.Pattern] = []
        if self.use_regex:
            flags = 0 if self.case_sensitive else re.IGNORECASE
            for pattern in self.filters:
                try:
                    self._compiled_patterns.append(re.compile(pattern, flags))
                except re.error as e:
                    raise ValueError(f"Invalid regex pattern '{pattern}': {e}")

        # Monitoring configuration
        self.interval = interval
        self.is_running = False
        self.data_points: List[Dict[str, Any]] = []
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Persistence configuration
        self._output_path = Path(output_path) if output_path else None
        self._resolved_output_path: Optional[Path] = None
        self._rotate_max_lines = rotate_max_lines
        self._rotate_max_bytes = rotate_max_bytes
        self._keep_in_memory = keep_in_memory
        self._summary_on_stop = summary_on_stop
        self._log_fp: Optional[Any] = None
        self._lines_written = 0
        self._bytes_written = 0

    def start(
        self,
        duration: Optional[int] = None,
        callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> None:
        """Start process monitoring.

        Args:
            duration: Duration in seconds (None for infinite)
            callback: Optional callback for each data point
        """
        if self.is_running:
            raise DataCollectionError("Process monitoring is already running")

        self.is_running = True
        self._stop_event.clear()
        self.data_points = []

        # Prepare persistence
        if self._output_path:
            self._prepare_output()

        def monitor_loop() -> None:
            start_time = time.time()

            while not self._stop_event.is_set():
                try:
                    # Collect data point
                    data_point = self._collect_data_point()
                    if self._keep_in_memory:
                        self.data_points.append(data_point)

                    # Persist to disk for crash-safety
                    if self._log_fp:
                        self._write_jsonl(data_point)

                    # Callback
                    if callback:
                        callback(data_point)

                    # Duration check
                    if duration and (time.time() - start_time) >= duration:
                        break

                    # Sleep until next interval
                    self._stop_event.wait(self.interval)

                except Exception as e:
                    logger.error(f"Process monitoring error: {e}")
                    continue

            self.is_running = False

        self._thread = threading.Thread(target=monitor_loop, daemon=True)
        self._thread.start()

    def stop(self, print_summary: bool = True, save_plot_to: Optional[str] = None) -> Dict[str, Any]:
        """Stop monitoring and return collected data.

        Args:
            print_summary: Whether to print summary to stdout
            save_plot_to: Optional path to save a plot

        Returns:
            Dictionary with monitoring results
        """
        # Stop the monitoring if it's still running
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)

        # Calculate summary statistics
        if self.data_points:
            summary = self._calculate_summary()
        else:
            summary = {"error": "No data points collected"}

        # Optionally print summary to stdout
        if print_summary:
            try:
                self._print_summary(summary)
            except Exception:
                pass

        # Write summary next to JSONL file
        if self._summary_on_stop and self._resolved_output_path:
            try:
                summary_path = self._resolved_output_path.with_suffix(".summary.json")
                with open(summary_path, "w", encoding="utf-8") as sfp:
                    json.dump(summary, sfp, ensure_ascii=False, indent=2, default=str)
            except Exception:
                pass

        # Optionally save a plot locally
        plot_path: Optional[str] = None
        if save_plot_to:
            try:
                plot_path = self._save_plot(save_plot_to)
            except Exception:
                plot_path = None

        # Close file handle
        try:
            if self._log_fp:
                self._log_fp.flush()
                self._log_fp.close()
        finally:
            self._log_fp = None

        return {
            "summary": summary,
            "data_points": self.data_points,
            "total_points": len(self.data_points),
            "plot_path": plot_path,
        }

    def _collect_data_point(self) -> Dict[str, Any]:
        """Collect a single data point with filtered processes."""
        timestamp = datetime.now().isoformat()
        matched_processes = []
        total_cpu = 0.0
        total_memory = 0
        process_count = 0

        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'exe', 'cpu_percent', 'memory_info', 'create_time']):
                try:
                    if self._matches_filter(proc.info):
                        # Get additional process details
                        proc_data = {
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': proc.info['cmdline'],
                            'exe': proc.info['exe'],
                            'cpu_percent': proc.info['cpu_percent'] or 0.0,
                            'memory_rss': proc.info['memory_info'].rss if proc.info['memory_info'] else 0,
                            'memory_vms': proc.info['memory_info'].vms if proc.info['memory_info'] else 0,
                            'create_time': proc.info['create_time'],
                        }

                        # Add human-readable memory sizes
                        proc_data['memory_rss_human'] = HumanReadable.bytes_to_size(proc_data['memory_rss'])
                        proc_data['memory_vms_human'] = HumanReadable.bytes_to_size(proc_data['memory_vms'])

                        # Include children if requested
                        if self.include_children:
                            try:
                                children = []
                                for child in psutil.Process(proc.info['pid']).children(recursive=True):
                                    children.append({
                                        'pid': child.pid,
                                        'name': child.name(),
                                        'cpu_percent': child.cpu_percent(),
                                        'memory_rss': child.memory_info().rss,
                                    })
                                proc_data['children'] = children
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                proc_data['children'] = []

                        matched_processes.append(proc_data)
                        total_cpu += proc_data['cpu_percent']
                        total_memory += proc_data['memory_rss']
                        process_count += 1

                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    # Process disappeared or access denied, skip
                    continue

        except Exception as e:
            logger.error(f"Error collecting process data: {e}")

        return {
            'timestamp': timestamp,
            'process_count': process_count,
            'total_cpu_percent': total_cpu,
            'total_memory_bytes': total_memory,
            'total_memory_human': HumanReadable.bytes_to_size(total_memory),
            'avg_cpu_percent': total_cpu / process_count if process_count > 0 else 0.0,
            'avg_memory_bytes': total_memory // process_count if process_count > 0 else 0,
            'filters_used': self.filters,
            'match_fields': self.match_fields,
            'processes': matched_processes,
        }

    def _matches_filter(self, proc_info: Dict[str, Any]) -> bool:
        """Check if a process matches any of the configured filters."""
        if not self.filters:
            return True  # No filters means match all processes

        for field in self.match_fields:
            field_value = proc_info.get(field)
            if field_value is None:
                continue

            # Convert to string for matching
            if field == 'cmdline' and isinstance(field_value, list):
                field_str = ' '.join(field_value) if field_value else ''
            else:
                field_str = str(field_value)

            # Apply case sensitivity
            search_str = field_str if self.case_sensitive else field_str.lower()

            # Check against each filter
            for i, filter_str in enumerate(self.filters):
                if self.use_regex:
                    # Use compiled regex patterns
                    if i < len(self._compiled_patterns) and self._compiled_patterns[i].search(search_str):
                        return True
                else:
                    # Simple string matching
                    match_str = filter_str if self.case_sensitive else filter_str.lower()
                    if match_str in search_str:
                        return True

        return False

    def _calculate_summary(self) -> Dict[str, Any]:
        """Calculate summary statistics from collected data."""
        if not self.data_points:
            return {}

        process_counts = [dp['process_count'] for dp in self.data_points]
        cpu_totals = [dp['total_cpu_percent'] for dp in self.data_points]
        memory_totals = [dp['total_memory_bytes'] for dp in self.data_points]

        samples = len(self.data_points)
        duration_seconds = samples * self.interval
        approx_rate_hz = (samples / duration_seconds) if duration_seconds > 0 else 0.0

        # Find most common processes
        all_processes = {}
        for dp in self.data_points:
            for proc in dp.get('processes', []):
                proc_name = proc.get('name', 'unknown')
                if proc_name not in all_processes:
                    all_processes[proc_name] = {'count': 0, 'max_cpu': 0.0, 'max_memory': 0}
                all_processes[proc_name]['count'] += 1
                all_processes[proc_name]['max_cpu'] = max(all_processes[proc_name]['max_cpu'], proc.get('cpu_percent', 0.0))
                all_processes[proc_name]['max_memory'] = max(all_processes[proc_name]['max_memory'], proc.get('memory_rss', 0))

        # Sort by frequency
        top_processes = sorted(all_processes.items(), key=lambda x: x[1]['count'], reverse=True)[:10]

        return {
            'duration_seconds': duration_seconds,
            'samples': samples,
            'interval_seconds': self.interval,
            'approx_rate_hz': approx_rate_hz,
            'filters_used': self.filters,
            'match_fields': self.match_fields,
            'case_sensitive': self.case_sensitive,
            'use_regex': self.use_regex,
            'process_count_avg': sum(process_counts) / len(process_counts) if process_counts else 0.0,
            'process_count_max': max(process_counts) if process_counts else 0,
            'process_count_min': min(process_counts) if process_counts else 0,
            'total_cpu_avg': sum(cpu_totals) / len(cpu_totals) if cpu_totals else 0.0,
            'total_cpu_max': max(cpu_totals) if cpu_totals else 0.0,
            'total_memory_avg': sum(memory_totals) / len(memory_totals) if memory_totals else 0,
            'total_memory_max': max(memory_totals) if memory_totals else 0,
            'total_memory_max_human': HumanReadable.bytes_to_size(max(memory_totals) if memory_totals else 0),
            'top_processes': top_processes,
            'start_time': self.data_points[0]['timestamp'] if self.data_points else None,
            'end_time': self.data_points[-1]['timestamp'] if self.data_points else None,
        }

    def _print_summary(self, summary: Dict[str, Any]) -> None:
        """Print a compact summary to stdout."""
        try:
            print("\033[96m" + "━" * 70 + "\033[0m")
            print("\033[96m" + f"{'Process Monitoring Summary':^70}" + "\033[0m")
            print("\033[96m" + "━" * 70 + "\033[0m")
            
            # Basic info
            print(f"Duration: {summary.get('duration_seconds', 0)} seconds")
            samples = summary.get('samples', 0)
            interval = summary.get('interval_seconds', 0)
            rate_hz = summary.get('approx_rate_hz', 0.0)
            print(f"Samples: {samples} (interval: {interval}s, ≈ {rate_hz:.3f} Hz)")
            print(f"Start Time: {summary.get('start_time', 'N/A')}")
            print(f"End Time: {summary.get('end_time', 'N/A')}")
            print()
            
            # Filter info
            filters = summary.get('filters_used', [])
            if filters:
                print(f"Filters: {', '.join(filters)}")
                print(f"Match Fields: {', '.join(summary.get('match_fields', []))}")
                print(f"Case Sensitive: {summary.get('case_sensitive', False)}")
                print(f"Regex Mode: {summary.get('use_regex', False)}")
                print()

            # Process statistics
            print("Process Statistics:")
            print(f"  Count - Avg: {summary.get('process_count_avg', 0):.1f}  "
                  f"Min: {summary.get('process_count_min', 0)}  "
                  f"Max: {summary.get('process_count_max', 0)}")
            print(f"  CPU Total - Avg: {summary.get('total_cpu_avg', 0):.1f}%  "
                  f"Max: {summary.get('total_cpu_max', 0):.1f}%")
            print(f"  Memory Total - Avg: {HumanReadable.bytes_to_size(summary.get('total_memory_avg', 0))}  "
                  f"Max: {summary.get('total_memory_max_human', '0 B')}")
            
            # Top processes
            top_processes = summary.get('top_processes', [])
            if top_processes:
                print()
                print("Top Processes (by frequency):")
                for i, (name, stats) in enumerate(top_processes[:5], 1):
                    print(f"  {i}. {name} - Seen {stats['count']} times, "
                          f"Max CPU: {stats['max_cpu']:.1f}%, "
                          f"Max Memory: {HumanReadable.bytes_to_size(stats['max_memory'])}")
            
            print("\033[96m" + "━" * 70 + "\033[0m")
        except Exception:
            # Best-effort printing; ignore formatting failures
            try:
                print("Summary:", summary)
            except Exception:
                pass

    def _save_plot(self, save_path: str) -> Optional[str]:
        """Save a plot of process metrics vs time.

        Returns the resolved file path if successful; otherwise None.
        """
        if not self.data_points:
            return None
        try:
            from syinfo.resource_monitor.visualization import create_monitoring_plot
        except Exception:
            return None

        # Transform data for plotting - map process data to system monitoring format
        plot_data = []
        for dp in self.data_points:
            # Map process monitoring fields to system monitoring format for visualization
            plot_data.append({
                'timestamp': dp['timestamp'],
                # Map process metrics to system format for plotting compatibility
                'cpu_percent': dp.get('total_cpu_percent', 0.0),  # Total CPU usage of filtered processes
                'memory_percent': min(100.0, (dp.get('total_memory_bytes', 0) / (1024 * 1024 * 1024)) * 10),  # Rough memory %
                'disk_percent': 0.0,  # Processes don't directly map to disk usage
                # Add process-specific network-like data for second subplot
                'network_io_rates': {
                    'bytes_sent_per_sec': dp.get('process_count', 0) * 1024,  # Process count as "sent"
                    'bytes_recv_per_sec': dp.get('total_memory_bytes', 0) / 1024,  # Memory as "received" 
                },
                # Keep original process data for reference
                'process_data': {
                    'process_count': dp.get('process_count', 0),
                    'total_cpu_percent': dp.get('total_cpu_percent', 0.0),
                    'total_memory_bytes': dp.get('total_memory_bytes', 0),
                    'total_memory_human': dp.get('total_memory_human', '0 B'),
                }
            })

        saved = create_monitoring_plot(plot_data, save_to=save_path, show=False)
        return saved

    # ----------------------------
    # Persistence helpers (same as SystemMonitor)
    # ----------------------------
    def _prepare_output(self) -> None:
        assert self._output_path is not None
        path = self._output_path
        if path.exists() and path.is_dir():
            fname = f"process-monitor-{datetime.now().strftime('%Y%m%d-%H%M%S')}.jsonl"
            self._resolved_output_path = path / fname
        else:
            parent = path.parent if path.suffix else path
            parent.mkdir(parents=True, exist_ok=True)
            if path.suffix:
                self._resolved_output_path = path
            else:
                fname = f"process-monitor-{datetime.now().strftime('%Y%m%d-%H%M%S')}.jsonl"
                self._resolved_output_path = parent / fname

        self._log_fp = open(self._resolved_output_path, "a", encoding="utf-8")
        try:
            self._bytes_written = self._resolved_output_path.stat().st_size
        except Exception:
            self._bytes_written = 0
        self._lines_written = 0

    def _write_jsonl(self, data_point: Dict[str, Any]) -> None:
        if not self._log_fp or not self._resolved_output_path:
            return
        try:
            line = json.dumps(data_point, ensure_ascii=False, default=str)
        except Exception:
            safe_dp = {k: (str(v) if not isinstance(v, (str, int, float, bool, type(None), dict, list)) else v) for k, v in data_point.items()}
            line = json.dumps(safe_dp, ensure_ascii=False)
        self._log_fp.write(line + "\n")
        self._log_fp.flush()
        self._lines_written += 1
        self._bytes_written += len(line) + 1
        self._maybe_rotate()

    def _maybe_rotate(self) -> None:
        if not self._resolved_output_path or not self._log_fp:
            return
        by_lines = self._rotate_max_lines is not None and self._lines_written >= int(self._rotate_max_lines)
        by_bytes = self._rotate_max_bytes is not None and self._bytes_written >= int(self._rotate_max_bytes)
        if not (by_lines or by_bytes):
            return
        try:
            self._log_fp.flush()
            self._log_fp.close()
        except Exception:
            pass
        finally:
            self._log_fp = None

        ts_suffix = datetime.now().strftime("%Y%m%d-%H%M%S")
        rotated = self._resolved_output_path.with_name(
            self._resolved_output_path.stem + f".{ts_suffix}" + self._resolved_output_path.suffix
        )
        try:
            os.replace(self._resolved_output_path, rotated)
        except Exception:
            try:
                self._resolved_output_path.rename(rotated)
            except Exception:
                pass
        self._log_fp = open(self._resolved_output_path, "a", encoding="utf-8")
        self._lines_written = 0
        self._bytes_written = 0


__all__ = ["ProcessMonitor"]
