# MCP Test Project

A simple Model Context Protocol (MCP) server/client implementation for testing Hermes Agent with GitHub MCP.

## Overview

This project demonstrates a basic MCP (Model Context Protocol) implementation with:

- **MCP Server** (`src/mcp_test/server.py`) - Exposes tools via stdio transport
- **MCP Client** (`src/mcp_test/client.py`) - Connects to and tests MCP servers
- **Data Models** (`src/mcp_test/models.py`) - Pydantic models for tool calls and results
- **Tests** (`tests/`) - Unit tests for models and server functionality

## Project Structure

```
mcp/
├── pyproject.toml          # Project configuration (dependencies, build, tools)
├── Makefile                # Development commands
├── .gitignore              # Git ignore rules
├── README.md               # This file
├── src/
│   └── mcp_test/
│       ├── __init__.py     # Package exports
│       ├── models.py       # Pydantic data models
│       ├── server.py       # MCP server implementation
│       └── client.py       # MCP client implementation
└── tests/
    ├── __init__.py         # Test package
    ├── test_models.py      # Tests for data models
    └── test_server.py      # Tests for server functionality
```

## Requirements

- Python 3.10+
- Dependencies listed in `pyproject.toml`

## Installation

```bash
# Install in development mode with dev dependencies
make install

# Or manually:
pip install -e ".[dev]"
```

## Running the Server

```bash
# Using make
make run-server

# Or directly
python -m mcp_test.server
```

The server runs over stdio and exposes these tools:
- `echo` - Echo back a message
- `add` - Add two numbers
- `get_server_info` - Get server metadata

## Running the Client

```bash
# Using make
make run-client

# Or directly
python -m mcp_test.client
```

The client will connect to the server (started as a subprocess) and run test calls.

## Running Tests

```bash
# Run all tests with coverage
make test

# Or directly
pytest -v
```

## Code Quality

```bash
# Run linting
make lint

# Format code
make format

# Type checking
make typecheck

# All checks
make check
```

## Development

### Adding a New Tool

1. Add the tool definition in `server.py` in the `list_tools()` handler
2. Add the implementation method (e.g., `_tool_your_tool`)
3. Add the tool call handler in `call_tool()`
4. Add a convenience method in `client.py` if needed
5. Write tests in `tests/test_server.py`

### Running a Single Test

```bash
pytest tests/test_models.py::test_tool_call_creation -v
```

## License

MIT License - see LICENSE file for details.

## Related

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Hermes Agent](https://hermes-agent.nousresearch.com/)