"""Network device discovery and MAC vendor lookup utilities.

This module provides network scanning capabilities to discover devices
on the local network segment. Uses ARP scanning with scapy and provides
MAC address vendor lookup via external APIs.

Note:
    Network scanning typically requires elevated privileges (sudo) on
    Linux/macOS systems due to raw socket access requirements.
"""

import os
import platform
import urllib.request

import getmac
from scapy.all import ARP, Ether, srp

from syinfo.constants import NEED_SUDO, UNKNOWN
from syinfo.utils import Execute, Logger

# Get logger instance
logger = Logger.get_logger()

__author__ = "Mohit Rajput"
__copyright__ = "Copyright (c)"
__version__ = "${VERSION}"
__email__ = "mohitrajput901@gmail.com"


def get_vendor(mac_address: str) -> str:
    """Look up the vendor/manufacturer of a MAC address.

    Uses multiple external APIs to resolve MAC address OUI (Organizationally
    Unique Identifier) to manufacturer name. Falls back between APIs if
    rate limits or errors are encountered.

    Args:
        mac_address: MAC address in any standard format (xx:xx:xx:xx:xx:xx)

    Returns:
        Vendor/manufacturer name, or 'unknown' if lookup fails

    Note:
        Makes external HTTP requests. May be rate-limited by API providers.
        Consider caching results for frequently looked-up addresses.

    Examples:
        >>> get_vendor("00:1B:63:84:45:E6")
        'Apple, Inc.'
        >>> get_vendor("invalid-mac")
        'unknown'
    """
    logger.debug(f"Looking up vendor for MAC address: {mac_address}")
    
    try:
        # Primary API: macvendors.com
        response = urllib.request.urlopen(f"http://api.macvendors.com/{mac_address}", timeout=5)
        device = response.read().decode("utf-8").strip()
        if device:
            logger.debug(f"Vendor lookup successful (macvendors.com): {device}")
            return device
            
    except Exception as e:
        # Common: HTTP Error 429 (Too Many Requests) or timeout
        logger.debug(f"Primary vendor lookup failed: {e}")
        
        try:
            # Fallback API: maclookup.app
            response = urllib.request.urlopen(
                f"https://api.maclookup.app/v2/macs/{mac_address}", timeout=5
            )
            data = response.read().decode("utf-8")
            # Parse JSON-like response for company field
            if 'company' in data:
                parts = data.split(",")
                for part in parts:
                    if 'company' in part:
                        device = part.replace('company":', "").replace('"', "").strip()
                        if device:
                            logger.debug(f"Vendor lookup successful (maclookup.app): {device}")
                            return device
                            
        except Exception as e2:
            logger.debug(f"Fallback vendor lookup also failed: {e2}")
    
    logger.debug(f"Unable to resolve vendor for MAC: {mac_address}")
    return UNKNOWN


def search_devices_on_network(time: int = 10, seach_device_vendor_too: bool = True) -> dict:
    """Discover devices on the local network using ARP scanning.

    Performs an ARP sweep of the local network segment to discover active
    devices. Optionally performs vendor lookup for discovered MAC addresses.

    Args:
        time: Scan timeout in seconds (default: 10)
        seach_device_vendor_too: Whether to lookup MAC vendors (default: True)

    Returns:
        Mapping of IP address to a dictionary with details, for example:
        {
          "192.168.1.10": {"mac_address": "aa:bb:cc:dd:ee:ff", "vendor": "..."}
        }

    Permission handling:
        On POSIX systems, raw socket operations typically require root. If the
        current process lacks sufficient privileges, this function returns
        the sentinel value NEED_SUDO.

    Notes:
        Vendor lookup makes external HTTP requests and may be rate-limited.

    Examples:
        >>> devices = search_devices_on_network(time=5, seach_device_vendor_too=False)
        >>> for ip, info in devices.items():
        ...     print(f"Found {ip} ({info.get('mac_address')})")
    """
    logger.info(f"Starting network device discovery (timeout: {time}s, vendor_lookup: {seach_device_vendor_too})")
    
    # Check for required elevated privileges
    plat = platform.system()
    if ((plat == "Linux") or (plat == "Darwin")) and hasattr(os, "geteuid") and (os.geteuid() != 0):
        logger.warning("Network scanning requires elevated privileges (sudo) on Linux/macOS")
        return NEED_SUDO

    # get needed infomation
    current_ip_on_network = Execute.on_shell("hostname -I")
    interface_mac_address = getmac.get_mac_address()
    gateway = Execute.on_shell("ip route | grep default | awk '{print $3}'")
    device_name_raw = Execute.on_shell("sudo dmidecode | grep 'SKU Number' | head -1")
    device_name = device_name_raw.split("SKU Number:")[-1].strip() if device_name_raw and "SKU Number:" in device_name_raw else UNKNOWN

    # Get the conected device info
    start, connected_devices = 0, {}

    # appending the original execution device information
    connected_devices[current_ip_on_network] = {
        "mac_address": interface_mac_address,
        "device_name": device_name,
        "identifier": "current device",
    }
    if seach_device_vendor_too:
        connected_devices[current_ip_on_network]["vendor"] = get_vendor(
            interface_mac_address,
        )

    while start <= time:
        start += 1
        devided = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=gateway + "/24")
        packets = srp(devided, timeout=0.5, verbose=False)[
            0
        ]  # "0.5" because of double attempts per second

        for result in packets:
            network_ip = result[1].psrc
            mac = result[1].hwsrc

            if (network_ip in connected_devices) and (
                (seach_device_vendor_too is False)
                or ("vendor" not in connected_devices[network_ip])
                or (connected_devices[network_ip]["vendor"] != UNKNOWN)
            ):
                continue

            connected_devices[network_ip] = {}
            connected_devices[network_ip]["mac_address"] = mac
            connected_devices[network_ip]["identifier"] = (
                "router" if network_ip == gateway else UNKNOWN
            )

            if seach_device_vendor_too:
                connected_devices[network_ip]["vendor"] = get_vendor(mac)

    return connected_devices


if __name__ == "__main__":
    connected_devices = search_devices_on_network(time=10, seach_device_vendor_too=True)
    print("\nconnected_devices:", connected_devices)
