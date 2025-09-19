"""
Streamable HTTP MCP Client implementation.

Dedicated client for the streamable-http transport protocol with 
optimized JSON-based communication and enhanced error handling.
"""

import requests
import logging
from typing import Dict, Any, Optional
from .base import BaseMCPClient

logger = logging.getLogger(__name__)


class StreamableHTTPMCPClient(BaseMCPClient):
    """
    Streamable HTTP transport implementation of MCP client.
    
    Optimized for JSON-based communication with enhanced error handling,
    session management, and support for all MCP features.
    """
    
    def __init__(
        self,
        base_url: str,
        client_info: Optional[Dict[str, Any]] = None,
        capabilities: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
        api_key: Optional[str] = None
    ):
        """
        Initialize Streamable HTTP MCP client.
        
        Args:
            base_url: Base URL of the MCP server
            client_info: Client information
            capabilities: Client capabilities
            timeout: Request timeout in seconds
            api_key: Optional API key for authentication
        """
        # Default client info
        default_client_info = {
            "name": "MCP Foundation Client",
            "version": "1.0.0",
            "description": "Streamable HTTP MCP client"
        }
        
        # Simple capabilities declaration 
        default_capabilities = {
            "tools": {
                "listChanged": True
            },
            "resources": {
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
        
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
            "User-Agent": f"{self.client_info['name']}/{self.client_info['version']}"
        }
        
        # Add API key if provided
        if api_key:
            self.headers["X-API-Key"] = api_key
    
    def _build_headers(self) -> Dict[str, str]:
        """Build request headers including session ID if available."""
        headers = self.headers.copy()
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        return headers
    
    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Parse response from the server (handles SSE format used by FastMCP).
        
        Args:
            response: HTTP response object
            
        Returns:
            Parsed response data
        """
        try:
            # FastMCP server responds with SSE format even for streamable-http
            content_type = response.headers.get("content-type", "")
            if "text/event-stream" in content_type:
                return self._parse_sse_response(response)
            else:
                return response.json()
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            return {"error": f"Response parsing failed: {str(e)}"}
    
    def _parse_sse_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Parse SSE response format used by FastMCP server.
        
        Args:
            response: HTTP response with SSE content
            
        Returns:
            Parsed SSE data
        """
        import json
        text = response.text.strip()
        
        # Handle SSE format: event: message\ndata: {...}
        if 'event: message' in text and 'data: ' in text:
            for line in text.splitlines():
                if line.startswith('data: '):
                    try:
                        return json.loads(line[6:])
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse SSE data line: {e}")
                        continue
        
        # Fallback to regular JSON parsing
        try:
            return response.json()
        except:
            return {"error": "Could not parse response", "raw_text": text}
    
    async def connect(self) -> Dict[str, Any]:
        """
        Establish connection to MCP server.
        
        Returns:
            Connection result
        """
        try:
            # Test connectivity with a simple request
            response = requests.get(
                f"{self.base_url}/health",
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return {"connected": True, "server_health": response.json()}
            else:
                return {"connected": False, "error": f"Server returned {response.status_code}"}
        except Exception as e:
            return {"connected": False, "error": str(e)}
    
    async def disconnect(self) -> None:
        """Close connection to MCP server."""
        self.session_id = None
        self.is_initialized = False
        logger.info("Disconnected from MCP server")
    
    async def initialize(self, protocol_version: str = "2024-11-05") -> Dict[str, Any]:
        """
        Initialize MCP session with server.
        
        Args:
            protocol_version: MCP protocol version
            
        Returns:
            Initialization response
        """
        try:
            payload = self._build_payload("initialize", {
                "protocolVersion": protocol_version,
                "capabilities": self.capabilities,
                "clientInfo": self.client_info
            })
            
            response = requests.post(
                f"{self.base_url}/mcp",
                json=payload,
                headers=self._build_headers(),
                timeout=self.timeout
            )
            
            # Extract session ID from response headers
            if response.status_code == 200:
                self.session_id = response.headers.get("mcp-session-id")
                result = self._parse_response(response)
                
                if "error" not in result:
                    logger.info(f"MCP session initialized: {self.session_id}")
                    return result
                else:
                    logger.error(f"MCP initialization failed: {result['error']}")
                    return result
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"MCP initialization request failed: {error_msg}")
                return {"error": error_msg}
                
        except Exception as e:
            logger.error(f"MCP initialization exception: {e}")
            return {"error": str(e)}
    
    async def notify_initialized(self) -> None:
        """Send initialized notification to server."""
        try:
            payload = self._build_payload("notifications/initialized", {}, include_id=False)
            
            response = requests.post(
                f"{self.base_url}/mcp",
                json=payload,
                headers=self._build_headers(),
                timeout=self.timeout
            )
            
            if response.status_code == 202:
                self.is_initialized = True
                logger.info("MCP initialized notification sent successfully")
            else:
                logger.warning(f"MCP notification failed: HTTP {response.status_code}")
                
        except Exception as e:
            logger.error(f"MCP notification exception: {e}")
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools from server."""
        return await self._make_request("tools/list")
    
    async def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Call a tool on the server."""
        return await self._make_request("tools/call", {
            "name": name,
            "arguments": arguments or {}
        })
    
    async def list_resources(self) -> Dict[str, Any]:
        """List available resources from server."""
        return await self._make_request("resources/list")
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource from the server."""
        return await self._make_request("resources/read", {"uri": uri})
    
    async def list_prompts(self) -> Dict[str, Any]:
        """List available prompts from server."""
        return await self._make_request("prompts/list")
    
    async def get_prompt(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get a prompt from the server."""
        return await self._make_request("prompts/get", {
            "name": name,
            "arguments": arguments or {}
        })
    
    async def _make_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a generic MCP request.
        
        Args:
            method: MCP method name
            params: Method parameters
            
        Returns:
            Response from server
        """
        try:
            payload = self._build_payload(method, params)
            
            response = requests.post(
                f"{self.base_url}/mcp",
                json=payload,
                headers=self._build_headers(),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return self._parse_response(response)
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    # Custom method for testing server functionality
    async def call(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Low-level method to call any custom MCP method.
        
        Args:
            method: Method name
            params: Method parameters
            
        Returns:
            Server response
        """
        return await self._make_request(method, params)
