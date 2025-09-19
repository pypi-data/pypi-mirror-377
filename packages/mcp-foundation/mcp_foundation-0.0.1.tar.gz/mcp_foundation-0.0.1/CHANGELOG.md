# Changelog

All notable changes to the MCP Foundation library will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Core library framework structure
- Client library with multiple transport options (HTTP, stdio, simple)
- Security framework with authentication, authorization, and rate limiting
- Monitoring and health check infrastructure
- Caching system with Redis support
- Event system with collectors and publishers
- Cost tracking and metrics
- Comprehensive example implementation in `examples/sample_mcp/`
- Release automation script (`release.sh`)

### Changed
- Restructured project from monolithic `kops-mcp` to library + examples
- Moved sample implementations to `examples/` directory
- Renamed package from `kops-mcp` to `mcp-foundation`

### Technical Details
- Python 3.8+ support
- FastAPI and FastMCP integration
- Async-first architecture
- Type hints throughout
- Comprehensive configuration management
- Enterprise-ready security features

## [1.0.0] - TBD

### Added
- Initial release of MCP Foundation library
- Core MCP server implementation framework
- Client library for MCP connections
- Security, monitoring, and caching infrastructure
- Complete example implementation
- Documentation and usage examples

[Unreleased]: https://git.zias.io/tools/mcp-foundation/compare/v1.0.0...HEAD
[1.0.0]: https://git.zias.io/tools/mcp-foundation/releases/tag/v1.0.0
