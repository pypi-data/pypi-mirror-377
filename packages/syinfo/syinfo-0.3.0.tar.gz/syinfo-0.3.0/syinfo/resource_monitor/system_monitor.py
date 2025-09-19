"""System monitor with optional on-disk persistence and rotation.

Crash-safe persistence: when output_path is set, each data point is appended
as one JSON object per line (JSONL). Optional rotation by lines/bytes.
"""

import json
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import psutil

from syinfo.exceptions import DataCollectionError
from syinfo.utils import Logger, HumanReadable

# Get logger instance
logger = Logger.get_logger()


class SystemMonitor:
    """Simple system monitoring with optional on-disk persistence.

    If ``output_path`` is provided, each data point is appended to a JSONL file
    (one JSON object per line). Basic rotation can be enabled by lines or bytes.
    """

    def __init__(
        self,
        interval: int = 60,
        output_path: Optional[str] = None,
        rotate_max_lines: Optional[int] = None,
        rotate_max_bytes: Optional[int] = None,
        keep_in_memory: bool = True,
        summary_on_stop: bool = True,
    ):
        """Initialize monitor.

        Args:
            interval: Monitoring interval in seconds
            output_path: Optional path (file or directory) to persist data (JSONL)
            rotate_max_lines: Rotate file after this many lines (optional)
            rotate_max_bytes: Rotate file after this many bytes (optional)
            keep_in_memory: Keep collected data points in memory (default True)
            summary_on_stop: Write summary JSON on stop (when output_path is set)
        """
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

        # Network I/O rate tracking
        self._prev_net_io: Optional[Dict[str, int]] = None
        self._prev_timestamp: Optional[float] = None

    def start(
        self,
        duration: Optional[int] = None,
        callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> None:
        """Start monitoring.

        Args:
            duration: Duration in seconds (None for infinite)
            callback: Optional callback for each data point
        """
        if self.is_running:
            raise DataCollectionError("Monitoring is already running")

        self.is_running = True
        self._stop_event.clear()
        self.data_points = []

        # Reset network I/O tracking
        self._prev_net_io = None
        self._prev_timestamp = None

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
                    logger.error(f"Monitoring error: {e}")
                    continue

            self.is_running = False

        self._thread = threading.Thread(target=monitor_loop, daemon=True)
        self._thread.start()

    def stop(self, print_summary: bool = True, save_plot_to: Optional[str] = None) -> Dict[str, Any]:
        """Stop monitoring and return collected data.

        Returns:
            Dictionary with monitoring results
        """
        if not self.is_running:
            return {"error": "Monitoring is not running"}

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
            except Exception as _:
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
        """Collect a single data point."""
        current_time = time.time()
        current_net_io = psutil.net_io_counters()
        current_net_dict = dict(current_net_io._asdict())
        
        # Calculate network I/O rates if we have previous data
        network_rates = {}
        if self._prev_net_io is not None and self._prev_timestamp is not None:
            time_delta = current_time - self._prev_timestamp
            if time_delta > 0:
                # Calculate bytes per second
                bytes_sent_rate = (current_net_dict['bytes_sent'] - self._prev_net_io['bytes_sent']) / time_delta
                bytes_recv_rate = (current_net_dict['bytes_recv'] - self._prev_net_io['bytes_recv']) / time_delta
                packets_sent_rate = (current_net_dict['packets_sent'] - self._prev_net_io['packets_sent']) / time_delta
                packets_recv_rate = (current_net_dict['packets_recv'] - self._prev_net_io['packets_recv']) / time_delta
                
                # Ensure rates are non-negative (handle counter resets)
                bytes_sent_rate = max(0, bytes_sent_rate)
                bytes_recv_rate = max(0, bytes_recv_rate)
                packets_sent_rate = max(0, packets_sent_rate)
                packets_recv_rate = max(0, packets_recv_rate)
                
                network_rates = {
                    'bytes_sent_per_sec': bytes_sent_rate,
                    'bytes_recv_per_sec': bytes_recv_rate,
                    'packets_sent_per_sec': packets_sent_rate,
                    'packets_recv_per_sec': packets_recv_rate,
                    'total_bytes_per_sec': bytes_sent_rate + bytes_recv_rate,
                    'total_packets_per_sec': packets_sent_rate + packets_recv_rate,
                }
                
                # Add human-readable rates
                network_rates.update({
                    'bytes_sent_per_sec_human': f"{HumanReadable.bytes_to_size(bytes_sent_rate)}/s",
                    'bytes_recv_per_sec_human': f"{HumanReadable.bytes_to_size(bytes_recv_rate)}/s",
                    'total_bytes_per_sec_human': f"{HumanReadable.bytes_to_size(bytes_sent_rate + bytes_recv_rate)}/s",
                })
        
        # Update previous values for next iteration
        self._prev_net_io = current_net_dict
        self._prev_timestamp = current_time
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "network_io_cumulative": current_net_dict,  # Keep cumulative for reference
            "network_io_rates": network_rates,  # New: rates per second
        }

    def _calculate_summary(self) -> Dict[str, Any]:
        """Calculate summary statistics from collected data."""
        if not self.data_points:
            return {}

        cpu_values = [dp["cpu_percent"] for dp in self.data_points]
        memory_values = [dp["memory_percent"] for dp in self.data_points]
        disk_values = [dp["disk_percent"] for dp in self.data_points]

        samples = len(self.data_points)
        duration_seconds = samples * self.interval
        approx_rate_hz = (samples / duration_seconds) if duration_seconds > 0 else 0.0

        return {
            "duration_seconds": duration_seconds,
            "samples": samples,
            "interval_seconds": self.interval,
            "approx_rate_hz": approx_rate_hz,
            "cpu_avg": sum(cpu_values) / len(cpu_values) if cpu_values else 0.0,
            "cpu_max": max(cpu_values) if cpu_values else 0.0,
            "memory_avg": sum(memory_values) / len(memory_values) if memory_values else 0.0,
            "memory_peak": max(memory_values) if memory_values else 0.0,
            "disk_avg": sum(disk_values) / len(disk_values) if disk_values else 0.0,
            "start_time": self.data_points[0]["timestamp"] if self.data_points else None,
            "end_time": self.data_points[-1]["timestamp"] if self.data_points else None,
        }

    def _print_summary(self, summary: Dict[str, Any]) -> None:
        """Print a compact summary to stdout."""
        try:
            print("\033[95m" + "━" * 60 + "\033[0m")
            print("\033[95m" + f"{'System Monitoring Summary':^60}" + "\033[0m")
            print("\033[95m" + "━" * 60 + "\033[0m")
            print(f"Duration: {summary.get('duration_seconds', 0)} seconds")
            # Sampling details
            samples = summary.get("samples", 0)
            interval = summary.get("interval_seconds", 0)
            rate_hz = summary.get("approx_rate_hz", 0.0)
            print(f"Samples: {samples} (interval: {interval}s, ≈ {rate_hz:.3f} Hz)")
            print(f"Start Time: {summary.get('start_time', 'N/A')}")
            print(f"End Time: {summary.get('end_time', 'N/A')}")
            print()
            print("Performance Metrics:")
            print(
                "  CPU Usage     - Avg: "
                + f"{summary.get('cpu_avg', 0):.1f}%  Max: {summary.get('cpu_max', 0):.1f}%"
            )
            print(
                "  Memory Usage  - Avg: "
                + f"{summary.get('memory_avg', 0):.1f}%  Peak: {summary.get('memory_peak', 0):.1f}%"
            )
            print("  Disk Usage    - Avg: " + f"{summary.get('disk_avg', 0):.1f}%")
            print("\033[95m" + "━" * 60 + "\033[0m")
        except Exception:
            # Best-effort printing; ignore formatting failures
            try:
                print("Summary:", summary)
            except Exception:
                pass

    def _save_plot(self, save_path: str) -> Optional[str]:
        """Save a simple PNG plot of CPU/Memory/Disk vs time.

        Returns the resolved file path if successful; otherwise None.
        """
        if not self.data_points:
            return None
        try:
            from syinfo.resource_monitor.visualization import create_monitoring_plot  # local import
        except Exception:
            return None

        saved = create_monitoring_plot(self.data_points, save_to=save_path, show=False)
        return saved

    # ----------------------------
    # Persistence helpers
    # ----------------------------
    def _prepare_output(self) -> None:
        assert self._output_path is not None
        path = self._output_path
        if path.exists() and path.is_dir():
            fname = f"monitor-{datetime.now().strftime('%Y%m%d-%H%M%S')}.jsonl"
            self._resolved_output_path = path / fname
        else:
            parent = path.parent if path.suffix else path
            parent.mkdir(parents=True, exist_ok=True)
            if path.suffix:
                self._resolved_output_path = path
            else:
                fname = f"monitor-{datetime.now().strftime('%Y%m%d-%H%M%S')}.jsonl"
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

__all__ = ["SystemMonitor"]

