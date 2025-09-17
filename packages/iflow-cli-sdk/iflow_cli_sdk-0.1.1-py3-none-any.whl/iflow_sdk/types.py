"""Type definitions for iFlow SDK.

This module contains all type definitions used throughout the SDK,
including message types, configuration options, and protocol structures.
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

# Protocol version
PROTOCOL_VERSION = 1  # WebSocket ACP v1


# Enums
class ToolCallStatus(str, Enum):
    """Status of a tool call."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    # Legacy aliases for backward compatibility
    RUNNING = "in_progress"
    FINISHED = "completed"
    ERROR = "failed"


class ToolCallConfirmationOutcome(str, Enum):
    """Outcome of a tool call confirmation request."""

    ALLOW = "allow"
    ALWAYS_ALLOW = "alwaysAllow"
    ALWAYS_ALLOW_MCP_SERVER = "alwaysAllowMcpServer"
    ALWAYS_ALLOW_TOOL = "alwaysAllowTool"
    REJECT = "reject"


class PermissionMode(str, Enum):
    """Permission mode for tool calls."""

    AUTO = "auto"  # Automatically approve all
    MANUAL = "manual"  # Ask for each confirmation
    SELECTIVE = "selective"  # Auto-approve certain types


class StopReason(str, Enum):
    """Reason for stopping a prompt turn."""

    END_TURN = "end_turn"  # The language model finishes responding without requesting more tools
    MAX_TOKENS = "max_tokens"  # The maximum token limit is reached
    REFUSAL = "refusal"  # The Agent refuses to continue
    CANCELLED = "cancelled"  # The Client cancels the turn


# Message chunks
@dataclass
class UserMessageChunk:
    """A chunk of a user message."""

    content: Union[str, Path]

    def to_dict(self) -> Dict[str, str]:
        """Convert to protocol format."""
        if isinstance(self.content, str):
            return {"text": self.content}
        else:
            return {"path": str(self.content)}


@dataclass
class AssistantMessageChunk:
    """A chunk of an assistant message."""

    text: Optional[str] = None
    thought: Optional[str] = None

    def __post_init__(self):
        """Validate that either text or thought is provided."""
        if self.text is None and self.thought is None:
            raise ValueError("Either text or thought must be provided")
        if self.text is not None and self.thought is not None:
            raise ValueError("Only one of text or thought can be provided")


# Tool call types
@dataclass
class ToolCallConfirmation:
    """Tool call confirmation details."""

    type: Literal["edit", "execute", "mcp", "fetch", "other"]
    description: Optional[str] = None

    # Type-specific fields
    command: Optional[str] = None  # For execute
    root_command: Optional[str] = None  # For execute
    server_name: Optional[str] = None  # For mcp
    tool_name: Optional[str] = None  # For mcp
    tool_display_name: Optional[str] = None  # For mcp
    urls: Optional[List[str]] = None  # For fetch

    def to_dict(self) -> Dict[str, Any]:
        """Convert to protocol format."""
        result: Dict[str, Any] = {"type": self.type}

        if self.description:
            result["description"] = self.description

        if self.type == "execute":
            if self.command:
                result["command"] = self.command
            if self.root_command:
                result["rootCommand"] = self.root_command

        elif self.type == "mcp":
            if self.server_name:
                result["serverName"] = self.server_name
            if self.tool_name:
                result["toolName"] = self.tool_name
            if self.tool_display_name:
                result["toolDisplayName"] = self.tool_display_name

        elif self.type == "fetch":
            if self.urls:
                result["urls"] = self.urls

        return result


@dataclass
class ToolCallContent:
    """Tool call content."""

    type: Literal["markdown", "diff"]

    # Content fields
    markdown: Optional[str] = None  # For markdown
    path: Optional[str] = None  # For diff
    old_text: Optional[str] = None  # For diff
    new_text: Optional[str] = None  # For diff

    def to_dict(self) -> Dict[str, Any]:
        """Convert to protocol format."""
        if self.type == "markdown":
            return {"type": "markdown", "markdown": self.markdown or ""}
        else:  # diff
            return {
                "type": "diff",
                "path": self.path or "",
                "oldText": self.old_text,
                "newText": self.new_text or "",
            }


@dataclass
class ToolCallLocation:
    """File location for a tool call."""

    path: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to protocol format."""
        result = {"path": self.path}
        if self.line_start is not None:
            result["lineStart"] = self.line_start
        if self.line_end is not None:
            result["lineEnd"] = self.line_end
        return result


@dataclass
class Icon:
    """Icon for tool calls."""

    type: Literal["emoji", "url"]
    value: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to protocol format."""
        return {"type": self.type, "value": self.value}


# Messages
@dataclass
class Message:
    """Base class for all messages."""

    type: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {"type": self.type}


@dataclass
class UserMessage(Message):
    """User message."""

    chunks: List[UserMessageChunk]

    def __init__(self, chunks: List[UserMessageChunk]):
        super().__init__(type="user")
        self.chunks = chunks

    def to_dict(self) -> Dict[str, Any]:
        """Convert to protocol format."""
        return {"type": self.type, "chunks": [chunk.to_dict() for chunk in self.chunks]}


