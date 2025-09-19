"""Device Information Module

This module provides comprehensive hardware and software information gathering
with detailed tree structure output, error handling, type hints, and performance optimizations.
"""

import glob
import copy
import os
import platform
import re
import sys
import time
import uuid
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import GPUtil
import getmac
import psutil
import yaml
from tabulate import tabulate

from syinfo.constants import UNKNOWN, NEED_SUDO
from syinfo.exceptions import (
    DataCollectionError,
    SystemAccessError, 
    ValidationError
)
from syinfo.utils import Execute, HumanReadable, create_highlighted_heading, handle_system_error, export_data, Logger

# Get logger instance
logger = Logger.get_logger()


class DeviceInfo:
    """Comprehensive device information collector.
    
    Provides detailed hardware information including CPU, memory, GPU, 
    disk, and manufacturer details. Uses system interfaces like /proc,
    /sys, DMI, and external tools to gather comprehensive data.
    
    All methods are static for stateless operation and can be called
    without instantiation. Results include both raw values and 
    human-readable formatted data.
    
    Examples:
        >>> info = DeviceInfo.get_all()
        >>> print(info['cpu_info']['design']['model name'])
        >>> DeviceInfo.print(info)  # Pretty-print tree format
    """
    
    def __init__(self) -> None:
        """Initialize the device information collector."""
        pass
    
    @staticmethod
    @handle_system_error
    def _get_device_info() -> Dict[str, Any]:
        """Get device manufacturer information from DMI.
        
        Returns:
            Dictionary containing device manufacturer details
            
        Raises:
            SystemAccessError: If DMI information cannot be accessed
        """
        try:
            dmi_path = Path("/sys/devices/virtual/dmi/id")
            if not dmi_path.exists():
                return {"error": "DMI information not available"}
            
            info = {}
            dmi_files = [
                f for f in dmi_path.glob("*") 
                if f.is_file() and "subsystem" not in f.name
            ]
            
            for file_path in dmi_files:
                try:
                    content = file_path.read_text().strip()
                    if content:  # Only add non-empty values
                        info[file_path.name] = content
                except (PermissionError, OSError):
                    # Log but continue with other files
                    continue
            
            # Sort by key name
            info = {k: v for k, v in sorted(info.items(), key=lambda item: item[0])}
            
            # Organize into categories
            organized_info = {}
            for key, value in info.items():
                if "_" in key:
                    category, field = key.split("_", 1)
                    if category not in organized_info:
                        organized_info[category] = {}
                    organized_info[category][field] = value
                else:
                    organized_info[key] = value
            
            return organized_info
            
        except Exception as e:
            return {"error": f"Failed to collect device manufacturer information: {str(e)}"}
    
    @staticmethod
    @handle_system_error
    @lru_cache(maxsize=1)
    def _get_cpu_info() -> Dict[str, Any]:
        """Get comprehensive CPU information from system interfaces.
        
        Reads from /proc/cpuinfo and gathers additional CPU data including
        frequency information, usage statistics, and core topology. Results
        are cached to avoid repeated expensive operations.
        
        Returns:
            Dict containing:
                - design: CPU model, vendor, architecture info
                - cores: Physical/logical core counts
                - frequency_Mhz: Current/min/max frequencies  
                - percentage_used: Current CPU utilization
                - Raw /proc/cpuinfo data organized by core
                
        Raises:
            SystemAccessError: If /proc/cpuinfo cannot be read
            
        Note:
            Function is cached with LRU cache (maxsize=1) for performance.
            CPU frequency and usage are live values at time of collection.
        """
        try:
            logger.debug("Reading CPU information from /proc/cpuinfo")
            cpu_info_raw = Execute.on_shell("cat /proc/cpuinfo")
            if cpu_info_raw == UNKNOWN:
                logger.warning("Unable to read /proc/cpuinfo - CPU info unavailable")
                return {"error": "Cannot read /proc/cpuinfo"}
            
            # Parse CPU info into blocks (one per logical core)
            cpu_blocks = [
                block.strip() for block in cpu_info_raw.split("\n\n") 
                if block.strip()
            ]
            logger.debug(f"Found {len(cpu_blocks)} CPU core blocks in /proc/cpuinfo")
            
            # Consolidate information from all CPU cores
            consolidated_info = {}
            for i, block in enumerate(cpu_blocks):
                try:
                    # Convert /proc/cpuinfo format to YAML-parseable format
                    yaml_block = block.replace("\t", "")  # Remove tabs
                    block_data = yaml.safe_load(yaml_block)
                    
                    if isinstance(block_data, dict):
                        for key, value in block_data.items():
                            if key not in consolidated_info:
                                consolidated_info[key] = []
                            consolidated_info[key].append(value)
                except yaml.YAMLError:
                    continue
            
            # Simplify values (remove duplicates, join unique values)
            for key, values in consolidated_info.items():
                unique_values = list(dict.fromkeys(values))  # Preserve order
                consolidated_info[key] = (
                    unique_values[0] if len(unique_values) == 1 
                    else " / ".join(str(v) for v in unique_values)
                )
            
            return consolidated_info
            
        except Exception as e:
            return {"error": f"Failed to collect CPU information: {str(e)}"}
    
    @staticmethod
    @handle_system_error
    @lru_cache(maxsize=1)
    def _get_ram_info() -> Dict[str, Any]:
        """Get detailed memory information from /proc/meminfo.
        
        Returns:
            Dictionary containing memory details with bytes and human-readable formats
        """
        try:
            meminfo_raw = Execute.on_shell("cat /proc/meminfo")
            if meminfo_raw == UNKNOWN:
                return {"error": "Cannot read /proc/meminfo"}
            
            # Parse memory info
            yaml_content = meminfo_raw.replace("\t", "")
            meminfo_data = yaml.safe_load(yaml_content)
            
            if not isinstance(meminfo_data, dict):
                return {"error": "Invalid format in /proc/meminfo"}
            
            # Convert to bytes and add human-readable format
            memory_info = {}
            for key, value_str in meminfo_data.items():
                try:
                    # Convert string values like "1024 kB" to bytes
                    bytes_value = HumanReadable.size_to_bytes(value_str)
                    memory_info[key] = {
                        "bytes": bytes_value,
                        "human_readable": HumanReadable.bytes_to_size(bytes_value)
                    }
                except (ValidationError, ValueError):
                    # Keep original value if conversion fails
                    memory_info[key] = {"raw": value_str}
            
            # Sort by size (descending)
            memory_info = dict(
                sorted(
                    memory_info.items(),
                    key=lambda x: x[1].get("bytes", 0),
                    reverse=True
                )
            )
            
            return memory_info
            
        except Exception as e:
            return {"error": f"Failed to collect memory information: {str(e)}"}

    @staticmethod
    @handle_system_error
    @lru_cache(maxsize=1)
    def _get_gpu_info() -> Dict[str, Any]:
        """Get GPU information in a robust, cross-hardware way.

        Tries multiple strategies:
        1) GPUtil (if available) for NVIDIA GPUs
        2) nvidia-smi CSV query (if available) as fallback
        3) lspci scan for generic GPU names as last resort

        Returns:
            Dictionary keyed by gpu_{index} with available fields.
        """
        gpu_info: Dict[str, Any] = {}

        # Strategy 1: GPUtil
        try:
            import GPUtil as _GPUtil  # local import to avoid hard dependency at import-time

            gpus = _GPUtil.getGPUs()
            for i, gpu in enumerate(gpus):
                gpu_id = f"gpu_{i}"
                gpu_info[gpu_id] = {
                    "id": getattr(gpu, "id", i),
                    "name": getattr(gpu, "name", UNKNOWN),
                    "uuid": getattr(gpu, "uuid", UNKNOWN),
                    "used_memory": getattr(gpu, "memoryUsed", 0) * 1048576,  # MB->B
                    "free_memory": getattr(gpu, "memoryFree", 0) * 1048576,
                    "total_memory": getattr(gpu, "memoryTotal", 0) * 1048576,
                    "temperature": getattr(gpu, "temperature", UNKNOWN),
                    "load_pct": getattr(gpu, "load", 0) * 100,
                }
        except Exception:
            # Ignore GPUtil failures; proceed to other strategies
            pass

        if gpu_info:
            return gpu_info

        # Strategy 2: nvidia-smi (if present)
        try:
            query_cmd = (
                "nvidia-smi --query-gpu=name,memory.total,memory.used,memory.free,"
                "temperature.gpu,utilization.gpu --format=csv,noheader,nounits"
            )
            result = Execute.on_shell(query_cmd)
            if result != UNKNOWN and result:
                lines = [ln.strip() for ln in result.split("\n") if ln.strip()]
                for i, line in enumerate(lines):
                    parts = [p.strip() for p in line.split(",")]
                    # Expecting: name, totalMB, usedMB, freeMB, tempC, util%
                    if len(parts) >= 6:
                        name, total_mb, used_mb, free_mb, temp_c, util = parts[:6]
                        gpu_info[f"gpu_{i}"] = {
                            "name": name,
                            "total_memory": int(float(total_mb)) * 1048576,
                            "used_memory": int(float(used_mb)) * 1048576,
                            "free_memory": int(float(free_mb)) * 1048576,
                            "temperature": int(float(temp_c)),
                            "load_pct": int(float(util)),
                        }
        except Exception:
            # Ignore and fallback further
            pass

        if gpu_info:
            return gpu_info

        # Strategy 3: lspci generic GPU listing
        try:
            lspci = Execute.on_shell("lspci | grep -i 'vga\\|3d\\|2d'")
            if lspci != UNKNOWN and lspci:
                lines = [ln.strip() for ln in lspci.split("\n") if ln.strip()]
                for i, line in enumerate(lines):
                    # Keep the line as the GPU name fallback
                    gpu_info[f"gpu_{i}"] = {"name": line}
        except Exception:
            pass

        return gpu_info
    
    @staticmethod
    def print(info: Dict[str, Any], return_msg: bool = False) -> Optional[str]:
        """Print system information in the original detailed tree format.
        
        Args:
            info: System information dictionary
            return_msg: If True, return the formatted string instead of printing
            
        Returns:
            Formatted string if return_msg=True, None otherwise
        """
        _msg = create_highlighted_heading(
            "System Information", line_symbol="━", total_length=100,
            prefix_suffix="", center_highlighter=(" ", " "),
        )
        _msg += "\n."
        _msg += "\n├── Device Information"
        _msg += f"\n│   ├── {'Mac Address':<20} {info['dev_info']['mac_address']}"
        _msg += f"\n│   ├── {'System Type':<20} {info['dev_info']['chassis']}"
        _msg += f"\n│   ├── {'Static Hostname':<20} {info['dev_info']['static_hostname']}"
        _msg += f"\n│   ├── {'Icon Name':<20} {info['dev_info']['icon_name']}"
        _msg += "\n│   ├── Operating Software"
        
        # Operating System details
        os_keys = list(info["dev_info"]["operating_system"].keys())
        for i, (category, val) in enumerate(info["dev_info"]["operating_system"].items()):
            connector = "└" if i == len(os_keys) - 1 else "├"
            display_name = " ".join(category.split("_")).capitalize()
            _msg += f"\n│   │   {connector}── {display_name:<20} {val}"
        
        _msg += "\n│   ├── Device Manufacturer"
        
        # Device manufacturer details
        device_keys = list(info["dev_info"]["device"].keys())
        for i, (category, val) in enumerate(info["dev_info"]["device"].items()):
            is_last_category = (i == len(device_keys) - 1)
            connector = "└" if is_last_category else "├"
            
            if not isinstance(val, dict):
                _msg += f"\n│   │   {connector}── {category:<16} {val}"
                continue
                
            _msg += f"\n│   │   {connector}── {category}"
            sub_keys = list(val.items())
            for j, (name, sub_val) in enumerate(sub_keys):
                is_last_sub = (j == len(sub_keys) - 1)
                prefix = " " if is_last_category else "│"
                sub_connector = "└" if is_last_sub else "├"
                _msg += f"\n│   │   {prefix}   {sub_connector}── {name:<16} {sub_val}"
        
        _msg += f"\n│   └── {'Py Version':<16} {info['dev_info']['python_version']}"
        
        # Time Information
        _msg += "\n├── Time"
        _msg += "\n│   ├── Current Time"
        _msg += f"\n│   │   ├── {'Timestamp':<16} {info['time']['current']['timestamp']}"
        _msg += f"\n│   │   └── {'Date/Time':<16} {info['time']['current']['readable']}"
        _msg += "\n│   ├── Boot Time"
        _msg += f"\n│   │   ├── {'Timestamp':<16} {info['time']['boot_time']['timestamp']}"
        _msg += f"\n│   │   └── {'Date/Time':<16} {info['time']['boot_time']['readable']}"
        _msg += "\n│   └── Uptime Time"
        _msg += f"\n│       ├── {'Seconds':<16} {info['time']['uptime']['in_seconds']}"
        _msg += f"\n│       └── {'Date/Time':<16} {info['time']['uptime']['readable']}"
        
        # CPU Information
        _msg += "\n├── CPU"
        _msg += "\n│   ├── Cores"
        _msg += f"\n│   │   ├── {'Physical':<16} {info['cpu_info']['cores']['physical']}"
        _msg += f"\n│   │   └── {'Total':<16} {info['cpu_info']['cores']['total']}"
        _msg += "\n│   ├── Frequency"
        
        # Handle frequency information (may not be available on all systems)
        try:
            freq_info = info["cpu_info"]["frequency_Mhz"]
            if isinstance(freq_info["min"], (int, float)):
                _msg += f"\n│   │   ├── {'Min':<16} {freq_info['min']:.2f} Mhz"
            if isinstance(freq_info["max"], (int, float)):
                _msg += f"\n│   │   ├── {'Max':<16} {freq_info['max']:.2f} Mhz"
            if isinstance(freq_info["current"], (int, float)):
                _msg += f"\n│   │   └── {'Current':<16} {freq_info['current']:.2f} Mhz"
        except (KeyError, TypeError):
            _msg += f"\n│   │   └── {'Status':<16} Frequency info unavailable"
        
        _msg += "\n│   ├── CPU Usage"
        _msg += f"\n│   │   ├── {'Total':<16} {info['cpu_info']['percentage_used']['total']:.1f} %"
        _msg += "\n│   │   └── CPU Usage Per Core"
        
        # Per-core CPU usage
        core_usage = info["cpu_info"]["percentage_used"]["per_core"]
        core_keys = list(core_usage.keys())
        for i, (core_name, pct) in enumerate(core_usage.items()):
            connector = "└" if i == len(core_keys) - 1 else "├"
            _msg += f"\n│   │       {connector}── {core_name + ' ':<16} {pct:4.1f} %"
        
        _msg += "\n│   └── CPU Design"
        design_keys = list(info["cpu_info"]["design"].keys())
        for i, (name, val) in enumerate(info["cpu_info"]["design"].items()):
            connector = "└" if i == len(design_keys) - 1 else "├"
            _msg += f"\n│       {connector}── {name:<16} {val}"
        
        # Memory Information
        _msg += "\n├── Memory"
        _msg += "\n│   ├── Virtual"
        _msg += f"\n│   │   ├── {'Used':<16} {info['memory_info']['virtual']['readable']['used']}"
        _msg += f"\n│   │   ├── {'Free':<16} {info['memory_info']['virtual']['readable']['available']}"
        _msg += f"\n│   │   ├── {'Total':<16} {info['memory_info']['virtual']['readable']['total']}"
        _msg += f"\n│   │   └── {'Percentage':<16} {info['memory_info']['virtual']['percent']} %"
        _msg += "\n│   ├── Swap"
        _msg += f"\n│   │   ├── {'Used':<16} {info['memory_info']['swap']['readable']['used']}"
        _msg += f"\n│   │   ├── {'Free':<16} {info['memory_info']['swap']['readable']['available']}"
        _msg += f"\n│   │   ├── {'Total':<16} {info['memory_info']['swap']['readable']['total']}"
        _msg += f"\n│   │   └── {'Percentage':<16} {info['memory_info']['swap']['percent']} %"
        _msg += "\n│   └── Design"
        
        # Memory design details
        design_keys = list(info["memory_info"]["design"].keys())
        for i, (category, val) in enumerate(info["memory_info"]["design"].items()):
            is_last_category = (i == len(design_keys) - 1)
            connector = "└" if is_last_category else "├"
            _msg += f"\n│       {connector}── {category}"
            
            if isinstance(val, dict):
                sub_keys = list(val.items())
                for j, (name, sub_val) in enumerate(sub_keys):
                    is_last_sub = (j == len(sub_keys) - 1)
                    prefix = " " if is_last_category else "│"
                    sub_connector = "└" if is_last_sub else "├"
                    _msg += f"\n│       {prefix}   {sub_connector}── {name:<16} {sub_val}"
        
        # Disk Information
        _msg += "\n├── Disk"
        _msg += "\n│   ├── Since Boot"
        _msg += f"\n│   │   ├── {'Total Read':<16} {info['disk_info']['since_boot']['total_read']}"
        _msg += f"\n│   │   └── {'Total Write':<16} {info['disk_info']['since_boot']['total_write']}"
        _msg += "\n│   └── Drives"
        
        # Disk drives information
        drives = info["disk_info"]["disks"]
        drive_keys = list(drives.keys())
        for i, (k, disk) in enumerate(drives.items()):
            is_last_drive = (i == len(drive_keys) - 1)
            connector = "└" if is_last_drive else "├"
            prefix = " " if is_last_drive else "│"
            
            _msg += f"\n│       {connector}── {k}"
            _msg += f"\n│       {prefix}   ├── {'Mountpoint':<16} {disk['mountpoint']}"
            _msg += f"\n│       {prefix}   ├── {'File System':<16} {disk['file_system_type']}"
            
            if "space" not in disk:
                _msg += f"\n│       {prefix}   └── Space .. NA"
            else:
                space = disk["space"]
                _msg += f"\n│       {prefix}   └── Space"
                _msg += f"\n│       {prefix}       ├── {'Used':<15} {space['used']}"
                _msg += f"\n│       {prefix}       ├── {'Free':<15} {space['free']}"
                _msg += f"\n│       {prefix}       ├── {'Total':<15} {space['total']}"
                _msg += f"\n│       {prefix}       └── {'Percent':<15} {space['percent']} %"
        
        # GPU Information (integrated into tree structure)
        # As the last top-level section, use "└" and no left vertical prefix.
        _msg += "\n└── GPU Information"
        top_prefix = "    "
        
        gpu_map: Dict[str, Any] = info.get("gpu_info", {}) or {}
        if gpu_map:
            gpu_keys = list(gpu_map.keys())
            
            # Field display mapping for better readability
            field_labels = {
                "name": "Name",
                "driver": "Driver",
                "total_memory": "Total Memory", 
                "used_memory": "Used Memory",
                "free_memory": "Free Memory",
                "temperature": "Temperature",
                "load_pct": "Load",
                "uuid": "UUID",
                "id": "ID"
            }
            
            def format_gpu_value(key: str, value: Any) -> str:
                """Format GPU values with appropriate units and formatting."""
                try:
                    if value is UNKNOWN or value is None:
                        return str(UNKNOWN)
                    if key.endswith("_memory") and isinstance(value, (int, float)):
                        return HumanReadable.bytes_to_size(int(value))
                    if key == "load_pct" and isinstance(value, (int, float)):
                        return f"{float(value):.1f}%"
                    if key == "temperature" and isinstance(value, (int, float)):
                        return f"{float(value):.0f}°C"
                    return str(value)
                except Exception:
                    return str(value)
            
            for i, (gpu_name, gpu_data) in enumerate(gpu_map.items()):
                is_last_gpu = (i == len(gpu_keys) - 1)
                gpu_connector = "└" if is_last_gpu else "├"
                gpu_prefix = " " if is_last_gpu else "│"

                _msg += f"\n{top_prefix}{gpu_connector}── {gpu_name}"
                
                if isinstance(gpu_data, dict) and gpu_data:
                    # Get all available fields for this GPU
                    available_fields = list(gpu_data.keys())
                    
                    for j, field in enumerate(available_fields):
                        is_last_field = (j == len(available_fields) - 1)
                        field_connector = "└" if is_last_field else "├"
                        field_label = field_labels.get(field, field.title().replace('_', ' '))
                        field_value = format_gpu_value(field, gpu_data[field])
                        
                        _msg += f"\n{top_prefix}{gpu_prefix}   {field_connector}── {field_label:<16} {field_value}"
                else:
                    _msg += f"\n{top_prefix}{gpu_prefix}   └── Status            No detailed information available"
        else:
            _msg += "\n    └── Status              No GPU detected"
        
        if return_msg:
            return _msg
        else:
            print(_msg)
            return None
    
    @staticmethod
    def get_all() -> Dict[str, Any]:
        """Get all system information.
        
        Returns:
            Complete system information dictionary
        """
        try:
            # Get system release information
            release_info = {}
            try:
                release_raw = Execute.on_shell("cat /etc/*release")
                if release_raw != UNKNOWN:
                    release_content = release_raw.replace("=", ": ")
                    release_info = yaml.safe_load(release_content) or {}
            except Exception:
                release_info = {}
            
            # Get hostname information
            hostname_info = {}
            try:
                hostname_raw = Execute.on_shell("hostnamectl")
                if hostname_raw != UNKNOWN:
                    hostname_content = "\n".join([
                        line.strip() for line in hostname_raw.split("\n")
                    ])
                    hostname_info = yaml.safe_load(hostname_content) or {}
            except Exception:
                hostname_info = {}
            
            # Get platform information
            uname = platform.uname()
            
            # Get timing information
            boot_time_timestamp = psutil.boot_time()
            boot_time = datetime.fromtimestamp(boot_time_timestamp)
            current_time = datetime.now()
            current_timestamp = time.time()
            
            # Get CPU frequency (may fail on some systems)
            cpu_freq = None
            try:
                cpu_freq = psutil.cpu_freq()
            except Exception:
                pass
            
            # Get memory information using psutil
            svmem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            disk_io = psutil.disk_io_counters()
            
            # GPU information
            gpu_info = DeviceInfo._get_gpu_info()
            
            # Disk information
            disk_info = {"device": {}}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info["device"][partition.device] = {
                        "mountpoint": partition.mountpoint,
                        "file_system_type": partition.fstype,
                        "space": {
                            "used": HumanReadable.bytes_to_size(usage.used),
                            "free": HumanReadable.bytes_to_size(usage.free),
                            "total": HumanReadable.bytes_to_size(usage.total),
                            "percent": usage.percent
                        }
                    }
                except PermissionError:
                    disk_info["device"][partition.device] = {
                        "mountpoint": partition.mountpoint,
                        "file_system_type": partition.fstype,
                    }
            
            # Build the complete information structure
            info = {
                "dev_info": {
                    "mac_address": getmac.get_mac_address(),
                    "chassis": hostname_info.get("Chassis", UNKNOWN),
                    "static_hostname": platform.node(),
                    "icon_name": hostname_info.get("Icon name", UNKNOWN),
                    "operating_system": {
                        "full_name": hostname_info.get("Operating System", UNKNOWN),
                        "distribution": release_info.get("NAME", UNKNOWN),
                        "platform": platform.platform(),
                        "version": release_info.get("VERSION", UNKNOWN),
                        "update_history": uname.version,
                        "id_like": release_info.get("ID_LIKE", UNKNOWN),
                        "system": uname.system,
                        "kernel": hostname_info.get("Kernel", uname.release),
                        "architecture": hostname_info.get("Architecture", uname.machine),
                        "release": uname.release,
                        "machine_id": hostname_info.get("Machine ID", UNKNOWN),
                        "boot_id": hostname_info.get("Boot ID", UNKNOWN),
                    },
                    "device": DeviceInfo._get_device_info(),
                    "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                },
                "time": {
                    "current": {
                        "timestamp": current_timestamp,
                        "readable": f"{current_time.year}/{current_time.month}/{current_time.day} {current_time.hour}:{current_time.minute}:{current_time.second}"
                    },
                    "boot_time": {
                        "timestamp": boot_time_timestamp,
                        "readable": f"{boot_time.year}/{boot_time.month}/{boot_time.day} {boot_time.hour}:{boot_time.minute}:{boot_time.second}"
                    },
                    "uptime": {
                        "in_seconds": round(current_timestamp - boot_time_timestamp, 1),
                        "readable": HumanReadable.time_spend(current_timestamp - boot_time_timestamp)
                    }
                },
                "cpu_info": {
                    "cores": {
                        "physical": psutil.cpu_count(logical=False),
                        "total": psutil.cpu_count(logical=True)
                    },
                    "frequency_Mhz": {
                        "min": cpu_freq.min if cpu_freq else UNKNOWN,
                        "max": cpu_freq.max if cpu_freq else UNKNOWN,
                        "current": cpu_freq.current if cpu_freq else UNKNOWN
                    },
                    "percentage_used": {
                        "total": psutil.cpu_percent(),
                        "per_core": {
                            f"Core {i+1:2d}": percentage
                            for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1))
                        }
                    },
                    "design": DeviceInfo._get_cpu_info()
                },
                "gpu_info": gpu_info,
                "memory_info": {
                    "virtual": {
                        "percent": svmem.percent,
                        "in_bytes": {
                            "used": svmem.used,
                            "available": svmem.available,
                            "total": svmem.total
                        },
                        "readable": {
                            "used": HumanReadable.bytes_to_size(svmem.used),
                            "available": HumanReadable.bytes_to_size(svmem.available),
                            "total": HumanReadable.bytes_to_size(svmem.total)
                        }
                    },
                    "swap": {
                        "percent": swap.percent,
                        "in_bytes": {
                            "used": swap.used,
                            "available": swap.free,
                            "total": swap.total
                        },
                        "readable": {
                            "used": HumanReadable.bytes_to_size(swap.used),
                            "available": HumanReadable.bytes_to_size(swap.free),
                            "total": HumanReadable.bytes_to_size(swap.total)
                        }
                    },
                    "design": DeviceInfo._get_ram_info()
                },
                "disk_info": {
                    "disks": disk_info["device"],
                    "since_boot": {
                        "total_read": HumanReadable.bytes_to_size(disk_io.read_bytes) if disk_io else "0 B",
                        "total_write": HumanReadable.bytes_to_size(disk_io.write_bytes) if disk_io else "0 B"
                    }
                }
            }
            
            return info
            
        except Exception as e:
            raise DataCollectionError(
                "Failed to collect comprehensive system information",
                original_exception=e
            )


    @staticmethod
    def export(
        format: str = "json",
        output_file: Optional[str] = None,
        include_sensitive: bool = False,
        info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Export device information to JSON or YAML.

        Args:
            format: Export format ("json" or "yaml")
            output_file: Optional path to write the exported content
            include_sensitive: Include potentially sensitive fields if True
            info: Optional pre-collected info dict to export

        Returns:
            Exported string content
        """
        data: Dict[str, Any] = info if info is not None else DeviceInfo.get_all()
        sanitized: Dict[str, Any] = copy.deepcopy(data)

        if not include_sensitive:
            try:
                if isinstance(sanitized.get("dev_info"), dict):
                    sanitized["dev_info"]["mac_address"] = "***"
                if isinstance(sanitized.get("network_info"), dict):
                    sanitized["network_info"]["mac_address"] = "***"
                    if isinstance(sanitized["network_info"].get("wifi"), dict):
                        if "password" in sanitized["network_info"]["wifi"]:
                            sanitized["network_info"]["wifi"]["password"] = "***"
            except Exception:
                pass

        return export_data(sanitized, format=format, output_file=output_file)


__all__ = ["DeviceInfo"]
