# Created by Jeff Hollaway

"""
AI Highlighter - Module 5: LLM Semantics & Title Generator
Enriches clips with AI-generated titles, summaries, and quality ratings.
Function: enrich_clips_with_semantics(vod_id, clips, transcript) -> List[dict]
LLM produces: 1-2 sentence summary, punchy title (<=80 chars), quality rating (low/medium/high)
Rules: AI clips with low quality may be dropped. Voice clips never dropped.
"""
import logging, json, re
from typing import List, Dict
logger = logging.getLogger(__name__)
try:
    from modules.models import ClipCandidate, ClipSource, QualityRating
except ImportError:
    from models import ClipCandidate, ClipSource, QualityRating

class LLMConfig:
    MODEL = "gpt-4"
    MAX_TOKENS = 200
    TEMPERATURE = 0.7

class LLMSemanticEngine:
    def __init__(self, config=None):
        self.config = config or LLMConfig()

    def _get_transcript_for_clip(self, clip, transcript):
        return " ".join(
            seg.text for seg in transcript
            if seg.start >= clip.start and seg.end <= clip.end)

    def _build_prompt(self, clip_text, clip_start, clip_end):
        return f"""Analyze this Twitch stream clip transcript and provide:
1. A punchy, engaging title (max 80 characters)
2. A 1-2 sentence summary of what happens
3. A quality rating: high, medium, or low

Clip time: {clip_start:.1f}s - {clip_end:.1f}s
Transcript: {clip_text[:500]}

Respond in JSON format:
{{"title": "...", "summary": "...", "quality": "high|medium|low"}}"""

    def _call_llm(self, prompt):
        try:
            import openai
            response = openai.chat.completions.create(
                model=self.config.MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.config.MAX_TOKENS,
                temperature=self.config.TEMPERATURE)
            text = response.choices[0].message.content
            return json.loads(text)
        except ImportError:
            logger.warning("OpenAI not installed, using fallback")
            return None
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return None

    def _fallback_enrich(self, clip, clip_text):
        words = clip_text.split()[:10]
        title = " ".join(words)[:80] if words else f"Clip at {clip.start:.0f}s"
        return {
            "title": title,
            "summary": f"Highlight clip from {clip.start:.1f}s to {clip.end:.1f}s.",
            "quality": "medium"}

    def enrich_clips_with_semantics(self, vod_id, clips, transcript):
        enriched = []
        for clip in clips:
            clip_text = self._get_transcript_for_clip(clip, transcript)
            llm_result = self._call_llm(
                self._build_prompt(clip_text, clip.start, clip.end))
            if not llm_result:
                llm_result = self._fallback_enrich(clip, clip_text)
            title = llm_result.get("title", "")[:80]
            summary = llm_result.get("summary", "")
            quality_str = llm_result.get("quality", "medium").lower()
            quality = QualityRating.MEDIUM
            if quality_str == "high": quality = QualityRating.HIGH
            elif quality_str == "low": quality = QualityRating.LOW
            if quality == QualityRating.LOW and clip.source == ClipSource.AI:
                logger.info(f"Dropping low-quality AI clip at {clip.start}s")
                continue
            if clip.source == ClipSource.VOICE_TRIGGER:
                logger.info(f"Keeping voice clip at {clip.start}s regardless of quality")
            enriched.append({
                "clip": clip, "title": title, "summary": summary,
                "quality_rating": quality, "vod_id": vod_id})
        logger.info(f"Enriched {len(enriched)} clips with semantics")
        return enriched
