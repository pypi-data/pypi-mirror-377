"""SyInfo CLI - Simple and Clean Implementation.

Keeps the beloved flag-based interface with a clean, maintainable structure.
Simple like the original, but with better error handling and some visual improvements.

Usage Examples:
    $ syinfo -d --json                      # Device info as JSON
    $ syinfo -s -t 10                       # System info with 10s timeout
    $ syinfo --system-monitor -t 300 -i 5   # Monitor system for 5 minutes  
    $ syinfo --process-monitor --filter python  # Monitor Python processes
    $ syinfo -l --pattern "error"           # Search logs for "error"
    $ syinfo -p --name "python"             # Analyze Python packages
    $ sudo syinfo -N                        # Scan network devices
"""

import re
import sys
import json
import argparse
import textwrap
import time
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# SyInfo imports
from syinfo.utils.logger import Logger, LoggerConfig

# Configure logger to ERROR level only
logger_config = LoggerConfig(
    log_level=40,  # ERROR level (40)
    output_to_stdout=True,
    verbose_logs=False,
    enable_incident_counting=False,
    enable_traceback=False
)
logger = Logger.get_logger(logger_config)

# Force set log level to ERROR (in case singleton was already created elsewhere)
logger_instance = Logger.get_instance()
if logger_instance:
    logger_instance.set_log_level(40)  # ERROR level

from syinfo._version import __version__
from syinfo.exceptions import SyInfoException
from syinfo.core.device_info import DeviceInfo
from syinfo.core.system_info import SystemInfo
from syinfo.core.network_info import NetworkInfo
from syinfo.resource_monitor.system_monitor import SystemMonitor
from syinfo.resource_monitor.process_monitoring import ProcessMonitor
from syinfo.analysis.logs import LogAnalyzer, LogAnalysisConfig


def info(msg: str, json_mode: bool = False) -> None:
    """Print info message."""
    if not json_mode:
        print(f"[INFO] {msg}")

def error(msg: str, json_mode: bool = False) -> None:
    """Print error message.""" 
    if json_mode:
        print(f"[ERROR] {msg}", file=sys.stderr)
    else:
        print(f"[ERROR] {msg}")

def warning(msg: str, json_mode: bool = False) -> None:
    """Print warning message."""
    if json_mode:
        print(f"[WARNING] {msg}", file=sys.stderr)
    else:
        print(f"[WARNING] {msg}")

def success(msg: str, json_mode: bool = False) -> None:
    """Print success message."""
    if not json_mode:
        print(f"[SUCCESS] {msg}")


def contact(msg: bool = True) -> str:
    """Display contact information."""
    _msg = "\n  Contact Information:"
    _msg += "\n    Email: \033[4m\033[94mmohitrajput901@gmail.com\033[0m"
    _msg += "\n    GitHub: \033[4m\033[94mhttps://github.com/MR901/syinfo\033[0m"
    if msg:
        print(_msg)
    return _msg


def handle_device_info(args) -> int:
    """Handle device information request."""
    try:
        device_info = DeviceInfo.get_all()
        # Output results
        if args.json:
            print(json.dumps(device_info, indent=2, default=str))
        elif not args.disable_print:
            DeviceInfo.print(device_info)
        return 0
        
    except Exception as e:
        error(f"Failed to collect device information: {e}", json_mode=args.json)
        return 1


def handle_system_info(args) -> int:
    """Handle complete system information request.""" 
    try:
        system_info = SystemInfo.get_all()
        # Output results
        if args.json:
            print(json.dumps(system_info, indent=2, default=str))
        elif not args.disable_print:
            SystemInfo.print(system_info)
        return 0
    except Exception as e:
        error(f"Failed to collect system information: {e}", json_mode=args.json)
        return 1


def handle_network_info(args) -> int:
    """Handle network information request."""
    try:
        network_info = NetworkInfo()
        net_data = network_info.get_all()
        
        # Output results
        if args.json:
            print(json.dumps(net_data, indent=2, default=str))
        elif not args.disable_print:
            NetworkInfo.print(net_data)

        return 0
            
    except Exception as e:
        error(f"Failed to collect network information: {e}", json_mode=args.json)
        return 1


