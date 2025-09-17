"""iFlow SDK Client for interacting with iFlow.

This module provides the main client class for communicating with iFlow
using the ACP (Agent Communication Protocol).
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional, Union

from ._errors import ConnectionError, ProtocolError
from ._internal.protocol import ACPProtocol
from ._internal.transport import WebSocketTransport
from ._internal.file_handler import FileSystemHandler
from ._internal.process_manager import IFlowProcessManager, IFlowNotInstalledError
from .types import (
    AssistantMessage,
    AssistantMessageChunk,
    ErrorMessage,
    IFlowOptions,
    Message,
    PermissionMode,
    TaskFinishMessage,
    ToolCallConfirmationOutcome,
    ToolCallMessage,
    ToolCallStatus,
    UserMessage,
    UserMessageChunk,
)

logger = logging.getLogger(__name__)


class IFlowClient:
    """Client for bidirectional, interactive conversations with iFlow.

    This client provides full control over the conversation flow with support
    for streaming, interrupts, and dynamic message sending. It implements the
    ACP protocol v0.0.9 for communication with iFlow.

    Key features:
    - **Bidirectional**: Send and receive messages at any time
    - **Stateful**: Maintains conversation context across messages
    - **Interactive**: Send follow-ups based on responses
    - **Tool calls**: Automatic or manual confirmation of tool usage
    - **Streaming**: Real-time streaming of assistant responses
    - **Control flow**: Support for interrupts and session management

    When to use IFlowClient:
    - Building chat interfaces or conversational UIs
    - Interactive debugging or exploration sessions
    - Multi-turn conversations with context
    - When you need to react to iFlow's responses
    - Real-time applications with user input
    - When you need interrupt capabilities

    When to use query() instead:
    - Simple one-off questions
    - Batch processing of prompts
    - Fire-and-forget automation scripts
    - When all inputs are known upfront
    - Stateless operations

    Example - Basic conversation:
        ```python
        async with IFlowClient() as client:
            # Send a message
            await client.send_message("What is 2 + 2?")

            # Receive response
            async for message in client.receive_messages():
                if isinstance(message, AssistantMessage):
                    print(message.chunk.text)
                elif isinstance(message, TaskFinishMessage):
                    break
        ```

    Example - With tool call handling:
        ```python
        options = IFlowOptions(permission_mode=PermissionMode.MANUAL)
        async with IFlowClient(options) as client:
            await client.send_message("Create a Python file")

            async for message in client.receive_messages():
                if isinstance(message, ToolCallMessage):
                    if message.confirmation:
                        # Manual confirmation required
                        approved = await ask_user_confirmation(message)
                        if approved:
                            await client.approve_tool_call(message.id)
                        else:
                            await client.reject_tool_call(message.id)
        ```

    Example - Sandbox mode:
        ```python
        options = IFlowOptions().for_sandbox()
        async with IFlowClient(options) as client:
            await client.send_message("Hello from sandbox!")
            # ...
        ```
    """

    def __init__(self, options: Optional[IFlowOptions] = None):
        """Initialize iFlow client.

        Args:
            options: Configuration options. If None, uses defaults.
        """
        self.options = options or IFlowOptions()
        self._transport: Optional[WebSocketTransport] = None
        self._protocol: Optional[ACPProtocol] = None
        self._connected = False
        self._authenticated = False
        self._message_task: Optional[asyncio.Task] = None
        self._message_queue: asyncio.Queue[Message] = asyncio.Queue()
        self._pending_tool_calls: Dict[str, ToolCallMessage] = {}
        self._pending_requests: Dict[int, asyncio.Future] = {}
        self._session_id: Optional[str] = None
        self._process_manager: Optional[IFlowProcessManager] = None
        self._process_started = False

        # Configure logging
        logging.basicConfig(level=self.options.log_level)

    async def connect(self) -> None:
        """Connect to iFlow and initialize the protocol.

        Performs the following steps:
        1. Establishes WebSocket connection
        2. Initializes ACP protocol
        3. Performs authentication if needed
        4. Starts message handler

        Raises:
            ConnectionError: If connection fails
            ProtocolError: If protocol initialization fails
        """
        if self._connected:
            logger.warning("Already connected")
            return

        try:
            # Check if we need to start iFlow process
            if self.options.auto_start_process:
                # Check if URL is the default localhost URL
                if self.options.url.startswith("ws://localhost:") or self.options.url.startswith("ws://127.0.0.1:"):
                    # Try to connect first to see if iFlow is already running
                    test_transport = WebSocketTransport(self.options.url, timeout=2.0)
                    try:
                        await test_transport.connect()
                        await test_transport.close()
                        logger.info("iFlow already running at %s", self.options.url)
                    except Exception:
                        # iFlow not running, start it
                        logger.info("iFlow not running, starting process...")
                        self._process_manager = IFlowProcessManager(self.options.process_start_port)
                        try:
                            iflow_url = await self._process_manager.start()
                            self.options.url = iflow_url  # Update URL to the actual port
                            self._process_started = True
                            logger.info("Started iFlow process at %s", iflow_url)
                            # Wait a bit for the process to be ready
                            await asyncio.sleep(1.0)
                        except IFlowNotInstalledError as e:
                            logger.error("iFlow not installed")
                            raise ConnectionError(str(e)) from e
                        except Exception as e:
                            logger.error("Failed to start iFlow process: %s", e)
                            raise ConnectionError(f"Failed to start iFlow process: {e}") from e
            
            # Create file handler if file access is enabled
            file_handler = None
            if self.options.file_access:
                file_handler = FileSystemHandler(
                    allowed_dirs=self.options.file_allowed_dirs,
                    read_only=self.options.file_read_only,
                    max_file_size=self.options.file_max_size
                )
                logger.info("File system access enabled with %s mode",
                           "read-only" if self.options.file_read_only else "read-write")
            
            # Create transport and protocol
            self._transport = WebSocketTransport(self.options.url, self.options.timeout)
            self._protocol = ACPProtocol(self._transport, file_handler, self.options.permission_mode)

            # Connect transport
            await self._transport.connect()

            # Initialize protocol
            init_result = await self._protocol.initialize()
            self._authenticated = init_result.get("isAuthenticated", False)

            # Authenticate if needed
            if not self._authenticated:
                await self._protocol.authenticate("iflow")  # Use iflow method by default
                self._authenticated = True

            # Create a new session with working directory and MCP servers
            self._session_id = await self._protocol.create_session(
                self.options.cwd, self.options.mcp_servers
            )
            logger.info("Created session: %s", self._session_id)

            # Start message handler
            self._message_task = asyncio.create_task(self._handle_messages())

            self._connected = True
            logger.info("Connected to iFlow")

        except Exception as e:
            await self._cleanup()
            raise ConnectionError(f"Failed to connect: {e}") from e

    async def load_session(self, session_id: str) -> None:
        """Load an existing session by ID.

        This method attempts to load a previously created session. Note that
        this functionality is not yet supported by iFlow (loadSession capability
        is false), so this will likely fail with current iFlow versions.

        Args:
            session_id: The session ID to load

        Raises:
            ConnectionError: If not connected
            ProtocolError: If session loading fails or is not supported
            
        Example:
            ```python
            async with IFlowClient() as client:
                try:
                    # Try to load a previous session
                    await client.load_session("session_123")
                except ProtocolError as e:
                    # Fallback to creating a new session
                    print(f"Could not load session: {e}")
            ```
        """
        if not self._connected or not self._protocol:
            raise ConnectionError("Not connected. Call connect() first.")

        try:
            await self._protocol.load_session(
                session_id, self.options.cwd, self.options.mcp_servers
            )
            self._session_id = session_id
            logger.info("Loaded session: %s", session_id)
        except ProtocolError as e:
            if "not supported" in str(e):
                logger.warning(
                    "session/load is not supported by current iFlow version. "
                    "Creating new session instead."
                )
                # Could optionally fallback to create_session here
                raise
            else:
                raise

    async def disconnect(self) -> None:
        """Disconnect from iFlow gracefully."""
        await self._cleanup()

    async def _cleanup(self) -> None:
        """Clean up resources."""
        self._connected = False

        # Cancel message handler
        if self._message_task:
            self._message_task.cancel()
            try:
                await self._message_task
            except asyncio.CancelledError:
                pass

        # Close transport
        if self._transport:
            await self._transport.close()

        # Stop iFlow process if we started it
        if self._process_manager and self._process_started:
            logger.info("Stopping iFlow process...")
            await self._process_manager.stop()
            self._process_manager = None
            self._process_started = False

        self._transport = None
        self._protocol = None
        logger.info("Disconnected from iFlow")

    async def send_message(self, text: str, files: Optional[List[Union[str, Path]]] = None) -> None:
        """Send a message to iFlow.

        Args:
            text: Message text
            files: Optional list of file paths to include

        Raises:
            ConnectionError: If not connected
            ProtocolError: If send fails
        """
        if not self._connected or not self._protocol or not self._session_id:
            raise ConnectionError("Not connected. Call connect() first.")

        # Create prompt content blocks for new protocol
        prompt = [{"type": "text", "text": text}]
        if files:
            for file in files:
                file_path = Path(file)
                
                # Check if file exists
                if not file_path.exists():
                    logger.warning("File not found, skipping: %s", file_path)
                    continue
                
                # Determine content type based on file extension
                suffix = file_path.suffix.lower()
                
                # Image files - use 'image' type with base64 data
                if suffix in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg']:
                    # For images, we need to read and encode as base64
                    # Note: iFlow expects 'data' field with base64 content and 'mimeType'
                    try:
                        import base64
                        with open(file_path, 'rb') as f:
                            image_data = base64.b64encode(f.read()).decode('utf-8')
                        
                        mime_type = {
                            '.png': 'image/png',
                            '.jpg': 'image/jpeg',
                            '.jpeg': 'image/jpeg',
                            '.gif': 'image/gif',
                            '.bmp': 'image/bmp',
                            '.webp': 'image/webp',
                            '.svg': 'image/svg+xml',
                        }.get(suffix, 'image/unknown')
                        
                        prompt.append({
                            "type": "image",
                            "data": image_data,
                            "mimeType": mime_type
                        })
                        logger.debug("Added image file: %s", file_path.name)
                    except Exception as e:
                        logger.error("Failed to read image file %s: %s", file_path, e)
                        continue
                
                # Audio files - use 'audio' type with base64 data
                elif suffix in ['.mp3', '.wav', '.m4a', '.ogg', '.flac']:
                    # For audio, we need to read and encode as base64
                    try:
                        import base64
                        with open(file_path, 'rb') as f:
                            audio_data = base64.b64encode(f.read()).decode('utf-8')
                        
                        mime_type = {
                            '.mp3': 'audio/mpeg',
                            '.wav': 'audio/wav',
                            '.m4a': 'audio/mp4',
                            '.ogg': 'audio/ogg',
                            '.flac': 'audio/flac',
                        }.get(suffix, 'audio/unknown')
                        
                        prompt.append({
                            "type": "audio",
                            "data": audio_data,
                            "mimeType": mime_type
                        })
                        logger.debug("Added audio file: %s", file_path.name)
                    except Exception as e:
                        logger.error("Failed to read audio file %s: %s", file_path, e)
                        continue
                
                # All other files - use 'resource_link' type
                else:
                    # For other files, use resource_link which references by URI
                    prompt.append({
                        "type": "resource_link",
                        "uri": file_path.absolute().as_uri(),
                        "name": file_path.name,
                        "title": file_path.stem,
                        "size": file_path.stat().st_size if file_path.exists() else None
                    })
                    logger.debug("Added resource link: %s", file_path.name)

        # Send prompt to session
        await self._protocol.send_prompt(self._session_id, prompt)
        logger.info("Sent prompt with %d content blocks", len(prompt))

    async def interrupt(self) -> None:
        """Interrupt the current message generation.

        Raises:
            ConnectionError: If not connected
        """
        if not self._connected or not self._protocol or not self._session_id:
            raise ConnectionError("Not connected")

        await self._protocol.cancel_session(self._session_id)
        logger.info("Sent interrupt signal")

    async def receive_messages(self) -> AsyncIterator[Message]:
        """Receive messages from iFlow.

        Yields:
            Messages from iFlow (AssistantMessage, ToolCallMessage, etc.)

        Raises:
            ConnectionError: If not connected
        """
        if not self._connected:
            raise ConnectionError("Not connected")

        while self._connected:
            try:
                message = await asyncio.wait_for(self._message_queue.get(), timeout=0.1)
                yield message
            except asyncio.TimeoutError:
                continue

    async def approve_tool_call(
        self, tool_id: str, outcome: ToolCallConfirmationOutcome = ToolCallConfirmationOutcome.ALLOW
    ) -> None:
        """Approve a tool call that requires confirmation.

        Args:
            tool_id: ID of the tool call to approve
            outcome: Approval outcome (allow, alwaysAllow, etc.)

        Raises:
            ValueError: If tool call not found
        """
        if tool_id not in self._pending_tool_calls:
            raise ValueError(f"Unknown tool call: {tool_id}")

        # In the current implementation, tool calls are auto-approved
        # This method is for future manual confirmation support
        logger.info("Approved tool call %s with outcome %s", tool_id, outcome)
        del self._pending_tool_calls[tool_id]

    async def reject_tool_call(self, tool_id: str) -> None:
        """Reject a tool call that requires confirmation.

        Args:
            tool_id: ID of the tool call to reject

        Raises:
            ValueError: If tool call not found
        """
        if tool_id not in self._pending_tool_calls:
            raise ValueError(f"Unknown tool call: {tool_id}")

        # In the current implementation, tool calls are auto-approved
        # This method is for future manual confirmation support
        logger.info("Rejected tool call %s", tool_id)
        del self._pending_tool_calls[tool_id]

    async def _handle_messages(self) -> None:
        """Background task to handle incoming messages."""
        if not self._protocol:
            return

        try:
            async for message_data in self._protocol.handle_messages():
                message = self._process_message(message_data)
                if message:
                    await self._message_queue.put(message)

        except asyncio.CancelledError:
            logger.debug("Message handler cancelled")
        except Exception as e:
            logger.error("Error in message handler: %s", e)
            error_msg = ErrorMessage(-1, str(e))
            await self._message_queue.put(error_msg)

    def _process_message(self, data: Dict[str, Any]) -> Optional[Message]:
        """Process raw message data into Message objects.

        Args:
            data: Raw message data from protocol

        Returns:
            Processed message or None
        """
        msg_type = data.get("type")

        if msg_type == "session_update":
            # Handle session updates from new protocol
            update_type = data.get("update_type")
            update = data.get("update", {})
            agent_id = data.get("agentId")  # Extract agent_id from session_update

            if update_type == "agent_message_chunk":
                # Agent response chunk
                content = update.get("content", {})
                if content.get("type") == "text":
                    text = content.get("text", "")
                    if text:
                        return AssistantMessage(AssistantMessageChunk(text=text), agent_id=agent_id)

            elif update_type == "agent_thought_chunk":
                # Agent thinking process
                content = update.get("content", {})
                if content.get("type") == "text":
                    thought = content.get("text", "")
                    if thought:
                        return AssistantMessage(
                            AssistantMessageChunk(thought=thought), agent_id=agent_id
                        )

            elif update_type == "tool_call":
                # Tool call started
                from .types import Icon, ToolCallContent, ToolCallLocation

                tool_msg = ToolCallMessage(
                    id=update.get("toolCallId", ""),
                    label=update.get("title", "Tool"),
                    icon=Icon("emoji", "🔧"),
                    status=ToolCallStatus(update.get("status", "in_progress")),
                    agent_id=agent_id,
                )

                # Store for tracking
                self._pending_tool_calls[tool_msg.id] = tool_msg
                return tool_msg

            elif update_type == "tool_call_update":
                # Tool call update
                tool_id = update.get("toolCallId")
                if tool_id in self._pending_tool_calls:
                    tool_msg = self._pending_tool_calls[tool_id]
                    tool_msg.status = ToolCallStatus(update.get("status", "completed"))
                    # Update agent_id if not already set
                    if not tool_msg.agent_id:
                        tool_msg.agent_id = agent_id

                    # Add content if available
                    content_list = update.get("content", [])
                    if content_list:
                        # Process tool output
                        for item in content_list:
                            if item.get("type") == "content":
                                content = item.get("content", {})
                                if content.get("type") == "text":
                                    # Return text from tool output with agent_id
                                    return AssistantMessage(
                                        AssistantMessageChunk(text=content.get("text", "")),
                                        agent_id=agent_id,
                                    )
                    return tool_msg

            elif update_type == "plan":
                # Plan update
                from .types import PlanEntry, PlanMessage

                entries_data = update.get("entries", [])
                entries = []
                for entry_data in entries_data:
                    entry = PlanEntry(
                        content=entry_data.get("content", ""),
                        priority=entry_data.get("priority", "medium"),
                        status=entry_data.get("status", "pending"),
                    )
                    entries.append(entry)

                if entries:
                    return PlanMessage(entries)

            elif update_type == "user_message_chunk":
                # User message echo (rarely used but supported in protocol)
                content = update.get("content", {})
                if content.get("type") == "text":
                    text = content.get("text", "")
                    if text:
                        # Return as UserMessage for completeness
                        return UserMessage([UserMessageChunk(text)])

        elif msg_type == "response":
            # Response to our request
            request_id = data.get("id")
            if request_id:
                # Handle pending request responses
                if request_id in self._pending_requests:
                    # This is handled by protocol layer
                    pass

            # Check if this is a prompt response with stopReason
            result = data.get("result", {})
            if "stopReason" in result:
                # Prompt completed with stopReason
                from .types import StopReason
                
                reason_str = result["stopReason"]
                stop_reason = None
                
                # Map string value to enum
                if reason_str == "end_turn":
                    stop_reason = StopReason.END_TURN
                elif reason_str == "max_tokens":
                    stop_reason = StopReason.MAX_TOKENS
                elif reason_str == "refusal":
                    stop_reason = StopReason.REFUSAL
                elif reason_str == "cancelled":
                    stop_reason = StopReason.CANCELLED
                
                return TaskFinishMessage(stop_reason=stop_reason)

        elif msg_type == "error":
            return ErrorMessage(
                code=data.get("code", -1),
                message=data.get("message", "Unknown error"),
                details=data.get("details"),
            )

        return None

    async def __aenter__(self) -> "IFlowClient":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Async context manager exit."""
        await self.disconnect()
        return False
