# Created by Jeff Hollaway

"""
AI Highlighter - Module 2: Voice-Triggered Clipping
Detects trigger phrases in transcript and creates clips.
Function: detect_voice_clips(vod_id, transcript) -> List[ClipCandidate]
Trigger phrases: clip that, clip this, clip it, save that, make a clip, etc.
Default duration: 30s, Max: 120s
Voice clips ALWAYS override AI scoring and must never be filtered out.
"""
import re, logging
from typing import List, Optional
logger = logging.getLogger(__name__)
try:
    from modules.models import TranscriptSegment, ClipCandidate, ClipSource
except ImportError:
    from models import TranscriptSegment, ClipCandidate, ClipSource

TRIGGER_PHRASES = [
    "clip that", "clip this", "clip it",
    "clip the last", "save that", "make a clip",
    "highlight that", "mark that",
    "last two minutes", "last couple minutes",
    "that was insane", "oh my god clip it",
]

DURATION_PATTERNS = [
    (r"last (\d+)\s*minutes?", lambda m: int(m.group(1)) * 60),
    (r"last (\d+)\s*seconds?", lambda m: int(m.group(1))),
    (r"last couple\s*minutes?", lambda m: 120),
    (r"last two\s*minutes?", lambda m: 120),
    (r"last few\s*minutes?", lambda m: 180),
]

DEFAULT_CLIP_DURATION = 30
MAX_CLIP_DURATION = 120
MIN_CLIP_DURATION = 30

class VoiceClipDetector:
    def __init__(self):
        self.triggers = TRIGGER_PHRASES
        self.duration_patterns = DURATION_PATTERNS

    def _is_trigger(self, text):
        t = text.lower().strip()
        for phrase in self.triggers:
            if phrase in t:
                return True
        return False

    def _extract_duration(self, text):
        t = text.lower().strip()
        for pattern, extractor in self.duration_patterns:
            m = re.search(pattern, t)
            if m:
                dur = extractor(m)
                return max(MIN_CLIP_DURATION, min(dur, MAX_CLIP_DURATION))
        return DEFAULT_CLIP_DURATION

    def detect_voice_clips(self, vod_id, transcript):
        clips = []
        for seg in transcript:
            if not self._is_trigger(seg.text):
                continue
            trigger_time = seg.end
            duration = self._extract_duration(seg.text)
            start = max(0, trigger_time - duration)
            end = trigger_time
            if end - start < MIN_CLIP_DURATION:
                end = start + MIN_CLIP_DURATION
            clip = ClipCandidate(
                vod_id=vod_id, start=round(start,2), end=round(end,2),
                score=1.0, source=ClipSource.VOICE_TRIGGER,
                reason=f"Voice trigger: {seg.text[:50]}")
            clips.append(clip)
            logger.info(f"Voice clip detected at {start:.1f}-{end:.1f}s: {seg.text[:40]}")
        return clips
