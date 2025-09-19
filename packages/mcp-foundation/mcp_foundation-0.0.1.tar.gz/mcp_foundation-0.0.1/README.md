# MCP Foundation

A **standard library** for building [Model Context Protocol (MCP)](https://modelcontextprotocol.io/docs/getting-started/intro) servers with support for multiple transport protocols. MCP Foundation simplifies MCP server development by providing a unified framework with built-in transport support, configuration management, and production-ready features.

## 🎯 Why MCP Foundation?

Building MCP servers from scratch is complex. MCP Foundation provides:

- ✅ **Multiple Transport Support**: STDIO, SSE, and Streamable-HTTP protocols
- ✅ **Unified Configuration**: Simple `.env` based configuration  
- ✅ **Production Ready**: Built-in security, monitoring, and logging
- ✅ **Developer Friendly**: Focus on your tools, not transport protocols
- ✅ **Reference Implementation**: Complete sample with gadgets tools

## 📦 Supported Transport Protocols

MCP Foundation supports all major MCP transport protocols:

| Transport            | Use Case                        | Client Support                                 |
|----------------------|---------------------------------|------------------------------------------------|
| 🖥️ **STDIO**         | Claude Desktop direct execution | Claude Desktop, CLI tools                      |
| 🌐 **Streamable-HTTP** | Modern web clients              | Cursor, web apps, <br>LangChain, LangGraph      |
| 🔄 **SSE**           | Legacy streaming clients        | Older MCP clients                              |

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create conda environment
conda create -n mcp-dev python=3.12
conda activate mcp-dev

# Install mcp-foundation in development mode with all dependencies 
# (REQUIRED - run from project root, not examples/)
# This automatically reads pyproject.toml - no separate installation needed
pip install -e ".[dev]"
```

## 🛠️ Building Your MCP Service

To build your own MCP service using mcp-foundation:

1. **Create your tools**:  
   Define your MCP tools using the `@mcp.tool()` decorator.

   ```python
   from mcp_foundation.server.mcp_server import get_mcp

   mcp = get_mcp()

   @mcp.tool()
   async def my_custom_tool(ctx, input: str) -> str:
       """Your custom MCP tool implementation."""
       return f"Processed: {input}"
   ```

2. **Register tools automatically**:  
   Tools are registered when decorated with `@mcp.tool()`.

3. **Configure transport and server settings**:  
   Set options like `MCP_TRANSPORT`, `MCP_HOST`, and `MCP_PORT` in your `.env` file.

For a complete example and more details, see [examples/README.md](examples/README.md).

## 📚 Examples & Reference

- **Complete Sample**: See `examples/sample_mcp/` for a full implementation
- **Gadgets Tools**: Reference implementation in `examples/sample_mcp/tools/gadgets/`
- **Configuration**: Environment-based config in `examples/.env.example`
- **Tests**: Transport validation in `examples/test/`

## 🎯 Benefits

**Before MCP Foundation:**
```python
# Manual transport handling
# Complex protocol implementation  
# Custom configuration management
# No built-in security/monitoring
```

**With MCP Foundation:**
```python
# Get MCP instance and decorate your tools
mcp = get_mcp()

@mcp.tool()
async def my_tool(ctx, input):
    return process(input)

# Everything else handled automatically
```

The foundation handles transport protocols, configuration, security, monitoring, and deployment - so you can focus on building great tools.
