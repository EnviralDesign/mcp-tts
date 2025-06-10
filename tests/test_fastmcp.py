#!/usr/bin/env python3
"""
Test script for FastMCP TTS server.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from mcp_server import mcp


async def test_tools():
    """Test the MCP tools."""
    print("🧪 Testing FastMCP TTS Server tools...")
    
    try:
        # Test tool listing
        print("\n📋 Testing list_tools...")
        tools = await mcp.list_tools()
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        print("\n🎉 FastMCP Server tools test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ FastMCP Server tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Test the tools
    print("Testing FastMCP tools...")
    
    # Basic server info
    print(f"✅ Server name: {mcp.name}")
    
    # Test tools async
    success = asyncio.run(test_tools())
    
    if success:
        print("\n🎉 All tests passed! FastMCP server is working correctly.")
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1) 