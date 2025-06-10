#!/usr/bin/env python3
"""
Direct test of MCP server functionality.
This will help us verify if the server is working before trying Cursor integration.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Test imports
try:
    import mcp.simple_server
    print("✅ MCP simple_server imported successfully")
except ImportError as e:
    print(f"❌ Could not import MCP simple_server: {e}")
    sys.exit(1)

async def test_basic_functionality():
    """Test basic functionality without the full MCP server."""
    print("🧪 Testing basic TTS functionality...")
    
    try:
        from config import Config
        from tts.manager import TTSManager
        
        # Test config loading
        config = Config.load()
        print("✅ Config loaded successfully")
        
        # Test TTS manager
        tts_manager = TTSManager(config)
        print("✅ TTS Manager created successfully")
        
        # Test device listing
        devices = tts_manager.get_audio_devices()
        print(f"✅ Found {len(devices)} audio devices")
        
        print("\n🎉 Basic functionality test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_basic_functionality())
    sys.exit(0 if success else 1) 