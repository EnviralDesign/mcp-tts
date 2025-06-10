#!/usr/bin/env python3
"""
Test script to demonstrate .env file loading.
"""

import os
from src.config import Config


def test_env_loading():
    """Test .env file loading functionality."""
    print("🔧 Testing .env file configuration loading...\n")

    # Load configuration (this will automatically load .env if it exists)
    config = Config.load()

    print("📋 Configuration loaded:")
    print(f"   Host: {config.host}")
    print(f"   Port: {config.port}")
    print(f"   TTS Provider: {config.tts.provider}")
    print(f"   TTS Voice: {config.tts.voice}")
    print(f"   Audio Volume: {config.audio.volume}")

    # Check API key
    if config.openai_api_key:
        # Mask the API key for security
        masked_key = (
            config.openai_api_key[:8] + "..." + config.openai_api_key[-4:]
            if len(config.openai_api_key) > 12
            else "***masked***"
        )
        print(f"   OpenAI API Key: {masked_key} ✅")
    else:
        print("   OpenAI API Key: Not found ❌")
        print("\n💡 To set your API key:")
        print("   1. Copy env.example to .env:")
        print("      cp env.example .env")
        print("   2. Edit .env and add your API key:")
        print("      OPENAI_API_KEY=your-actual-api-key-here")

    print("\n🔍 Environment check:")
    print(f"   OPENAI_API_KEY in env: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
    print(f"   .env file exists: {'Yes' if os.path.exists('.env') else 'No'}")

    # For CI: just assert that config loads successfully
    assert config is not None, "Config should load successfully"
    assert config.tts.provider == "openai", "TTS provider should be openai"
    assert config.audio.volume > 0, "Audio volume should be greater than 0"

    # API key is optional for this test
    print("✅ Environment loading test passed!")


if __name__ == "__main__":
    test_env_loading()
