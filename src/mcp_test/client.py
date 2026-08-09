"""
MCP Test Client implementation.

A simple MCP client that can connect to and test MCP servers.
"""

import asyncio
import json
import logging
from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import CallToolResult, ListToolsResult, TextContent, Tool

from .models import ToolCall, ToolCallStatus, ToolResult


logger = logging.getLogger(__name__)


class MCPTestClient:
    """MCP Test Client for connecting to and testing MCP servers."""

    def __init__(self, server_command: list[str]) -> None:
        """
        Initialize the client.

        Args:
            server_command: Command to start the MCP server (e.g., ["python", "-m", "mcp_test.server"])
        """
        self.server_command = server_command
        self.session: ClientSession | None = None
        self._exit_stack = AsyncExitStack()
        self._tools: list[Tool] = []

    async def connect(self) -> None:
        """Connect to the MCP server."""
        server_params = StdioServerParameters(command=self.server_command[0], args=self.server_command[1:])

        stdio_transport = await self._exit_stack.enter_async_context(stdio_client(server_params))
        read_stream, write_stream = stdio_transport

        self.session = await self._exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )

        await self.session.initialize()
        await self._refresh_tools()
        logger.info("Connected to MCP server")

    async def _refresh_tools(self) -> None:
        """Refresh the list of available tools."""
        if not self.session:
            raise RuntimeError("Not connected to server")
        result: ListToolsResult = await self.session.list_tools()
        self._tools = result.tools
        logger.debug("Available tools: %s", [t.name for t in self._tools])

    async def list_tools(self) -> list[Tool]:
        """Get list of available tools."""
        if not self.session:
            raise RuntimeError("Not connected to server")
        await self._refresh_tools()
        return self._tools

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        """Call a tool on the server."""
        if not self.session:
            raise RuntimeError("Not connected to server")

        result: CallToolResult = await self.session.call_tool(name, arguments)

        # Parse the result
        if result.content and isinstance(result.content[0], TextContent):
            try:
                parsed = json.loads(result.content[0].text)
                return ToolResult(**parsed)
            except (json.JSONDecodeError, TypeError):
                return ToolResult(
                    call_id="",
                    success=False,
                    error=f"Failed to parse result: {result.content[0].text}",
                )
        return ToolResult(call_id="", success=False, error="No content in result")

    async def test_echo(self, message: str) -> ToolResult:
        """Test the echo tool."""
        return await self.call_tool("echo", {"message": message})

    async def test_add(self, a: float, b: float) -> ToolResult:
        """Test the add tool."""
        return await self.call_tool("add", {"a": a, "b": b})

    async def get_server_info(self) -> ToolResult:
        """Get server information."""
        return await self.call_tool("get_server_info", {})

    async def close(self) -> None:
        """Close the client connection."""
        await self._exit_stack.aclose()
        self.session = None
        logger.info("Disconnected from MCP server")

    async def __aenter__(self) -> "MCPTestClient":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()


async def main() -> None:
    """Run a quick test of the client against the server."""
    # This assumes the server is importable as a module
    client = MCPTestClient(["python", "-m", "mcp_test.server"])
    try:
        await client.connect()

        # List tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")

        # Test echo
        result = await client.test_echo("Hello, MCP!")
        print(f"Echo result: {result}")

        # Test add
        result = await client.test_add(5, 3)
        print(f"Add result: {result}")

        # Get server info
        result = await client.get_server_info()
        print(f"Server info: {result}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())