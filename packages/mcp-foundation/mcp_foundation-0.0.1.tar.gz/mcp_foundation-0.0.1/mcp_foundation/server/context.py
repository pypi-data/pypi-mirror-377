from fastmcp import FastMCP
from typing import Optional
import threading

class MCPContext:
    """
    Global thread-safe context for the active MCP server.
    Provides singleton-like interface to set, get, and clear the server.
    """
    _server: Optional[FastMCP] = None
    _lock = threading.Lock()

    @classmethod
    def set_server(cls, server: FastMCP, overwrite: bool = False) -> None:
        """
        Set the global MCP server instance.
        Raises an error if a server is already set unless overwrite=True.
        """
        with cls._lock:
            if cls._server is not None and not overwrite:
                raise RuntimeError("MCP server already set in MCPContext. Use overwrite=True to replace.")
            cls._server = server

    @classmethod
    def get_server(cls) -> FastMCP:
        """Retrieve the global MCP server instance."""
        with cls._lock:
            if cls._server is None:
                raise RuntimeError("No MCP server has been set in MCPContext")
            return cls._server

    @classmethod
    def clear(cls) -> None:
        """Clear the global MCP server instance."""
        with cls._lock:
            cls._server = None


def get_mcp() -> FastMCP:
    """Convenience function to get the MCP server from context."""
    return MCPContext.get_server()
