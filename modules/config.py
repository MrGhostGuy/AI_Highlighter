
import os
import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

@dataclass
class TranscriptionConfig:
    """Configuration for the transcription engine."""
    model_name: str = "large-v2"
    language: str = "en"
    chunk_duration: float = 30.0
    overlap_duration: float = 2.0
    min_confidence: float = 0.5
    device: str = "cuda"
    batch_size: int = 16

@dataclass
class ScoringConfig:
    """Configuration for highlight scoring weights."""
    audio_weight: float = 0.3
    chat_weight: float = 0.3
    visual_weight: float = 0.2
    semantic_weight: float = 0.2
    score_threshold: float = 0.6
    peak_window_seconds: int = 10

@dataclass
class ClipConfig:
    """Configuration for clip extraction rules."""
    min_length: int = 30
    max_length: int = 120
    default_voice_duration: int = 30
    max_voice_duration: int = 120
    backward_expand: int = 25
    forward_expand: int = 75
    merge_gap_threshold: int = 10

@dataclass
class RenderConfig:
    """Configuration for vertical rendering."""
    WIDTH: int = 1080
    HEIGHT: int = 1920
    FPS: int = 30
    CODEC: str = "libx264"
    CRF: int = 23
    PRESET: str = "medium"
    AUDIO_CODEC: str = "aac"
    aspect_ratio: str = "9:16"
    caption_font: str = "Arial-Bold"
    caption_fontsize: int = 48
    caption_color: str = "white"
    caption_shadow: bool = True
    caption_max_lines: int = 2
    facecam_position: str = "top"
    gameplay_position: str = "middle"
    caption_position: str = "bottom"

@dataclass
class APIConfig:
    """Configuration for the API layer."""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    cors_origins: list = field(default_factory=lambda: ["*"])
    max_upload_size_mb: int = 5000
    rate_limit_per_minute: int = 60

@dataclass
class DashboardConfig:
    """Configuration for the web dashboard."""
    theme: str = "futuristic"
    accent_color: str = "#00f0ff"
    background_color: str = "#0a0a1a"
    card_color: str = "#12122a"
    text_color: str = "#e0e0ff"
    font_family: str = "Orbitron, sans-serif"
    enable_qr_code: bool = True
    qr_code_size: int = 200
    mobile_responsive: bool = True
    auto_refresh_interval: int = 5


@dataclass
class TwitchConfig:
    client_id: str = os.environ.get('TWITCH_CLIENT_ID', '')
    client_secret: str = os.environ.get('TWITCH_CLIENT_SECRET', '')
    token_url: str = 'https://id.twitch.tv/oauth2/token'
    api_base_url: str = 'https://api.twitch.tv/helix'
    
@dataclass
class PipelineConfig:
    """Master configuration for the entire AI Highlighter system."""
    project_name: str = "AI Highlighter"
    version: str = "2.0.0"
    base_dir: str = ""
    output_dir: str = "output"
    temp_dir: str = "temp"
    log_level: str = "INFO"
    log_file: str = "ai_highlighter.log"
    transcription: TranscriptionConfig = field(default_factory=TranscriptionConfig)
    scoring: ScoringConfig = field(default_factory=ScoringConfig)
    clip: ClipConfig = field(default_factory=ClipConfig)
    render: RenderConfig = field(default_factory=RenderConfig)
    api: APIConfig = field(default_factory=APIConfig)
    dashboard: DashboardConfig = field(default_factory=DashboardConfig)
    twitch: TwitchConfig = field(default_factory=TwitchConfig)

    def __post_init__(self):
        if not self.base_dir:
            self.base_dir = str(Path(__file__).parent.parent)
        os.makedirs(os.path.join(self.base_dir, self.output_dir), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, self.temp_dir), exist_ok=True)

    def save(self, path: str = None):
        if path is None:
            path = os.path.join(self.base_dir, "config.json")
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2)
        logger.info(f"Configuration saved to {path}")

    @classmethod
    def load(cls, path: str) -> "PipelineConfig":
        with open(path, "r") as f:
            data = json.load(f)
        trans = TranscriptionConfig(**data.pop("transcription", {}))
        score = ScoringConfig(**data.pop("scoring", {}))
        clip = ClipConfig(**data.pop("clip", {}))
        render = RenderConfig(**data.pop("render", {}))
        api = APIConfig(**data.pop("api", {}))
        dash = DashboardConfig(**data.pop("dashboard", {}))
        return cls(transcription=trans, scoring=score, clip=clip,
                   render=render, api=api, dashboard=dash, **data)

    def validate(self):
        assert 0 <= self.scoring.audio_weight <= 1
        assert 0 <= self.scoring.chat_weight <= 1
        assert 0 <= self.scoring.visual_weight <= 1
        assert 0 <= self.scoring.semantic_weight <= 1
        total = (self.scoring.audio_weight + self.scoring.chat_weight +
                 self.scoring.visual_weight + self.scoring.semantic_weight)
        assert abs(total - 1.0) < 0.01, f"Scoring weights must sum to 1.0, got {total}"
        assert self.clip.min_length >= 30, "Min clip length must be >= 30s"
        assert self.clip.max_length <= 120, "Max clip length must be <= 120s"
        assert self.render.WIDTH == 1080 and self.render.HEIGHT == 1920
        logger.info("Configuration validated successfully")
        return True
