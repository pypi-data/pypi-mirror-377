"""System Information Module - Final Clean Version

This module provides comprehensive system information by combining device and network data.
"""

import multiprocessing
import os
import platform
import sys
from typing import Any, Dict, Optional
import copy

import cpuinfo
import psutil

from syinfo.core.device_info import DeviceInfo
from syinfo.core.network_info import NetworkInfo
from syinfo.utils import export_data


class SystemInfo:
    """Get the system (hardware+software+network) related information."""

    @staticmethod
    def print(info: Dict[str, Any], return_msg: bool = False) -> Optional[str]:
        """Print system information.

        Args:
            info: System information dictionary
            return_msg: If True, return formatted string instead of printing

        Returns:
            Formatted string if return_msg=True, None otherwise
        """
        _msg = DeviceInfo.print(info, return_msg=True)
        _msg += "\n\n"
        _msg += NetworkInfo.print(info, return_msg=True)

        if return_msg:
            return _msg
        else:
            print(_msg)
            return None

    @staticmethod
    def get_all(
        search_period: int = 10, search_device_vendor_too: bool = True,
    ) -> Dict[str, Any]:
        """Aggregate all the information related to the device and network.

        Args:
            search_period: Network scanning period in seconds
            search_device_vendor_too: Whether to include vendor information for network devices

        Returns:
            Complete system information dictionary
        """
        device_info = DeviceInfo.get_all()
        network_info = NetworkInfo.get_all(search_period, search_device_vendor_too)
        device_info["network_info"] = network_info["network_info"]
        return device_info

    @staticmethod
    def export(
        format: str = "json",
        output_file: Optional[str] = None,
        include_sensitive: bool = False,
        info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Export combined system (device + network) information.

        Args:
            format: Export format ("json" or "yaml")
            output_file: Optional path to write the exported content
            include_sensitive: Include potentially sensitive fields if True
            info: Optional pre-collected info dict to export

        Returns:
            Exported string content
        """
        data: Dict[str, Any] = (
            info if info is not None else SystemInfo.get_all()
        )
        sanitized: Dict[str, Any] = copy.deepcopy(data)

        if not include_sensitive:
            try:
                di = sanitized.get("dev_info")
                if isinstance(di, dict):
                    di["mac_address"] = "***"
                ni = sanitized.get("network_info")
                if isinstance(ni, dict):
                    ni["mac_address"] = "***"
                    if isinstance(ni.get("wifi"), dict) and "password" in ni["wifi"]:
                        ni["wifi"]["password"] = "***"
            except Exception:
                pass

        return export_data(sanitized, format=format, output_file=output_file)




def print_brief_sys_info() -> None:
    """Print system/device configuration in a brief format."""
    physical_mem = psutil.virtual_memory()
    total_phy_mem = str(round(physical_mem.total / (1024.0**3), 2)) + " GB"
    total_phy_avail = str(round(physical_mem.available / (1024.0**3), 2)) + " GB"

    swap_mem = psutil.swap_memory()
    total_swp_mem = str(round(swap_mem.total / (1024.0**3), 2)) + " GB"
    total_swp_free = str(round(swap_mem.free / (1024.0**3), 2)) + " GB"

    _msg = f"■{'━'*100:100s}■"
    _msg += "\n┃{0}┃".format(" " * 43 + "\033[1m SYSTEM INFO \033[0m" + " " * 44)
    _msg += f"\n■{'─'*100:100s}■"
    _msg += "\n┃  {0:26s}: {1:78s}┃".format(
        "\033[1mMachine Name\033[0m", platform.node(),
    )
    _msg += "\n┃  {0:26s}: {1:78s}┃".format(
        "\033[1mOperating System\033[0m", platform.platform(),
    )
    _msg += "\n┃  {0:26s}: {1:78s}┃".format(
        "\033[1mPython Version\033[0m",
        f"{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}",
    )
    _msg += "\n┃  {0:26s}: {1:78s}┃".format("\033[1mCurrent WD\033[0m", os.getcwd())
    _msg += "\n┃  {0:26s}  {1:78s}┃".format("\033[1mHardware\033[0m", "")
    _msg += "\n┃          {0:26s}  {1:70s}┃".format("\033[1mCPU\033[0m", "")
    _msg += "\n┃                  {0:26s}: {1:62s}┃".format(
        "\033[1mBrand\033[0m", cpuinfo.get_cpu_info()["brand_raw"],
    )
    _msg += "\n┃                  {0:26s}: {1:62s}┃".format(
        "\033[1m# of cores\033[0m", str(multiprocessing.cpu_count()),
    )
    _msg += "\n┃          {0:26s}  {1:70s}┃".format("\033[1mRAM\033[0m", "")
    _msg += "\n┃                  {0:26s}: {1:62s}┃".format(
        "\033[1mTotal\033[0m", total_phy_mem,
    )
    _msg += "\n┃                  {0:26s}: {1:62s}┃".format(
        "\033[1mAvailable\033[0m", total_phy_avail,
    )
    _msg += "\n┃          {0:26s}  {1:70s}┃".format("\033[1mSwap Memory\033[0m", "")
    _msg += "\n┃                  {0:26s}: {1:62s}┃".format(
        "\033[1mTotal\033[0m", total_swp_mem,
    )
    _msg += "\n┃                  {0:26s}: {1:62s}┃".format(
        "\033[1mFree\033[0m", total_swp_free,
    )
    _msg += f"\n■{'━'*100:100s}■"
    print(_msg)


__all__ = ["SystemInfo", "print_brief_sys_info"]
