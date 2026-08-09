"""
Tests for MCP Test Server.
"""

import pytest
from mcp_test.server import MCPTestServer
from mcp_test.models import ToolCallStatus, ToolResult


def test_server_initialization() -> None:
    """Test server initialization."""
    server = MCPTestServer(name="test-server", version="1.0.0")
    assert server.name == "test-server"
    assert server.version == "1.0.0"
    assert server.server is not None


def test_server_tool_registration() -> None:
    """Test that tools are registered."""
    server = MCPTestServer()
    # The tools are registered during initialization via _register_tools
    # We can't easily test the internal _tool_calls without running the server
    assert hasattr(server, '_tool_calls')
    assert isinstance(server._tool_calls, dict)


@pytest.mark.asyncio
async def test_tool_echo() -> None:
    """Test the echo tool directly."""
    server = MCPTestServer()
    result = await server._tool_echo("test-call-1", {"message": "hello"})
    assert isinstance(result, ToolResult)
    assert result.success is True
    assert result.result == {"echo": "hello"}
    assert result.call_id == "test-call-1"


@pytest.mark.asyncio
async def test_tool_echo_missing_argument() -> None:
    """Test the echo tool with missing required argument."""
    server = MCPTestServer()
    with pytest.raises(ValueError, match="Missing required argument: 'message'"):
        await server._tool_echo("test-call-2", {})


@pytest.mark.asyncio
async def test_tool_add() -> None:
    """Test the add tool directly."""
    server = MCPTestServer()
    result = await server._tool_add("test-call-3", {"a": 5, "b": 3})
    assert isinstance(result, ToolResult)
    assert result.success is True
    assert result.result == {"sum": 8}
    assert result.call_id == "test-call-3"


@pytest.mark.asyncio
async def test_tool_add_with_floats() -> None:
    """Test the add tool with float numbers."""
    server = MCPTestServer()
    result = await server._tool_add("test-call-4", {"a": 2.5, "b": 3.1})
    assert isinstance(result, ToolResult)
    assert result.success is True
    assert result.result == {"sum": 5.6}
    assert result.call_id == "test-call-4"


@pytest.mark.asyncio
async def test_tool_add_missing_arguments() -> None:
    """Test the add tool with missing required arguments."""
    server = MCPTestServer()
    with pytest.raises(ValueError, match="Missing required argument: 'a'"):
        await server._tool_add("test-call-5", {"b": 3})
    with pytest.raises(ValueError, match="Missing required argument: 'b'"):
        await server._tool_add("test-call-6", {"a": 5})


@pytest.mark.asyncio
async def test_tool_get_server_info() -> None:
    """Test the get_server_info tool directly."""
    server = MCPTestServer(name="custom-server", version="2.0.0")
    result = await server._tool_get_server_info("test-call-7", {})
    assert isinstance(result, ToolResult)
    assert result.success is True
    assert result.result["name"] == "custom-server"
    assert result.result["version"] == "2.0.0"
    assert set(result.result["tools"]) == {"echo", "add", "get_server_info"}
    assert result.call_id == "test-call-7"


@pytest.mark.asyncio
async def test_tool_call_tracking() -> None:
    """Test that tool calls are tracked."""
    server = MCPTestServer()
    initial_count = len(server._tool_calls)

    await server._tool_echo("test-call-8", {"message": "test"})
    assert len(server._tool_calls) == initial_count + 1

    # Check the tracked call
    call_id = list(server._tool_calls.keys())[-1]
    call = server._tool_calls[call_id]
    assert call.name == "echo"
    assert call.arguments == {"message": "test"}
    assert call.status == ToolCallStatus.COMPLETED