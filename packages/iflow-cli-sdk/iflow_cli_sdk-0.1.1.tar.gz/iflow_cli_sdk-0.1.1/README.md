# iFlow Python SDK

[![PyPI Version](https://img.shields.io/pypi/v/iflow-cli-sdk)](https://pypi.org/project/iflow-cli-sdk/)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![WebSocket Protocol](https://img.shields.io/badge/protocol-ACP%20v1-orange)](docs/protocol.md)

[English](README.md) | [中文](README_CN.md)

A powerful Python SDK for interacting with iFlow CLI using the Agent Communication Protocol (ACP). Build AI-powered applications with full control over conversations, tool execution, and SubAgent orchestration.

**✨ Key Feature: The SDK automatically manages the iFlow process - no manual setup required!**

## Features

- 🚀 **Automatic Process Management** - Zero-config setup! SDK auto-starts and manages iFlow CLI
- 🔌 **Smart Port Detection** - Automatically finds available ports, no conflicts
- 🔄 **Bidirectional Communication** - Real-time streaming of messages and responses
- 🛠️ **Tool Call Management** - Handle and control tool executions with fine-grained permissions
- 🤖 **SubAgent Support** - Track and manage multiple AI agents with `agent_id` propagation
- 📋 **Task Planning** - Receive and process structured task plans
- 🔍 **Raw Data Access** - Debug and inspect protocol-level messages
- ⚡ **Async/Await Support** - Modern asynchronous Python with full type hints
- 🎯 **Simple & Advanced APIs** - From one-line queries to complex conversation management
- 📦 **Full ACP v1 Protocol** - Complete implementation of the Agent Communication Protocol

## Installation

### 1. Install iFlow CLI

If you haven't installed iFlow CLI yet:

**Mac/Linux/Ubuntu:**
```bash
bash -c "$(curl -fsSL https://gitee.com/iflow-ai/iflow-cli/raw/main/install.sh)"
```

**Windows:**
```bash
npm install -g @iflow-ai/iflow-cli@latest
```

### 2. Install the SDK

**Install from PyPI (Recommended):**

```bash
pip install iflow-cli-sdk
```

**Or install from source:**

```bash
git clone https://github.com/yourusername/iflow-cli-sdk-python.git
cd iflow-cli-sdk-python
pip install -e .
```

## Quick Start

The SDK **automatically manages the iFlow process** - no manual setup required!

### Default Usage (Automatic Process Management)

```python
import asyncio
from iflow_sdk import IFlowClient

async def main():
    # SDK automatically:
    # 1. Detects if iFlow is installed
    # 2. Starts iFlow process if not running
    # 3. Finds an available port
    # 4. Cleans up on exit
    async with IFlowClient() as client:
        await client.send_message("Hello, iFlow!")
        
        async for message in client.receive_messages():
            print(message)
            # Process messages...

asyncio.run(main())
```

**No need to manually start iFlow!** The SDK handles everything for you.

### Advanced: Manual Process Control

If you need to manage iFlow yourself (rare cases):

```python
import asyncio
from iflow_sdk import IFlowClient, IFlowOptions

async def main():
    # Disable automatic process management
    options = IFlowOptions(
        auto_start_process=False,
        url="ws://localhost:8090/acp"  # Connect to existing iFlow
    )
    
    async with IFlowClient(options) as client:
        await client.send_message("Hello, iFlow!")

asyncio.run(main())
```

**Note:** Manual mode requires you to start iFlow separately:
```bash
iflow --experimental-acp --port 8090
```

### Simple Examples

#### Simple Query

```python
import asyncio
from iflow_sdk import query

async def main():
    response = await query("What is the capital of France?")
    print(response)  # "The capital of France is Paris."

asyncio.run(main())
```

#### Interactive Conversation

```python
import asyncio
from iflow_sdk import IFlowClient, AssistantMessage, TaskFinishMessage

async def chat():
    async with IFlowClient() as client:
        await client.send_message("Explain quantum computing")
        
        async for message in client.receive_messages():
            if isinstance(message, AssistantMessage):
                print(message.chunk.text, end="", flush=True)
            elif isinstance(message, TaskFinishMessage):
                break

asyncio.run(chat())
```

#### Tool Call Control

```python
import asyncio
from iflow_sdk import IFlowClient, IFlowOptions, PermissionMode, ToolCallMessage, TaskFinishMessage

async def main():
    options = IFlowOptions(permission_mode=PermissionMode.CONFIRM)
    
    async with IFlowClient(options) as client:
        await client.send_message("Create a file called test.txt")
        
        async for message in client.receive_messages():
            if isinstance(message, ToolCallMessage):
                print(f"Tool requested: {message.label}")
                # Tool calls are handled automatically based on permission_mode
            elif isinstance(message, TaskFinishMessage):
                break

asyncio.run(main())
```

## API Reference

### Core Classes

- **`IFlowClient`**: Main client for bidirectional communication
- **`IFlowOptions`**: Configuration options
- **`RawDataClient`**: Access to raw protocol data

### Message Types

- **`AssistantMessage`**: AI assistant responses
- **`ToolCallMessage`**: Tool execution requests
- **`PlanMessage`**: Structured task plans with priority and status
- **`TaskFinishMessage`**: Task completion signal with stop reason (end_turn, max_tokens, refusal, cancelled)

### Convenience Functions

- `query(prompt)`: Simple synchronous query
- `query_stream(prompt)`: Streaming responses
- `query_sync(prompt)`: Synchronous with timeout

## Project Structure

```
iflow-sdk-python/
├── src/iflow_sdk/
│   ├── __init__.py          # Public API exports
│   ├── client.py            # Main IFlowClient implementation
│   ├── query.py             # Simple query functions
│   ├── types.py             # Type definitions and messages
│   ├── raw_client.py        # Raw protocol access
│   └── _internal/
│       ├── protocol.py      # ACP protocol handler
│       ├── transport.py     # WebSocket transport layer
│       └── launcher.py      # iFlow process management
├── tests/                   # Test suite
│   ├── test_basic.py        # Basic functionality tests
│   └── test_protocol.py     # Protocol compliance tests
├── examples/                # Usage examples
│   ├── comprehensive_demo.py
│   ├── quick_start.py
│   └── advanced_client.py
└── docs/                    # Documentation
```

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/iflow_sdk
# Run specific test
pytest tests/test_basic.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Check style
flake8 src/ tests/
```

## Protocol Support

The SDK implements the Agent Communication Protocol (ACP) v1, supporting:

- **Session Management**: Create, load, and manage conversation sessions
- **Message Types**: 
  - `agent_message_chunk` - Assistant responses
  - `agent_thought_chunk` - Internal reasoning
  - `tool_call` / `tool_call_update` - Tool execution lifecycle
  - `plan` - Structured task planning
  - `user_message_chunk` - User message echoing
- **Authentication**: Built-in iFlow authentication
- **File System Access**: Read/write file permissions
- **SubAgent Support**: Full `agent_id` tracking and management

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


---

Built with ❤️ for the AI development community