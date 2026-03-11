
"""
AI Highlighter System - Data Models
Section 2: Complete data models as specified in the Master Specification.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
from datetime import datetime

class VodStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ClipSource(Enum):
    AI = "ai"
    VOICE_TRIGGER = "voice_trigger"

class QualityRating(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class Vod:
    id: str
    twitch_vod_id: str
    source_url: str
    duration_seconds: float
    status: VodStatus = VodStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    def validate(self):
        assert self.duration_seconds > 0
        assert self.source_url.startswith("http")
        assert self.twitch_vod_id

@dataclass
class TranscriptSegment:
    vod_id: str
    start: float
    end: float
    text: str
    confidence: float
    def validate(self):
        assert 0 <= self.start < self.end
        assert 0.0 <= self.confidence <= 1.0
        assert self.text.strip()

@dataclass
class FeatureVector:
    vod_id: str
    timestamp: float
    audio_energy: float = 0.0
    audio_spike: bool = False
    motion_intensity: float = 0.0
    scene_change: bool = False
    chat_hype: float = 0.0
    semantic_importance: float = 0.0
    def validate(self):
        assert self.timestamp >= 0
        assert 0.0 <= self.audio_energy <= 1.0
        assert 0.0 <= self.motion_intensity <= 1.0
        assert 0.0 <= self.chat_hype <= 1.0
        assert 0.0 <= self.semantic_importance <= 1.0

@dataclass
class ClipCandidate:
    vod_id: str
    start: float
    end: float
    score: float
    source: ClipSource
    reason: str
    def validate(self):
        assert 0 <= self.start < self.end
        dur = self.end - self.start
        assert 30 <= dur <= 120
        assert 0.0 <= self.score <= 1.0
    @property
    def duration(self): return self.end - self.start
    @property
    def is_voice_triggered(self): return self.source == ClipSource.VOICE_TRIGGER

@dataclass
class RenderedClip:
    id: str
    vod_id: str
    start: float
    end: float
    title: str
    summary: str
    quality_rating: QualityRating
    output_path: str
    format_spec: dict = field(default_factory=lambda: {
        "resolution": "1080x1920", "codec": "H.264",
        "audio_codec": "AAC", "fps": 30, "aspect_ratio": "9:16"
    })
    source: ClipSource = ClipSource.AI
    created_at: datetime = field(default_factory=datetime.utcnow)
    def validate(self):
        assert 0 <= self.start < self.end
        assert len(self.title) <= 80
        assert self.output_path