@dataclass
class AssistantMessage(Message):
    """Assistant message."""

    chunk: AssistantMessageChunk
    agent_id: Optional[str] = None

    def __init__(self, chunk: AssistantMessageChunk, agent_id: Optional[str] = None):
        super().__init__(type="assistant")
        self.chunk = chunk
        self.agent_id = agent_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert to protocol format."""
        result = {"type": self.type}
        if self.chunk.text is not None:
            result["text"] = self.chunk.text
        if self.chunk.thought is not None:
            result["thought"] = self.chunk.thought
        if self.agent_id is not None:
            result["agent_id"] = self.agent_id
        return result


@dataclass
class ToolCallMessage(Message):
    """Tool call message."""

    id: str
    label: str
    icon: Icon
    status: ToolCallStatus
    content: Optional[ToolCallContent] = None
    locations: Optional[List[ToolCallLocation]] = None
    confirmation: Optional[ToolCallConfirmation] = None
    agent_id: Optional[str] = None

    def __init__(
        self,
        id: str,
        label: str,
        icon: Icon,
        status: ToolCallStatus = ToolCallStatus.RUNNING,
        content: Optional[ToolCallContent] = None,
        locations: Optional[List[ToolCallLocation]] = None,
        confirmation: Optional[ToolCallConfirmation] = None,
        agent_id: Optional[str] = None,
    ):
        super().__init__(type="tool_call")
        self.id = id
        self.label = label
        self.icon = icon
        self.status = status
        self.content = content
        self.locations = locations
        self.confirmation = confirmation
        self.agent_id = agent_id


@dataclass
class PlanEntry:
    """Plan entry for task planning."""

    content: str
    priority: Literal["high", "medium", "low"]
    status: Literal["pending", "in_progress", "completed"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to protocol format."""
        return {"content": self.content, "priority": self.priority, "status": self.status}


@dataclass
class PlanMessage(Message):
    """Plan update message."""

    entries: List[PlanEntry]

    def __init__(self, entries: List[PlanEntry]):
        super().__init__(type="plan")
        self.entries = entries

    def to_dict(self) -> Dict[str, Any]:
        """Convert to protocol format."""
        return {"type": self.type, "entries": [entry.to_dict() for entry in self.entries]}


@dataclass
class TaskFinishMessage(Message):
    """Task finish notification with stop reason."""

    stop_reason: Optional[StopReason] = None

    def __init__(self, stop_reason: Optional[StopReason] = None):
        super().__init__(type="task_finish")
        self.stop_reason = stop_reason

    def to_dict(self) -> Dict[str, Any]:
        """Convert to protocol format."""
        result = {"type": self.type}
        if self.stop_reason:
            result["stop_reason"] = self.stop_reason.value
        return result


@dataclass
class ErrorMessage(Message):
    """Error message."""

    code: int
    message: str
    details: Optional[Dict[str, Any]] = None

    def __init__(self, code: int, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(type="error")
        self.code = code
        self.message = message
        self.details = details


# Configuration
@dataclass
class IFlowOptions:
    """Configuration options for iFlow SDK.

    Attributes:
        url: WebSocket URL for iFlow connection
        cwd: Working directory for CLI operations
        mcp_servers: List of MCP servers to configure
        permission_mode: How to handle tool call permissions
        auto_approve_types: Tool types to auto-approve in selective mode
        timeout: Connection and operation timeout in seconds
        log_level: Logging level
        metadata: Additional metadata to send with requests
        file_access: Enable file system access for iFlow
        file_allowed_dirs: List of directories iFlow can access
        file_read_only: If True, only allow read operations
        file_max_size: Maximum file size in bytes for read operations
        auto_start_process: Automatically start iFlow process if not running
        process_start_port: Starting port number for auto-started iFlow process
    """

    url: str = "ws://localhost:8090/acp"
    cwd: str = field(default_factory=lambda: os.getcwd())
    mcp_servers: List[Dict[str, Any]] = field(default_factory=list)
    permission_mode: PermissionMode = PermissionMode.AUTO
    auto_approve_types: List[str] = field(default_factory=lambda: ["edit", "fetch"])
    timeout: float = 30.0
    log_level: str = "INFO"
    metadata: Dict[str, Any] = field(default_factory=dict)
    file_access: bool = False  # Disabled by default for security
    file_allowed_dirs: Optional[List[str]] = None  # None = current directory only
    file_read_only: bool = False  # Allow writes by default when enabled
    file_max_size: int = 10 * 1024 * 1024  # 10MB default
    auto_start_process: bool = True  # Automatically start iFlow process
    process_start_port: int = 8090  # Starting port for iFlow process

    def for_sandbox(
        self, sandbox_url: str = "wss://sandbox.iflow.ai/acp?peer=iflow"
    ) -> "IFlowOptions":
        """Create options for sandbox mode.

        Args:
            sandbox_url: Sandbox WebSocket URL

        Returns:
            New IFlowOptions configured for sandbox
        """
        return IFlowOptions(
            url=sandbox_url,
            permission_mode=self.permission_mode,
            auto_approve_types=self.auto_approve_types.copy(),
            timeout=self.timeout,
            log_level=self.log_level,
            metadata=self.metadata.copy(),
        )