def handle_monitoring(args) -> int:
    """Handle system monitoring."""
    try:
        duration = args.time
        interval = args.interval
        
        info(f"Starting system monitoring: {duration}s duration, {interval}s intervals", json_mode=args.json)
        if not args.disable_print and not args.json:
            warning("Press Ctrl+C to stop monitoring early", json_mode=args.json)

        # Create and start monitor
        monitor = SystemMonitor(
            interval=interval,
            output_path=getattr(args, 'output', None),
            keep_in_memory=True
        )
        
        monitor.start()
        
        # Wait for completion with interrupt handling
        try:
            time.sleep(duration + 1)  # Wait a bit longer than monitoring duration
            
            # Get results
            if monitor.is_running:
                results = monitor.stop(print_summary=not args.json)
            else:
                results = {
                    "total_points": len(monitor.data_points),
                    "data_points": monitor.data_points
                }
                
        except KeyboardInterrupt:
            warning("Monitoring interrupted by user", json_mode=args.json)
            results = monitor.stop(print_summary=not args.json) if monitor.is_running else {
                "error": "Monitoring interrupted", 
                "data_points": monitor.data_points
            }
        
        # Output results
        if args.json:
            print(json.dumps(results, indent=2, default=str))
        elif not args.disable_print:
            total_points = results.get('total_points', 0)
            info(f"Monitoring completed: {total_points} data points collected", json_mode=args.json)
            
        success("Monitoring completed successfully", json_mode=args.json)
        return 0
        
    except Exception as e:
        error(f"Monitoring failed: {e}", json_mode=args.json)
        return 1


def handle_process_monitoring(args) -> int:
    """Handle process monitoring."""
    try:
        duration = args.time
        interval = args.interval
        process_filter = getattr(args, 'filter', None)
        match_field = getattr(args, 'match_field', 'name')
        
        info(f"Starting process monitoring: {duration}s duration, {interval}s intervals", json_mode=args.json)
        if process_filter:
            info(f"Filtering processes by {match_field}: '{process_filter}'", json_mode=args.json)
        else:
            info("Monitoring all processes (use --filter to specify process name)", json_mode=args.json)
            
        if not args.disable_print and not args.json:
            warning("Press Ctrl+C to stop monitoring early", json_mode=args.json)
        
        # Create and configure process monitor
        monitor = ProcessMonitor(
            filters=[process_filter] if process_filter else None,
            match_fields=[match_field],
            interval=interval,
            output_path=getattr(args, 'output', None),
            keep_in_memory=True
        )
        
        monitor.start()
        
        # Wait for completion with interrupt handling
        try:
            time.sleep(duration + 1)
            
            # Get results
            if monitor.is_running:
                results = monitor.stop(print_summary=not args.json)
            else:
                results = {
                    "total_points": len(monitor.data_points),
                    "data_points": monitor.data_points
                }
                
        except KeyboardInterrupt:
            warning("Process monitoring interrupted by user", json_mode=args.json)
            results = monitor.stop(print_summary=not args.json) if monitor.is_running else {
                "error": "Process monitoring interrupted",
                "data_points": monitor.data_points
            }
        
        # Output results
        if args.json:
            print(json.dumps(results, indent=2, default=str))
        elif not args.disable_print:
            total_points = results.get('total_points', 0)
            info(f"Process monitoring completed: {total_points} data points collected", json_mode=args.json)
            
            # Show sample data if available
            data_points = results.get('data_points', [])
            if data_points and not args.json:
                info("Sample process data:", json_mode=args.json)
                for i, point in enumerate(data_points[:3]):  # Show first 3
                    if 'processes' in point:
                        print(f"  Point {i+1}: {len(point['processes'])} processes monitored")
        
        success("Process monitoring completed successfully", json_mode=args.json)
        return 0
        
    except Exception as e:
        error(f"Process monitoring failed: {e}", json_mode=args.json)
        return 1


def handle_log_analysis(args) -> int:
    """Handle log analysis."""
    try:
        info("Analyzing system logs...", json_mode=args.json)
        
        # Build configuration
        config = LogAnalysisConfig()
        
        if hasattr(args, 'pattern') and args.pattern:
            config.pattern = re.compile(args.pattern, re.IGNORECASE)
            info(f"Searching for pattern: '{args.pattern}'", json_mode=args.json)
        
        if hasattr(args, 'level') and args.level:
            info(f"Filtering by log level: {args.level}", json_mode=args.json)
        
        # Run analysis
        analyzer = LogAnalyzer(config)
        entries = analyzer.query_logs()
        
        # Limit results
        limit = getattr(args, 'limit', 50)
        entries = entries[:limit]
        
        # Output results
        if args.json:
            log_data = [
                {
                    "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                    "level": e.level,
                    "process": getattr(e, 'process', None),
                    "message": e.message,
                    "file": e.file_path,
                    "line": e.line_number
                }
                for e in entries
            ]
            print(json.dumps(log_data, indent=2, default=str))
        elif not args.disable_print:
            info(f"Found {len(entries)} matching log entries", json_mode=args.json)
            
            # Display sample entries
            if not args.json:  # Only show formatted output in non-JSON mode
                for entry in entries[:10]:
                    timestamp = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S") if entry.timestamp else "Unknown"
                    level = entry.level or "INFO"
                    message = entry.message[:80] + "..." if len(entry.message) > 80 else entry.message
                    print(f"{timestamp} | {level:8} | {message}")
        
        success("Log analysis completed", json_mode=args.json)
        return 0
        
    except Exception as e:
        error(f"Log analysis failed: {e}", json_mode=args.json)
        return 1


