"""
TTS Manager - coordinates TTS providers and audio playback.
"""

import logging
from typing import Dict, Optional

from tts.providers.base import TTSProvider, TTSRequest
from tts.providers.openai_fm import OpenAITTSProvider
from audio.player import AudioPlayer
from config import Config

logger = logging.getLogger(__name__)


class TTSManager:
    """Manages TTS providers and coordinates audio playback."""

    def __init__(self, config: Config):
        self.config = config
        self.audio_player = AudioPlayer(
            sample_rate=config.audio.sample_rate, buffer_size=config.audio.buffer_size
        )
        self.audio_player.set_volume(config.audio.volume)

        # Initialize providers
        self.providers: Dict[str, TTSProvider] = {}
        self._initialize_providers()

        # Set default provider
        self.current_provider = config.tts.provider

    def _initialize_providers(self):
        """Initialize available TTS providers."""
        try:
            # Initialize OpenAI provider if API key is available
            if self.config.openai_api_key:
                self.providers["openai"] = OpenAITTSProvider(self.config.openai_api_key)
                logger.info("OpenAI TTS provider initialized")
            else:
                logger.warning("OpenAI API key not provided - OpenAI TTS unavailable")

        except Exception as e:
            logger.error(f"Error initializing TTS providers: {e}")

    async def generate_and_play(
        self,
        text: str,
        voice: Optional[str] = None,
        instructions: Optional[str] = None,
        device_index: Optional[int] = None,
        speed: float = 1.0,
    ) -> bool:
        """
        Generate speech and play it through speakers.

        Args:
            text: Text to convert to speech
            voice: Voice to use (None for default)
            instructions: Voice style instructions
            device_index: Audio device to use (None for default)
            speed: Speech speed (0.25 to 4.0)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the current provider
            provider = self.get_current_provider()
            if not provider:
                logger.error("No TTS provider available")
                return False

            # Create TTS request
            request = TTSRequest(
                text=text,
                voice=voice or self.config.tts.voice,
                speed=speed,
                language=self.config.tts.language,
                instructions=instructions
                or self.config.get_current_voice_instructions(),
            )

            logger.info(f"Generating speech: {len(text)} chars with {provider.name}")

            # Generate audio
            audio_data = await provider.generate_speech(request)

            # Play audio
            success = await self.audio_player.play_audio_data(audio_data, device_index)

            if success:
                logger.info("Speech playback completed successfully")
            else:
                logger.error("Speech playback failed")

            return success

        except Exception as e:
            logger.error(f"Error in generate_and_play: {e}")
            return False

    async def generate_and_stream(
        self,
        text: str,
        voice: Optional[str] = None,
        instructions: Optional[str] = None,
        device_index: Optional[int] = None,
        speed: float = 1.0,
    ) -> bool:
        """
        Generate speech and stream it for real-time playback.

        Args:
            text: Text to convert to speech
            voice: Voice to use (None for default)
            instructions: Voice style instructions
            device_index: Audio device to use (None for default)
            speed: Speech speed (0.25 to 4.0)

        Returns:
            True if successful, False otherwise
        """
        try:
            provider = self.get_current_provider()
            if not provider:
                logger.error("No TTS provider available")
                return False

            request = TTSRequest(
                text=text,
                voice=voice or self.config.tts.voice,
                speed=speed,
                language=self.config.tts.language,
                instructions=instructions
                or self.config.get_current_voice_instructions(),
            )

            logger.info(f"Streaming speech: {len(text)} chars with {provider.name}")

            # Generate and stream audio
            audio_stream = provider.generate_speech_stream(request)
            success = await self.audio_player.stream_audio(audio_stream, device_index)

            if success:
                logger.info("Speech streaming completed successfully")
            else:
                logger.error("Speech streaming failed")

            return success

        except Exception as e:
            logger.error(f"Error in generate_and_stream: {e}")
            return False

    def get_current_provider(self) -> Optional[TTSProvider]:
        """Get the currently selected TTS provider."""
        return self.providers.get(self.current_provider)

    def set_provider(self, provider_name: str) -> bool:
        """
        Set the current TTS provider.

        Args:
            provider_name: Name of the provider to use

        Returns:
            True if provider was set successfully, False otherwise
        """
        if provider_name in self.providers:
            self.current_provider = provider_name
            logger.info(f"Switched to TTS provider: {provider_name}")
            return True
        else:
            logger.error(f"TTS provider not available: {provider_name}")
            return False

    def get_available_providers(self) -> list[str]:
        """Get list of available TTS provider names."""
        return list(self.providers.keys())

    def get_supported_voices(self) -> list[str]:
        """Get supported voices for the current provider."""
        provider = self.get_current_provider()
        if provider:
            return provider.get_supported_voices()
        return []

    def get_supported_languages(self) -> list[str]:
        """Get supported languages for the current provider."""
        provider = self.get_current_provider()
        if provider:
            return provider.get_supported_languages()
        return []

    def stop_playback(self):
        """Stop current audio playback."""
        self.audio_player.stop()

    def set_volume(self, volume: float):
        """Set audio playback volume (0.0 to 1.0)."""
        self.audio_player.set_volume(volume)
        self.config.audio.volume = volume

    def get_volume(self) -> float:
        """Get current audio playback volume."""
        return self.audio_player.get_volume()

    def get_audio_devices(self):
        """Get available audio output devices."""
        return AudioPlayer.get_audio_devices()

    def test_audio_device(self, device_index: Optional[int] = None) -> bool:
        """Test an audio device."""
        return AudioPlayer.test_device(device_index)

    async def test_tts_provider(self, provider_name: str) -> bool:
        """Test if a TTS provider is working."""
        provider = self.providers.get(provider_name)
        if not provider:
            return False

        if hasattr(provider, "test_connection"):
            return await provider.test_connection()
        else:
            # Generic test - try to generate a short phrase
            try:
                test_request = TTSRequest(
                    text="Test message", voice=self.config.tts.voice
                )
                audio_data = await provider.generate_speech(test_request)
                return len(audio_data) > 0
            except Exception:
                return False

    def get_status(self) -> dict:
        """Get current TTS manager status."""
        return {
            "current_provider": self.current_provider,
            "available_providers": self.get_available_providers(),
            "is_playing": self.audio_player.is_playing,
            "volume": self.get_volume(),
            "supported_voices": self.get_supported_voices(),
            "supported_languages": self.get_supported_languages(),
            "audio_devices": [
                {
                    "index": device.index,
                    "name": device.name,
                    "channels": device.channels,
                    "is_default": device.is_default,
                }
                for device in self.get_audio_devices()
            ],
        }
