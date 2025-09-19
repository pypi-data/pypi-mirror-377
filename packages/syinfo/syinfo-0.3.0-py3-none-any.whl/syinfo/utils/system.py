"""System operations and command execution utilities."""

import os
import platform
import subprocess
import urllib.request
from pathlib import Path
from typing import Dict, Optional, Union

from syinfo.constants import UNKNOWN, NEED_SUDO
from syinfo.exceptions import SystemAccessError, ValidationError
from .common import handle_system_error
from .logger import Logger

# Get logger instance
logger = Logger.get_logger()


class Execute:
    """Execute commands on shell or make API requests with proper error handling.
    
    This class provides secure command execution and API request functionality
    with comprehensive error handling and logging.
    """

    @staticmethod
    @handle_system_error
    def on_shell(
        cmd: str, 
        line_no: Optional[int] = None,
        timeout: Optional[int] = 30,
        capture_stderr: bool = True
    ) -> str:
        """Execute a shell command with proper error handling.
        
        Args:
            cmd: Shell command to execute
            line_no: Specific line number to return (None for all output)
            timeout: Command timeout in seconds
            capture_stderr: Whether to capture stderr output
            
        Returns:
            Command output as string
            
        Raises:
            SystemAccessError: If command requires elevated privileges
            ValidationError: If command is invalid
            
        Examples:
            >>> Execute.on_shell("echo 'hello'")
            'hello'
        """
        if not cmd or not isinstance(cmd, str):
            raise ValidationError("Command must be a non-empty string", details={"field_name": "cmd"})
            
        # Security check: warn about potentially dangerous commands
        dangerous_cmds = ["rm -rf", "dd if=", "mkfs", "fdisk", ":(){:|:&};:"]
        if any(danger in cmd.lower() for danger in dangerous_cmds):
            logger.warning(f"Potentially dangerous command detected: {cmd}")
        
        result: str = UNKNOWN
        
        try:
            # Use subprocess.run for better control and security
            process_result = subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE if capture_stderr else None,
                timeout=timeout,
                text=True,
                check=False  # Don't raise exception on non-zero exit
            )
            
            if process_result.stderr and capture_stderr:
                error_msg = process_result.stderr.strip()
                if error_msg:
                    logger.warning(f"Command stderr: {error_msg}")
            
            stdout = process_result.stdout or ""
            
            if line_no is not None:
                lines = stdout.split("\n")
                if 0 <= line_no < len(lines):
                    result = lines[line_no].strip()
                else:
                    logger.warning(f"Line number {line_no} out of range for command output")
                    result = UNKNOWN
            else:
                result = stdout.strip()
                
        except subprocess.TimeoutExpired:
            raise SystemAccessError(
                f"Command timed out after {timeout} seconds: {cmd}",
                details={"timeout": timeout, "command": cmd}
            )
        except subprocess.SubprocessError as e:
            raise SystemAccessError(
                f"Failed to execute command: {cmd}",
                details={"error": str(e), "command": cmd}
            )
        except Exception as e:
            logger.error(f"Unexpected error executing command '{cmd}': {e}")
            raise
        
        # Check if sudo is needed
        if (
            platform.system() in ["Linux", "Darwin"]
            and "sudo " in cmd.lower()
            and os.getuid() != 0
            and result == UNKNOWN
        ):
            logger.info(f"Command may need elevated privileges: {cmd}")
            return NEED_SUDO
            
        return result

    @staticmethod
    def api(
        url: str, 
        line_no: Optional[int] = None,
        timeout: int = 30,
        headers: Optional[Dict[str, str]] = None
    ) -> str:
        """Make an API request with proper error handling.
        
        Args:
            url: URL to request
            line_no: Specific line number to return (None for all response)
            timeout: Request timeout in seconds
            headers: Optional HTTP headers
            
        Returns:
            API response as string
            
        Raises:
            ValidationError: If URL is invalid
            SystemAccessError: If request fails
            
        Examples:
            >>> Execute.api("https://api.github.com")
            '{"current_user_url":"https://api.github.com/user",...}'
        """
        if not url or not isinstance(url, str):
            raise ValidationError("URL must be a non-empty string", details={"field_name": "url"})
            
        if not url.startswith(("http://", "https://")):
            raise ValidationError("URL must start with http:// or https://", details={"field_name": "url"})
        
        result: str = UNKNOWN
        
        try:
            # Create request with headers
            request = urllib.request.Request(url)
            
            # Add default user agent
            request.add_header("User-Agent", "SyInfo/1.0 (+https://github.com/MR901/syinfo)")
            
            # Add custom headers if provided
            if headers:
                for key, value in headers.items():
                    request.add_header(key, value)
            
            # Make request with timeout
            with urllib.request.urlopen(request, timeout=timeout) as response:
                content = response.read().decode("utf-8")
                
                if line_no is not None:
                    lines = content.split("\n")
                    if 0 <= line_no < len(lines):
                        result = lines[line_no].strip()
                    else:
                        logger.warning(f"Line number {line_no} out of range for API response")
                        result = UNKNOWN
                else:
                    result = content.strip()
                    
        except urllib.error.HTTPError as e:
            raise SystemAccessError(
                f"HTTP error {e.code} requesting {url}: {e.reason}",
                details={"status_code": e.code, "url": url}
            )
        except urllib.error.URLError as e:
            raise SystemAccessError(
                f"URL error requesting {url}: {e.reason}",
                details={"url": url, "reason": str(e.reason)}
            )
        except Exception as e:
            logger.error(f"Unexpected error requesting {url}: {e}")
            raise SystemAccessError(
                f"Failed to request {url}: {str(e)}",
                details={"url": url, "error": str(e)}
            )
        
        return result


def safe_file_read(file_path: Union[str, Path], encoding: str = "utf-8") -> str:
    """Safely read a file with proper error handling.
    
    Args:
        file_path: Path to the file
        encoding: File encoding
        
    Returns:
        File contents as string
        
    Raises:
        SystemAccessError: If file cannot be read
    """
    path = Path(file_path)
    
    if not path.exists():
        raise SystemAccessError(
            f"File not found: {path}",
            resource_path=str(path)
        )
    
    if not path.is_file():
        raise SystemAccessError(
            f"Path is not a file: {path}",
            resource_path=str(path)
        )
    
    try:
        return path.read_text(encoding=encoding)
    except PermissionError:
        raise SystemAccessError(
            f"Permission denied reading file: {path}",
            required_privilege="read",
            resource_path=str(path)
        )
    except UnicodeDecodeError as e:
        raise SystemAccessError(
            f"Cannot decode file {path} with encoding {encoding}: {e}",
            resource_path=str(path)
        )


__all__ = ["Execute", "safe_file_read"]
