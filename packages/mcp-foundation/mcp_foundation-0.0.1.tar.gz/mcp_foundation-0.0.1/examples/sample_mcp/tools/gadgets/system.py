"""
System information gadgets.

Local system utilities for testing MCP functionality with safe,
read-only system operations and information gathering.
"""

import os
import sys
import platform
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from fastmcp import Context
from mcp_foundation.server.context import get_mcp
from ..utils.validate import validate_required_param

mcp = get_mcp()


@mcp.tool()
async def get_system_info(
    ctx: Context
) -> Dict[str, Any]:
    """
    Get comprehensive system information.
    
    Returns:
        Dictionary containing system details
    """
    return {
        "operating_system": {
            "name": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.architecture()[0]
        },
        "python": {
            "version": sys.version,
            "version_info": {
                "major": sys.version_info.major,
                "minor": sys.version_info.minor,
                "micro": sys.version_info.micro
            },
            "executable": sys.executable,
            "platform": sys.platform
        },
        "environment": {
            "user": os.environ.get("USER", os.environ.get("USERNAME", "unknown")),
            "home": os.environ.get("HOME", os.environ.get("USERPROFILE", "unknown")),
            "shell": os.environ.get("SHELL", "unknown"),
            "path_entries": len(os.environ.get("PATH", "").split(os.pathsep))
        },
        "current_working_directory": os.getcwd(),
        "timestamp": datetime.now().isoformat()
    }


@mcp.tool()
async def get_current_time(
    ctx: Context,
    timezone: str = "UTC",
    format: str = "iso"
) -> Dict[str, Any]:
    """
    Get current time with various formatting options.
    
    Args:
        timezone: Timezone identifier (limited to basic ones)
        format: Output format (iso, human, unix, custom)
        
    Returns:
        Dictionary containing time in various formats
    """
    validate_required_param("timezone", timezone)
    validate_required_param("format", format)
    
    now = datetime.now()
    
    # Basic timezone support (UTC offset only)
    if timezone.upper() == "UTC":
        utc_offset = 0
    elif timezone.upper() in ["EST", "EASTERN"]:
        utc_offset = -5
    elif timezone.upper() in ["PST", "PACIFIC"]:
        utc_offset = -8
    elif timezone.upper() in ["CST", "CENTRAL"]:
        utc_offset = -6
    elif timezone.upper() in ["MST", "MOUNTAIN"]:
        utc_offset = -7
    else:
        utc_offset = 0  # Default to UTC
    
    # Apply basic offset (simplified, doesn't handle DST)
    import datetime as dt
    adjusted_time = now + dt.timedelta(hours=utc_offset)
    
    formats = {
        "iso": adjusted_time.isoformat(),
        "human": adjusted_time.strftime("%A, %B %d, %Y at %I:%M:%S %p"),
        "unix": int(adjusted_time.timestamp()),
        "date_only": adjusted_time.strftime("%Y-%m-%d"),
        "time_only": adjusted_time.strftime("%H:%M:%S"),
        "custom": adjusted_time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return {
        "timezone": timezone,
        "current_time": formats.get(format, formats["iso"]),
        "all_formats": formats,
        "day_of_week": adjusted_time.strftime("%A"),
        "day_of_year": adjusted_time.timetuple().tm_yday,
        "week_number": adjusted_time.isocalendar()[1]
    }


@mcp.tool()
async def list_directory(
    ctx: Context,
    path: str = ".",
    show_hidden: bool = False,
    sort_by: str = "name"
) -> Dict[str, Any]:
    """
    List directory contents safely (read-only operation).
    
    Args:
        path: Directory path to list (defaults to current directory)
        show_hidden: Whether to show hidden files/directories
        sort_by: Sort criteria (name, size, modified, type)
        
    Returns:
        Dictionary containing directory listing and metadata
    """
    validate_required_param("path", path)
    
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            raise ValueError(f"Path does not exist: {path}")
        if not path_obj.is_dir():
            raise ValueError(f"Path is not a directory: {path}")
        
        items = []
        total_size = 0
        
        for item in path_obj.iterdir():
            # Skip hidden files if not requested
            if not show_hidden and item.name.startswith('.'):
                continue
            
            try:
                stat = item.stat()
                size = stat.st_size if item.is_file() else 0
                total_size += size
                
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": size,
                    "size_human": _format_bytes(size),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "permissions": oct(stat.st_mode)[-3:],
                    "extension": item.suffix if item.is_file() else None
                })
            except (OSError, PermissionError):
                # Skip items we can't access
                continue
        
        # Sort items
        sort_key_map = {
            "name": lambda x: x["name"].lower(),
            "size": lambda x: x["size"],
            "modified": lambda x: x["modified"],
            "type": lambda x: (x["type"], x["name"].lower())
        }
        
        if sort_by in sort_key_map:
            items.sort(key=sort_key_map[sort_by])
        
        return {
            "path": str(path_obj.absolute()),
            "items": items,
            "summary": {
                "total_items": len(items),
                "files": len([i for i in items if i["type"] == "file"]),
                "directories": len([i for i in items if i["type"] == "directory"]),
                "total_size": total_size,
                "total_size_human": _format_bytes(total_size)
            },
            "sort_by": sort_by,
            "show_hidden": show_hidden
        }
        
    except Exception as e:
        raise ValueError(f"Error listing directory: {str(e)}")


