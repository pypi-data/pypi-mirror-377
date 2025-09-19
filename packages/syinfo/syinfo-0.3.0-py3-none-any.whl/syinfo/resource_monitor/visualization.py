"""Visualization helpers for monitoring JSONL outputs.

Provides matplotlib backend. If matplotlib is unavailable, save/show will be skipped.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Union


def _read_jsonl(path: str | Path) -> List[Dict]:
    p = Path(path)
    data: List[Dict] = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return data


def _normalize_data(data_or_path: Union[str, Path, List[Dict]]) -> List[Dict]:
    if isinstance(data_or_path, (str, Path)):
        return _read_jsonl(data_or_path)
    if isinstance(data_or_path, list):
        return data_or_path
    return []


# Essential keys for system monitoring
system_essential_keys = ("timestamp", "cpu_percent", "memory_percent", "disk_percent")

# Essential keys for process monitoring  
process_essential_keys = ("timestamp", "process_count", "total_cpu_percent")


def create_monitoring_plot(
    data_or_path: Union[str, Path, List[Dict]],
    save_to: Optional[str] = None,
    show: bool = False,
) -> Optional[str]:
    """Create monitoring plots from data or JSONL file using matplotlib.

    Supports both system monitoring data (CPU/Memory/Disk/Network) and process
    monitoring data. If save_to is provided, saves a PNG and returns its path.
    Returns None if plotting is not available.
    """
    try:
        import matplotlib
        if not show:
            matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.ticker import FuncFormatter
    except Exception:
        return None

    data = _normalize_data(data_or_path)
    if not data:
        return None

    # Detect data type and filter appropriately
    is_process_data = any(all(k in d for k in process_essential_keys) for d in data[:3])  # Check first few
    is_system_data = any(all(k in d for k in system_essential_keys) for d in data[:3])
    
    if is_process_data:
        # Process monitoring data
        cleaned = [d for d in data if all(k in d for k in process_essential_keys)]
        data_type = "process"
    elif is_system_data:
        # System monitoring data  
        cleaned = [d for d in data if all(k in d for k in system_essential_keys)]
        data_type = "system"
    else:
        # Try to use data as-is if it has timestamp
        cleaned = [d for d in data if "timestamp" in d]
        data_type = "unknown"
    
    if not cleaned:
        return None

    x = [d.get("timestamp") for d in cleaned]
    
    if data_type == "process":
        # Process monitoring metrics
        cpu = [d.get("total_cpu_percent", 0.0) for d in cleaned]
        mem = [d.get("process_count", 0) for d in cleaned]  # Process count as "memory-like" metric
        disk = [d.get("total_memory_bytes", 0) / (1024 * 1024) for d in cleaned]  # Memory in MB as "disk-like"
        
        # Process-specific network data (memory usage rates)
        has_net_rates = False  # Process data doesn't have network rates
        sent_rate = [d.get("total_memory_bytes", 0) / 1024 for d in cleaned]  # Memory as "sent"
        recv_rate = [d.get("process_count", 0) * 100 for d in cleaned]  # Process count scaled as "received"
    else:
        # System monitoring metrics (original logic)
        cpu = [d.get("cpu_percent", 0.0) for d in cleaned]
        mem = [d.get("memory_percent", 0.0) for d in cleaned]
        disk = [d.get("disk_percent", 0.0) for d in cleaned]

    # Prepare optional network/secondary data 
    if data_type != "process":
        # System monitoring: use network I/O data
        has_net_rates = any(isinstance(d.get("network_io_rates"), dict) and d.get("network_io_rates") for d in cleaned)
        if has_net_rates:
            sent_rate = [float((d.get("network_io_rates") or {}).get("bytes_sent_per_sec", 0) or 0) for d in cleaned]
            recv_rate = [float((d.get("network_io_rates") or {}).get("bytes_recv_per_sec", 0) or 0) for d in cleaned]
        else:
            # Fallback to old cumulative data if rates not available (backward compatibility)
            has_net_cumulative = any(isinstance(d.get("network_io"), dict) for d in cleaned)
            if has_net_cumulative:
                sent_rate = [int((d.get("network_io") or {}).get("bytes_sent", 0) or 0) for d in cleaned]
                recv_rate = [int((d.get("network_io") or {}).get("bytes_recv", 0) or 0) for d in cleaned]
            else:
                sent_rate, recv_rate = [], []

    # Layout: two rows if network data present; otherwise single plot
    has_network_data = has_net_rates or (sent_rate and recv_rate)
    if has_network_data:
        fig, axs = plt.subplots(2, 1, sharex=True, figsize=(10, 8), height_ratios=[2, 1])
        ax_top, ax_bottom = axs
    else:
        fig, ax_top = plt.subplots(1, 1, figsize=(10, 6))
        ax_bottom = None

    # Top plot: Main metrics (adapt labels based on data type)
    if data_type == "process":
        ax_top.plot(x, cpu, label="Total CPU %")
        ax_top.plot(x, mem, label="Process Count")  
        ax_top.plot(x, disk, label="Memory (MB)")
        ax_top.set_ylabel("Mixed Metrics")
        ax_top.set_title("Process Monitor Metrics")
    else:
        ax_top.plot(x, cpu, label="CPU %")
        ax_top.plot(x, mem, label="Memory %")
        ax_top.plot(x, disk, label="Disk %")
        ax_top.set_ylabel("Percent")
        ax_top.set_title("System Monitor Metrics")
    
    ax_top.legend(loc="upper left")
    for label in ax_top.get_xticklabels():
        label.set_rotation(45)
        label.set_ha("right")

    # Bottom plot: Network IO with human-readable formatter
    if has_network_data and ax_bottom is not None:
        ax_bottom.plot(x, sent_rate, label="Bytes Sent/sec" if has_net_rates else "Bytes Sent", color="#1f77b4")
        ax_bottom.plot(x, recv_rate, label="Bytes Received/sec" if has_net_rates else "Bytes Received", color="#ff7f0e")
        ax_bottom.set_ylabel("Network IO (bytes/sec)" if has_net_rates else "Network IO (bytes)")
        ax_bottom.legend(loc="upper left")

        # Use HumanReadable to format ticks nicely
        try:
            from syinfo.utils import HumanReadable  # local import to avoid heavy deps

            def _fmt_bytes(y, pos):
                try:
                    if has_net_rates:
                        return f"{HumanReadable.bytes_to_size(int(y))}/s"
                    else:
                        return HumanReadable.bytes_to_size(int(y))
                except Exception:
                    return str(y)

            ax_bottom.yaxis.set_major_formatter(FuncFormatter(_fmt_bytes))
        except Exception:
            pass

    fig.tight_layout()

    saved_path: Optional[str] = None
    try:
        if save_to:
            save_path = Path(save_to)
            if save_path.exists() and save_path.is_dir():
                from datetime import datetime as _dt

                fname = f"monitor-{_dt.now().strftime('%Y%m%d-%H%M%S')}.png"
                save_path = save_path / fname
            else:
                parent = save_path.parent if save_path.suffix else save_path
                try:
                    parent.mkdir(parents=True, exist_ok=True)
                except Exception:
                    pass
                if not save_path.suffix:
                    save_path = parent / "monitor-plot.png"
            fig.savefig(str(save_path), dpi=120)
            saved_path = str(save_path)
        if show:
            plt.show()
    finally:
        try:
            import matplotlib.pyplot as _plt
            _plt.close(fig)
        except Exception:
            pass

    return saved_path


__all__ = [
    "create_monitoring_plot",
]


