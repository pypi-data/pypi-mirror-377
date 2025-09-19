# mcp_foundation Examples

This directory contains examples demonstrating how to use the `mcp_foundation` library to build MCP (Model Context Protocol) servers with gadgets tools.

## Quick Start

### 1. Python Environment (One-time Setup)

If you've already followed the setup in [main README.md](../README.md), **skip this step** - examples share the same Python virtual environment:

```bash
# Only needed if you haven't set up the environment yet
conda activate mcp-dev  # Environment already configured with mcp-foundation
```

### 2. Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit configuration as needed
nano .env  # or use your preferred editor
```

### 3. Run Sample MCP Service

```bash
# Start the sample MCP server
python -m sample_mcp.main
```

## Required Python Packages

**Examples use the same virtual environment as the main project.** Once you've installed `mcp-foundation` following the main README, all dependencies are already available.

The shared environment includes:

```
...
mcp-foundation   0.0.1       /Users/jliu/Workspace/kafka/mcp-foundation
mcp              1.12.3
fastapi          0.116.1
uvicorn          0.35.0
python-dotenv    1.1.1
... 
```

> **Note:**  
> No additional installation needed - examples share the project's Python virtual environment.

## Done!