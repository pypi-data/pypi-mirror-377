"""Diagnostic and logging gadgets."""

from typing import Dict, Any
from fastmcp import Context
from mcp_foundation.server.context import get_mcp
from mcp_foundation.components.logging.logging import get_log_manager, get_logger
from ..utils.validate import validate_required_param

mcp = get_mcp()


@mcp.tool()
async def system_diagnostics(ctx: Context) -> Dict[str, Any]:
    """Get system diagnostics and logging information."""
    log_manager = get_log_manager()
    
    if log_manager:
        logging_stats = log_manager.get_stats()
    else:
        logging_stats = {"status": "using_default_logging"}
    
    return {
        "status": "System running normally",
        "logging": logging_stats,
        "diagnostics": {
            "components_loaded": "cache, logging, monitoring, event, security",
            "server_type": "FastMCP",
            "transport": "streamable-http"
        },
        "health": "OK"
    }


@mcp.tool()
async def log_message(ctx: Context, level: str, message: str, component: str = "user") -> Dict[str, Any]:
    """
    Log a custom message at the specified level.
    Useful for testing logging functionality.
    """
    validate_required_param("level", level)
    validate_required_param("message", message)
    
    # Get logger for the specified component
    logger = get_logger(f"sample.{component}")
    
    # Log at the specified level
    level_upper = level.upper()
    if hasattr(logger, level.lower()):
        log_func = getattr(logger, level.lower())
        log_func(f"User message: {message}")
        
        return {
            "action": "logged",
            "level": level_upper,
            "message": message,
            "component": component,
            "status": "Message logged successfully"
        }
    else:
        return {
            "error": f"Invalid log level: {level}",
            "valid_levels": ["debug", "info", "warning", "error", "critical"]
        }


@mcp.tool()
async def set_log_level(ctx: Context, level: str) -> Dict[str, Any]:
    """
    Change the logging level dynamically.
    """
    validate_required_param("level", level)
    
    log_manager = get_log_manager()
    if not log_manager:
        return {
            "error": "Log manager not initialized",
            "status": "Using default logging configuration"
        }
    
    try:
        old_level = log_manager.config.level
        log_manager.set_level(level)
        
        return {
            "action": "log_level_changed",
            "old_level": old_level,
            "new_level": level.upper(),
            "status": f"Log level changed from {old_level} to {level.upper()}"
        }
    except Exception as e:
        return {
            "error": f"Failed to change log level: {e}",
            "valid_levels": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        }


@mcp.tool()
async def test_logging_levels(ctx: Context) -> Dict[str, Any]:
    """
    Test all logging levels to demonstrate logging functionality.
    """
    logger = get_logger("sample.test")
    
    # Test each logging level
    logger.debug("This is a DEBUG message - detailed information for diagnosis")
    logger.info("This is an INFO message - general information about operation")
    logger.warning("This is a WARNING message - something unexpected happened")
    logger.error("This is an ERROR message - something failed but application continues")
    logger.critical("This is a CRITICAL message - serious error occurred")
    
    return {
        "action": "logging_test_completed",
        "message": "Test messages logged at all levels",
        "levels_tested": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        "note": "Check console output to see the formatted log messages"
    }


@mcp.tool()
async def debug_info(ctx: Context, component: str = "server") -> Dict[str, Any]:
    """
    Get detailed debug information for troubleshooting.
    """
    logger = get_logger(f"sample.debug")
    logger.info(f"Debug info requested for component: {component}")
    
    debug_data = {
        "timestamp": "2025-01-20T07:00:00Z",
        "component": component,
        "debug_info": {
            "memory_usage": "Normal",
            "response_time": "< 100ms",
            "active_connections": 1,
            "error_count": 0
        },
        "recent_activity": [
            "Server started successfully",
            "Components initialized",
            "Tools loaded and registered"
        ]
    }
    
    logger.debug(f"Debug data collected: {debug_data}")
    
    return {
        "component": component,
        "debug_data": debug_data,
        "status": "Debug information collected successfully"
    }
