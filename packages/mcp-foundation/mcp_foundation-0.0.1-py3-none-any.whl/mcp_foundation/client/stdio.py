"""
STDIO MCP Client implementation.

Provides MCP client for stdio transport protocol used by Claude Desktop
direct execution mode and other stdio-based MCP integrations.
"""

import sys
import json
import asyncio
import logging
from typing import Dict, Any, Optional
from .base import BaseMCPClient

logger = logging.getLogger(__name__)


class StdioMCPClient(BaseMCPClient):
    """
    STDIO transport implementation of MCP client.
    
    Used for direct process execution scenarios like Claude Desktop's
    command-based MCP server integration.
    """
    
    def __init__(
        self,
        client_info: Optional[Dict[str, Any]] = None,
        capabilities: Optional[Dict[str, Any]] = None,
        process_handle: Optional[Any] = None
    ):
        """
        Initialize STDIO MCP client.
        
        Args:
            client_info: Client information
            capabilities: Client capabilities
            process_handle: Optional subprocess handle for external processes
        """
        # Default client info
        default_client_info = {
            "name": "KOPS MCP STDIO Client",
            "version": "1.12.3",
            "description": "STDIO MCP client for Kafka Operations Platform"
        }
        
        # STDIO-optimized capabilities
        default_capabilities = {
            "tools": {
                "listChanged": True
            },
            "resources": {
                "subscribe": False,  # Limited in stdio mode
                "listChanged": True
            },
            "prompts": {
                "listChanged": True
            }
        }
        
        super().__init__(
            client_info=client_info or default_client_info,
            capabilities=capabilities or default_capabilities
        )
        
        self.process_handle = process_handle
        self.reader = None
        self.writer = None
        
    async def connect(self) -> Dict[str, Any]:
        """
        Establish connection to MCP server via stdio.
        
        Returns:
            Connection result dictionary
        """
        try:
            if self.process_handle:
                # External process mode
                self.reader = asyncio.StreamReader()
                self.writer = self.process_handle.stdin
                
                # Create reader from subprocess stdout
                loop = asyncio.get_event_loop()
                transport, protocol = await loop.connect_read_pipe(
                    lambda: asyncio.StreamReaderProtocol(self.reader),
                    self.process_handle.stdout
                )
            else:
                # Direct stdio mode (when running as subprocess)
                self.reader = asyncio.StreamReader()
                self.writer = sys.stdout
                
                # Setup stdin reader
                loop = asyncio.get_event_loop()
                transport, protocol = await loop.connect_read_pipe(
                    lambda: asyncio.StreamReaderProtocol(self.reader),
                    sys.stdin
                )
            
            logger.info("STDIO MCP connection established")
            return {"connected": True}
            
        except Exception as e:
            logger.error(f"STDIO connection failed: {e}")
            return {"connected": False, "error": str(e)}
    
    async def disconnect(self) -> None:
        """Close stdio connection."""
        if self.writer and hasattr(self.writer, 'close'):
            self.writer.close()
            if hasattr(self.writer, 'wait_closed'):
                await self.writer.wait_closed()
        
        logger.info("STDIO MCP connection closed")
    
    async def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send JSON-RPC request via stdio.
        
        Args:
            request: JSON-RPC request dictionary
            
        Returns:
            Response dictionary
        """
        try:
            # Send request
            request_json = json.dumps(request) + '\n'
            if hasattr(self.writer, 'write'):
                self.writer.write(request_json.encode())
                await self.writer.drain()
            else:
                # Direct stdout write
                sys.stdout.write(request_json)
                sys.stdout.flush()
            
            # Read response
            response_line = await self.reader.readline()
            response_data = response_line.decode().strip()
            
            if response_data:
                return json.loads(response_data)
            else:
                return {"error": "Empty response from server"}
                
        except Exception as e:
            logger.error(f"STDIO request failed: {e}")
            return {"error": str(e)}
    
    async def initialize(self, protocol_version: str = "2024-11-05") -> Dict[str, Any]:
        """
        Initialize MCP session with server.
        
        Args:
            protocol_version: MCP protocol version
            
        Returns:
            Initialization response
        """
        request = {
            "jsonrpc": "2.0",
            "id": "init",
            "method": "initialize",
            "params": {
                "protocolVersion": protocol_version,
                "capabilities": self.capabilities,
                "clientInfo": self.client_info
            }
        }
        
        result = await self._send_request(request)
        if "error" not in result:
            self.is_initialized = True
            logger.info("STDIO MCP session initialized")
        
        return result
    
    async def notify_initialized(self) -> None:
        """Send initialized notification to server."""
        request = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        await self._send_request(request)
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools from server."""
        request = {
            "jsonrpc": "2.0",
            "id": "list_tools",
            "method": "tools/list"
        }
        
        return await self._send_request(request)
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the server."""
        request = {
            "jsonrpc": "2.0",
            "id": f"call_{name}",
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments
            }
        }
        
        return await self._send_request(request)
    
    async def list_resources(self) -> Dict[str, Any]:
        """List available resources from server."""
        request = {
            "jsonrpc": "2.0",
            "id": "list_resources",
            "method": "resources/list"
        }
        
        return await self._send_request(request)
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource from the server."""
        request = {
            "jsonrpc": "2.0",
            "id": f"read_{uri}",
            "method": "resources/read",
            "params": {"uri": uri}
        }
        
        return await self._send_request(request)
    
    async def list_prompts(self) -> Dict[str, Any]:
        """List available prompts from server."""
        request = {
            "jsonrpc": "2.0",
            "id": "list_prompts",
            "method": "prompts/list"
        }
        
        return await self._send_request(request)
    
    async def get_prompt(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get a prompt from the server."""
        request = {
            "jsonrpc": "2.0",
            "id": f"prompt_{name}",
            "method": "prompts/get",
            "params": {
                "name": name,
                "arguments": arguments or {}
            }
        }
        
        return await self._send_request(request)