def handle_package_analysis(args) -> int:
    """Handle package analysis."""
    try:
        info("Analyzing installed packages...", json_mode=args.json)
        
        from syinfo.analysis.packages import PackageManager, PackageManagerType
        
        pm = PackageManager()
        manager_filter = None
        
        # Handle manager filter (case-insensitive; accept enum name or value)
        if hasattr(args, 'manager') and args.manager:
            raw = str(args.manager).strip()
            parsed = None
            try:
                # Try by enum NAME (e.g., "APT", "PIP")
                parsed = PackageManagerType[raw.upper()]
            except Exception:
                try:
                    # Try by enum VALUE (e.g., "apt", "pip")
                    parsed = PackageManagerType(raw.lower())
                except Exception:
                    parsed = None
            if parsed is not None:
                manager_filter = parsed
                info(f"Filtering by package manager: {parsed.value}", json_mode=args.json)
            else:
                warning(f"Unknown package manager: {args.manager}", json_mode=args.json)
        
        # Handle name filter
        name_filter = getattr(args, 'name', "") or ""
        if name_filter:
            info(f"Filtering by package name: '{name_filter}'", json_mode=args.json)
        
        # Get packages
        packages = pm.list_packages(
            manager=manager_filter,
            name_filter=name_filter,
            as_dict=False  # Get PackageInfo objects
        )
        
        # Output results
        if args.json:
            package_data = [
                {
                    "name": p.name,
                    "version": p.version,
                    "architecture": p.architecture,
                    "description": p.description
                }
                for p in packages
            ]
            print(json.dumps(package_data, indent=2, default=str))
        elif not args.disable_print:
            info(f"Found {len(packages)} packages", json_mode=args.json)
            
            if packages and not args.json:  # Only show formatted output in non-JSON mode
                print(f"\n{'Package Name':30} {'Version':15} {'Architecture':12}")
                print("-" * 60)
                for pkg in packages[:20]:  # Show first 20
                    name = pkg.name[:29]
                    version = (pkg.version or "N/A")[:14]
                    arch = (pkg.architecture or "N/A")[:11]
                    print(f"{name:30} {version:15} {arch:12}")
        
        success("Package analysis completed", json_mode=args.json)
        return 0
        
    except Exception as e:
        error(f"Package analysis failed: {e}", json_mode=args.json)
        return 1


