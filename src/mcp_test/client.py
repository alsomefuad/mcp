"""
MCP Test Client implementation.

A simple MCP client that can connect to and test MCP servers.
"""

import asyncio
import json
import logging
import sys
from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import CallToolResult, ListToolsResult, TextContent, Tool

from .models import ToolResult


logger = logging.getLogger(__name__)


class MCPTestClient:
    """MCP Test Client for connecting to and testing MCP servers."""

    def __init__(self, server_command: list[str]) -> None:
        """
        Initialize the client.

        Args:
            server_command: Command to start the MCP server (e.g.,
                ["python", "-m", "mcp_test.server"])
        """
        self.server_command = server_command
        self.session: ClientSession | None = None
        self._exit_stack = AsyncExitStack()
        self._tools: list[Tool] = []

    async def connect(self) -> None:
        """Connect to the MCP server."""
        server_params = StdioServerParameters(
            command=self.server_command[0], args=self.server_command[1:]
        )

        stdio_transport = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
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

    def _extract_text_content(self, result: CallToolResult) -> str:
        """Extract text content from tool result, handling multiple content blocks."""
        if not result.content:
            return ""
        text_parts = []
        for content in result.content:
            if isinstance(content, TextContent):
                text_parts.append(content.text)
        return "".join(text_parts)

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        """Call a tool on the server."""
        if not self.session:
            raise RuntimeError("Not connected to server")

        result: CallToolResult = await self.session.call_tool(name, arguments)

        # Parse the result - handle multiple content blocks
        text_content = self._extract_text_content(result)
        if text_content:
            try:
                parsed = json.loads(text_content)
                return ToolResult(**parsed)
            except (json.JSONDecodeError, TypeError):
                return ToolResult(
                    call_id="",
                    success=False,
                    error=f"Failed to parse result: {text_content}",
                )
        return ToolResult(call_id="", success=False, error="No text content in result")

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

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        await self.close()


def _get_server_module_path() -> list[str]:
    """Get the command to run the server module."""
    return [sys.executable, "-m", "mcp_test.server"]


async def main() -> None:
    """Run a quick test of the client against the server."""
    client = MCPTestClient(_get_server_module_path())
    try:
        await client.connect()

        # List tools
        tools = await client.list_tools()
        logger.info("Available tools: %s", [t.name for t in tools])

        # Test echo
        result = await client.test_echo("Hello, MCP!")
        logger.info("Echo result: %s", result)

        # Test add
        result = await client.test_add(5, 3)
        logger.info("Add result: %s", result)

        # Get server info
        result = await client.get_server_info()
        logger.info("Server info: %s", result)

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
