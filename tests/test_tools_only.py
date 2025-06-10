import json
import subprocess
import sys
import time

try:
    # Start the MCP server
    proc = subprocess.Popen(
        ["uv", "run", "python", "-m", "src.mcp_server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="C:/repos/mcp-cursor-tts"
    )
    
    # Initialize first
    init_req = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {}},
        "id": 1
    }
    proc.stdin.write(json.dumps(init_req) + "\n")
    proc.stdin.flush()
    
    # Read init response
    init_resp = proc.stdout.readline()
    print("Server initialized successfully")
    
    # Request tools list
    tools_req = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 2
    }
    proc.stdin.write(json.dumps(tools_req) + "\n")
    proc.stdin.flush()
    
    # Read tools response
    tools_resp = proc.stdout.readline().strip()
    if tools_resp:
        data = json.loads(tools_resp)
        if "result" in data and "tools" in data["result"]:
            tools = data["result"]["tools"]
            print(f"Found {len(tools)} tools:")
            for tool in tools:
                print(f"  - {tool['name']}: {tool.get('description', 'No description')}")
        else:
            print("No tools found in response:", data)
    else:
        print("No response to tools/list")
    
    proc.terminate()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc() 