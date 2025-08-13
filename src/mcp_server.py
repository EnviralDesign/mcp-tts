#!/usr/bin/env python3
"""
MCP Server entry point for Cursor IDE integration using FastMCP.
This runs only the MCP server via stdio (no web interface).
"""

import sys
import os
from pathlib import Path

try:
    # When installed as a package, src/ contents are at package root
    from tts.manager import TTSManager
    from config import Config
except ImportError:
    # Fallback for local development
    src_dir = Path(__file__).parent
    sys.path.insert(0, str(src_dir))

    from tts.manager import TTSManager
    from config import Config

from mcp.server import FastMCP

# Initialize components  
print(f"🚀 MCP Server starting up...")
print(f"   OPENAI_API_KEY: {'✅ Present' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
print(f"   ELEVENLABS_API_KEY: {'✅ Present' if os.getenv('ELEVENLABS_API_KEY') else '❌ Missing'}")
print(f"   MCP_TTS_VOICE: {os.getenv('MCP_TTS_VOICE', 'default')}")
print(f"   MCP_TTS_VOICE_PRESET: {os.getenv('MCP_TTS_VOICE_PRESET', 'default')}")
print(f"   MCP_TTS_SPEED: {os.getenv('MCP_TTS_SPEED', '1.0')}")

config = Config.load()
tts_manager = TTSManager(config)

# Create FastMCP server instance
mcp = FastMCP("mcp_tts_server")


@mcp.tool()
async def text_to_speech(text: str) -> str:
    """
    Convert text to speech and play through speakers.
    All settings (voice, speed, device, etc.) are configured via environment variables in MCP config.

    Args:
        text: Text to convert to speech

    Returns:
        Success or error message
    """
    if not text:
        return "Error: No text provided"

    # Reload config to get latest user settings (ensures fresh env vars)
    global config, tts_manager
    config = Config.load()
    tts_manager.config = config
    # Sync provider selection from config each call to allow hot switches via MCP env
    if config.tts.provider:
        tts_manager.set_provider(config.tts.provider)

    # All settings come from config (single source of truth)
    voice = config.tts.voice
    voice_instructions = config.get_current_voice_instructions()
    speed = config.tts.speed
    
    # Find device index from config
    device_index = None
    if config.audio.default_device:
        devices = tts_manager.get_audio_devices()
        for device in devices:
            if config.audio.default_device.lower() in device.name.lower():
                device_index = device.index
                break
    elif config.audio.default_device_index is not None:
        device_index = config.audio.default_device_index

    # Generate and play speech
    try:
        # Check if provider is available first
        provider = tts_manager.get_current_provider()
        if not provider:
            return f"❌ No TTS provider available. Current provider: {tts_manager.current_provider}. Available providers: {', '.join(tts_manager.get_available_providers()) or 'None'}"

        # Always use non-streaming for simplicity (can be made configurable later)
        success = await tts_manager.generate_and_play(
            text=text,
            voice=voice,
            instructions=voice_instructions,
            device_index=device_index,
            speed=speed,
        )

        if success:
            return f"✅ Successfully played speech: {len(text)} characters"
        else:
            return f"❌ Failed to generate or play speech"
    except Exception as e:
        return f"❌ Error: {str(e)}"


@mcp.tool()
def list_audio_devices() -> str:
    """
    List available audio output devices.

    Returns:
        List of available audio devices with their details
    """
    devices = tts_manager.get_audio_devices()

    if not devices:
        return "No audio devices found"

    device_list = ["Available Audio Devices:"]
    for device in devices:
        status = "🔊 (default)" if device.is_default else "🔇"
        device_list.append(
            f"  {device.index}: {device.name} {status}"
            f" - {device.channels} channels @ {device.sample_rate}Hz"
        )

    return "\n".join(device_list)


@mcp.tool()
def test_audio_device(device_index: int = None) -> str:
    """
    Test an audio device by playing a test tone.

    Args:
        device_index: Audio device index to test (optional, uses default if not specified)

    Returns:
        Success or error message
    """
    success = tts_manager.test_audio_device(device_index)

    if success:
        device_info = (
            "default device" if device_index is None else f"device {device_index}"
        )
        return f"✅ Audio test successful for {device_info}"
    else:
        return f"❌ Audio test failed for device {device_index}"


@mcp.tool()
def stop_speech() -> str:
    """
    Stop current speech playback.

    Returns:
        Confirmation message
    """
    tts_manager.stop_playback()
    return "🛑 Speech playback stopped"


@mcp.tool()
def get_tts_status() -> str:
    """
    Get current TTS server status and configuration.

    Returns:
        Current status information
    """
    status = tts_manager.get_status()

    status_text = [
        "🎵 TTS Server Status:",
        f"  Provider: {status['current_provider']}",
        f"  Volume: {status['volume']:.1%}",
        f"  Playing: {'Yes' if status['is_playing'] else 'No'}",
        f"  Available Providers: {', '.join(status['available_providers'])}",
        f"  Supported Voices: {', '.join(status['supported_voices'][:5])}{'...' if len(status['supported_voices']) > 5 else ''}",
        f"  Audio Devices: {len(status['audio_devices'])} found",
    ]

    return "\n".join(status_text)


@mcp.tool()
def get_current_config() -> str:
    """
    Get current TTS configuration settings (voice, preset, device, etc.).

    Returns:
        Current configuration details
    """
    # Reload config to get latest settings (this may be why it works!)
    global config, tts_manager
    current_config = Config.load()
    
    # Update the global config and tts_manager too
    config = current_config
    tts_manager.config = config

    config_text = [
        "⚙️ Current TTS Configuration:",
        f"  🎤 Voice: {current_config.tts.voice}",
        f"  🎭 Voice Preset: {current_config.tts.current_preset}",
        f"  📝 Custom Instructions: {'Yes' if current_config.tts.custom_instructions.strip() else 'No (using preset)'}",
        f"  ⚡ Speed: {current_config.tts.speed}x",
        f"  🔊 Volume: {current_config.audio.volume:.1%}",
        f"  🎵 Default Device: {current_config.audio.default_device or 'System default'}",
        f"  🎵 Default Device Index: {current_config.audio.default_device_index or 'None set'}",
        "",
        "💡 Current voice instructions:",
        f"  \"{current_config.get_current_voice_instructions()[:100]}{'...' if len(current_config.get_current_voice_instructions()) > 100 else ''}\"",
    ]

    return "\n".join(config_text)


@mcp.tool()
def set_volume(volume: float) -> str:
    """
    Set audio playback volume.

    Args:
        volume: Volume level from 0.0 to 1.0

    Returns:
        Confirmation message
    """
    if not 0.0 <= volume <= 1.0:
        return "❌ Volume must be between 0.0 and 1.0"

    tts_manager.set_volume(volume)
    return f"🔊 Volume set to {volume:.1%}"


def main():
    """Entry point for uvx execution."""
    # Run the server using stdio transport for Cursor integration
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
