from typing import Optional, Literal
from pydantic import BaseModel, field_validator

TransportType = Literal["streamable-http", "stdio"]

class ServerConfig(BaseModel):
    """MCP Server-specific configuration."""
    
    # Server identification
    name: str = "MCP Server"
    version: str = "1.0.0"
    description: str = "MCP Server built with mcp-foundation"
    
    # Transport settings
    transport: TransportType = "streamable-http"
    host: str = "127.0.0.1"
    port: int = 8000
    
    # Protocol settings
    protocol_version: str = "2024-11-05"
    mask_error_details: bool = False
    
    # Tool management
    on_duplicate_tools: str = "error"  # "error", "warn", "ignore"
    on_duplicate_resources: str = "error"
    on_duplicate_prompts: str = "error"
    
    @field_validator('transport')
    @classmethod
    def validate_transport(cls, v):
        valid_transports = ["streamable-http", "stdio"]
        if v not in valid_transports:
            raise ValueError(f"Invalid transport '{v}'. Must be one of: {valid_transports}")
        return v
