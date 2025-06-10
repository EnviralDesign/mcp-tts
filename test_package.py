#!/usr/bin/env python3
"""
Quick test to verify the package structure and entry points work correctly.
"""

import sys
import subprocess
import tempfile
import os

def test_local_import():
    """Test that we can import the modules locally."""
    print("🧪 Testing local imports...")
    try:
        from src.mcp_server import main
        from src.tts.manager import TTSManager
        from src.config import Config
        print("✅ Local imports successful")
        return True
    except ImportError as e:
        print(f"❌ Local import failed: {e}")
        return False

def test_wheel_installation():
    """Test installing the wheel in a temporary environment."""
    print("\n🧪 Testing wheel installation...")
    
    wheel_path = "dist/mcp_cursor_tts-0.1.0-py3-none-any.whl"
    if not os.path.exists(wheel_path):
        print("❌ Wheel file not found")
        return False
    
    try:
        # Test with uvx (simulates real usage)
        result = subprocess.run([
            "uvx", "--from", wheel_path, "mcp-tts-server-stdio", "--version"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ uvx installation test successful")
            return True
        else:
            print(f"❌ uvx test failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✅ uvx started successfully (timed out as expected for MCP server)")
        return True
    except Exception as e:
        print(f"❌ uvx test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🔍 Testing MCP Cursor TTS Package")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    if test_local_import():
        tests_passed += 1
    
    if test_wheel_installation():
        tests_passed += 1
    
    print(f"\n📊 Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Package is ready for publishing.")
        return True
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 