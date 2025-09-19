"""
Standard configuration module for MCP Sample Server.

Uses python-dotenv to load .env files automatically.
Follows standard Python configuration patterns with Config class.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from the examples directory (parent of sample_mcp)
dotenv_path = Path(__file__).parent.parent / '.env'
# Use override=False so environment variables take precedence over .env file
env_loaded = load_dotenv(dotenv_path, override=False)

# Print debug info about .env loading
if env_loaded:
    print(f"✅ Successfully loaded .env file from: {dotenv_path}")
else:
    print(f"⚠️  No .env file found at: {dotenv_path}, using defaults")

def get_log_directory():
    """Get the appropriate log directory based on environment."""
    # Check for explicit log directory in environment
    if log_dir := os.getenv("MCP_LOG_DIR"):
        return Path(log_dir)

    # Development mode - use project root logs
    if os.getenv("MCP_DEV_MODE", "true").lower() == "true":
        project_root = Path(__file__).parent.parent.parent
        return project_root / "logs"

    # Production mode - use system appropriate location
    if os.name == 'posix':  # Unix/Linux/macOS
        if Path.home().exists():
            # macOS: ~/Library/Logs/mcp-foundation
            # Linux: ~/.local/share/logs/mcp-foundation
            if "darwin" in os.uname().sysname.lower():
                return Path.home() / "Library" / "Logs" / "mcp-foundation"
            else:
                return Path.home() / ".local" / "share" / "logs" / "mcp-foundation"

    # Fallback to temp directory
    return Path("/tmp") / "mcp-foundation" / "logs"

class Config:
    """Configuration class that loads from environment variables."""

    # Server identification
    SERVER_NAME = os.getenv("MCP_SERVER_NAME", "Sample MCP Server")
    SERVER_VERSION = os.getenv("MCP_SERVER_VERSION", "1.0.0")
    SERVER_DESCRIPTION = os.getenv("MCP_SERVER_DESCRIPTION", "Sample MCP server")

    # Protocol settings
    PROTOCOL_VERSION = os.getenv("MCP_PROTOCOL_VERSION", "2024-11-05")
    TRANSPORT = os.getenv("MCP_TRANSPORT", "streamable-http")
    HOST = os.getenv("MCP_HOST", "127.0.0.1")
    PORT = int(os.getenv("MCP_PORT", "8000"))

    # Tool configuration
    ENABLE_KAFKA_TOOLS = os.getenv("MCP_ENABLE_KAFKA_TOOLS", "false").lower() == "true"
    ENABLE_AWS_TOOLS = os.getenv("MCP_ENABLE_AWS_TOOLS", "false").lower() == "true"
    ENABLE_HOST_TOOLS = os.getenv("MCP_ENABLE_HOST_TOOLS", "false").lower() == "true"
    ENABLE_NOTIFY_TOOLS = os.getenv("MCP_ENABLE_NOTIFY_TOOLS", "true").lower() == "true"
    ENABLE_JIRA_TOOLS = os.getenv("MCP_ENABLE_JIRA_TOOLS", "false").lower() == "true"
    ENABLE_ECHO_TOOL = os.getenv("MCP_ENABLE_ECHO_TOOL", "true").lower() == "true"
    ENABLE_GADGETS_TOOLS = os.getenv("MCP_ENABLE_GADGETS_TOOLS", "true").lower() == "true"

    # Security settings
    SECURITY_ENABLED = os.getenv("MCP_SECURITY_ENABLED", "true").lower() == "true"
    SECURITY_DEV_MODE = os.getenv("MCP_SECURITY_DEV_MODE", "true").lower() == "true"
    AUTH_REQUIRED = os.getenv("MCP_AUTH_REQUIRED", "false").lower() == "true"
    API_KEY = os.getenv("MCP_API_KEY", "test-admin-key")

    # Monitoring
    METRICS_ENABLED = os.getenv("MCP_METRICS_ENABLED", "true").lower() == "true"
    HEALTH_ENABLED = os.getenv("MCP_HEALTH_ENABLED", "true").lower() == "true"

    # Logging configuration
    LOG_LEVEL = os.getenv("MCP_LOG_LEVEL", "INFO")
    LOG_TOOL_CALLS = os.getenv("MCP_LOG_TOOL_CALLS", "false").lower() == "true"
    LOG_DIR = get_log_directory()

    # Development
    DEV_MODE = os.getenv("MCP_DEV_MODE", "true").lower() == "true"
    DEBUG = os.getenv("MCP_DEBUG", "false").lower() == "true"

    @classmethod
    def print_config(cls):
        """Print current configuration for debugging."""
        print("\n📋 Current Configuration:")
        print(f"  Server Name: {cls.SERVER_NAME}")
        print(f"  Version: {cls.SERVER_VERSION}")
        print(f"  Transport: {cls.TRANSPORT}")
        print(f"  Host:Port: {cls.HOST}:{cls.PORT}")
        print(f"  API Key: {cls.API_KEY}")
        print(f"  Log Level: {cls.LOG_LEVEL}")
        print(f"  Log Directory: {cls.LOG_DIR}")
        print(f"  Debug Mode: {cls.DEBUG}")
        print(f"  Gadgets Enabled: {cls.ENABLE_GADGETS_TOOLS}")

    @classmethod
    def ensure_log_directory(cls):
        """Ensure the log directory exists."""
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)
        return cls.LOG_DIR


# Create a global config instance for easy import
config = Config()

# Print config on import for debugging
if os.getenv("MCP_DEBUG", "false").lower() == "true":
    config.print_config()
