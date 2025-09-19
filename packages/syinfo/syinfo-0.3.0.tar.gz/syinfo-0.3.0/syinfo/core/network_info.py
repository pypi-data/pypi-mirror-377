"""Get Network info."""

import contextlib
import json
import copy
import re
from typing import Any, Dict, Optional

import getmac
import psutil
import requests
import yaml

from syinfo.constants import UNKNOWN
from syinfo.exceptions import SystemAccessError
from syinfo.core.search_network import search_devices_on_network
from syinfo.utils import Execute, HumanReadable, create_highlighted_heading, export_data, Logger

# Get logger instance
logger = Logger.get_logger()

__author__ = "Mohit Rajput"
__copyright__ = "Copyright (c)"
__version__ = "${VERSION}"
__email__ = "mohitrajput901@gmail.com"


class NetworkInfo:
    """Gather information on network."""

    @staticmethod
    def is_internet_present(timeout=5):
        """Check if the internet connection is available or not."""
        url = "http://google.com/"
        try:
            request = requests.get(url, timeout=timeout)
            return True
        except (requests.ConnectionError, requests.Timeout):
            return False

    @staticmethod
    def check_ipv(txt):
        """Seems to be formatting the ipv4 and ipv6 properly in in the string if both are present"""
        ipv4 = r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
        ipv6 = (
            "(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:"
            "[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:"
            "[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}"
            "(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:"
            ")|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}"
            r"[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]"
            r"|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))"
        )

        x = re.search(ipv4, txt)
        y = re.search(ipv6, txt)
        if x and y:
            txt = txt.replace(" ", ", ")
        return txt

    @staticmethod
    def get_public_ip():
        """Get public IP."""
        public_ip = UNKNOWN
        urls = [
            "https://icanhazip.com",
            "https://ifconfig.me/ip",
        ]
        for url in urls:
            result = Execute.api(url, line_no=0)
            if result != UNKNOWN:
                public_ip = result
                break
        return public_ip

    @staticmethod
    def get_public_ip_info(public_ip):
        """Get the details on the public IP."""
        url = f"https://ip-api.io/json/{public_ip}"
        response = Execute.api(url, line_no=None)
        info = json.loads(response)
        isp = info["organisation"]
        demographic = {
            "country": info["country_name"],
            "city": info["city"],
            "region": info["region_name"],
            "latitude": info["latitude"],
            "longitude": info["longitude"],
            "zip_code": info["zip_code"],
            "maps": "https://www.google.com/maps/search/?api=1&query={},{}".format(
                info["latitude"], info["longitude"],
            ),  # https://stackoverflow.com/a/52943975
            # maps = f"https://www.google.com/maps/@{lat},{lon},14z"
            "meta": {
                "country_code": info["country_code"],
                "region_code": info["region_code"],
                "countryCapital": info["countryCapital"],
                "time_zone": info["time_zone"],
                "callingCode": info["callingCode"],
                "currency": info["currency"],
                "currencySymbol": info["currencySymbol"],
                "emojiFlag": info["emojiFlag"],
                "flagUrl": info["flagUrl"],
                "public_ip": info["ip"],
                "is_in_european_union": info["is_in_european_union"],
                "metro_code": info["metro_code"],
                "suspiciousFactors": info["suspiciousFactors"],
            },
        }
        return isp, demographic

    @staticmethod
    def get_wifiname_and_password():
        """Get the name and the password for the connected Wifi."""
        wifi_name = Execute.on_shell("iwgetid -r")
        password = Execute.on_shell(
            f"nmcli -s -g 802-11-wireless-security.psk connection show {wifi_name}",
            None,
        )
        if len(password) != 0:
            return wifi_name, password

        new_wifi_name = "{} {}".format(
            Execute.on_shell(
                "nmcli -s -g 802-11-wireless-security.psk | grep 'connected to' | awk '{print $4}'",
            ),
            Execute.on_shell(
                "nmcli -s -g 802-11-wireless-security.psk | grep 'connected to' | awk '{print $5}'",
            ),
        )
        password = Execute.on_shell(
            f"nmcli -s -g 802-11-wireless-security.psk connection show {new_wifi_name}",
            None,
        )
        if len(password) != 0:
            return new_wifi_name, password

        return wifi_name, UNKNOWN

    @staticmethod
    def get_available_wifi_options():
        """List the available options for the wifi."""
        cmd = """
        nmcli -f ssid,mode,chan,rate,signal,bars,security,in-use,bssid -t device wifi \
          | sed 's/\\\\:/-/g' \
          | jq -sR 'split("\n") | map(split(":")) | map({"network": .[0], "mode": .[1], "channel": .[2], "rate": .[3], "signal": .[4], "bars": .[5], "security": .[6], "in-use": .[7], "mac": .[8]})'
        """
        wifi_options = json.loads(Execute.on_shell(cmd, None))
        wifi_options = [d for d in wifi_options if d["network"]]
        for d in wifi_options:
            d["in-use"] = False if d["in-use"].strip() == 0 else True
            d["mac"] = d["mac"].replace("-", ":")
            d["signal"] = int(d["signal"])
        return wifi_options

    @staticmethod
    def calculate_current_wifi_signal_strength():
        """Get the signal strength of the connected wifi."""
        strength, quality = UNKNOWN, UNKNOWN
        try:
            with contextlib.redirect_stdout(None):
                # signal = int(Execute.on_shell("iwconfig | grep level | awk '{print $4}'").replace("level=", ""))
                strength = Execute.on_shell(
                    "iwconfig | grep -o 'Signal level=[0-9a-zA-Z -]*'",
                ).replace("Signal level=", "")
                signal = int(strength.split()[0])

                if signal >= -30:
                    quality = "[7/7] super strong"
                elif (signal < -30) and (signal >= -50):
                    quality = "[6/7] excellent signal"
                elif (signal < -50) and (signal >= -67):
                    quality = "[5/7] good signal"
                elif (signal < -67) and (signal >= -70):
                    quality = "[4/7] reliable signal"
                elif (signal < -70) and (signal >= -80):
                    quality = "[3/7] not strong signal"
                elif (signal < -80) and (signal >= -90):
                    quality = "[2/7] unreliable signal"
                elif signal < -90:
                    quality = "[1/7] super weak signal"

                strength = f"{signal} DBm"
        finally:
            return strength, quality

    @staticmethod
    def get_device_interfaces():
        """Get details on network interfaces."""

        def _convert_to_dict(txt):
            d = yaml.load(txt, Loader=yaml.FullLoader)
            di = {}
            for k, val in d.items():
                category, kk = k.split(".")
                category, kk = category.lower(), kk.lower()
                if category not in di:
                    di[category] = {}
                di[category][kk] = val
            return di

        network_meta = [
            _convert_to_dict(e)
            for e in Execute.on_shell("nmcli device show", None).split("\n\n")
        ]
        # network_meta = {e["general"]["device"]:e for e in network_meta}
        return network_meta

    @staticmethod
    def print(info, return_msg=False):
        """Print network information."""
        _msg = create_highlighted_heading(
            "Network Information",
            line_symbol="━",
            total_length=100,
            prefix_suffix="",
            center_highlighter=(" ", " "),
        )
        _msg += "\n."
        d = info["network_info"]
        _msg += "\n└── Network Information"
        _msg += "\n    ├── {:.<16} {}".format("Hostname", d["hostname"])
        _msg += "\n    ├── {:.<16} {}".format("Mac Address", d["mac_address"])
        _msg += "\n    ├── {:.<16} {}".format(
            "Internet Available", d["internet_present"],
        )
        _msg += "\n    ├── Data transfer since boot"
        _msg += "\n    │   ├── Sent"
        _msg += "\n    │   │   ├── {:.<16} {}".format(
            "Data (Bytes) ", d["transfer_stats"]["sent"]["in_bytes"],
        )
        _msg += "\n    │   │   └── {:.<16} {}".format(
            "Data ", d["transfer_stats"]["sent"]["readable"],
        )
        _msg += "\n    │   └── Received"
        _msg += "\n    │       ├── {:.<16} {}".format(
            "Data (Bytes) ", d["transfer_stats"]["received"]["in_bytes"],
        )
        _msg += "\n    │       └── {:.<16} {}".format(
            "Data ", d["transfer_stats"]["received"]["readable"],
        )
        _msg += "\n    ├── Physical & Virtual Interfaces"
        _msg += "\n    │   ├── Brief"
        for category, val in d["interfaces"]["brief"].items():
            _msg += "\n    │   │   {}── {}".format(
                "└" if category == list(d["interfaces"]["brief"].keys())[-1] else "├",
                category,
            )
            for name, sub_val in val.items():
                _msg += "\n    │   │   {}   {}── {:.<16} {}".format(
                    (
                        " "
                        if category == list(d["interfaces"]["brief"].keys())[-1]
                        else "│"
                    ),
                    (
                        "└"
                        if name == list(d["interfaces"]["brief"][category].keys())[-1]
                        else "├"
                    ),
                    name,
                    sub_val,
                )
        _msg += "\n    │   └── Detailed"
        for i, di in enumerate(d["interfaces"]["detailed"]):
            _msg += "\n    │       {}──{: >3} ──┐".format(
                "└" if (i + 1) == len(d["interfaces"]["detailed"]) else "├", i,
            )
            for category, val in di.items():
                _msg += "\n    │       {}        {}── {}".format(
                    " " if (i + 1) == len(d["interfaces"]["detailed"]) else "│",
                    "└" if category == list(di.keys())[-1] else "├",
                    category,
                )
                for name, sub_val in val.items():
                    _msg += "\n    │       {}        {}   {}── {:.<16} {}".format(
                        " " if (i + 1) == len(d["interfaces"]["detailed"]) else "│",
                        " " if category == list(di.keys())[-1] else "│",
                        "└" if name == list(di[category].keys())[-1] else "├",
                        name,
                        sub_val,
                    )
        # Wifi
        _msg += "\n    ├── Wifi Connection"
        for category, val in d["wifi"].items():
            if isinstance(val, list) is False:
                _msg += "\n    │   ├── {:.<16} {}".format(
                    " ".join(category.split("_")).capitalize(), val,
                )
            else:
                _msg += "\n    │   └── {}".format(
                    " ".join(category.split("_")).capitalize(),
                )
                for i, di in enumerate(d["wifi"]["options"]):
                    _msg += "\n    │       {}──{: >3} ──┐".format(
                        "└" if (i + 1) == len(d["wifi"]["options"]) else "├", i,
                    )
                    for category, val in di.items():
                        _msg += "\n    │       {}        {}── {:.<16} {}".format(
                            " " if (i + 1) == len(d["wifi"]["options"]) else "│",
                            "└" if category == list(di.keys())[-1] else "├",
                            " ".join(category.split("_")).capitalize(),
                            val,
                        )
        # Devices on the network
        _msg += "\n    ├── Devices Available on Network"
        if isinstance(d["devices_on_network"], dict) is False:
            _msg += "\n    │   └── {:.>32} * {:.<32}".format(
                d["devices_on_network"], d["devices_on_network"],
            )
        else:
            for category, val in d["devices_on_network"].items():
                _msg += "\n    │   {}── {}".format(
                    (
                        "└"
                        if category == list(d["devices_on_network"].keys())[-1]
                        else "├"
                    ),
                    category,
                )
                for name, sub_val in val.items():
                    _msg += "\n    │   {}   {}── {:.<16} {}".format(
                        # " " if (i+1) == len(d["devices_on_network"]) else "│",
                        (
                            " "
                            if category == list(d["devices_on_network"].keys())[-1]
                            else "│"
                        ),
                        (
                            "└"
                            if name
                            == list(d["devices_on_network"][category].keys())[-1]
                            else "├"
                        ),
                        name,
                        sub_val,
                    )
        # Current Addresses
        _msg += "\n    ├── Current Addresses"
        for category, val in d["current_addresses"].items():
            _msg += "\n    │   {}── {:.<16} {}".format(
                "└" if category == list(d["current_addresses"].keys())[-1] else "├",
                " ".join(category.split("_")).capitalize(),
                val,
            )
        # Demographic
        _msg += "\n    └── Demographic Information"
        for category, val in d["demographic"].items():
            if isinstance(val, dict) is False:
                _msg += "\n        {}── {:.<16} {}".format(
                    "└" if category == list(d["demographic"].keys())[-1] else "├",
                    " ".join(category.split("_")).capitalize(),
                    val,
                )
            else:
                _msg += "\n        {}── {}".format(
                    "└" if category == list(d["demographic"].keys())[-1] else "├",
                    " ".join(category.split("_")).capitalize(),
                )
                for name, sub_val in val.items():
                    _msg += "\n        {}   {}── {:.<16} {}".format(
                        # " " if (i+1) == len(d["devices_on_network"]) else "│",
                        " " if category == list(d["demographic"].keys())[-1] else "│",
                        (
                            "└"
                            if name == list(d["demographic"][category].keys())[-1]
                            else "├"
                        ),
                        name,
                        sub_val,
                    )
        if return_msg:
            return _msg
        else:
            print(_msg)

    @staticmethod
    def get_all(search_period=10, search_device_vendor_too=True):
        """Aggregate all the information related to the network."""
        public_ip = NetworkInfo.check_ipv(NetworkInfo.get_public_ip())

        # get IO statistics since boot
        net_io = psutil.net_io_counters()
        # get all network interfaces (virtual and physical)
        if_addrs = psutil.net_if_addrs()
        network_di = {}
        for interface_name, interface_addresses in if_addrs.items():
            network_di[interface_name] = {}
            for address in interface_addresses:
                if address.family.name == "AF_INET":
                    network_di[interface_name]["ip_address"] = address.address
                    network_di[interface_name]["nwtmask"] = address.netmask
                    network_di[interface_name]["broadcast_ip"] = address.broadcast
                elif address.family.name == "AF_PACKET":
                    network_di[interface_name]["mac_address"] = address.address
                    network_di[interface_name]["nwtmask"] = address.netmask
                    network_di[interface_name]["broadcast_mac"] = address.broadcast
        interfaces_detailed = NetworkInfo.get_device_interfaces()
        isp, demographic = NetworkInfo.get_public_ip_info(public_ip)
        wifi_name, wifi_password = NetworkInfo.get_wifiname_and_password()
        wifi_strength, wifi_quality = (
            NetworkInfo.calculate_current_wifi_signal_strength()
        )
        wifi_options = NetworkInfo.get_available_wifi_options()
        devices_on_network = search_devices_on_network(
            time=search_period, seach_device_vendor_too=search_device_vendor_too,
        )

        # ----------------------------------< Dict Creation >---------------------------------- #
        info = {
            "network_info": {
                "hostname": Execute.on_shell("hostname"),
                "mac_address": getmac.get_mac_address(),
                "internet_present": NetworkInfo.is_internet_present(),
                "transfer_stats": {
                    "sent": {
                        "in_bytes": net_io.bytes_sent,
                        "readable": HumanReadable.bytes_to_size(net_io.bytes_sent),
                    },
                    "received": {
                        "in_bytes": net_io.bytes_recv,
                        "readable": HumanReadable.bytes_to_size(net_io.bytes_recv),
                    },
                },
                "interfaces": {"brief": network_di, "detailed": interfaces_detailed},
                "wifi": {
                    "wifi_name": wifi_name,
                    "password": wifi_password,
                    # Avoid sudo; attempt without sudo and fall back gracefully
                    "security": (lambda: (
                        Execute.on_shell(
                            "wpa_cli status | grep 'key_mgmt'",
                            timeout=5,
                        ).replace("key_mgmt=", "")
                        if True else UNKNOWN
                    ))() if True else UNKNOWN,
                    "interface": Execute.on_shell(
                        "route | grep default | awk '{print $8}'",
                    ),
                    "frequency": Execute.on_shell(
                        "iwgetid -f | grep -o 'Frequency:[0-9a-zA-Z .]*'",
                    ).replace("Frequency:", ""),
                    "channel": Execute.on_shell(
                        "iwgetid -c | awk '{print $2}'",
                    ).replace("Channel:", ""),
                    "signal_strength": wifi_strength,
                    "signal_quality": wifi_quality,
                    "options": wifi_options,
                },
                "devices_on_network": devices_on_network,
                "current_addresses": {
                    "isp": isp,
                    "public_ip": public_ip,
                    "ip_address_host": Execute.on_shell("hostname -i"),
                    "ip_address": Execute.on_shell("hostname -I"),
                    "gateway": Execute.on_shell(
                        "ip route | grep default | awk '{print $3}'",
                    ),
                    "dns_1": Execute.on_shell(
                        "nmcli dev show | grep DNS | awk '{print $2}'", 0,
                    ),
                    "dns_2": Execute.on_shell(
                        "nmcli dev show | grep DNS | awk '{print $2}'", 1,
                    ),
                },
                "demographic": demographic,
            },
        }

        return info

    @staticmethod
    def export(
        format: str = "json",
        output_file: Optional[str] = None,
        include_sensitive: bool = False,
        info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Export network information to JSON or YAML.

        Args:
            format: Export format ("json" or "yaml")
            output_file: Optional path to write the exported content
            include_sensitive: Include potentially sensitive fields if True
            info: Optional pre-collected info dict to export

        Returns:
            Exported string content
        """
        data: Dict[str, Any] = (
            info if info is not None else NetworkInfo.get_all(search_period=0, search_device_vendor_too=False)
        )
        sanitized: Dict[str, Any] = copy.deepcopy(data)

        if not include_sensitive:
            try:
                ni = sanitized.get("network_info")
                if isinstance(ni, dict):
                    ni["mac_address"] = "***"
                    if isinstance(ni.get("wifi"), dict) and "password" in ni["wifi"]:
                        ni["wifi"]["password"] = "***"
            except Exception:
                pass

        return export_data(sanitized, format=format, output_file=output_file)
