#!/usr/bin/env python3
"""Test interactive conversation example from README"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.iflow_sdk import IFlowClient, AssistantMessage, TaskFinishMessage

async def chat():
    async with IFlowClient() as client:
        await client.send_message("Explain quantum computing in one sentence")
        
        received_messages = 0
        async for message in client.receive_messages():
            if isinstance(message, AssistantMessage):
                print(message.chunk.text, end="", flush=True)
                received_messages += 1
            elif isinstance(message, TaskFinishMessage):
                break
        
        assert received_messages > 0, "Should receive at least one assistant message"
        print(f"\n✅ Interactive conversation test passed ({received_messages} messages)")

if __name__ == "__main__":
    asyncio.run(chat())