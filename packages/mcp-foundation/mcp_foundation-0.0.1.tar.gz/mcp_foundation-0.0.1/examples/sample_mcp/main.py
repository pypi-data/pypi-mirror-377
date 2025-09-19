#!/usr/bin/env python3
"""Sample MCP Server - Reference Implementation"""

import asyncio
from pathlib import Path
from typing import Optional

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from mcp_foundation.config.base import Settings
from mcp_foundation.config.server import ServerConfig
from mcp_foundation.server.mcp_server import create_mcp
from mcp_foundation.server.context import MCPContext
from mcp_foundation.components.logging.logging import get_logger

# Import config from current directory
try:
    from .config import Config
except ImportError:
    from config import Config


class SampleMCPServer:
    def __init__(self, config_path: Optional[Path] = None, transport: str = "streamable-http"):
        self.config_path = config_path
        
        # Create Settings using the new structured config
        server_config = ServerConfig(
            name=Config.SERVER_NAME,
            version=Config.SERVER_VERSION,
            description=Config.SERVER_DESCRIPTION,
            transport=transport,  # Use the provided transport
            host=Config.HOST,
            port=Config.PORT
        )
        
        self.settings = Settings(server=server_config)
        self.server_component = create_mcp(self.settings)
        self.logger = get_logger("sample.server")
        self.logger.info(f"Sample MCP Server initialized with transport: {transport}")
        self.server = self.server_component.get_server()
        
        # Set the server in global context for tools to access
        MCPContext.set_server(self.server)

    async def _load_sample_tools(self) -> None:
        # Tool loading is controlled by application config, not server config
        if not Config.ENABLE_GADGETS_TOOLS:
            self.logger.info("Gadgets tools disabled in application config")
            return
            
        try:
            from tools.gadgets import math, text, fun, system, performance, diagnostics
            self.logger.info("✅ Loaded gadgets tools modules - tools auto-registered via @mcp.tool() decorator")
        except ImportError as e:
            self.logger.warning(f"Could not load gadgets tools: {e}")
        except Exception as e:
            self.logger.error(f"Error loading gadgets tools: {e}")
            raise

    async def start(self, host: str = "localhost", port: int = 8000) -> None:
        self.logger.info(f"Starting Sample MCP Server on {host}:{port}")
        await self._load_sample_tools()
        
        # Much simpler - MCPServer handles transport logic automatically
        await self.server_component.run(host=host, port=port)

    async def stop(self) -> None:
        self.logger.info("Sample MCP Server stopped")
        # Clear the context when stopping
        MCPContext.clear()


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Sample MCP Server - Reference Implementation"
    )
    parser.add_argument(
        "--host", 
        default="localhost", 
        help="Host to bind to (default: localhost)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--config", 
        type=Path,
        help="Path to configuration file"
    )
    parser.add_argument(
        "--transport",
        choices=["streamable-http", "stdio", "sse"],
        default="streamable-http",
        help="Transport type to use (default: streamable-http)"
    )
    
    args = parser.parse_args()
    server = SampleMCPServer(config_path=args.config, transport=args.transport)
    logger = get_logger("sample.main")
    
    try:
        await server.start(host=args.host, port=args.port)
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())
