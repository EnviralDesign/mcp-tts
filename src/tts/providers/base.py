"""
Base TTS provider interface.
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional
from dataclasses import dataclass


@dataclass
class TTSRequest:
    """TTS request parameters."""

    text: str
    voice: str = "ballad"
    speed: float = 1.0
    language: str = "en"
    instructions: Optional[str] = None


class TTSProvider(ABC):
    """Abstract base class for TTS providers."""

    @abstractmethod
    async def generate_speech(self, request: TTSRequest) -> bytes:
        """
        Generate speech audio from text.

        Args:
            request: TTS request parameters

        Returns:
            Raw audio data (PCM format)
        """
        pass

    @abstractmethod
    async def generate_speech_stream(self, request: TTSRequest) -> AsyncIterator[bytes]:
        """
        Generate speech audio as a stream.

        Args:
            request: TTS request parameters

        Yields:
            Audio data chunks
        """
        pass

    @abstractmethod
    def get_supported_voices(self) -> list[str]:
        """Get list of supported voice names."""
        pass

    @abstractmethod
    def get_supported_languages(self) -> list[str]:
        """Get list of supported language codes."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass
