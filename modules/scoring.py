# Created by Jeff Hollaway

"""
AI Highlighter - Module 4: Highlight Scoring Engine
Scores and extracts clip candidates from feature vectors.
Function: score_highlights(features) -> List[ClipCandidate]
Weights: Audio=0.3, Chat=0.3, Visual=0.2, Semantic=0.2
Clip length: 30-120s, dynamic based on highlight density.
Merges overlapping clips when gap < 10s.
"""
import logging
from typing import List
logger = logging.getLogger(__name__)
try:
    from modules.models import FeatureVector, ClipCandidate, ClipSource
except ImportError:
    from models import FeatureVector, ClipCandidate, ClipSource

WEIGHTS = {"audio": 0.3, "chat": 0.3, "visual": 0.2, "semantic": 0.2}
MIN_CLIP = 30
MAX_CLIP = 120
SCORE_THRESHOLD = 0.4
MERGE_GAP = 10

class HighlightScoringEngine:
    def __init__(self, weights=None, threshold=None):
        self.weights = weights or WEIGHTS
        self.threshold = threshold or SCORE_THRESHOLD

    def _compute_score(self, fv):
        return (self.weights["audio"] * fv.audio_energy +
                self.weights["chat"] * fv.chat_hype +
                self.weights["visual"] * fv.motion_intensity +
                self.weights["semantic"] * fv.semantic_importance)

    def _find_peaks(self, scores, min_distance=30):
        peaks = []
        for i in range(1, len(scores)-1):
            if scores[i] > self.threshold and scores[i] >= scores[i-1] and scores[i] >= scores[i+1]:
                if not peaks or (i - peaks[-1]) >= min_distance:
                    peaks.append(i)
        return peaks

    def _determine_clip_bounds(self, peak, scores, duration):
        start = max(0, peak - MIN_CLIP // 2)
        end = min(duration, peak + MIN_CLIP // 2)
        while start > 0 and (end - start) < MAX_CLIP:
            if start > 0 and scores[int(start)-1] > self.threshold * 0.5:
                start -= 1
            else:
                break
        while end < duration and (end - start) < MAX_CLIP:
            if int(end) < len(scores) and scores[int(end)] > self.threshold * 0.5:
                end += 1
            else:
                break
        if end - start < MIN_CLIP:
            extra = MIN_CLIP - (end - start)
            start = max(0, start - extra / 2)
            end = min(duration, end + extra / 2)
        return round(start, 2), round(end, 2)

    def _merge_clips(self, clips):
        if not clips: return clips
        clips.sort(key=lambda c: c.start)
        merged = [clips[0]]
        for clip in clips[1:]:
            last = merged[-1]
            if clip.start - last.end < MERGE_GAP:
                new_end = max(last.end, clip.end)
                if new_end - last.start <= MAX_CLIP:
                    merged[-1] = ClipCandidate(
                        vod_id=last.vod_id, start=last.start, end=new_end,
                        score=max(last.score, clip.score),
                        source=last.source, reason=f"{last.reason}; {clip.reason}")
                    continue
            merged.append(clip)
        return merged

    def score_highlights(self, features):
        if not features: return []
        vod_id = features[0].vod_id
        duration = max(f.timestamp for f in features) + 1
        scores = [0.0] * int(duration)
        for fv in features:
            t = int(fv.timestamp)
            if 0 <= t < len(scores):
                scores[t] = self._compute_score(fv)
        peaks = self._find_peaks(scores)
        clips = []
        for peak in peaks:
            start, end = self._determine_clip_bounds(peak, scores, duration)
            avg_score = sum(scores[int(start):int(end)]) / max(1, int(end)-int(start))
            clip = ClipCandidate(
                vod_id=vod_id, start=start, end=end,
                score=round(avg_score, 3), source=ClipSource.AI,
                reason=f"Peak at {peak}s, avg_score={avg_score:.3f}")
            clips.append(clip)
        clips = self._merge_clips(clips)
        logger.info(f"Scoring found {len(clips)} highlight clips")
        return clips
