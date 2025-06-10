#!/usr/bin/env python3
"""
MCP Server entry point for Cursor IDE integration using FastMCP.
This runs only the MCP server via stdio (no web interface).
"""

import sys
import asyncio
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
config = Config.load()
tts_manager = TTSManager(config)

# Create FastMCP server instance
mcp = FastMCP("mcp_tts_server")


@mcp.tool()
async def text_to_speech(text: str, voice: str = None, voice_instructions: str = None, 
                         speed: float = 1.0, device_name: str = None, stream: bool = False) -> str:
    """
    Convert text to speech and play through speakers with customizable voice style.
    
    Args:
        text: Text to convert to speech
        voice: Voice to use (e.g., 'alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer', 'ballad')
        voice_instructions: Custom voice style instructions (e.g., 'friendly and energetic', 'professional and calm')
        speed: Speech speed from 0.25 to 4.0 (default: 1.0)
        device_name: Audio device name to use (optional)
        stream: Whether to stream audio for faster playback (default: false)
    
    Returns:
        Success or error message
    """
    if not text:
        return "Error: No text provided"
    
    # Reload config to get latest user settings
    global config, tts_manager
    config = Config.load()
    tts_manager.config = config
    
    # Find device index by name if provided, or use saved default
    device_index = None
    if device_name:
        devices = tts_manager.get_audio_devices()
        for device in devices:
            if device_name.lower() in device.name.lower():
                device_index = device.index
                break
    elif config.audio.default_device_index is not None:
        device_index = config.audio.default_device_index
    
    # Generate and play speech
    try:
        if stream:
            success = await tts_manager.generate_and_stream(
                text=text,
                voice=voice,
                instructions=voice_instructions,
                device_index=device_index,
                speed=speed
            )
        else:
            success = await tts_manager.generate_and_play(
                text=text,
                voice=voice,
                instructions=voice_instructions,
                device_index=device_index,
                speed=speed
            )
        
        if success:
            return f"✅ Successfully played speech: {len(text)} characters"
        else:
            return "❌ Failed to generate or play speech"
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
        device_info = "default device" if device_index is None else f"device {device_index}"
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
        f"  Audio Devices: {len(status['audio_devices'])} found"
    ]
    
    return "\n".join(status_text)


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