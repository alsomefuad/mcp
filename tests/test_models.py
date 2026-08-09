"""
Tests for MCP Test package.
"""

import pytest
from mcp_test.models import ToolCall, ToolCallStatus, ToolResult, ServerInfo


def test_tool_call_creation() -> None:
    """Test ToolCall model creation."""
    call = ToolCall(id="test-1", name="echo", arguments={"message": "hello"})
    assert call.id == "test-1"
    assert call.name == "echo"
    assert call.arguments == {"message": "hello"}
    assert call.status == ToolCallStatus.PENDING


def test_tool_call_status_transitions() -> None:
    """Test ToolCall status transitions."""
    call = ToolCall(id="test-2", name="add", arguments={"a": 1, "b": 2})
    assert call.status == ToolCallStatus.PENDING

    call.status = ToolCallStatus.RUNNING
    assert call.status == ToolCallStatus.RUNNING

    call.status = ToolCallStatus.COMPLETED
    assert call.status == ToolCallStatus.COMPLETED

    call.status = ToolCallStatus.FAILED
    assert call.status == ToolCallStatus.FAILED


def test_tool_result_success() -> None:
    """Test successful ToolResult."""
    result = ToolResult(call_id="test-1", success=True, result={"echo": "hello"})
    assert result.call_id == "test-1"
    assert result.success is True
    assert result.result == {"echo": "hello"}
    assert result.error is None


def test_tool_result_failure() -> None:
    """Test failed ToolResult."""
    result = ToolResult(call_id="test-2", success=False, error="Tool not found")
    assert result.call_id == "test-2"
    assert result.success is False
    assert result.result is None
    assert result.error == "Tool not found"


def test_server_info() -> None:
    """Test ServerInfo model."""
    info = ServerInfo(name="test-server", version="1.0.0", tools=["echo", "add"])
    assert info.name == "test-server"
    assert info.version == "1.0.0"
    assert info.tools == ["echo", "add"]


@pytest.mark.asyncio
async def test_mcp_models_serialization() -> None:
    """Test that models can be serialized and deserialized."""
    call = ToolCall(id="test-3", name="echo", arguments={"msg": "test"})
    call_json = call.model_dump_json()
    call_restored = ToolCall.model_validate_json(call_json)
    assert call_restored.id == call.id
    assert call_restored.name == call.name
    assert call_restored.arguments == call.arguments

    result = ToolResult(call_id="test-3", success=True, result={"data": 123})
    result_json = result.model_dump_json()
    result_restored = ToolResult.model_validate_json(result_json)
    assert result_restored.call_id == result.call_id
    assert result_restored.success == result.success
    assert result_restored.result == result.result