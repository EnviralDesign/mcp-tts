@echo off
cd /d "C:\repos\mcp-tts"
set PYTHONIOENCODING=utf-8
rem Prefer uv for running the module directly (no bare "python")
uv run -m src.mcp_server