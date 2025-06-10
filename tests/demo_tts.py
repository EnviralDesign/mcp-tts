#!/usr/bin/env python3
"""
Demo script for MCP TTS Server - demonstrates full text-to-speech playback.
"""

import asyncio
import logging
from src.config import Config
from src.tts.manager import TTSManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_tts():
    """Demonstrate TTS functionality with actual audio playback."""
    print("🎵 MCP TTS Server Demo\n")
    
    # Load configuration
    config = Config.load()
    if not config.openai_api_key:
        print("❌ No OpenAI API key found. Set OPENAI_API_KEY environment variable.")
        return
    
    # Initialize TTS manager
    print("🔧 Initializing TTS manager...")
    tts_manager = TTSManager(config)
    
    # Show status
    status = tts_manager.get_status()
    print(f"✅ TTS Manager ready:")
    print(f"   Provider: {status['current_provider']}")
    print(f"   Voice: {config.tts.voice}")
    print(f"   Volume: {status['volume']:.1%}")
    print(f"   Default device: {status['audio_devices'][0]['name'] if status['audio_devices'] else 'None'}")
    
    # Demo text
    demo_text = """
    Hello! This is a demonstration of the MCP Text-to-Speech server for Cursor IDE. 
    The server is working correctly and can generate high-quality speech using OpenAI's API. 
    You should now hear this message through your speakers. The system supports multiple voices, 
    custom instructions, and cross-platform audio playback.
    """
    
    print(f"\n🗣️  Playing demo message ({len(demo_text)} characters)...")
    print("📢 You should hear audio through your speakers now!\n")
    
    try:
        # Generate and play speech
        success = await tts_manager.generate_and_play(
            text=demo_text.strip(),
            voice=config.tts.voice,
            instructions="Speak clearly and enthusiastically, like demonstrating new technology"
        )
        
        if success:
            print("✅ Demo completed successfully!")
            print("🎉 The MCP TTS server is fully functional and ready for Cursor integration.")
        else:
            print("❌ Demo playback failed. Check audio device settings.")
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")


async def main():
    """Main demo function."""
    try:
        await demo_tts()
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user.")
    except Exception as e:
        print(f"❌ Demo error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 