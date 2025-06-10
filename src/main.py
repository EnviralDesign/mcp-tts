#!/usr/bin/env python3
"""
MCP Text-to-Speech Server for Cursor IDE
Provides TTS capabilities through an MCP server with cross-platform audio playback.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

import uvicorn  # noqa: E402
from fastapi import FastAPI, Request  # noqa: E402
from fastapi.responses import HTMLResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

from api.routes import create_api_routes, initialize_tts_manager  # noqa: E402
from config import Config  # noqa: E402

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app(config: Config) -> FastAPI:
    """Create the FastAPI application with MCP server integration."""
    app = FastAPI(
        title="MCP TTS Server",
        description="Text-to-Speech server with MCP protocol support",
        version="0.1.0",
    )

    # Initialize TTS manager for API routes
    initialize_tts_manager(config)

    # Add API routes
    api_routes = create_api_routes()
    app.include_router(api_routes, prefix="/api")

    # Serve static files
    if os.path.exists("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def read_root(request: Request):
        """Serve the main web UI."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>MCP TTS Server</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; background: #f8f9fa; }
                .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .status { padding: 20px; border-radius: 8px; margin: 20px 0; }
                .status.running { background-color: #d4edda; border: 1px solid #c3e6cb; }
                .status.error { background-color: #f8d7da; border: 1px solid #f5c6cb; }
                
                .config-section { margin: 30px 0; padding: 25px; background: #f8f9fa; border-radius: 10px; border: 1px solid #e9ecef; }
                .config-section h2 { margin-top: 0; color: #333; }
                
                .tools-section { margin: 30px 0; padding: 25px; background: #f0f9ff; border-radius: 10px; border: 1px solid #bae6fd; }
                .tools-section h2 { margin-top: 0; color: #333; }
                .tools-list { margin: 15px 0; }
                .tools-list li { margin: 10px 0; padding: 8px 0; }
                
                .troubleshooting { margin: 20px 0; padding: 20px; background: #fef3f2; border-radius: 8px; border: 1px solid #fed7d3; }
                .troubleshooting h4 { margin: 15px 0 10px 0; color: #991b1b; }
                .troubleshooting ol, .troubleshooting ul { margin: 10px 0; padding-left: 20px; }
                .troubleshooting li { margin: 6px 0; line-height: 1.4; }
                .troubleshooting strong { color: #7c2d12; }
                
                .code-block { margin: 20px 0; border: 1px solid #d1d5db; border-radius: 8px; overflow: hidden; }
                .code-header { background: #374151; color: white; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; font-size: 14px; font-weight: 600; }
                .copy-btn { background: #4ade80; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 12px; }
                .copy-btn:hover { background: #22c55e; }
                .copy-btn.copied { background: #059669; }
                
                pre { margin: 0; padding: 20px; background: #1f2937; color: #f9fafb; font-family: 'Courier New', monospace; font-size: 14px; line-height: 1.5; overflow-x: auto; }
                code { background: #e5e7eb; padding: 2px 6px; border-radius: 4px; font-family: 'Courier New', monospace; font-size: 14px; }
                
                h1 { color: #1f2937; margin-bottom: 10px; }
                h2 { color: #374151; margin-bottom: 15px; }
                ul { margin: 20px 0; }
                li { margin: 8px 0; }
                a { color: #3b82f6; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>MCP Text-to-Speech Server</h1>
                <div class="status running">
                    <h2>✅ Server Running</h2>
                    <p>The MCP TTS server is running on port 8742</p>
                    <p>Configure Cursor to use this server for text-to-speech capabilities.</p>
                </div>
                
                <div class="config-section">
                    <h2>🔌 Cursor MCP Integration</h2>
                    <p>Add this configuration to your Cursor MCP settings file:</p>
                    <p><strong>File location:</strong> <code>~/.cursor/mcp.json</code> (or <code>C:\\Users\\[username]\\.cursor\\mcp.json</code> on Windows)</p>
                    
                    <div class="code-block">
                        <div class="code-header">
                            <span>mcp.json - Option 1 (Recommended)</span>
                            <button onclick="copyToClipboard('config1')" class="copy-btn">📋 Copy</button>
                        </div>
                        <pre id="mcp-config">{
  "mcpServers": {
    "mcp_tts_server": {
      "command": "C:/repos/mcp-cursor-tts/start-mcp-tts.bat"
    }
  }
}</pre>
                    </div>
                    
                    <div class="code-block" style="margin-top: 15px;">
                        <div class="code-header">
                            <span>mcp.json - Option 2 (Alternative)</span>
                            <button onclick="copyToClipboard('config2')" class="copy-btn">📋 Copy</button>
                        </div>
                        <pre id="mcp-config-alt">{
  "mcpServers": {
    "mcp_tts_server": {
      "command": "uv",
      "args": ["--directory", "C:/repos/mcp-cursor-tts", "run", "python", "src/mcp_server.py"],
      "env": {}
    }
  }
}</pre>
                    </div>
                    <div class="troubleshooting">
                        <h4>📝 Setup Instructions:</h4>
                        <ol>
                            <li>Copy one of the configurations above</li>
                            <li>Open your Cursor MCP settings (Settings → MCP → Add New Global MCP Server)</li>
                            <li>Paste the configuration into your <code>mcp.json</code> file</li>
                            <li><strong>Important:</strong> Update the path <code>C:/repos/mcp-cursor-tts</code> to your actual project location</li>
                            <li>For Option 2: Replace <code>[USERNAME]</code> with your actual Windows username</li>
                            <li>Restart Cursor or click the refresh button in MCP settings</li>
                        </ol>
                        
                        <h4>🔧 Troubleshooting:</h4>
                        <ul>
                            <li><strong>Server shows but 0 tools:</strong> This was a common issue that we've now fixed! Try the updated configuration above.</li>
                            <li><strong>Command not found:</strong> Try Option 2 with the full path to <code>uv.exe</code></li>
                            <li><strong>Connection issues:</strong> Ensure the project path is correct and matches your actual location</li>
                            <li><strong>Tools not working in chat:</strong> Make sure you're in Agent mode and try mentioning tools by name</li>
                            <li><strong>Environment issues:</strong> Verify you have a valid OpenAI API key in your <code>.env</code> file</li>
                        </ul>
                        
                        <p><strong>✅ Success indicators:</strong> You should see "mcp_tts_server" or "tts_server" in your MCP settings with <span style="color: #059669; font-weight: bold;">6 tools enabled</span>.</p>
                        
                        <div style="margin: 15px 0; padding: 15px; background: #d1fae5; border-radius: 8px; border: 1px solid #059669;">
                            <strong>🎉 Recent Fix:</strong> We've resolved the "0 tools enabled" issue by simplifying the MCP server implementation. 
                            The server now properly registers all 6 tools and should work reliably with Cursor.
                        </div>
                    </div>
                </div>
                
                <div class="tools-section">
                    <h2>🛠️ Available MCP Tools</h2>
                    <p>Once connected to Cursor, your AI assistant will have access to these tools:</p>
                    <ul class="tools-list">
                        <li><strong>🎵 text_to_speech</strong> - Convert text to speech with customizable voices and styles</li>
                        <li><strong>🔊 list_audio_devices</strong> - Show available audio output devices</li>
                        <li><strong>🧪 test_audio_device</strong> - Test audio device with a tone</li>
                        <li><strong>⏹️ stop_speech</strong> - Stop current audio playback</li>
                        <li><strong>📊 get_tts_status</strong> - Get server status and configuration</li>
                        <li><strong>🔈 set_volume</strong> - Adjust playback volume</li>
                    </ul>
                    <p><em>Example: "Can you read me a summary of the changes you just made using text-to-speech with a professional voice?"</em></p>
                </div>

                <div>
                    <h2>Quick Links</h2>
                    <ul>
                        <li><a href="/config">⚙️ Configuration</a> - Voice and audio settings</li>
                        <li><a href="/api/devices">🔊 Audio Devices</a> - List available audio output devices</li>
                        <li><a href="/api/health">❤️ Server Health</a> - Current server health</li>
                        <li><a href="/docs">📚 API Documentation</a> - OpenAPI docs</li>
                    </ul>
                </div>
            </div>
            
            <script>
                async function copyToClipboard(configId = 'config1') {
                    let configText, copyBtn;
                    
                    if (configId === 'config1') {
                        configText = document.getElementById('mcp-config').textContent;
                        copyBtn = document.querySelector('.copy-btn');
                    } else {
                        configText = document.getElementById('mcp-config-alt').textContent;
                        copyBtn = document.querySelectorAll('.copy-btn')[1];
                    }
                    
                    try {
                        await navigator.clipboard.writeText(configText);
                        copyBtn.textContent = '✅ Copied!';
                        copyBtn.classList.add('copied');
                        
                        setTimeout(() => {
                            copyBtn.textContent = '📋 Copy';
                            copyBtn.classList.remove('copied');
                        }, 2000);
                    } catch (err) {
                        // Fallback for older browsers
                        const textArea = document.createElement('textarea');
                        textArea.value = configText;
                        document.body.appendChild(textArea);
                        textArea.select();
                        document.execCommand('copy');
                        document.body.removeChild(textArea);
                        
                        copyBtn.textContent = '✅ Copied!';
                        copyBtn.classList.add('copied');
                        
                        setTimeout(() => {
                            copyBtn.textContent = '📋 Copy';
                            copyBtn.classList.remove('copied');
                        }, 2000);
                    }
                }
            </script>
        </body>
        </html>
        """

    @app.get("/config", response_class=HTMLResponse)
    async def config_page(request: Request):
        """Serve the configuration page."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>MCP TTS Server - Configuration</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 1000px; margin: 0 auto; background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #333; margin-bottom: 30px; }
                .section { margin-bottom: 30px; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; }
                .section h2 { margin-top: 0; color: #555; }
                .form-group { margin-bottom: 20px; }
                label { display: block; margin-bottom: 5px; font-weight: 600; color: #333; }
                select, input, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
                textarea { height: 120px; resize: vertical; font-family: monospace; }
                .preset-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
                .preset-card { border: 2px solid #e0e0e0; border-radius: 8px; padding: 15px; cursor: pointer; transition: all 0.2s; }
                .preset-card:hover { border-color: #007bff; }
                .preset-card.active { border-color: #007bff; background: #f0f8ff; }
                .preset-card h3 { margin: 0 0 8px 0; color: #333; font-size: 16px; }
                .preset-card p { margin: 0; color: #666; font-size: 14px; }
                .button-group { display: flex; gap: 10px; margin-top: 20px; }
                button { padding: 12px 24px; border: none; border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
                .btn-primary { background: #007bff; color: white; }
                .btn-primary:hover { background: #0056b3; }
                .btn-secondary { background: #6c757d; color: white; }
                .btn-secondary:hover { background: #545b62; }
                .btn-danger { background: #dc3545; color: white; }
                .btn-danger:hover { background: #c82333; }
                .btn-success { background: #28a745; color: white; }
                .btn-success:hover { background: #218838; }
                .status { padding: 15px; border-radius: 6px; margin: 10px 0; }
                .status.success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
                .status.error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
                .range-container { display: flex; align-items: center; gap: 10px; }
                .range-container input[type="range"] { flex: 1; }
                .range-container span { min-width: 60px; font-weight: 600; color: #555; }
                .back-link { margin-bottom: 20px; }
                .back-link a { color: #007bff; text-decoration: none; }
                .back-link a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="back-link">
                    <a href="/">← Back to Main</a>
                </div>
                <h1>⚙️ TTS Configuration</h1>
                <div id="status"></div>
                
                <div class="section">
                    <h2>🎵 Voice Settings</h2>
                    <div class="form-group">
                        <label for="voice">Voice:</label>
                        <select id="voice">
                            <option value="alloy">Alloy</option>
                            <option value="echo">Echo</option>
                            <option value="fable">Fable</option>
                            <option value="onyx">Onyx</option>
                            <option value="nova">Nova</option>
                            <option value="shimmer">Shimmer</option>
                            <option value="ballad">Ballad</option>
                            <option value="verse">Verse</option>
                            <option value="ash">Ash</option>
                            <option value="coral">Coral</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="speed">Speed:</label>
                        <div class="range-container">
                            <input type="range" id="speed" min="0.25" max="4.0" step="0.25" value="1.0">
                            <span id="speed-value">1.0x</span>
                        </div>
                    </div>
                </div>

                                 <div class="section">
                     <h2>🎭 Voice Style Templates</h2>
                     <div id="preset-grid" class="preset-grid">
                         <!-- Presets will be loaded here -->
                     </div>
                    
                                         <div class="form-group">
                         <label for="custom-instructions">Current Voice Instructions:</label>
                         <textarea id="custom-instructions" placeholder="Select a preset above or enter custom voice instructions here..."></textarea>
                         <small style="color: #666;">This shows the current active voice instructions. Click any preset above to populate this field as a starting point, then edit as needed.</small>
                     </div>
                </div>

                <div class="section">
                    <h2>🔊 Audio Settings</h2>
                    <div class="form-group">
                        <label for="audio-device">Audio Device:</label>
                        <select id="audio-device">
                            <option value="">Default Device</option>
                            <!-- Devices will be loaded here -->
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="volume">Volume:</label>
                        <div class="range-container">
                            <input type="range" id="volume" min="0" max="1" step="0.1" value="0.8">
                            <span id="volume-value">80%</span>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>🧪 Test & Controls</h2>
                    <div class="form-group">
                        <label for="test-text">Test Text:</label>
                        <textarea id="test-text" style="height: 80px;">Hello! This is a test of the current voice settings. You should hear this message with the selected voice, speed, and style.</textarea>
                    </div>
                    <div class="button-group">
                        <button class="btn-success" onclick="testSpeech()">🎵 Test Speech</button>
                        <button class="btn-secondary" onclick="stopSpeech()">⏹️ Stop</button>
                    </div>
                </div>

                <div class="button-group">
                    <button class="btn-primary" onclick="saveConfig()">💾 Save Settings</button>
                    <button class="btn-danger" onclick="resetConfig()">🔄 Reset to Defaults</button>
                </div>
            </div>

            <script>
                let currentConfig = {};
                let presets = {};

                // Load initial data
                async function loadData() {
                    try {
                        // Load presets
                        const presetsResponse = await fetch('/api/config/presets');
                        const presetsData = await presetsResponse.json();
                        presets = {};
                        presetsData.forEach(preset => {
                            presets[preset.id] = preset;
                        });
                        renderPresets();

                        // Load current config
                        const configResponse = await fetch('/api/config/current');
                        currentConfig = await configResponse.json();
                        updateUI();

                        // Load audio devices
                        const devicesResponse = await fetch('/api/devices');
                        const devices = await devicesResponse.json();
                        renderAudioDevices(devices);

                    } catch (error) {
                        showStatus('Error loading configuration: ' + error.message, 'error');
                    }
                }

                function renderPresets() {
                    const grid = document.getElementById('preset-grid');
                    grid.innerHTML = '';
                    
                    Object.entries(presets).forEach(([id, preset]) => {
                        const card = document.createElement('div');
                        card.className = 'preset-card';
                        card.onclick = () => selectPreset(id);
                        card.innerHTML = `
                            <h3>${preset.name}</h3>
                            <p>${preset.description}</p>
                        `;
                        grid.appendChild(card);
                    });
                }

                function renderAudioDevices(devices) {
                    const select = document.getElementById('audio-device');
                    select.innerHTML = '<option value="">Default Device</option>';
                    
                    devices.forEach(device => {
                        const option = document.createElement('option');
                        option.value = device.index;
                        option.textContent = `${device.name}${device.is_default ? ' (Default)' : ''}`;
                        select.appendChild(option);
                    });
                }

                                 function updateUI() {
                     document.getElementById('voice').value = currentConfig.voice || 'ballad';
                     document.getElementById('speed').value = currentConfig.speed || 1.0;
                     document.getElementById('speed-value').textContent = `${currentConfig.speed || 1.0}x`;
                     document.getElementById('volume').value = currentConfig.volume || 0.8;
                     document.getElementById('volume-value').textContent = `${Math.round((currentConfig.volume || 0.8) * 100)}%`;
                     document.getElementById('audio-device').value = currentConfig.audio_device_index || '';

                     // Always show the current active voice instructions in the textarea
                     const currentInstructions = currentConfig.current_voice_instructions || '';
                     document.getElementById('custom-instructions').value = currentInstructions;

                     // Update preset selection visual
                     document.querySelectorAll('.preset-card').forEach(card => {
                         card.classList.remove('active');
                     });
                     
                     if (currentConfig.current_preset && currentConfig.current_preset !== 'custom') {
                         const activeCard = Array.from(document.querySelectorAll('.preset-card')).find(card => {
                             return card.querySelector('h3').textContent === presets[currentConfig.current_preset]?.name;
                         });
                         if (activeCard) activeCard.classList.add('active');
                     }
                 }

                                 function selectPreset(presetId) {
                     if (presets[presetId]) {
                         // Populate the custom instructions field with the preset's instructions
                         const presetInstructions = presets[presetId].instructions;
                         document.getElementById('custom-instructions').value = presetInstructions;
                         
                         // Update the config to reflect this preset selection
                         currentConfig.current_preset = presetId;
                         currentConfig.current_voice_instructions = presetInstructions;
                         
                         // Update visual selection
                         document.querySelectorAll('.preset-card').forEach(card => {
                             card.classList.remove('active');
                         });
                         
                         const activeCard = Array.from(document.querySelectorAll('.preset-card')).find(card => {
                             return card.querySelector('h3').textContent === presets[presetId].name;
                         });
                         if (activeCard) activeCard.classList.add('active');
                     }
                 }

                // Event listeners
                document.getElementById('speed').addEventListener('input', (e) => {
                    document.getElementById('speed-value').textContent = `${e.target.value}x`;
                });

                document.getElementById('volume').addEventListener('input', (e) => {
                    document.getElementById('volume-value').textContent = `${Math.round(e.target.value * 100)}%`;
                });

                                 document.getElementById('custom-instructions').addEventListener('input', (e) => {
                     // When user manually edits, clear preset selection and mark as custom
                     const currentInstructions = currentConfig.current_voice_instructions || '';
                     if (e.target.value !== currentInstructions) {
                         document.querySelectorAll('.preset-card').forEach(card => {
                             card.classList.remove('active');
                         });
                         currentConfig.current_preset = 'custom';
                         currentConfig.current_voice_instructions = e.target.value;
                     }
                 });

                                 async function saveConfig() {
                     try {
                         const customInstructionsValue = document.getElementById('custom-instructions').value;
                         
                         const config = {
                             voice: document.getElementById('voice').value,
                             speed: parseFloat(document.getElementById('speed').value),
                             volume: parseFloat(document.getElementById('volume').value),
                             audio_device_index: document.getElementById('audio-device').value || null,
                             custom_instructions: customInstructionsValue
                         };

                         // Check if the current instructions match a preset exactly
                         let matchingPreset = null;
                         for (const [presetId, preset] of Object.entries(presets)) {
                             if (preset.instructions === customInstructionsValue) {
                                 matchingPreset = presetId;
                                 break;
                             }
                         }

                         if (matchingPreset) {
                             // Instructions match a preset, save as preset
                             config.preset = matchingPreset;
                             config.custom_instructions = ''; // Clear custom since we're using preset
                         } else {
                             // Custom instructions, save as custom
                             config.custom_instructions = customInstructionsValue;
                         }

                        const response = await fetch('/api/config/update', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(config)
                        });

                        const result = await response.json();
                        if (result.success) {
                            showStatus('✅ ' + result.message, 'success');
                            loadData(); // Reload current config
                        } else {
                            showStatus('❌ Failed to save: ' + result.message, 'error');
                        }
                    } catch (error) {
                        showStatus('❌ Error saving: ' + error.message, 'error');
                    }
                }

                async function resetConfig() {
                    if (!confirm('Reset all settings to defaults?')) return;
                    
                    try {
                        const response = await fetch('/api/config/reset', { method: 'POST' });
                        const result = await response.json();
                        
                        if (result.success) {
                            showStatus('✅ ' + result.message, 'success');
                            loadData(); // Reload data
                        } else {
                            showStatus('❌ Failed to reset: ' + result.message, 'error');
                        }
                    } catch (error) {
                        showStatus('❌ Error resetting: ' + error.message, 'error');
                    }
                }

                async function testSpeech() {
                    try {
                        const text = document.getElementById('test-text').value;
                        if (!text.trim()) {
                            showStatus('❌ Please enter some test text', 'error');
                            return;
                        }

                        const config = {
                            text: text,
                            voice: document.getElementById('voice').value,
                            speed: parseFloat(document.getElementById('speed').value),
                            device_index: document.getElementById('audio-device').value || null
                        };

                                                 // Always use whatever is currently in the instructions field
                         const currentInstructions = document.getElementById('custom-instructions').value;
                         if (currentInstructions.trim()) {
                             config.voice_instructions = currentInstructions;
                         }

                        showStatus('🎵 Playing test speech...', 'success');

                        const response = await fetch('/api/speak', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(config)
                        });

                        const result = await response.json();
                        if (result.success) {
                            showStatus('✅ Test speech started', 'success');
                        } else {
                            showStatus('❌ Test failed: ' + result.message, 'error');
                        }
                    } catch (error) {
                        showStatus('❌ Error testing speech: ' + error.message, 'error');
                    }
                }

                async function stopSpeech() {
                    try {
                        const response = await fetch('/api/stop', { method: 'POST' });
                        const result = await response.json();
                        showStatus('⏹️ Speech stopped', 'success');
                    } catch (error) {
                        showStatus('❌ Error stopping speech: ' + error.message, 'error');
                    }
                }

                function showStatus(message, type) {
                    const status = document.getElementById('status');
                    status.className = `status ${type}`;
                    status.textContent = message;
                    setTimeout(() => {
                        status.textContent = '';
                        status.className = '';
                    }, 5000);
                }

                // Load data on page load
                loadData();
            </script>
        </body>
        </html>
        """

    return app


async def run_web_server(config: Config):
    """Run the web server."""
    app = create_app(config)

    # Create uvicorn config
    uvicorn_config = uvicorn.Config(
        app, host=config.host, port=config.port, log_level="info"
    )

    # Create and run server
    server = uvicorn.Server(uvicorn_config)
    await server.serve()


async def main_async():
    """Async main entry point for the MCP TTS server."""
    logger.info("Starting MCP TTS Server Web Interface...")

    # Load configuration
    config = Config.load()

    # Run the web server for configuration and testing
    # MCP server runs separately via src/mcp_server.py when called by Cursor
    logger.info(f"Starting web server on http://{config.host}:{config.port}")
    await run_web_server(config)


def main():
    """Main entry point for the MCP TTS server."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
