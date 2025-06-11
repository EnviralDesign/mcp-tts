# MCP Text-to-Speech for Cursor IDE

Add text-to-speech capabilities to Cursor IDE. Let your AI assistant speak responses, summaries, and explanations out loud.

## 🚀 Quick Start

**Prerequisites:** [Cursor IDE](https://cursor.sh) and an [OpenAI API key](https://platform.openai.com/api-keys)

**Setup:** Add this to your Cursor MCP settings (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "mcp_tts_server": {
      "command": "uvx",
      "args": ["--from", "mcp-tts", "mcp-tts-server-stdio"],
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key-here",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

**That's it!** Restart Cursor and try asking: *"Can you read me a summary using text-to-speech?"*

## ⚙️ Configuration Options

You can control the TTS system using these environment variables in your MCP config:

| Variable | Description | Example Values | Default |
|----------|-------------|----------------|---------|
| `OPENAI_API_KEY` | **Required** - Your OpenAI API key | `sk-proj-abc123...` | - |
| `MCP_TTS_VOICE` | OpenAI voice to use | `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`, `ballad` | `ballad` |
| `MCP_TTS_VOICE_PRESET` | Voice style preset | `default`, `professional`, `calm`, `nyc_cabbie`, `chill_surfer`, `cheerleader`, `emo_teenager`, `eternal_optimist`, `dramatic` | `default` |
| `MCP_TTS_CUSTOM_INSTRUCTIONS` | Custom voice instructions (overrides preset) | `"Speak like a pirate"` | - |
| `MCP_TTS_SPEED` | Speech speed | `0.25` to `4.0` | `1.0` |
| `MCP_TTS_VOLUME` | Playback volume | `0.0` to `1.0` | `0.8` |
| `MCP_TTS_DEVICE_NAME` | Audio device name (partial match) | `"Speakers"`, `"Headphones"` | - |
| `MCP_TTS_DEVICE_INDEX` | Audio device index | `0`, `1`, `2`, etc. | - |

**Tip:** To find your audio device name, first run with basic config, then use the `list_audio_devices` tool to see available devices.

### Voice Presets

You can use these built-in voice style presets:
- `default` - Clear, friendly, and conversational
- `professional` - Authoritative business voice
- `calm` - Composed, reassuring with quiet authority
- `nyc_cabbie` - Fast-talking New Yorker with edge
- `chill_surfer` - Laid-back, mellow, effortlessly cool
- `cheerleader` - High-energy, enthusiastic, motivational
- `emo_teenager` - Sarcastic, disinterested, melancholic
- `eternal_optimist` - Positive, solution-oriented
- `dramatic` - Low, hushed, suspenseful with theatrical flair

## 🎵 Usage Examples

- *"Use text-to-speech to explain this code"*
- *"Read me the changes you just made"*  
- *"List my audio devices"*
- *"Switch to a professional voice style"*

## 📚 Full Documentation

For advanced configuration, voice presets, troubleshooting, and development setup, see [SETUP_GUIDE.md](SETUP_GUIDE.md).

---

**Status:** ✅ Working with Cursor IDE • 🎵 7 TTS tools available • 🔊 Cross-platform audio

## 🛠️ Available Tools

This MCP server provides the following tools in Cursor:

- **text_to_speech** — Convert text to speech and play it through your speakers using the current configuration.
- **list_audio_devices** — List all available audio output devices on your system.
- **test_audio_device** — Play a test tone on a selected audio device to verify it works.
- **stop_speech** — Stop any current speech playback immediately.
- **get_tts_status** — Show the current TTS server status, provider, volume, and device info.
- **get_current_config** — Display the current voice, preset, device, and all active TTS settings.
- **set_volume** — Change the playback volume for speech output.