@mcp.tool()
async def check_disk_space(
    ctx: Context,
    path: str = "."
) -> Dict[str, Any]:
    """
    Check available disk space for a given path.
    
    Args:
        path: Path to check disk space for
        
    Returns:
        Dictionary containing disk space information
    """
    validate_required_param("path", path)
    
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            raise ValueError(f"Path does not exist: {path}")
        
        # Get disk usage
        total, used, free = shutil.disk_usage(path)
        
        usage_percent = (used / total) * 100 if total > 0 else 0
        
        return {
            "path": str(path_obj.absolute()),
            "disk_space": {
                "total": total,
                "used": used,
                "free": free,
                "usage_percent": round(usage_percent, 2)
            },
            "human_readable": {
                "total": _format_bytes(total),
                "used": _format_bytes(used),
                "free": _format_bytes(free)
            },
            "status": _get_disk_status(usage_percent)
        }
        
    except Exception as e:
        raise ValueError(f"Error checking disk space: {str(e)}")


@mcp.tool()
async def get_environment_vars(
    ctx: Context,
    filter_pattern: str = "",
    include_sensitive: bool = False
) -> Dict[str, Any]:
    """
    Get environment variables with optional filtering.
    
    Args:
        filter_pattern: Pattern to filter variable names (case-insensitive)
        include_sensitive: Whether to include potentially sensitive variables
        
    Returns:
        Dictionary containing environment variables
    """
    # Define sensitive variable patterns
    sensitive_patterns = [
        "password", "secret", "key", "token", "auth", "credential",
        "private", "secure", "api_key", "access_key"
    ]
    
    filtered_vars = {}
    sensitive_vars = []
    
    for key, value in os.environ.items():
        # Apply filter pattern
        if filter_pattern and filter_pattern.lower() not in key.lower():
            continue
        
        # Check if variable might be sensitive
        is_sensitive = any(pattern in key.lower() for pattern in sensitive_patterns)
        
        if is_sensitive:
            if include_sensitive:
                filtered_vars[key] = "***MASKED***"
            sensitive_vars.append(key)
        else:
            filtered_vars[key] = value
    
    return {
        "environment_variables": filtered_vars,
        "total_count": len(os.environ),
        "filtered_count": len(filtered_vars),
        "sensitive_variables_found": len(sensitive_vars),
        "sensitive_variable_names": sensitive_vars if not include_sensitive else [],
        "filter_applied": filter_pattern,
        "include_sensitive": include_sensitive
    }


def _format_bytes(bytes_value: int) -> str:
    """Convert bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def _get_disk_status(usage_percent: float) -> str:
    """Get disk usage status description."""
    if usage_percent < 70:
        return "Normal"
    elif usage_percent < 85:
        return "Moderate usage"
    elif usage_percent < 95:
        return "High usage - consider cleanup"
    else:
        return "Critical - immediate action needed"
