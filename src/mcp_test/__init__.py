"""
MCP Test Package

A simple Model Context Protocol (MCP) server/client implementation
for testing Hermes Agent with GitHub MCP.
"""

from .server import MCPTestServer
from .client import MCPTestClient
from .models import ToolCall, ToolResult

__version__ = "0.1.0"
__all__ = [
    "MCPTestServer",
    "MCPTestClient",
    "ToolCall",
    "ToolResult",
]