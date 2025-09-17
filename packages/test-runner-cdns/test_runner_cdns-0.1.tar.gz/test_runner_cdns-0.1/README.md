# Incremental RTL Analysis

AI-enhanced RTL analysis system with a three-stage workflow that processes specification documents and RTL repositories to generate comprehensive micro-architecture documentation via HTTP MCP server.

## Features

- **Three-Stage Workflow**: Specification processing → Change mapping → Documentation generation
- **LLM Integration**: AI-powered code analysis and documentation
- **MCP Server**: HTTP Model Context Protocol for AI assistant integration
- **Parallel Processing**: Concurrent RTL file analysis
- **HTML Reports**: Rich formatted output with structured data

## Architecture

1. **Input Processing**: Load and analyze RTL repo + specifications
2. **Change Mapping**: Map spec changes to RTL implementation
3. **Documentation**: Generate micro-architecture reports

## Quick Start

```bash
./run_http_mcp_server.sh  # Starts server on http://hostname:8899/mcp
```

## MCP Tools

- `stage1_input_processing` - Process RTL repo and spec document
- `stage2_change_mapping` - Map changes to implementation  
- `stage3_documentation_generation` - Generate documentation

## Configuration

- Config file: `~/.cadence/fesa_user_config.yml`
- JEDAI server authentication
- Virtual environment auto-activation

## Output

Reports include block overviews, signal analysis, feature mapping, dependencies, implementation impact, and integration guidelines.
