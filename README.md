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

## 🎵 Usage Examples

- *"Use text-to-speech to explain this code"*
- *"Read me the changes you just made"*  
- *"List my audio devices"*
- *"Switch to a professional voice style"*

## 📚 Full Documentation

For advanced configuration, voice presets, troubleshooting, and development setup, see [SETUP_GUIDE.md](SETUP_GUIDE.md).

---

**Status:** ✅ Working with Cursor IDE • 🎵 7 TTS tools available • 🔊 Cross-platform audio
