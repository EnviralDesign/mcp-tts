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
echo 🔑 Publishing to PyPI with uv...
echo ⚠️  Make sure you have your PyPI token ready!
echo.
uv publish

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