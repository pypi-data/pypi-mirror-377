from typing import Optional
import logging

from fastmcp import FastMCP
from ..config.base import Settings

class MCPServer:
	"""
	MCP Server wrapper class that provides a clean API for server initialization
	and component management. This is the main entry point for the new server architecture.
	"""
	
	def __init__(self, config: Optional[Settings] = None):
		"""Initialize MCPServer with configuration - accepts Settings object from xxx-mcp."""
		self.config = config or Settings()  # Default if none provided
		self.server: Optional[FastMCP] = None
		self.components = []
		self.logger = logging.getLogger(__name__)
		
	def initialize(self) -> None:
		"""Initialize the MCP server and load components."""
		self.logger.info("Initializing MCP Server...")
		
		# Create the FastMCP server instance directly
		self.server = self._create_fastmcp_server()
		
		# Load and register components
		self._load_components()
		
		self.logger.info("✅ MCP Server initialization complete")
	
	def _create_fastmcp_server(self) -> FastMCP:
		"""Create and configure FastMCP server instance."""
		# Use the new structured config
		server_config = self.config.server
		
		server = FastMCP(
			name=server_config.name,
			version=server_config.version,
			instructions=server_config.description,
			mask_error_details=server_config.mask_error_details,
			on_duplicate_tools=server_config.on_duplicate_tools,
			on_duplicate_resources=server_config.on_duplicate_resources,
			on_duplicate_prompts=server_config.on_duplicate_prompts
		)
		
		self.logger.info(f"Created MCP server: {server_config.name} v{server_config.version}")
		return server
		
	def _load_components(self) -> None:
		"""Load and register all available components."""
		from ..components.cache.cache import CacheComponent
		from ..components.monitoring.monitoring import MonitoringComponent
		from ..components.event.event import EventComponent
		from ..components.logging.logging import LoggingComponent
		from ..components.security.security import SecurityComponent
		
		component_classes = [
			CacheComponent,
			MonitoringComponent, 
			EventComponent,
			LoggingComponent,
			SecurityComponent
		]
		
		for component_class in component_classes:
			try:
				component = component_class()
				component.register(self.server, self.config)
				self.components.append(component)
				self.logger.info(f"✅ Registered component: {component.name}")
			except Exception as e:
				self.logger.warning(f"⚠️ Failed to register component {component_class.__name__}: {e}")
				
	async def run(self, host: str = "localhost", port: int = 8000) -> None:
		"""Run the MCP server with transport from config."""
		if not self.server:
			raise RuntimeError("Server not initialized. Call initialize() first.")
		
		transport = self.config.server.transport
		host = host or self.config.server.host
		port = port or self.config.server.port
		
		self.logger.info(f"Starting MCP server with transport: {transport}")
		
		try:
			if transport == "stdio":
				await self._run_stdio_transport()
			elif transport == "streamable-http":
				await self._run_http_transport(transport, host, port)
			else:
				raise ValueError(f"Unsupported transport: {transport}")
		except KeyboardInterrupt:
			self.logger.info("Received interrupt signal")
		except Exception as e:
			self.logger.error(f"Error running MCP server: {e}")
			raise

	async def _run_stdio_transport(self) -> None:
		"""Handle STDIO transport startup."""
		self.logger.info("Starting MCP server with STDIO transport")
		if hasattr(self.server, "run_stdio_async"):
			await self.server.run_stdio_async()
		else:
			raise RuntimeError("STDIO transport not supported by FastMCP server")

	async def _run_http_transport(self, transport: str, host: str, port: int) -> None:
		"""Handle HTTP-based transport startup."""
		self.logger.info(f"Starting MCP server with {transport} transport on {host}:{port}")
		if hasattr(self.server, "run_http_async"):
			await self.server.run_http_async(host=host, port=port)
		else:
			raise RuntimeError(f"{transport} transport not supported by FastMCP server")
                
	def get_server(self) -> Optional[FastMCP]:
		"""Get the underlying FastMCP server instance."""
		return self.server
	
	def reset(self) -> None:
		"""Reset the server instance (useful for testing)."""
		self.server = None
		self.components = []


def create_mcp(config: Optional[Settings] = None) -> MCPServer:
	"""Create and initialize a new MCPServer instance."""
	server = MCPServer(config)
	server.initialize()
	return server
