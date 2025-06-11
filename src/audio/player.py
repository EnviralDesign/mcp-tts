"""
Cross-platform audio playback for TTS audio streams.
"""

import os
import logging
import numpy as np
from typing import Optional, List, AsyncIterable
from dataclasses import dataclass
from io import BytesIO

logger = logging.getLogger(__name__)

# Check if we're running in CI mode
CI_MODE = os.getenv("CI_MODE") == "true" or os.getenv("CI") == "true"

if not CI_MODE:
    import sounddevice as sd
else:
    # Mock sounddevice for CI
    logger.info("Running in CI mode - audio functionality will be mocked")

    class MockSoundDevice:
        """Mock sounddevice for CI environments."""

        @staticmethod
        def play(*args, **kwargs):
            logger.debug("Mock audio play called")

        @staticmethod
        def wait():
            logger.debug("Mock audio wait called")

        @staticmethod
        def query_devices():
            return [
                {
                    "name": "Mock Audio Device",
                    "max_output_channels": 2,
                    "default_samplerate": 44100,
                }
            ]

        class default:
            device = [None, 0]  # Input, Output

    sd = MockSoundDevice()


@dataclass
class AudioDevice:
    """Represents an audio output device."""

    index: int
    name: str
    channels: int
    sample_rate: float
    is_default: bool = False


class AudioPlayer:
    """Handles cross-platform audio playback using sounddevice."""

    def __init__(self, sample_rate: int = 24000, buffer_size: int = 1024):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.current_stream: Optional[sd.OutputStream] = None
        self.is_playing = False
        self._volume = 0.8

    async def play_audio_data(
        self, audio_data: bytes, device_index: Optional[int] = None
    ) -> bool:
        """
        Play audio data through the specified device.

        Args:
            audio_data: Raw PCM audio data
            device_index: Target audio device index (None for default)

        Returns:
            True if playback succeeded, False otherwise
        """
        try:
            # print(f"DEBUG: Received audio data: {len(audio_data)} bytes")
            if len(audio_data) == 0:
                # print("DEBUG: No audio data received!")
                return False
                
            # Convert bytes to numpy array (assuming 16-bit PCM)
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            # print(f"DEBUG: Converted to audio array: {len(audio_array)} samples")

            # Convert to float32 and normalize
            audio_float = audio_array.astype(np.float32) / 32768.0

            # Apply volume
            audio_float *= self._volume

            # Handle mono/stereo conversion if needed
            if len(audio_float.shape) == 1:
                # Mono audio - duplicate for stereo if device expects it
                device_info = self.get_device_info(device_index)
                if device_info and device_info.channels > 1:
                    audio_float = np.column_stack((audio_float, audio_float))

            # Play the audio
            await self._play_array(audio_float, device_index)
            return True

        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            return False

    async def _play_array(
        self, audio_array: np.ndarray, device_index: Optional[int] = None
    ):
        """Play a numpy audio array."""
        self.is_playing = True

        try:
            # Use simpler blocking playback - more reliable
            sd.play(
                audio_array,
                samplerate=self.sample_rate,
                device=device_index,
                blocking=False,
            )

            # Wait for playback to complete
            sd.wait()

        except Exception as e:
            logger.error(f"Error in audio playback: {e}")
            raise
        finally:
            self.is_playing = False
            self.current_stream = None

    async def stream_audio(
        self, audio_stream: AsyncIterable[bytes], device_index: Optional[int] = None
    ) -> bool:
        """
        Stream audio data in real-time.

        Args:
            audio_stream: Async iterator yielding audio chunks
            device_index: Target audio device index

        Returns:
            True if streaming succeeded, False otherwise
        """
        try:
            self.is_playing = True

            # Buffer for collecting audio chunks
            audio_buffer = BytesIO()

            async for chunk in audio_stream:
                audio_buffer.write(chunk)

                # If we have enough data, play it
                if (
                    audio_buffer.tell() >= self.buffer_size * 2
                ):  # 2 bytes per sample for 16-bit
                    audio_data = audio_buffer.getvalue()
                    audio_buffer = BytesIO()  # Reset buffer

                    await self.play_audio_data(audio_data, device_index)

            # Play any remaining data
            remaining_data = audio_buffer.getvalue()
            if remaining_data:
                await self.play_audio_data(remaining_data, device_index)

            return True

        except Exception as e:
            logger.error(f"Error streaming audio: {e}")
            return False
        finally:
            self.is_playing = False

    def stop(self):
        """Stop current audio playback."""
        if self.current_stream and self.is_playing:
            self.current_stream.stop()
            self.is_playing = False

    def set_volume(self, volume: float):
        """Set playback volume (0.0 to 1.0)."""
        self._volume = max(0.0, min(1.0, volume))

    def get_volume(self) -> float:
        """Get current playback volume."""
        return self._volume

    @staticmethod
    def get_audio_devices() -> List[AudioDevice]:
        """Get list of available audio output devices."""
        devices = []

        try:
            device_info = sd.query_devices()
            default_device = sd.default.device[1]  # Output device

            for i, device in enumerate(device_info):
                if device["max_output_channels"] > 0:  # Output device
                    devices.append(
                        AudioDevice(
                            index=i,
                            name=device["name"],
                            channels=device["max_output_channels"],
                            sample_rate=device["default_samplerate"],
                            is_default=(i == default_device),
                        )
                    )

        except Exception as e:
            logger.error(f"Error querying audio devices: {e}")

        return devices

    @staticmethod
    def get_device_info(device_index: Optional[int] = None) -> Optional[AudioDevice]:
        """Get information about a specific device."""
        try:
            devices = AudioPlayer.get_audio_devices()

            if device_index is None:
                # Return default device
                for device in devices:
                    if device.is_default:
                        return device
                return devices[0] if devices else None

            # Find device by index
            for device in devices:
                if device.index == device_index:
                    return device

        except Exception as e:
            logger.error(f"Error getting device info: {e}")

        return None

    @staticmethod
    def test_device(device_index: Optional[int] = None) -> bool:
        """Test if an audio device is working."""
        if CI_MODE:
            logger.info(f"CI mode: mock testing device {device_index}")
            return True

        try:
            # Generate a simple test tone (440 Hz for 0.5 seconds)
            duration = 0.5
            sample_rate = 24000
            t = np.linspace(0, duration, int(sample_rate * duration))
            test_tone = 0.3 * np.sin(2 * np.pi * 440 * t)

            # Play the test tone
            sd.play(test_tone, samplerate=sample_rate, device=device_index)
            sd.wait()  # Wait for playback to complete

            return True

        except Exception as e:
            logger.error(f"Error testing device {device_index}: {e}")
            return False
