import json
import subprocess
import sys
import os
from pathlib import Path


def test_mcp_server():
    # Proper initialize request with clientInfo
    init_request = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"},
        },
        "id": 1,
    }

    # Tools list request
    tools_request = {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 2}

    # Get current working directory (should be project root)
    project_root = Path.cwd()
    if not (project_root / "src" / "mcp_server.py").exists():
        project_root = Path(__file__).parent.parent

    print(f"Testing MCP server from: {project_root}")

    # Set CI mode for testing
    env = os.environ.copy()
    env["CI_MODE"] = "true"

    try:
        # Start MCP server
        proc = subprocess.Popen(
            ["uv", "run", "python", "-m", "src.mcp_server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(project_root),
            env=env,
        )

        # Send initialize
        proc.stdin.write(json.dumps(init_request) + "\n")
        proc.stdin.flush()

        # Read response
        init_response = proc.stdout.readline().strip()
        if init_response:
            init_data = json.loads(init_response)
            print("✅ Server initialized successfully")
            print(
                f"   Server name: {init_data.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}"
            )
            print(
                f"   Protocol version: {init_data.get('result', {}).get('protocolVersion', 'Unknown')}"
            )

        # Send tools list request
        proc.stdin.write(json.dumps(tools_request) + "\n")
        proc.stdin.flush()

        # Read tools response
        tools_response = proc.stdout.readline().strip()
        assert tools_response, "Should receive response to tools/list request"

        tools_data = json.loads(tools_response)
        assert "result" in tools_data, f"Response should contain 'result': {tools_data}"
        assert (
            "tools" in tools_data["result"]
        ), f"Result should contain 'tools': {tools_data['result']}"

        tools = tools_data["result"]["tools"]
        print(f"\n✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"   • {tool['name']}: {tool.get('description', 'No description')}")

        assert len(tools) > 0, "Should find at least one tool"
        print("✅ MCP server test passed!")

    except Exception as e:
        # Re-raise as assertion error for pytest
        raise AssertionError(f"MCP server test failed: {e}")
    finally:
        try:
            proc.terminate()
        except Exception:
            pass


if __name__ == "__main__":
    try:
        test_mcp_server()
        print("✅ All tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
