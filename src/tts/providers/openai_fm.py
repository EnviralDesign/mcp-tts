"""
OpenAI TTS provider using the OpenAI FM API.
"""

import logging
from typing import AsyncIterator
from openai import AsyncOpenAI

from .base import TTSProvider, TTSRequest

logger = logging.getLogger(__name__)


class OpenAITTSProvider(TTSProvider):
    """OpenAI TTS provider using the FM API with promptable voice styles."""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self._supported_voices = [
            "alloy",
            "echo",
            "fable",
            "onyx",
            "nova",
            "shimmer",
            "ballad",
            "verse",
            "ash",
            "coral",  # FM API voices
        ]
        self._supported_languages = [
            "en",
            "es",
            "fr",
            "de",
            "it",
            "pt",
            "ru",
            "ja",
            "ko",
            "zh",
        ]

    async def generate_speech(self, request: TTSRequest) -> bytes:
        """Generate speech audio from text using OpenAI TTS."""
        try:
            logger.info(f"Generating speech for {len(request.text)} characters")

            # Prepare the TTS request
            tts_kwargs = {
                "model": "gpt-4o-mini-tts",  # Updated model from OpenAI
                "voice": request.voice,
                "input": request.text,
                "speed": request.speed,
                "response_format": "pcm",  # Raw PCM for direct playback
            }

            # Add voice instructions if available (for FM API)
            if request.instructions:
                tts_kwargs["instructions"] = request.instructions

            response = await self.client.audio.speech.create(**tts_kwargs)

            # Read the audio content
            audio_data = response.content

            logger.info(f"Generated {len(audio_data)} bytes of audio")
            return audio_data

        except Exception as e:
            logger.error(f"Error generating speech with OpenAI: {e}")
            raise

    async def generate_speech_stream(self, request: TTSRequest) -> AsyncIterator[bytes]:
        """Generate speech audio as a stream."""
        try:
            logger.info(f"Streaming speech for {len(request.text)} characters")

            # Prepare the TTS request for streaming
            tts_kwargs = {
                "model": "gpt-4o-mini-tts",
                "voice": request.voice,
                "input": request.text,
                "speed": request.speed,
                "response_format": "pcm",
            }

            # Add voice instructions if available
            if request.instructions:
                tts_kwargs["instructions"] = request.instructions

            # Use streaming response
            async with self.client.audio.speech.with_streaming_response.create(
                **tts_kwargs
            ) as response:
                async for chunk in response.iter_bytes():
                    yield chunk

        except Exception as e:
            logger.error(f"Error streaming speech with OpenAI: {e}")
            raise

    def get_supported_voices(self) -> list[str]:
        """Get list of supported voice names."""
        return self._supported_voices.copy()

    def get_supported_languages(self) -> list[str]:
        """Get list of supported language codes."""
        return self._supported_languages.copy()

    @property
    def name(self) -> str:
        """Provider name."""
        return "openai"

    async def test_connection(self) -> bool:
        """Test if the OpenAI API connection is working."""
        try:
            # Test with a short phrase
            test_request = TTSRequest(
                text="Hello, this is a test.", voice="alloy", speed=1.0
            )

            audio_data = await self.generate_speech(test_request)
            return len(audio_data) > 0

        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False

    def create_voice_instruction(
        self,
        tone: str = "friendly",
        pace: str = "normal",
        style: str = "conversational",
        additional: str = "",
    ) -> str:
        """
        Create a voice instruction for the FM API.

        Args:
            tone: Voice tone (friendly, professional, energetic, calm, etc.)
            pace: Speaking pace (slow, normal, fast)
            style: Speaking style (conversational, formal, casual, etc.)
            additional: Any additional instructions

        Returns:
            Formatted voice instruction string
        """
        instruction_parts = []

        if tone:
            instruction_parts.append(f"Tone: {tone}")
        if pace and pace != "normal":
            instruction_parts.append(f"Pace: {pace}")
        if style:
            instruction_parts.append(f"Style: {style}")
        if additional:
            instruction_parts.append(additional)

        return ". ".join(instruction_parts) + "."
