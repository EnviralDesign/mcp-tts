#!/usr/bin/env python3
"""
Test MCP server integration by simulating Cursor's interaction.
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path


async def test_mcp_stdio():
    """Test the MCP server via stdio like Cursor would."""
    print("🧪 Testing MCP TTS Server via stdio (like Cursor)...")

    try:
        # Start the MCP server process
        proc = subprocess.Popen(
            ["uv", "run", "python", "src/mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent,
        )

        # Send initialize request
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        }

        print("📤 Sending initialize request...")
        proc.stdin.write(json.dumps(initialize_request) + "\n")
        proc.stdin.flush()

        # Read response
        response_line = proc.stdout.readline().strip()
        if response_line:
            response = json.loads(response_line)
            print(
                f"✅ Initialize response: {response.get('result', {}).get('capabilities', 'OK')}"
            )

        # Send tools/list request
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        }

        print("📤 Sending tools/list request...")
        proc.stdin.write(json.dumps(tools_request) + "\n")
        proc.stdin.flush()

        # Read tools response
        tools_response_line = proc.stdout.readline().strip()
        if tools_response_line:
            tools_response = json.loads(tools_response_line)
            tools = tools_response.get("result", {}).get("tools", [])
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"  - {tool['name']}")

        # Clean up
        proc.terminate()
        proc.wait(timeout=5)

        print("\n🎉 MCP stdio integration test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ MCP stdio test failed: {e}")
        if "proc" in locals():
            proc.terminate()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_mcp_stdio())
    sys.exit(0 if success else 1)
