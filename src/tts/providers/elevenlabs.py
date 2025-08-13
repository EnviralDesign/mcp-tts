"""
ElevenLabs TTS provider using the official ElevenLabs Python SDK.

Returns raw PCM 16-bit audio at 24kHz for compatibility with the AudioPlayer.
"""

import logging
from typing import AsyncIterator, Dict, List, Optional, Any
import httpx
from elevenlabs.client import ElevenLabs
from .base import TTSProvider, TTSRequest


logger = logging.getLogger(__name__)


class ElevenLabsTTSProvider(TTSProvider):
    """
    ElevenLabs TTS provider implemented via REST using httpx.AsyncClient.

    Notes:
    - Expects `request.voice` to be an ElevenLabs `voice_id` (string). If you
      provide a voice name instead of an ID, the request will likely fail unless
      the API accepts names transparently. You can retrieve available voices and
      IDs via `get_supported_voices()`.
    - Returns 16-bit PCM at 24kHz by requesting `output_format="pcm_24000"`.
    - ElevenLabs does not support a generic "speed" parameter like OpenAI; the
      provided `speed` is ignored.
    """

    def __init__(self, api_key: str, model_id: str = "eleven_multilingual_v2"):
        self.api_key = api_key
        self.model_id = model_id
        self._base_url = "https://api.elevenlabs.io/v1"
        self.client = ElevenLabs(api_key=api_key)
        self._supported_languages: List[str] = [
            "en",
            "es",
            "fr",
            "de",
            "it",
            "pt",
            "ja",
            "ko",
            "zh",
        ]
        # Canonical name -> id, and lowercase name -> id for lookup
        self._voice_cache: Optional[Dict[str, str]] = None
        self._voice_cache_lower: Optional[Dict[str, str]] = None
        self._voices_full: Optional[List[Dict[str, Any]]] = None

    async def _post_json(self, url: str, json: dict, stream: bool = False) -> httpx.Response:
        # Kept for rare fallback cases; primary path uses SDK
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        timeout = httpx.Timeout(60.0, connect=15.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            if stream:
                return await client.post(url, headers=headers, json=json, timeout=timeout)
            return await client.post(url, headers=headers, json=json)

    def _resolve_voice_id(self, voice_or_id: str) -> str:
        """Return a voice_id from either an id or known name."""
        if not voice_or_id:
            raise ValueError("Voice is required for ElevenLabs")
        self._ensure_voice_cache()
        # If provided as name and exists in cache, map to id (case-insensitive)
        if self._voice_cache:
            if voice_or_id in self._voice_cache:
                return self._voice_cache[voice_or_id]
            if self._voice_cache_lower and voice_or_id.lower() in self._voice_cache_lower:
                return self._voice_cache_lower[voice_or_id.lower()]
        # Attempt a refresh once if not found
        self._ensure_voice_cache(force_refresh=True)
        if self._voice_cache:
            if voice_or_id in self._voice_cache:
                return self._voice_cache[voice_or_id]
            if self._voice_cache_lower and voice_or_id.lower() in self._voice_cache_lower:
                return self._voice_cache_lower[voice_or_id.lower()]
        # Otherwise assume it is already an id
        # If it's not a known name and not obviously an id, fall back to first available
        # Heuristic: ElevenLabs voice_id is typically a 20+ char token; if short, likely invalid
        if len(voice_or_id) < 16 and self._voice_cache:
            # Return the first available voice id
            try:
                return next(iter(self._voice_cache.values()))
            except StopIteration:
                pass
        return voice_or_id

    async def generate_speech(self, request: TTSRequest) -> bytes:
        """Generate speech audio from text using ElevenLabs.

        Returns raw PCM 16-bit audio at 24kHz if successful.
        """
        try:
            if not request.voice:
                raise ValueError("ElevenLabs requires a voice or voice_id in request.voice")

            voice_id = self._resolve_voice_id(request.voice)
            logger.info("Requesting ElevenLabs TTS (non-stream)")
            audio = self.client.text_to_speech.convert(
                text=request.text,
                voice_id=voice_id,
                model_id=self.model_id,
                output_format="pcm_24000",
            )
            # Coerce to bytes if SDK returns a generator/iterator
            if isinstance(audio, (bytes, bytearray)):
                data = bytes(audio)
            else:
                try:
                    data = b"".join(
                        chunk for chunk in audio if isinstance(chunk, (bytes, bytearray))
                    )
                except TypeError:
                    # Fallback if not iterable
                    data = bytes(audio) if audio is not None else b""
            # Ensure even-length for int16 PCM
            if len(data) % 2 != 0:
                data = data[:-1]
            return data
        except Exception as e:
            logger.error(f"Error generating speech with ElevenLabs: {e}")
            raise

    async def generate_speech_stream(self, request: TTSRequest) -> AsyncIterator[bytes]:
        """Generate speech audio as a stream using ElevenLabs streaming endpoint."""
        if not request.voice:
            raise ValueError("ElevenLabs requires a voice or voice_id in request.voice")

        voice_id = self._resolve_voice_id(request.voice)
        logger.info("Requesting ElevenLabs TTS (stream)")
        # SDK returns an iterator with bytes and possibly other events; yield bytes only
        stream_iter = self.client.text_to_speech.stream(
            text=request.text,
            voice_id=voice_id,
            model_id=self.model_id,
            output_format="pcm_24000",
        )
        for chunk in stream_iter:
            if isinstance(chunk, (bytes, bytearray)) and chunk:
                # Ensure even-length frames for int16 PCM
                if len(chunk) % 2 != 0:
                    chunk = chunk[:-1]
                if chunk:
                    yield bytes(chunk)

    def _ensure_voice_cache(self, force_refresh: bool = False):
        # Intentionally synchronous call via httpx for simplicity; cache results
        if self._voice_cache is not None and not force_refresh:
            return
        try:
            # Prefer SDK
            # SDK v2 endpoint for all voices may be under .voices.list() or .search()
            # Try list() first; fallback to search()
            try:
                resp = self.client.voices.list()
            except Exception:
                resp = self.client.voices.search()
            cache: Dict[str, str] = {}
            cache_lower: Dict[str, str] = {}
            voices_full: List[Dict[str, Any]] = []
            voices = getattr(resp, "voices", None) or resp or []
            for v in voices:
                # SDK models often have attributes; fallback to dict access
                name = getattr(v, "name", None) or (v.get("name") if isinstance(v, dict) else None)
                vid = getattr(v, "voice_id", None) or getattr(v, "voiceId", None) or (
                    v.get("voice_id") if isinstance(v, dict) else None
                )
                preview = getattr(v, "preview_url", None) or (v.get("preview_url") if isinstance(v, dict) else None)
                if name and vid:
                    cache[name] = vid
                    cache_lower[name.lower()] = vid
                    voices_full.append({"name": name, "voice_id": vid, "preview_url": preview})
            # Fallback to REST if SDK returned empty
            if not cache:
                headers = {"xi-api-key": self.api_key}
                with httpx.Client(timeout=httpx.Timeout(30.0, connect=10.0)) as client:
                    r = client.get(f"{self._base_url}/voices", headers=headers)
                    r.raise_for_status()
                    data = r.json()
                    for v in data.get("voices", []) or []:
                        name = v.get("name")
                        vid = v.get("voice_id") or v.get("voiceId")
                        if name and vid:
                            cache[name] = vid
                            cache_lower[name.lower()] = vid
                            voices_full.append(
                                {
                                    "name": name,
                                    "voice_id": vid,
                                    "preview_url": v.get("preview_url"),
                                }
                            )
            self._voice_cache = cache
            self._voice_cache_lower = cache_lower
            self._voices_full = voices_full
        except Exception as e:
            logger.warning(f"Could not fetch ElevenLabs voices: {e}")
            if self._voice_cache is None:
                self._voice_cache = {}
                self._voice_cache_lower = {}
                self._voices_full = []

    def get_supported_voices(self) -> list[str]:
        # Returns voice NAMES known to the account for convenience
        self._ensure_voice_cache()
        return list(self._voice_cache.keys()) if self._voice_cache else []

    def list_voices(self) -> List[Dict[str, str]]:
        """Return list of dicts with name and voice_id."""
        self._ensure_voice_cache()
        if self._voices_full is not None:
            return list(self._voices_full)
        if not self._voice_cache:
            return []
        return [
            {"name": name, "voice_id": vid, "preview_url": None}
            for name, vid in self._voice_cache.items()
            if name and name.strip()
        ]

    def get_supported_languages(self) -> list[str]:
        return self._supported_languages.copy()

    @property
    def name(self) -> str:
        return "elevenlabs"


