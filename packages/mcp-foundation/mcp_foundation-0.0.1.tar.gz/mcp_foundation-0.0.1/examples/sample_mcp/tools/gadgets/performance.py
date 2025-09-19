"""Performance and optimization gadgets."""

import asyncio
import time
from typing import Dict, Any
from fastmcp import Context
from mcp_foundation.server.context import get_mcp
from mcp_foundation.components.cache.cache import cached, get_cache
from ..utils.validate import validate_required_param

mcp = get_mcp()


@mcp.tool()
async def server_status(ctx: Context) -> Dict[str, Any]:
    """Get server performance and status information."""
    cache = get_cache()
    stats = await cache.get_stats()
    
    return {
        "status": "Server is running optimally",
        "memory_cache": {
            "enabled": stats["enabled"],
            "entries": stats["entries"],
            "hit_rate": f"{stats['hit_rate']}%",
            "efficiency": "High" if stats["hit_rate"] > 50 else "Normal"
        },
        "uptime": "Active",
        "performance": "Good"
    }


@mcp.tool()
@cached(ttl=30, key_prefix="math")
async def calculate_cube(ctx: Context, number: int) -> Dict[str, Any]:
    """
    Calculate the cube of a number with optimized performance.
    Repeated calls with same number return instantly.
    """
    from mcp_foundation.components.logging.logging import get_logger
    
    validate_required_param("number", number)
    
    logger = get_logger("tools.performance")
    logger.info(f"Starting cube calculation for {number}")
    
    # Simulate computational work
    await asyncio.sleep(2)
    
    result = number * number * number
    logger.debug(f"Calculated {number}³ = {result}")
    
    return {
        "input": number,
        "result": result,
        "operation": "cube",
        "formula": f"{number}³ = {result}",
        "performance": "Optimized for repeated calls"
    }


@mcp.tool()
async def store_user_preference(ctx: Context, preference_name: str, value: str, expire_hours: int = 1) -> Dict[str, Any]:
    """
    Store a user preference with automatic expiration.
    """
    validate_required_param("preference_name", preference_name)
    validate_required_param("value", value)
    
    cache = get_cache()
    ttl = expire_hours * 3600  # Convert hours to seconds
    success = await cache.set(f"user_pref:{preference_name}", value, ttl)
    
    return {
        "preference": preference_name,
        "value": value,
        "expires_in_hours": expire_hours,
        "stored": success,
        "message": f"Preference saved and will expire in {expire_hours} hour(s)"
    }


@mcp.tool()
async def get_user_preference(ctx: Context, preference_name: str) -> Dict[str, Any]:
    """
    Retrieve a stored user preference.
    """
    validate_required_param("preference_name", preference_name)
    
    cache = get_cache()
    value = await cache.get(f"user_pref:{preference_name}")
    
    return {
        "preference": preference_name,
        "value": value,
        "found": value is not None,
        "status": "Retrieved" if value is not None else "Not found or expired"
    }


@mcp.tool()
async def clear_preferences(ctx: Context) -> Dict[str, Any]:
    """Clear all stored user preferences."""
    cache = get_cache()
    count = await cache.clear()
    
    return {
        "action": "clear_preferences",
        "cleared_items": count,
        "message": f"Cleared {count} stored items"
    }
