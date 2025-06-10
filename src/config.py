"""
Configuration management for the MCP TTS Server.
"""

import os
import yaml
import json
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from dotenv import load_dotenv


# Voice instruction presets based on OpenAI.fm examples
VOICE_PRESETS = {
    "default": {
        "name": "Default",
        "description": "Clear, friendly, and conversational",
        "instructions": "Clear, friendly, and conversational",
    },
    "professional": {
        "name": "Professional",
        "description": "Clear, authoritative, and composed business voice",
        "instructions": "Voice: Clear, authoritative, and composed, projecting confidence and professionalism.\n\nTone: Neutral and informative, maintaining a balance between formality and approachability.\n\nPunctuation: Structured with commas and pauses for clarity, ensuring information is digestible and well-paced.\n\nDelivery: Steady and measured, with slight emphasis on key figures and deadlines to highlight critical points.",
    },
    "calm": {
        "name": "Calm",
        "description": "Composed, reassuring voice with quiet authority",
        "instructions": 'Voice Affect: Calm, composed, and reassuring; project quiet authority and confidence.\n\nTone: Sincere, empathetic, and gently authoritative—express genuine apology while conveying competence.\n\nPacing: Steady and moderate; unhurried enough to communicate care, yet efficient enough to demonstrate professionalism.\n\nEmotion: Genuine empathy and understanding; speak with warmth, especially during apologies ("I\'m very sorry for any disruption...").\n\nPronunciation: Clear and precise, emphasizing key reassurances ("smoothly," "quickly," "promptly") to reinforce confidence.\n\nPauses: Brief pauses after offering assistance or requesting details, highlighting willingness to listen and support.',
    },
    "nyc_cabbie": {
        "name": "NYC Cabbie",
        "description": "Fast-talking New Yorker with edge and efficiency",
        "instructions": 'Voice: Gruff, fast-talking, and a little worn-out, like a New York cabbie who\'s seen it all but still keeps things moving.\n\nTone: Slightly exasperated but still functional, with a mix of sarcasm and no-nonsense efficiency.\n\nDialect: Strong New York accent, with dropped "r"s, sharp consonants, and classic phrases like whaddaya and lemme guess.\n\nPronunciation: Quick and clipped, with a rhythm that mimics the natural hustle of a busy city conversation.\n\nFeatures: Uses informal, straight-to-the-point language, throws in some dry humor, and keeps the energy just on the edge of impatience but still helpful.',
    },
    "chill_surfer": {
        "name": "Chill Surfer",
        "description": "Laid-back, mellow, and effortlessly cool",
        "instructions": "Voice: Laid-back, mellow, and effortlessly cool, like a surfer who's never in a rush.\n\nTone: Relaxed and reassuring, keeping things light even when the customer is frustrated.\n\nSpeech Mannerisms: Uses casual, friendly phrasing with surfer slang like dude, gnarly, and boom to keep the conversation chill.\n\nPronunciation: Soft and drawn-out, with slightly stretched vowels and a naturally wavy rhythm in speech.\n\nTempo: Slow and easygoing, with a natural flow that never feels rushed, creating a calming effect.",
    },
    "cheerleader": {
        "name": "Cheerleader",
        "description": "High-energy, enthusiastic, and motivational",
        "instructions": "Personality/affect: a high-energy cheerleader helping with administrative tasks\n\nVoice: Enthusiastic, and bubbly, with an uplifting and motivational quality.\n\nTone: Encouraging and playful, making even simple tasks feel exciting and fun.\n\nDialect: Casual and upbeat, using informal phrasing and pep talk-style expressions.\n\nPronunciation: Crisp and lively, with exaggerated emphasis on positive words to keep the energy high.\n\nFeatures: Uses motivational phrases, cheerful exclamations, and an energetic rhythm to create a sense of excitement and engagement.",
    },
    "emo_teenager": {
        "name": "Emo Teenager",
        "description": "Sarcastic, disinterested, and melancholic",
        "instructions": "Tone: Sarcastic, disinterested, and melancholic, with a hint of passive-aggressiveness.\n\nEmotion: Apathy mixed with reluctant engagement.\n\nDelivery: Monotone with occasional sighs, drawn-out words, and subtle disdain, evoking a classic emo teenager attitude.",
    },
    "eternal_optimist": {
        "name": "Eternal Optimist",
        "description": "Positive and solution-oriented, always hopeful",
        "instructions": "Tone: Positive and solution-oriented, always focusing on the next steps rather than dwelling on the problem.\n\nDialect: Neutral and professional, avoiding overly casual speech but maintaining a friendly and approachable style.\n\nPronunciation: Clear and precise, with a natural rhythm that emphasizes key words to instill confidence and keep the customer engaged.\n\nFeatures: Uses empathetic phrasing, gentle reassurance, and proactive language to shift the focus from frustration to resolution.",
    },
    "dramatic": {
        "name": "Dramatic",
        "description": "Low, hushed, and suspenseful with theatrical flair",
        "instructions": 'Voice Affect: Low, hushed, and suspenseful; convey tension and intrigue.\n\nTone: Deeply serious and mysterious, maintaining an undercurrent of unease throughout.\n\nPacing: Slow, deliberate, pausing slightly after suspenseful moments to heighten drama.\n\nEmotion: Restrained yet intense—voice should subtly tremble or tighten at key suspenseful points.\n\nEmphasis: Highlight sensory descriptions ("footsteps echoed," "heart hammering," "shadows melting into darkness") to amplify atmosphere.\n\nPronunciation: Slightly elongated vowels and softened consonants for an eerie, haunting effect.\n\nPauses: Insert meaningful pauses after phrases like "only shadows melting into darkness," and especially before the final line, to enhance suspense dramatically.',
    },
}


