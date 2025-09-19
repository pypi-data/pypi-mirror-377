"""Analysis: Cross-platform package inventory helpers.

Detects available package managers at runtime and lists installed packages.
Linux-first support for APT/YUM/DNF/SNAP plus PIP/Conda/NPM.
"""

from __future__ import annotations

import json
import platform
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from syinfo.utils import Logger

# Get logger instance
logger = Logger.get_logger()


class PackageManagerType(Enum):
    APT = "apt"
    YUM = "yum"
    DNF = "dnf"
    PIP = "pip"
    CONDA = "conda"
    NPM = "npm"
    SNAP = "snap"


@dataclass
class PackageInfo:
    name: str
    version: str
    architecture: str = ""
    description: str = ""
    manager: str = ""


class PackageManager:
    """Cross-platform package manager interface.
    
    Detects available package managers at runtime and provides unified
    access to package information across different systems. Supports
    APT, YUM, DNF, PIP, Conda, NPM, and SNAP package managers.
    
    Attributes:
        platform: Current platform name (linux, darwin, etc.)
        supported_managers: List of detected package managers
        
    Examples:
        >>> manager = PackageManager()
        >>> packages = manager.list_packages(name_filter="python")
        >>> print(f"Found {len(packages)} packages")
    """
    
    def __init__(self) -> None:
        """Initialize package manager with auto-detection of available managers."""
        self.platform = platform.system().lower()
        logger.info(f"Initializing PackageManager on {self.platform}")
        self.supported_managers = self._detect_available_managers()

    def _detect_available_managers(self) -> List[PackageManagerType]:
        """Detect available package managers on the system.
        
        Uses parallel probing to quickly identify which package managers
        are installed and accessible. Probes are run with timeouts to avoid
        hanging on unresponsive commands.
        
        Returns:
            List of detected PackageManagerType enums
            
        Note:
            Detection timeout can be customized via SYINFO_PM_DETECT_TIMEOUT 
            environment variable (default: 2 seconds).
        """
        managers: List[PackageManagerType] = []
        # Command-line tests for each package manager
        tests: Dict[PackageManagerType, List[str]] = {
            PackageManagerType.APT: ["dpkg", "--version"],
            PackageManagerType.YUM: ["yum", "--version"],
            PackageManagerType.DNF: ["dnf", "--version"],
            PackageManagerType.PIP: ["pip", "--version"],
            PackageManagerType.CONDA: ["conda", "--version"],
            PackageManagerType.NPM: ["npm", "--version"],
            PackageManagerType.SNAP: ["snap", "--version"],
        }

        # Import here to avoid circular imports
        import os
        from concurrent.futures import ThreadPoolExecutor, as_completed

        # Allow timeout customization via environment variable
        try:
            timeout_s = float(os.environ.get("SYINFO_PM_DETECT_TIMEOUT", "2"))
            logger.debug(f"Using package manager detection timeout: {timeout_s}s")
        except Exception:
            timeout_s = 2.0
            logger.debug("Using default package manager detection timeout: 2.0s")

        def probe(item: tuple[PackageManagerType, List[str]]) -> Optional[PackageManagerType]:
            """Probe a single package manager for availability.
            
            Args:
                item: Tuple of (PackageManagerType, command_list)
                
            Returns:
                PackageManagerType if available, None otherwise
            """
            mgr, cmd = item
            try:
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=timeout_s,
                    check=False  # Don't raise on non-zero exit
                )
                if result.returncode == 0:
                    logger.debug(f"Detected package manager: {mgr.value}")
                    return mgr
            except subprocess.TimeoutExpired:
                logger.debug(f"Package manager detection timeout for {mgr.value}")
            except FileNotFoundError:
                logger.debug(f"Package manager not found: {mgr.value}")
            except Exception as e:
                logger.debug(f"Error detecting package manager {mgr.value}: {e}")
            return None

        # Run probes in parallel for faster detection
        logger.debug("Starting package manager detection...")
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_map = {executor.submit(probe, item): item[0] for item in tests.items()}
            for future in as_completed(future_map):
                mgr = future.result()
                if mgr:
                    managers.append(mgr)

        logger.info(f"Detected {len(managers)} package managers: {[m.value for m in managers]}")
        return managers

    def _list_packages_for_manager(
        self,
        manager: PackageManagerType,
        name_filter: str,
        installed_only: bool,
    ) -> List[PackageInfo]:
        """Route package listing to appropriate manager-specific method.
        
        Args:
            manager: Package manager type to query
            name_filter: Filter packages by name (case-insensitive)
            installed_only: Whether to list only installed packages
            
        Returns:
            List of PackageInfo objects
            
        Note:
            Each package manager has different capabilities and command syntax.
        """
        logger.debug(f"Listing packages for {manager.value} (filter: '{name_filter}', installed_only: {installed_only})")
        
        # Dispatch to manager-specific implementation
        handler_map = {
            PackageManagerType.APT: lambda: self._list_apt_packages(name_filter, installed_only),
            PackageManagerType.PIP: lambda: self._list_pip_packages(name_filter),
            PackageManagerType.DNF: lambda: self._list_dnf_packages(name_filter, installed_only),
            PackageManagerType.YUM: lambda: self._list_yum_packages(name_filter, installed_only),
            PackageManagerType.CONDA: lambda: self._list_conda_packages(name_filter),
            PackageManagerType.NPM: lambda: self._list_npm_packages(name_filter),
            PackageManagerType.SNAP: lambda: self._list_snap_packages(name_filter),
        }
        
        if manager in handler_map:
            try:
                packages = handler_map[manager]()
                logger.debug(f"Found {len(packages)} packages from {manager.value}")
                return packages
            except Exception as e:
                logger.error(f"Failed to list packages from {manager.value}: {e}")
                return []
        else:
            logger.warning(f"Unsupported package manager: {manager.value}")
            return []

    def _list_apt_packages(self, name_filter: str, installed_only: bool) -> List[PackageInfo]:
        packages: List[PackageInfo] = []
        cmd = (
            "dpkg-query -W -f='${Package}\\t${Version}\\t${Architecture}\\t${Description}\\n'"
            if installed_only
            else "apt list"
        )
        if name_filter:
            cmd = f"{cmd} | grep -i '{name_filter}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                if installed_only:
                    parts = line.split("\t")
                    if len(parts) >= 4:
                        packages.append(
                            PackageInfo(
                                name=parts[0],
                                version=parts[1],
                                architecture=parts[2],
                                description=parts[3],
                                manager="apt",
                            )
                        )
        return packages

    def _list_pip_packages(self, name_filter: str) -> List[PackageInfo]:
        packages: List[PackageInfo] = []
        result = subprocess.run(
            "pip list --format=json", shell=True, capture_output=True, text=True
        )
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                for pkg in data:
                    if name_filter and name_filter.lower() not in pkg["name"].lower():
                        continue
                    packages.append(
                        PackageInfo(
                            name=pkg["name"],
                            version=pkg["version"],
                            architecture="python",
                            description=f"Python package: {pkg['name']}",
                            manager="pip",
                        )
                    )
            except json.JSONDecodeError:
                pass
        return packages

    def _list_dnf_packages(self, name_filter: str, installed_only: bool) -> List[PackageInfo]:
        packages: List[PackageInfo] = []
        status = "installed" if installed_only else "all"
        cmd = f"dnf list --{status}"
        if name_filter:
            cmd = f"{cmd} | grep -i '{name_filter}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n")[1:]:
                parts = line.split()
                if len(parts) >= 3:
                    packages.append(
                        PackageInfo(
                            name=parts[0].split(".")[0],
                            version=parts[1],
                            architecture=parts[0].split(".")[-1] if "." in parts[0] else "",
                            manager="dnf",
                        )
                    )
        return packages

    def _list_yum_packages(self, name_filter: str, installed_only: bool) -> List[PackageInfo]:
        packages: List[PackageInfo] = []
        status = "installed" if installed_only else "all"
        cmd = f"yum list {status}"
        if name_filter:
            cmd = f"{cmd} | grep -i '{name_filter}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n")[1:]:
                parts = line.split()
                if len(parts) >= 3:
                    packages.append(
                        PackageInfo(
                            name=parts[0].split(".")[0],
                            version=parts[1],
                            architecture=parts[0].split(".")[-1] if "." in parts[0] else "",
                            manager="yum",
                        )
                    )
        return packages

    def _list_conda_packages(self, name_filter: str) -> List[PackageInfo]:
        packages: List[PackageInfo] = []
        result = subprocess.run(
            "conda list --json", shell=True, capture_output=True, text=True
        )
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                for pkg in data:
                    if name_filter and name_filter.lower() not in pkg["name"].lower():
                        continue
                    packages.append(
                        PackageInfo(
                            name=pkg["name"],
                            version=pkg.get("version", "unknown"),
                            description=f"Conda package: {pkg['name']}",
                            manager="conda",
                        )
                    )
            except json.JSONDecodeError:
                pass
        return packages

    def _list_npm_packages(self, name_filter: str) -> List[PackageInfo]:
        packages: List[PackageInfo] = []
        result = subprocess.run(
            "npm list --json --depth=0", shell=True, capture_output=True, text=True
        )
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                deps = data.get("dependencies", {})
                for name, info in deps.items():
                    if name_filter and name_filter.lower() not in name.lower():
                        continue
                    packages.append(
                        PackageInfo(
                            name=name,
                            version=info.get("version", "unknown"),
                            description=f"NPM package: {name}",
                            manager="npm",
                        )
                    )
            except json.JSONDecodeError:
                pass
        return packages

    def _list_snap_packages(self, name_filter: str) -> List[PackageInfo]:
        packages: List[PackageInfo] = []
        result = subprocess.run("snap list", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")[1:]
            for line in lines:
                parts = line.split()
                if len(parts) >= 3:
                    name = parts[0]
                    if name_filter and name_filter.lower() not in name.lower():
                        continue
                    packages.append(
                        PackageInfo(
                            name=name,
                            version=parts[1],
                            description=f"Snap package: {name}",
                            manager="snap",
                        )
                    )
        return packages

    def list_packages(
        self,
        name_filter: str = "",
        manager: Optional[PackageManagerType] = None,
        installed_only: bool = True,
        as_dict: bool = True,
    ) -> Union[List[PackageInfo], List[Dict[str, str]]]:
        """List packages from one or all supported package managers.

        Args:
            name_filter: Filter packages by name (case-insensitive substring match).
            manager: Specific package manager to query. If None, queries all supported managers.
            installed_only: Whether to include only installed packages.
            as_dict: If True, return list of dictionaries instead of PackageInfo objects.

        Returns:
            List of unique PackageInfo objects or dictionaries. Duplicates across managers are removed.

        Examples:
            >>> pm = PackageManager()
            >>> all_packages = pm.list_packages()
            >>> python_packages = pm.list_packages(name_filter="python")
            >>> apt_packages = pm.list_packages(manager=PackageManagerType.APT)
            >>> PackageManager().list_packages(
            ... # name_filter="matplot", manager=PackageManagerType.PIP,
            ... name_filter="gcc", manager=PackageManagerType.APT,
            ... installed_only= True, as_dict=True
)
        """
        managers_to_query = [manager] if manager else self.supported_managers
        all_packages: List[PackageInfo] = []

        for mgr in managers_to_query:
            try:
                all_packages.extend(
                    self._list_packages_for_manager(mgr, name_filter, installed_only)
                )
            except Exception as exc:
                logger.debug("Failed to query %s: %s", mgr.value, exc)

        unique: Dict[tuple, PackageInfo] = {}
        for pkg in all_packages:
            key = (pkg.name, pkg.manager)
            if key not in unique:
                unique[key] = pkg
        
        result = list(unique.values())
        
        if as_dict:
            from dataclasses import asdict
            return [asdict(pkg) for pkg in result]
        
        return result

