"""
Data models for MCP Test.

Defines the core data structures used for tool calls and results.
"""

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class ToolCallStatus(str, Enum):
    """Status of a tool call."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ToolCall(BaseModel):
    """Represents a tool call request."""
    id: str = Field(..., description="Unique identifier for the tool call")
    name: str = Field(..., description="Name of the tool to call")
    arguments: dict[str, Any] = Field(default_factory=dict, description="Arguments to pass to the tool")
    status: ToolCallStatus = Field(default=ToolCallStatus.PENDING, description="Current status of the tool call")


class ToolResult(BaseModel):
    """Represents the result of a tool call."""
    call_id: str = Field(..., description="ID of the tool call this result belongs to")
    success: bool = Field(..., description="Whether the tool call succeeded")
    result: Any | None = Field(default=None, description="Result data from the tool")
    error: str | None = Field(default=None, description="Error message if the call failed")


class ServerInfo(BaseModel):
    """Information about the MCP server."""
    name: str = Field(..., description="Server name")
    version: str = Field(..., description="Server version")
    tools: list[str] = Field(default_factory=list, description="List of available tool names")