#!/usr/bin/env python3
"""
Test script for MCP TTS Server components.
"""

import asyncio
import logging
from src.config import Config
from src.audio.player import AudioPlayer
from src.tts.manager import TTSManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_audio_devices():
    """Test audio device enumeration."""
    print("🔍 Testing audio devices...")

    devices = AudioPlayer.get_audio_devices()
    if devices:
        print(f"✅ Found {len(devices)} audio devices:")
        for device in devices:
            status = "🔊 (default)" if device.is_default else "🔇"
            print(f"  - {device.index}: {device.name} {status}")
    else:
        print("❌ No audio devices found")

    return len(devices) > 0


async def test_tts_manager():
    """Test TTS manager initialization."""
    print("\n🔍 Testing TTS manager...")

    config = Config.load()
    if not config.openai_api_key:
        print("❌ No OpenAI API key found - set OPENAI_API_KEY environment variable")
        return False

    tts_manager = TTSManager(config)

    # Test status
    status = tts_manager.get_status()
    print("✅ TTS Manager initialized:")
    print(f"  - Provider: {status['current_provider']}")
    print(f"  - Available providers: {status['available_providers']}")
    print(f"  - Supported voices: {len(status['supported_voices'])} voices")
    print(f"  - Volume: {status['volume']:.1%}")

    return len(status["available_providers"]) > 0


async def test_simple_tts():
    """Test simple TTS generation (no playback)."""
    print("\n🔍 Testing TTS generation...")

    config = Config.load()
    if not config.openai_api_key:
        print("❌ No OpenAI API key - skipping TTS test")
        return False

    try:
        from src.tts.providers.openai_fm import OpenAITTSProvider

        provider = OpenAITTSProvider(config.openai_api_key)

        # Test connection
        connection_ok = await provider.test_connection()
        if connection_ok:
            print("✅ OpenAI TTS connection test passed")
            return True
        else:
            print("❌ OpenAI TTS connection test failed")
            return False

    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 MCP TTS Server Component Tests\n")

    tests = [
        ("Audio Devices", test_audio_devices()),
        ("TTS Manager", test_tts_manager()),
        ("TTS Generation", test_simple_tts()),
    ]

    results = []
    for test_name, test_coro in tests:
        try:
            result = await test_coro
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))

    print("\n📊 Test Results:")
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
        if result:
            passed += 1

    print(f"\n🎯 {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("🎉 All tests passed! The MCP TTS server is ready to use.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    asyncio.run(main())
