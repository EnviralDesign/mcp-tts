"""
FastAPI routes for the TTS server web interface.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from tts.manager import TTSManager
from config import Config, VOICE_PRESETS

logger = logging.getLogger(__name__)

# Global TTS manager instance (will be initialized when server starts)
tts_manager: Optional[TTSManager] = None


# Pydantic models for API requests/responses
class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = None
    voice_instructions: Optional[str] = None
    speed: float = 1.0
    device_index: Optional[int] = None
    stream: bool = False


class VolumeRequest(BaseModel):
    volume: float


class DeviceTestRequest(BaseModel):
    device_index: Optional[int] = None


class AudioDevice(BaseModel):
    index: int
    name: str
    channels: int
    sample_rate: float
    is_default: bool


class ServerStatus(BaseModel):
    current_provider: str
    available_providers: List[str]
    is_playing: bool
    volume: float
    supported_voices: List[str]
    supported_languages: List[str]
    audio_devices: List[AudioDevice]


class ConfigUpdateRequest(BaseModel):
    voice: Optional[str] = None
    speed: Optional[float] = None
    preset: Optional[str] = None
    custom_instructions: Optional[str] = None
    audio_device: Optional[str] = None
    audio_device_index: Optional[int] = None
    volume: Optional[float] = None


class VoicePreset(BaseModel):
    id: str
    name: str
    description: str
    instructions: str


def create_api_routes() -> APIRouter:
    """Create and configure API routes."""
    router = APIRouter()

    @router.get("/status", response_model=ServerStatus)
    async def get_status():
        """Get current server status."""
        if not tts_manager:
            raise HTTPException(status_code=503, detail="TTS manager not initialized")

        status = tts_manager.get_status()

        return ServerStatus(
            current_provider=status["current_provider"],
            available_providers=status["available_providers"],
            is_playing=status["is_playing"],
            volume=status["volume"],
            supported_voices=status["supported_voices"],
            supported_languages=status["supported_languages"],
            audio_devices=[AudioDevice(**device) for device in status["audio_devices"]],
        )

    @router.get("/devices", response_model=List[AudioDevice])
    async def get_audio_devices():
        """Get available audio output devices."""
        if not tts_manager:
            raise HTTPException(status_code=503, detail="TTS manager not initialized")

        devices = tts_manager.get_audio_devices()
        return [
            AudioDevice(
                index=device.index,
                name=device.name,
                channels=device.channels,
                sample_rate=device.sample_rate,
                is_default=device.is_default,
            )
            for device in devices
        ]

    @router.post("/test-device")
    async def test_audio_device(request: DeviceTestRequest):
        """Test an audio device."""
        if not tts_manager:
            raise HTTPException(status_code=503, detail="TTS manager not initialized")

        success = tts_manager.test_audio_device(request.device_index)

        if success:
            device_info = (
                "default device"
                if request.device_index is None
                else f"device {request.device_index}"
            )
            return {
                "success": True,
                "message": f"Audio test successful for {device_info}",
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Audio test failed for device {request.device_index}",
            )

    @router.post("/speak")
    async def text_to_speech(request: TTSRequest, background_tasks: BackgroundTasks):
        """Convert text to speech and play it."""
        if not tts_manager:
            raise HTTPException(status_code=503, detail="TTS manager not initialized")

        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        # Validate speed
        if not 0.25 <= request.speed <= 4.0:
            raise HTTPException(
                status_code=400, detail="Speed must be between 0.25 and 4.0"
            )

        # Run TTS in background
        if request.stream:
            background_tasks.add_task(
                tts_manager.generate_and_stream,
                text=request.text,
                voice=request.voice,
                instructions=request.voice_instructions,
                device_index=request.device_index,
                speed=request.speed,
            )
        else:
            background_tasks.add_task(
                tts_manager.generate_and_play,
                text=request.text,
                voice=request.voice,
                instructions=request.voice_instructions,
                device_index=request.device_index,
                speed=request.speed,
            )

        return {
            "success": True,
            "message": f"Started TTS for {len(request.text)} characters",
            "streaming": request.stream,
        }

    @router.post("/stop")
    async def stop_speech():
        """Stop current speech playback."""
        if not tts_manager:
            raise HTTPException(status_code=503, detail="TTS manager not initialized")

        tts_manager.stop_playback()
        return {"success": True, "message": "Speech playback stopped"}

    @router.post("/volume")
    async def set_volume(request: VolumeRequest):
        """Set audio playback volume."""
        if not tts_manager:
            raise HTTPException(status_code=503, detail="TTS manager not initialized")

        if not 0.0 <= request.volume <= 1.0:
            raise HTTPException(
                status_code=400, detail="Volume must be between 0.0 and 1.0"
            )

        tts_manager.set_volume(request.volume)
        return {"success": True, "message": f"Volume set to {request.volume:.1%}"}

    @router.get("/volume")
    async def get_volume():
        """Get current audio playback volume."""
        if not tts_manager:
            raise HTTPException(status_code=503, detail="TTS manager not initialized")

        volume = tts_manager.get_volume()
        return {"volume": volume}

    @router.get("/voices")
    async def get_supported_voices():
        """Get supported voices for the current provider."""
        if not tts_manager:
            raise HTTPException(status_code=503, detail="TTS manager not initialized")

        voices = tts_manager.get_supported_voices()
        return {"voices": voices}

    @router.get("/languages")
    async def get_supported_languages():
        """Get supported languages for the current provider."""
        if not tts_manager:
            raise HTTPException(status_code=503, detail="TTS manager not initialized")

        languages = tts_manager.get_supported_languages()
        return {"languages": languages}

    @router.get("/providers")
    async def get_available_providers():
        """Get available TTS providers."""
        if not tts_manager:
            raise HTTPException(status_code=503, detail="TTS manager not initialized")

        providers = tts_manager.get_available_providers()
        return {"providers": providers}

    @router.post("/provider/{provider_name}")
    async def set_provider(provider_name: str):
        """Set the current TTS provider."""
        if not tts_manager:
            raise HTTPException(status_code=503, detail="TTS manager not initialized")

        success = tts_manager.set_provider(provider_name)

        if success:
            return {
                "success": True,
                "message": f"Switched to provider: {provider_name}",
            }
        else:
            raise HTTPException(
                status_code=400, detail=f"Provider not available: {provider_name}"
            )

    @router.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "server": "MCP TTS Server", "version": "0.1.0"}

    @router.get("/config/presets", response_model=List[VoicePreset])
    async def get_voice_presets():
        """Get available voice presets."""
        return [
            VoicePreset(
                id=preset_id,
                name=preset["name"],
                description=preset["description"],
                instructions=preset["instructions"],
            )
            for preset_id, preset in VOICE_PRESETS.items()
        ]

    @router.get("/config/current")
    async def get_current_config():
        """Get current configuration."""
        if not tts_manager:
            raise HTTPException(status_code=503, detail="TTS manager not initialized")

        config = tts_manager.config
        return {
            "voice": config.tts.voice,
            "speed": config.tts.speed,
            "current_preset": config.tts.current_preset,
            "custom_instructions": config.tts.custom_instructions,
            "current_voice_instructions": config.get_current_voice_instructions(),
            "audio_device": config.audio.default_device,
            "audio_device_index": config.audio.default_device_index,
            "volume": config.audio.volume,
        }

    @router.post("/config/update")
    async def update_config(request: ConfigUpdateRequest):
        """Update configuration settings."""
        if not tts_manager:
            raise HTTPException(status_code=503, detail="TTS manager not initialized")

        config = tts_manager.config
        updated = []

        if request.voice is not None:
            config.tts.voice = request.voice
            updated.append(f"voice: {request.voice}")

        if request.speed is not None:
            if not 0.25 <= request.speed <= 4.0:
                raise HTTPException(
                    status_code=400, detail="Speed must be between 0.25 and 4.0"
                )
            config.tts.speed = request.speed
            updated.append(f"speed: {request.speed}")

        if request.preset is not None:
            if request.preset in VOICE_PRESETS:
                config.tts.current_preset = request.preset
                config.tts.custom_instructions = ""  # Clear custom when using preset
                updated.append(f"preset: {request.preset}")
            else:
                raise HTTPException(
                    status_code=400, detail=f"Unknown preset: {request.preset}"
                )

        if request.custom_instructions is not None:
            config.tts.custom_instructions = request.custom_instructions
            if request.custom_instructions.strip():
                config.tts.current_preset = "custom"
                updated.append("custom instructions set")

        if request.audio_device is not None:
            config.audio.default_device = request.audio_device
            updated.append(f"audio device: {request.audio_device}")

        if request.audio_device_index is not None:
            config.audio.default_device_index = request.audio_device_index
            updated.append(f"audio device index: {request.audio_device_index}")

        if request.volume is not None:
            if not 0.0 <= request.volume <= 1.0:
                raise HTTPException(
                    status_code=400, detail="Volume must be between 0.0 and 1.0"
                )
            config.audio.volume = request.volume
            tts_manager.set_volume(request.volume)
            updated.append(f"volume: {request.volume:.1%}")

        # Save settings
        config.save_user_settings()

        return {
            "success": True,
            "message": f"Updated: {', '.join(updated)}",
            "updated_fields": updated,
        }

    @router.post("/config/reset")
    async def reset_config():
        """Reset configuration to defaults."""
        if not tts_manager:
            raise HTTPException(status_code=503, detail="TTS manager not initialized")

        # Reset to defaults
        config = tts_manager.config
        config.tts.voice = "ballad"
        config.tts.speed = 1.0
        config.tts.current_preset = "default"
        config.tts.custom_instructions = ""
        config.audio.volume = 0.8
        config.audio.default_device = None
        config.audio.default_device_index = None

        # Apply volume change
        tts_manager.set_volume(config.audio.volume)

        # Save settings
        config.save_user_settings()

        return {"success": True, "message": "Configuration reset to defaults"}

    return router


def initialize_tts_manager(config: Config):
    """Initialize the global TTS manager."""
    global tts_manager
    tts_manager = TTSManager(config)
    logger.info("TTS Manager initialized for API routes")