def handle_network_scan(args) -> int:
    """Handle network device scanning."""
    try:
        info("Scanning network for devices...", json_mode=args.json)
        if not args.json:  # Only show warning in non-JSON mode
            warning("Note: Network scanning requires sudo privileges on Linux/macOS", json_mode=args.json)
        
        from syinfo.core.search_network import search_devices_on_network
        from syinfo.constants import NEED_SUDO
        
        # Perform scan
        devices_dict = search_devices_on_network(
            time=args.time,
            seach_device_vendor_too=not getattr(args, 'disable_vendor_search', True)
        )
        
        # Handle permission issues
        if devices_dict == NEED_SUDO:
            error("Network scanning requires elevated privileges", json_mode=args.json)
            info("Try running: sudo syinfo -N", json_mode=args.json)
            return 1
        
        # Output results
        if args.json:
            print(json.dumps(devices_dict, indent=2, default=str))
        elif not args.disable_print:
            if not devices_dict:
                warning("No devices found on network", json_mode=args.json)
            else:
                success(f"Found {len(devices_dict)} devices on network", json_mode=args.json)
                
                if not args.json:  # Only show formatted output in non-JSON mode
                    print(f"\n{'IP Address':15} {'MAC Address':18} {'Vendor':30}")
                    print("-" * 65)
                    
                    for ip, device_info in devices_dict.items():
                        if isinstance(device_info, dict):
                            mac = device_info.get('mac_address', 'Unknown')
                            vendor = str(device_info.get('vendor', 'Unknown'))[:29]
                            ip_clean = ip.split()[0] if ' ' in ip else ip  # Take first IP if multiple
                            print(f"{ip_clean:15} {mac:18} {vendor:30}")
        
        success("Network scan completed", json_mode=args.json)
        return 0
        
    except Exception as e:
        error(f"Network scan failed: {e}", json_mode=args.json)
        return 1


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="\033[1m\033[94mSyInfo - System Information Collection & Analysis Tool\033[0m\n" + "─" * 100 + "\n\n\033[1mWhen to Use:\033[0m\n  \033[36mDevice Info\033[0m     → System specs, hardware inventory, compatibility checks\n  \033[94mSystem Info\033[0m     → Complete reports, documentation, initial diagnostics\n  \033[92mMonitoring\033[0m      → Performance issues, resource usage tracking, optimization\n  \033[95mAnalysis\033[0m       → Troubleshooting, security audits, maintenance tasks\n  \033[93mNetwork Scan\033[0m   → Network mapping, device discovery, security assessment\n",
        epilog=textwrap.dedent("""
────────────────────────────────────────────────────────────────────────────────────────────────────

\033[1mSample Commands:\033[0m

  \033[1m\033[96mCore Information Collection:\033[0m \033[2m(Quick system insights)\033[0m
      \033[4mBasic Commands:\033[0m
        \033[2m# Hardware specs - useful for inventory/documentation\033[0m
        $ syinfo -d --json
        \033[2m# Network config - troubleshooting connectivity\033[0m  
        $ syinfo -n -t 10
        \033[2m# Full system report - comprehensive overview\033[0m
        $ syinfo -s                           
      
      \033[4mWith jq Filtering:\033[0m
        \033[2m# Get CPU core count\033[0m
        $ syinfo -d --json | jq '.cpu_info.cores'
        \033[2m# Get memory usage\033[0m
        $ syinfo -s --json | jq '.memory_info.virtual.percent' 

  \033[1m\033[92mResource Monitoring:\033[0m \033[2m(Performance analysis)\033[0m
      \033[4mMonitoring Commands:\033[0m
        \033[2m# Track CPU/RAM/disk - performance issues\033[0m
        $ syinfo --system-monitor -t 300 -i 5
        \033[2m# Monitor specific apps - resource debugging\033[0m
        $ syinfo --process-monitor --filter python 
      
      \033[4mWith jq Filtering:\033[0m
        \033[2m# Average CPU usage\033[0m
        $ syinfo --system-monitor -t 60 --json | jq '.summary.avg_cpu'    
        \033[2m# Process details\033[0m
        $ syinfo --process-monitor --json | jq '.data_points[0].processes' 

  \033[1m\033[95mAnalysis & Investigation:\033[0m \033[2m(Troubleshooting & auditing)\033[0m
      \033[4mAnalysis Commands:\033[0m
        \033[2m# Find system errors - debugging crashes/issues\033[0m
        $ syinfo -l --pattern error              
        \033[2m# Package inventory - dependency management\033[0m
        $ syinfo -p --name python                
      
      \033[4mWith jq Filtering:\033[0m
        \033[2m# Filter error logs\033[0m
        $ syinfo -l --json | jq '.entries[] | select(.level=="ERROR")'
        \033[2m# Find Python packages\033[0m
        $ syinfo -p --json | jq '.packages[] | select(.name | test("py"))'

  \033[1m\033[93mNetwork Operations:\033[0m \033[2m(Requires sudo, works on local networks)\033[0m
      \033[4mNetwork Commands:\033[0m
        \033[2m# Device discovery - network mapping/security audit\033[0m
        $ sudo syinfo -N                       
      
      \033[4mWith jq Filtering:\033[0m
        \033[2m# Extract IP, MAC, and vendor\033[0m
        $ sudo syinfo -N --json | jq 'to_entries[] | {ip: .key, mac: .value.mac_address, vendor: .value.vendor}'
        \033[2m# Count discovered devices\033[0m
        $ sudo syinfo -N --json | jq 'keys | length'

────────────────────────────────────────────────────────────────────────────────────────────────────

\033[1mContact Information:\033[0m
    Email  : \033[4m\033[94mmohitrajput901@gmail.com\033[0m
    GitHub : \033[4m\033[94mhttps://github.com/MR901/syinfo\033[0m

────────────────────────────────────────────────────────────────────────────────────────────────────
        """)
    )
    
    # Version and contact
    parser.add_argument(
        "-v", "--version", 
        action="version", 
        version=f"syinfo {__version__}", 
        help="show version information"
    )
    parser.add_argument(
        "-c", "--contact", 
        action="store_true", 
        help="show contact information"
    )
    
    # Core Information Collection
    parser.add_argument(
        "-d", "--device", 
        action="store_true",
        help="\033[96mshow hardware/device information\033[0m"
    )
    parser.add_argument(
        "-n", "--network", 
        action="store_true",
        help="\033[96mshow network information\033[0m"
    )
    parser.add_argument(
        "-s", "--system", 
        action="store_true",
        help="\033[94mshow complete system information\033[0m"
    )
    
    # Resource Monitoring
    parser.add_argument(
        "--system-monitor", 
        action="store_true",
        help="\033[92mstart real-time system monitoring\033[0m"
    )
    parser.add_argument(
        "--process-monitor", 
        action="store_true",
        help="\033[92mstart process-specific monitoring\033[0m"
    )
    
    # Analysis & Investigation
    parser.add_argument(
        "-l", "--logs",
        action="store_true",
        help="\033[95manalyze and search system logs\033[0m"
    )
    parser.add_argument(
        "-p", "--packages",
        action="store_true",
        help="\033[95manalyze installed packages\033[0m"
    )
    
    # Network Operations
    parser.add_argument(
        "-N", "--scan-network",
        action="store_true",
        help="\033[93mscan network for devices (requires sudo)\033[0m"
    )
    
    # Time and interval options
    parser.add_argument(
        "-t", "--time", 
        type=int, 
        default=10,
        help="timeout/duration in seconds (default: 10) - use with monitoring/network ops"
    )
    parser.add_argument(
        "-i", "--interval", 
        type=int, 
        default=5,
        help="monitoring interval in seconds (default: 5) - lower = more detailed data"
    )
    
    # Log analysis options
    parser.add_argument(
        "--pattern", 
        type=str,
        help="search pattern for log analysis (regex) - use 'error|fail|crash' for issues"
    )
    parser.add_argument(
        "--level", 
        type=str,
        help="log level filter (error, warning, info, debug) - 'error' for critical issues"
    )
    parser.add_argument(
        "--limit", 
        type=int,
        default=50,
        help="maximum number of results (default: 50)"
    )
    
    # Package analysis options  
    parser.add_argument(
        "--manager", 
        type=str,
        help="package manager filter (apt, yum, pip, etc.)"
    )
    parser.add_argument(
        "--name", 
        type=str,
        help="package name filter"
    )
    
    # Process monitoring options
    parser.add_argument(
        "--filter", 
        type=str,
        help="process name filter for process monitoring - e.g. 'python', 'nginx', 'mysql'"
    )
    parser.add_argument(
        "--match-field", 
        type=str,
        choices=["name", "cmdline", "exe"],
        default="name",
        help="field to match process filter against (default: name)"
    )
    
    # Output options
    parser.add_argument(
        "--json", 
        action="store_true",
        help="output results as JSON"
    )
    parser.add_argument(
        "--disable-print", 
        action="store_true", 
        help="disable formatted output (JSON only)"
    )
    parser.add_argument(
        "--disable-vendor-search", 
        action="store_true", 
        help="disable MAC vendor lookup in network scanning (faster scan, less info)"
    )
    
    return parser


def main() -> int:
    """Main CLI entry point."""
    
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Handle contact flag
        if args.contact:
            contact(msg=True)
            return 0
            
        # Handle information collection flags (original simple structure!)
        if args.device:
            return handle_device_info(args)
            
        elif args.system:
            return handle_system_info(args)
            
        elif args.network:
            return handle_network_info(args)
                
        elif args.system_monitor:
            return handle_monitoring(args)
            
        elif args.process_monitor:
            return handle_process_monitoring(args)
            
        elif args.logs:
            return handle_log_analysis(args)
            
        elif args.packages:
            return handle_package_analysis(args)
            
        elif args.scan_network:
            return handle_network_scan(args)
                
        else:
            # No flags provided - show help
            parser.print_help()
        return 0
        
    except KeyboardInterrupt:
        print()
        print("[WARNING] Operation cancelled by user", file=sys.stderr)
        return 130
        
    except SyInfoException as e:
        print(f"[ERROR] SyInfo error: {e}", file=sys.stderr)
        return 1
        
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