@dataclass
class TTSConfig:
    """TTS provider configuration."""

    provider: str = "openai"
    voice: str = "ballad"
    speed: float = 1.0
    language: str = "en"
    default_instructions: str = "Clear, friendly, and conversational"
    current_preset: str = "default"
    custom_instructions: str = ""


@dataclass
class AudioConfig:
    """Audio playback configuration."""

    default_device: Optional[str] = None
    default_device_index: Optional[int] = None
    volume: float = 0.8
    sample_rate: int = 24000
    buffer_size: int = 1024


@dataclass
class Config:
    """Main configuration class."""

    host: str = "localhost"
    port: int = 8742
    tts: TTSConfig = field(default_factory=TTSConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    openai_api_key: Optional[str] = None
    log_level: str = "INFO"

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "Config":
        """Load configuration from file and environment variables."""
        # Load .env file first
        load_dotenv()

        config = cls()

        # Load from config file if it exists
        if config_path is None:
            config_path = "config/default.yaml"

        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                file_config = yaml.safe_load(f)
                config = cls._merge_config(config, file_config)

        # Load user settings if they exist
        user_config_path = "config/user_settings.json"
        if os.path.exists(user_config_path):
            config = cls._load_user_settings(config, user_config_path)

        # Override with environment variables (including from .env)
        config._load_env_vars()

        return config

    def _load_env_vars(self):
        """Load configuration from environment variables."""
        self.openai_api_key = os.getenv("OPENAI_API_KEY", self.openai_api_key)
        self.host = os.getenv("MCP_TTS_HOST", self.host)
        self.port = int(os.getenv("MCP_TTS_PORT", str(self.port)))
        self.log_level = os.getenv("MCP_TTS_LOG_LEVEL", self.log_level)

        # TTS Configuration via Environment Variables
        if os.getenv("MCP_TTS_VOICE"):
            self.tts.voice = os.getenv("MCP_TTS_VOICE")

        if os.getenv("MCP_TTS_SPEED"):
            try:
                self.tts.speed = float(os.getenv("MCP_TTS_SPEED"))
            except ValueError:
                print(
                    f"Warning: Invalid MCP_TTS_SPEED value, using default: {self.tts.speed}"
                )

        if os.getenv("MCP_TTS_VOICE_PRESET"):
            preset = os.getenv("MCP_TTS_VOICE_PRESET")
            if preset in VOICE_PRESETS:
                self.tts.current_preset = preset
                # Update default instructions from the preset
                self.tts.default_instructions = VOICE_PRESETS[preset]["instructions"]
            else:
                print(
                    f"Warning: Unknown voice preset '{preset}', using default. Available presets: {', '.join(VOICE_PRESETS.keys())}"
                )

        if os.getenv("MCP_TTS_CUSTOM_INSTRUCTIONS"):
            self.tts.custom_instructions = os.getenv("MCP_TTS_CUSTOM_INSTRUCTIONS")

        # Audio Configuration via Environment Variables
        if os.getenv("MCP_TTS_VOLUME"):
            try:
                volume = float(os.getenv("MCP_TTS_VOLUME"))
                if 0.0 <= volume <= 1.0:
                    self.audio.volume = volume
                else:
                    print(
                        f"Warning: MCP_TTS_VOLUME must be between 0.0 and 1.0, using default: {self.audio.volume}"
                    )
            except ValueError:
                print(
                    f"Warning: Invalid MCP_TTS_VOLUME value, using default: {self.audio.volume}"
                )

        if os.getenv("MCP_TTS_DEVICE_NAME"):
            self.audio.default_device = os.getenv("MCP_TTS_DEVICE_NAME")

        if os.getenv("MCP_TTS_DEVICE_INDEX"):
            try:
                self.audio.default_device_index = int(os.getenv("MCP_TTS_DEVICE_INDEX"))
            except ValueError:
                print(
                    f"Warning: Invalid MCP_TTS_DEVICE_INDEX value, using default: {self.audio.default_device_index}"
                )

    @staticmethod
    def _merge_config(base_config: "Config", file_config: Dict[str, Any]) -> "Config":
        """Merge file configuration with base configuration."""
        if "host" in file_config:
            base_config.host = file_config["host"]
        if "port" in file_config:
            base_config.port = file_config["port"]
        if "log_level" in file_config:
            base_config.log_level = file_config["log_level"]

        # Merge TTS config
        if "tts" in file_config:
            tts_config = file_config["tts"]
            if "provider" in tts_config:
                base_config.tts.provider = tts_config["provider"]
            if "voice" in tts_config:
                base_config.tts.voice = tts_config["voice"]
            if "speed" in tts_config:
                base_config.tts.speed = tts_config["speed"]
            if "language" in tts_config:
                base_config.tts.language = tts_config["language"]
            if "default_instructions" in tts_config:
                base_config.tts.default_instructions = tts_config[
                    "default_instructions"
                ]

        # Merge Audio config
        if "audio" in file_config:
            audio_config = file_config["audio"]
            if "default_device" in audio_config:
                base_config.audio.default_device = audio_config["default_device"]
            if "default_device_index" in audio_config:
                base_config.audio.default_device_index = audio_config[
                    "default_device_index"
                ]
            if "volume" in audio_config:
                base_config.audio.volume = audio_config["volume"]
            if "sample_rate" in audio_config:
                base_config.audio.sample_rate = audio_config["sample_rate"]
            if "buffer_size" in audio_config:
                base_config.audio.buffer_size = audio_config["buffer_size"]

        return base_config

    @staticmethod
    def _load_user_settings(base_config: "Config", user_config_path: str) -> "Config":
        """Load user settings from JSON file."""
        try:
            with open(user_config_path, "r") as f:
                user_settings = json.load(f)

            # Apply user settings
            if "tts" in user_settings:
                tts = user_settings["tts"]
                if "voice" in tts:
                    base_config.tts.voice = tts["voice"]
                if "speed" in tts:
                    base_config.tts.speed = tts["speed"]
                if "current_preset" in tts:
                    base_config.tts.current_preset = tts["current_preset"]
                if "custom_instructions" in tts:
                    base_config.tts.custom_instructions = tts["custom_instructions"]

            if "audio" in user_settings:
                audio = user_settings["audio"]
                if "default_device" in audio:
                    base_config.audio.default_device = audio["default_device"]
                if "default_device_index" in audio:
                    base_config.audio.default_device_index = audio[
                        "default_device_index"
                    ]
                if "volume" in audio:
                    base_config.audio.volume = audio["volume"]

        except Exception as e:
            print(f"Warning: Could not load user settings: {e}")

        return base_config

    def save_user_settings(self, user_config_path: str = "config/user_settings.json"):
        """Save current user settings to JSON file."""
        os.makedirs(os.path.dirname(user_config_path), exist_ok=True)

        user_settings = {
            "tts": {
                "voice": self.tts.voice,
                "speed": self.tts.speed,
                "current_preset": self.tts.current_preset,
                "custom_instructions": self.tts.custom_instructions,
            },
            "audio": {
                "default_device": self.audio.default_device,
                "default_device_index": self.audio.default_device_index,
                "volume": self.audio.volume,
            },
        }

        with open(user_config_path, "w") as f:
            json.dump(user_settings, f, indent=2)

    def get_current_voice_instructions(self) -> str:
        """Get the current voice instructions based on preset or custom."""
        if self.tts.custom_instructions.strip():
            return self.tts.custom_instructions
        elif self.tts.current_preset in VOICE_PRESETS:
            return VOICE_PRESETS[self.tts.current_preset]["instructions"]
        else:
            return self.tts.default_instructions

    def save(self, config_path: str = "config/default.yaml"):
        """Save current configuration to file."""
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        config_dict = {
            "host": self.host,
            "port": self.port,
            "log_level": self.log_level,
            "tts": {
                "provider": self.tts.provider,
                "voice": self.tts.voice,
                "speed": self.tts.speed,
                "language": self.tts.language,
                "default_instructions": self.tts.default_instructions,
            },
            "audio": {
                "default_device": self.audio.default_device,
                "volume": self.audio.volume,
                "sample_rate": self.audio.sample_rate,
                "buffer_size": self.audio.buffer_size,
            },
        }

        with open(config_path, "w") as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
