import json
import subprocess
import sys
import time

def test_mcp_server():
    # Proper initialize request with clientInfo
    init_request = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        },
        "id": 1
    }
    
    # Tools list request
    tools_request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 2
    }
    
    try:
        # Start MCP server
        proc = subprocess.Popen(
            ["uv", "run", "python", "-m", "src.mcp_server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="C:/repos/mcp-cursor-tts"
        )
        
        # Send initialize
        proc.stdin.write(json.dumps(init_request) + "\n")
        proc.stdin.flush()
        
        # Read response
        init_response = proc.stdout.readline().strip()
        if init_response:
            init_data = json.loads(init_response)
            print("✅ Server initialized successfully")
            print(f"   Server name: {init_data.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
            print(f"   Protocol version: {init_data.get('result', {}).get('protocolVersion', 'Unknown')}")
        
        # Send tools list request
        proc.stdin.write(json.dumps(tools_request) + "\n")
        proc.stdin.flush()
        
        # Read tools response
        tools_response = proc.stdout.readline().strip()
        if tools_response:
            tools_data = json.loads(tools_response)
            if "result" in tools_data and "tools" in tools_data["result"]:
                tools = tools_data["result"]["tools"]
                print(f"\n✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"   • {tool['name']}: {tool.get('description', 'No description')}")
                return True
            else:
                print("❌ No tools found in response")
                print(f"Response: {tools_data}")
                return False
        else:
            print("❌ No response to tools/list request")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        try:
            proc.terminate()
        except:
            pass

if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1) 