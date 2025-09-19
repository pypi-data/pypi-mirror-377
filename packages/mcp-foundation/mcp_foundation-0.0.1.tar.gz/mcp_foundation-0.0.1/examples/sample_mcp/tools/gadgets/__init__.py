"""
Gadgets tools package.

This package contains fun, local sample tools for testing MCP functionality.
All tools work locally without external dependencies and are safe to use.
Perfect for demonstrating MCP capabilities with various clients.
"""

# Import modules to ensure MCP tools are registered
from . import math, text, system, fun

__all__ = ["math", "text", "system", "fun"]
