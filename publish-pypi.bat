@echo off
echo.
echo 📦 MCP-TTS PyPI Publisher
echo =========================
echo.

echo 🔍 Checking current git status...
git status --porcelain
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error checking git status
    pause
    exit /b 1
)

echo.
echo 🧹 Cleaning previous builds...
if exist "dist\" (
    rmdir /s /q "dist"
    echo ✅ Removed old dist/ folder
)

echo.
echo 🔧 Installing build dependencies...
uv add --dev build twine
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install build dependencies
    pause
    exit /b 1
)

echo.
echo 🏗️ Building package...
uv run python -m build
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Build failed!
    pause
    exit /b 1
)

echo.
echo 📋 Checking package...
uv run python -m twine check dist/*
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Package check failed!
    pause
    exit /b 1
)

echo.
echo 🔑 Publishing to PyPI...
echo ⚠️  Make sure you have your PyPI token ready!
echo.
uv run python -m twine upload dist/*

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Successfully published to PyPI!
    echo 🌐 Check it out: https://pypi.org/project/mcp-tts/
    echo.
    echo 💡 Don't forget to:
    echo   1. Push your changes: git push origin main
    echo   2. Create a GitHub release if desired
) else (
    echo.
    echo ❌ Publishing failed!
    echo 💡 Make sure you have a valid PyPI token configured
)

echo.
pause 