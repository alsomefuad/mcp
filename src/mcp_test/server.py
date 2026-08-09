"""
MCP Test Server implementation.

A simple MCP server that exposes tools for testing.
"""

import asyncio
import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    TextContent,
    Tool,
)

from .models import ServerInfo, ToolCall, ToolCallStatus, ToolResult


logger = logging.getLogger(__name__)


class MCPTestServer:
    """MCP Test Server that provides sample tools."""

    def __init__(self, name: str = "mcp-test-server", version: str = "0.1.0") -> None:
        self.name = name
        self.version = version
        self.server = Server(name)
        self._tool_calls: dict[str, ToolCall] = {}
        self._register_tools()

    def _register_tools(self) -> None:
        """Register available tools with the MCP server."""

        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List all available tools."""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="echo",
                        description="Echo back the input message",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "message": {"type": "string", "description": "Message to echo"}
                            },
                            "required": ["message"],
                        },
                    ),
                    Tool(
                        name="add",
                        description="Add two numbers together",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "a": {"type": "number", "description": "First number"},
                                "b": {"type": "number", "description": "Second number"},
                            },
                            "required": ["a", "b"],
                        },
                    ),
                    Tool(
                        name="get_server_info",
                        description="Get information about this server",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                        },
                    ),
                ]
            )

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
            """Handle tool calls."""
            call_id = f"{name}-{len(self._tool_calls) + 1}"
            tool_call = ToolCall(id=call_id, name=name, arguments=arguments)
            self._tool_calls[call_id] = tool_call
            tool_call.status = ToolCallStatus.RUNNING

            try:
                if name == "echo":
                    result = await self._tool_echo(arguments)
                elif name == "add":
                    result = await self._tool_add(arguments)
                elif name == "get_server_info":
                    result = await self._tool_get_server_info(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")

                tool_call.status = ToolCallStatus.COMPLETED
                return CallToolResult(content=[TextContent(type="text", text=json.dumps(result.model_dump()))])

            except Exception as e:
                logger.exception("Tool call failed")
                tool_call.status = ToolCallStatus.FAILED
                error_result = ToolResult(call_id=call_id, success=False, error=str(e))
                return CallToolResult(content=[TextContent(type="text", text=json.dumps(error_result.model_dump()))])

    async def _tool_echo(self, arguments: dict[str, Any]) -> ToolResult:
        """Echo tool implementation."""
        message = arguments.get("message", "")
        return ToolResult(call_id="", success=True, result={"echo": message})

    async def _tool_add(self, arguments: dict[str, Any]) -> ToolResult:
        """Add tool implementation."""
        a = arguments.get("a", 0)
        b = arguments.get("b", 0)
        return ToolResult(call_id="", success=True, result={"sum": a + b})

    async def _tool_get_server_info(self, arguments: dict[str, Any]) -> ToolResult:
        """Get server info tool implementation."""
        info = ServerInfo(
            name=self.name,
            version=self.version,
            tools=["echo", "add", "get_server_info"],
        )
        return ToolResult(call_id="", success=True, result=info.model_dump())

    async def run(self) -> None:
        """Run the MCP server over stdio."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, self.server.create_initialization_options())


async def main() -> None:
    """Entry point for the MCP server."""
    server = MCPTestServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())