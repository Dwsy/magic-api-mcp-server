# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-24

### Added
- Initial release of Magic-API MCP Server
- Complete MCP (Model Context Protocol) implementation for Magic-API development
- 10 comprehensive tool modules:
  - **SystemTools**: System information and metadata
  - **DocumentationTools**: Comprehensive Magic-API documentation and knowledge base
  - **ApiTools**: Direct API calling and testing capabilities
  - **ResourceManagementTools**: Full CRUD operations for Magic-API resources
  - **QueryTools**: Efficient resource querying and retrieval
  - **DebugTools**: Advanced debugging with breakpoints and step execution
  - **SearchTools**: Content search across API scripts and TODO comments
  - **BackupTools**: Complete backup and restore functionality
  - **ClassMethodTools**: Java class and method introspection
  - **CodeGenerationTools**: Code generation templates (currently disabled)
- Docker support with production and development configurations
- Comprehensive Makefile for easy Docker operations
- Full documentation with usage examples and MCP prompts
- Support for multiple tool combinations (full, minimal, development, production, etc.)
- Command-line interface with rich argument parsing
- Environment variable configuration for all settings

### Features
- **Multi-tool Architecture**: Modular design allowing flexible tool combinations
- **Rich Documentation**: Extensive inline documentation and usage examples
- **MCP Integration**: Full Model Context Protocol compliance
- **Docker Ready**: Complete containerization with development and production setups
- **Comprehensive Testing**: Built-in health checks and connection testing
- **Developer Friendly**: Hot reload support in development mode

### Technical Details
- **Python Version**: Requires Python 3.13+
- **Key Dependencies**: FastMCP, Pydantic, Requests, WebSockets
- **Architecture**: Modular tool registry system with composable tools
- **Deployment**: Supports uvx, local Python, and Docker deployments

### Known Limitations
- CodeGenerationTools currently disabled, enable by uncommenting in __init__.py
- Requires active Magic-API service for full functionality
- WebSocket debugging features require WebSocket connection to Magic-API

---

## Development

### Building from Source
```bash
# Install uv (if not already installed)
pip install uv

# Clone and setup
git clone <repository-url>
cd magic-api-mcp-server
uv sync

# Run locally
uv run python run_mcp.py
```

### Docker Development
```bash
# Quick start development environment
make quick-start

# Production deployment
make deploy
```

---

[Unreleased]: https://github.com/yourusername/magic-api-mcp-server/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/magic-api-mcp-server/releases/tag/v0.1.0
