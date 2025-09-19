"""
Base MCP Client implementation.

Provides abstract base class for MCP clients with common functionality
and interface definitions for different transport implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import uuid
import logging

logger = logging.getLogger(__name__)


class BaseMCPClient(ABC):
    """
    Abstract base class for MCP clients.
    
    Provides common functionality and interface definitions for
    MCP client implementations using different transport protocols.
    """
    
    def __init__(self, client_info: Dict[str, Any], capabilities: Dict[str, Any]):
        """
        Initialize the MCP client.
        
        Args:
            client_info: Information about this client
            capabilities: Client capabilities declaration
        """
        self.client_info = client_info
        self.capabilities = capabilities
        self.session_id: Optional[str] = None
        self.is_initialized = False
        
    @abstractmethod
    async def connect(self) -> Dict[str, Any]:
        """
        Establish connection to MCP server.
        
        Returns:
            Connection result dictionary
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to MCP server."""
        pass
    
    @abstractmethod
    async def initialize(self, protocol_version: str = "2024-11-05") -> Dict[str, Any]:
        """
        Initialize MCP session with server.
        
        Args:
            protocol_version: MCP protocol version to use
            
        Returns:
            Initialization response from server
        """
        pass
    
    @abstractmethod
    async def notify_initialized(self) -> None:
        """Send initialized notification to server."""
        pass
    
    @abstractmethod
    async def list_tools(self) -> Dict[str, Any]:
        """
        List available tools from server.
        
        Returns:
            Dictionary containing available tools
        """
        pass
    
    @abstractmethod
    async def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Call a tool on the server.
        
        Args:
            name: Tool name to call
            arguments: Tool arguments
            
        Returns:
            Tool execution results
        """
        pass
    
    @abstractmethod
    async def list_resources(self) -> Dict[str, Any]:
        """
        List available resources from server.
        
        Returns:
            Dictionary containing available resources
        """
        pass
    
    @abstractmethod
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """
        Read a resource from the server.
        
        Args:
            uri: Resource URI to read
            
        Returns:
            Resource content
        """
        pass
    
    @abstractmethod
    async def list_prompts(self) -> Dict[str, Any]:
        """
        List available prompts from server.
        
        Returns:
            Dictionary containing available prompts
        """
        pass
    
    @abstractmethod
    async def get_prompt(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get a prompt from the server.
        
        Args:
            name: Prompt name
            arguments: Prompt arguments
            
        Returns:
            Prompt content
        """
        pass
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        return str(uuid.uuid4())
    
    def _build_payload(self, method: str, params: Optional[Dict[str, Any]] = None, 
                      include_id: bool = True) -> Dict[str, Any]:
        """
        Build JSON-RPC payload for MCP request.
        
        Args:
            method: RPC method name
            params: Method parameters
            include_id: Whether to include request ID
            
        Returns:
            JSON-RPC payload dictionary
        """
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }
        
        if include_id:
            payload["id"] = self._generate_request_id()
            
        return payload
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on MCP connection.
        
        Returns:
            Health check results
        """
        try:
            if not self.is_initialized:
                return {"healthy": False, "error": "Not initialized"}
            
            # Try to list tools as a basic health check
            result = await self.list_tools()
            if "error" in result:
                return {"healthy": False, "error": result["error"]}
            
            return {
                "healthy": True,
                "session_id": self.session_id,
                "tool_count": len(result.get("tools", [])),
                "client_info": self.client_info
            }
        except Exception as e:
            return {"healthy": False, "error": str(e)}
