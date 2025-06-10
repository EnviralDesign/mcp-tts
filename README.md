# MCP Text-to-Speech Server for Cursor IDE

A cross-platform MCP (Model Context Protocol) server that provides text-to-speech capabilities for Cursor IDE, allowing AI assistants to provide audio summaries and speech output through local speakers.

## ✅ Current Status

**Working Features:**
- ✅ **MCP Server** - 7 tools registered and working with Cursor
- ✅ **Environment Variable Configuration** - Configure voice, preset, device, and volume directly in MCP settings
- ✅ **Web Configuration Interface** - Voice presets, device selection, settings management  
- ✅ **OpenAI TTS Integration** - Using `gpt-4o-mini-tts` with custom voice instructions
- ✅ **Cross-platform Audio** - Audio device detection and playback working
- ✅ **Voice Presets** - 9 presets including professional, NYC cabbie, chill surfer styles
- ✅ **Persistent Configuration** - Settings saved between sessions

## 🚀 Quick Start

### Option 1: uvx Installation (Recommended for End Users)

The easiest way to use this server is through `uvx`, which automatically handles installation and dependencies:

**Prerequisites:**
- [uv](https://github.com/astral-sh/uv) package manager (for uvx)
- OpenAI API key
- Cursor IDE

**Setup:**
Just add this to your Cursor MCP configuration - no cloning or setup required!

**Note:** The package provides two executables:
- `mcp-tts-server-stdio` - For MCP/Cursor integration (what you want)
- `mcp-tts-server` - For standalone web interface

### Option 2: Local Development Setup

For development or if you want to modify the code:

**Prerequisites:**
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- OpenAI API key
- Cursor IDE

**Installation:**

1. **Clone and setup:**
   ```bash
   git clone <your-repo>
   cd mcp-tts
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Configure environment:**
   ```bash
   cp env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

### Running the Servers

#### 🎵 MCP Server (for Cursor integration)
```bash
# Using the batch file (recommended for Windows)
start-mcp-tts.bat

# Or directly
uv run python src/mcp_server.py
```

#### 🌐 Web Configuration Server
```bash
# Start web interface
uv run python src/main.py

# Then visit: http://localhost:8742
```

## 🔌 Cursor Integration

### MCP Configuration

Add this to your Cursor MCP settings file (`~/.cursor/mcp.json`):

**Single Source of Truth (Recommended - Using uvx):**

```json
{
  "mcpServers": {
    "mcp_tts_server": {
      "command": "uvx",
      "args": ["--from", "mcp-tts", "mcp-tts-server-stdio"],
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key-here",
        "PYTHONIOENCODING": "utf-8",
        "MCP_TTS_VOICE": "nova",
        "MCP_TTS_VOICE_PRESET": "professional",
        "MCP_TTS_SPEED": "1.2",
        "MCP_TTS_VOLUME": "0.8",
        "MCP_TTS_DEVICE_NAME": "Speakers"
      }
    }
  }
}

Local development (direct command):
```json
{
  "mcpServers": {
    "mcp_tts_server": {
      "command": "uv",
      "args": ["--directory", "C:/repos/mcp-tts", "run", "python", "src/mcp_server.py"],
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key-here",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

**Important for local options:** Update the path `C:/repos/mcp-tts` to match your actual project location.

### Available MCP Tools

Once connected to Cursor, you'll have access to these 7 tools:

- 🎵 **text_to_speech** - Convert text to speech with customizable voices and styles
- 🔊 **list_audio_devices** - Show available audio output devices  
- 🧪 **test_audio_device** - Test audio device with a tone
- ⏹️ **stop_speech** - Stop current audio playback
- 📊 **get_tts_status** - Get server status and configuration
- ⚙️ **get_current_config** - Show current voice, preset, device, and volume settings
- 🔈 **set_volume** - Adjust playback volume

### Example Usage in Cursor

Try asking your AI assistant:
- *"Can you read me a summary of the changes you just made using text-to-speech?"*
- *"List my available audio devices"*
- *"Show me my current configuration"*
- *"Use the NYC cabbie voice style to explain this code"*

### Common Configuration Examples

**For Professional Presentations:**
```json
"env": {
  "OPENAI_API_KEY": "your-key-here",
  "MCP_TTS_VOICE": "nova",
  "MCP_TTS_VOICE_PRESET": "professional",
  "MCP_TTS_SPEED": "0.9",
  "MCP_TTS_DEVICE_NAME": "Speakers"
}
```

**For Casual Coding Sessions:**
```json
"env": {
  "OPENAI_API_KEY": "your-key-here", 
  "MCP_TTS_VOICE": "ballad",
  "MCP_TTS_VOICE_PRESET": "chill_surfer",
  "MCP_TTS_SPEED": "1.1",
  "MCP_TTS_DEVICE_NAME": "Headphones"
}
```

## ⚙️ Configuration

### Environment Variables (uvx users)

You can now configure most TTS settings directly in your Cursor MCP configuration without needing the web interface:

| Variable | Description | Example Values | Default |
|----------|-------------|----------------|---------|
| `OPENAI_API_KEY` | **Required** - Your OpenAI API key | `sk-proj-abc123...` | - |
| `MCP_TTS_VOICE` | OpenAI voice to use | `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`, `ballad` | `ballad` |
| `MCP_TTS_VOICE_PRESET` | Voice style preset | `default`, `professional`, `calm`, `nyc_cabbie`, `chill_surfer`, `cheerleader`, `emo_teenager`, `eternal_optimist`, `dramatic` | `default` |
| `MCP_TTS_CUSTOM_INSTRUCTIONS` | Custom voice instructions | `"Speak like a pirate"` | - |
| `MCP_TTS_SPEED` | Speech speed | `0.25` to `4.0` | `1.0` |
| `MCP_TTS_VOLUME` | Playback volume | `0.0` to `1.0` | `0.8` |
| `MCP_TTS_DEVICE_NAME` | Audio device name (partial match) | `"Speakers"`, `"Headphones"` | - |
| `MCP_TTS_DEVICE_INDEX` | Audio device index | `0`, `1`, `2`, etc. | - |

**Tip:** To find your audio device name, first run with basic config, then use the `list_audio_devices` tool to see available devices.

### Voice Presets

The server includes 9 voice style presets:

- **Default** - Clear, friendly, and conversational
- **Professional** - Authoritative business voice  
- **Calm** - Composed, reassuring with quiet authority
- **NYC Cabbie** - Fast-talking New Yorker with edge
- **Chill Surfer** - Laid-back, mellow, effortlessly cool
- **Cheerleader** - High-energy, enthusiastic, motivational
- **Emo Teenager** - Sarcastic, disinterested, melancholic
- **Eternal Optimist** - Positive, solution-oriented
- **Dramatic** - Low, hushed, suspenseful with theatrical flair

### Web Interface

Visit `http://localhost:8742` for:
- Voice and audio device configuration
- Voice preset selection and custom instructions
- Real-time testing and preview
- Settings persistence

## 📁 Project Structure

```
mcp-tts/
├── src/
│   ├── mcp_server.py          # FastMCP server (for Cursor)
│   ├── main.py               # Web configuration server
│   ├── config.py             # Configuration management
│   ├── api/
│   │   └── routes.py         # FastAPI routes
│   ├── tts/
│   │   ├── manager.py        # TTS coordination
│   │   └── providers/
│   │       ├── base.py       # Provider interface
│   │       └── openai_fm.py  # OpenAI FM API implementation
│   └── audio/
│       ├── player.py         # Cross-platform audio playback
│       └── devices.py        # Audio device enumeration
├── tests/                    # All test files
├── config/
│   ├── default.yaml          # Default configuration
│   └── user_settings.json    # Persistent user settings
├── static/                   # Web UI assets
├── start-mcp-tts.bat         # Windows startup script
└── .env                      # Environment variables
```

## 🧪 Testing

Run the test suite:
```bash
# Test MCP server functionality  
uv run python tests/test_fastmcp.py

# Test TTS functionality
uv run python tests/demo_tts.py

# Test web API
uv run python tests/test_server.py
```

## 🔧 Development Commands

```bash
# Start MCP server for Cursor
uv run python src/mcp_server.py

# Start web interface for configuration  
uv run python src/main.py

# Test basic functionality
uv run python tests/test_fastmcp.py

# Test TTS with real audio
uv run python tests/demo_tts.py

# Check health
curl http://localhost:8742/api/health
```

## 🐛 Troubleshooting

### Common Issues

**"0 tools enabled" in Cursor:**
- ✅ **Fixed!** - Updated to use modern FastMCP API
- Ensure you're using the correct batch file path
- Restart Cursor after updating MCP configuration

**"Module not found" errors:**
- ✅ **Fixed!** - All import conflicts resolved
- Make sure you're using `uv run` commands

**Audio not working:**
- Check available devices: Use the `list_audio_devices` tool in Cursor
- Test audio device: Use the `test_audio_device` tool
- Verify OpenAI API key in MCP configuration
- Try setting `MCP_TTS_DEVICE_INDEX` to a specific device number

**Configuration not working:**
- Use the `get_current_config` tool to see what settings are active
- Check environment variable names are exactly as documented (case-sensitive)
- Restart Cursor after changing MCP configuration
- For audio device issues, try both `MCP_TTS_DEVICE_NAME` and `MCP_TTS_DEVICE_INDEX`

**Server won't start:**
- Check port 8742 isn't in use: `netstat -an | findstr 8742`
- Verify all dependencies installed: `uv sync`

### Recent Fixes Applied

- ✅ Migrated from old MCP API to FastMCP
- ✅ Fixed import conflicts (`mcp/` → `mcp_old/`)  
- ✅ Updated all relative imports to absolute imports
- ✅ Organized test files into `tests/` directory
- ✅ Fixed batch file to use correct server path

## 📚 API Documentation

With the web server running, visit:
- Main interface: `http://localhost:8742`
- API docs: `http://localhost:8742/docs`  
- Health check: `http://localhost:8742/api/health`

## 📦 Publishing to PyPI

To make this package available via `uvx` for all users:

1. **Update package metadata:**
   ```bash
   # Edit pyproject.toml with your details:
   # - author name/email
   # - repository URLs
   # - version number
   ```

2. **Build the package:**
   ```bash
   uv build
   ```

3. **Publish to PyPI:**
   ```bash
   # Install twine if needed
   uv add --dev twine
   
   # Upload to PyPI (you'll need PyPI credentials)
   uv run twine upload dist/*
   ```

4. **Test the published package:**
   ```bash
   uvx mcp-tts-server-stdio
   ```

This package is already published to PyPI as `mcp-tts`, which is why the simple uvx command works!

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `uv run python tests/test_fastmcp.py`
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**🎉 Status: Fully Functional!** 
The MCP TTS server is working correctly with Cursor IDE. All 7 tools are registered and accessible through natural language interaction. **NEW:** Environment variable configuration allows complete customization without needing the web interface - perfect for uvx users!
