# Created by Jeff Hollaway

import os
import logging
import json
from datetime import datetime
from typing import List, Optional

logger = logging.getLogger(__name__)

class HighlighterPipeline:
    def __init__(self, config):
        self.config = config
        self.config.validate()
        logger.info(f"Pipeline initialized: v{config.version}")

    def run(self, vod_url: str, media_path: str, chat_data=None):
        logger.info(f"Starting pipeline for: {vod_url}")
        start = datetime.now()
        vod_id = self._generate_vod_id(vod_url)
        results = {"vod_id": vod_id, "vod_url": vod_url, "stages": {}}

        # Stage 1: Transcription
        logger.info("[1/7] Transcription")
        from modules.transcription import TranscriptionEngine
        te = TranscriptionEngine(self.config)
        transcript = te.transcribe_vod(vod_id, media_path)
        results["stages"]["transcription"] = {"segments": len(transcript), "status": "complete"}

        # Stage 2: Voice-Triggered Clipping
        logger.info("[2/7] Voice-Triggered Clipping")
        from modules.voice_clipping import VoiceClipDetector
        vcd = VoiceClipDetector(self.config)
        voice_clips = vcd.detect_voice_triggered_clips(transcript)
        results["stages"]["voice_clipping"] = {"clips": len(voice_clips), "status": "complete"}

        # Stage 3: Feature Extraction
        logger.info("[3/7] Feature Extraction")
        from modules.feature_extraction import FeatureExtractor
        fe = FeatureExtractor(self.config)
        features = fe.extract_features(vod_id, media_path, transcript, chat_data)
        results["stages"]["feature_extraction"] = {"features": len(features), "status": "complete"}

        # Stage 4: Highlight Scoring
        logger.info("[4/7] Highlight Scoring")
        from modules.scoring import HighlightScorer
        hs = HighlightScorer(self.config)
        ai_clips = hs.score_highlights(features)
        results["stages"]["scoring"] = {"clips": len(ai_clips), "status": "complete"}

        # Stage 5: Merge & Deduplicate
        logger.info("[5/7] Merging Clips")
        all_clips = self._merge_clips(voice_clips, ai_clips)
        results["stages"]["merging"] = {"total_clips": len(all_clips), "status": "complete"}

        # Stage 6: LLM Semantics
        logger.info("[6/7] LLM Semantics & Titles")
        from modules.llm_semantics import LLMSemanticEnricher
        enricher = LLMSemanticEnricher(self.config)
        enriched = enricher.enrich_clips_with_semantics(vod_id, all_clips, transcript)
        results["stages"]["semantics"] = {"enriched": len(enriched), "status": "complete"}

        # Stage 7: Rendering
        logger.info("[7/7] Vertical Rendering")
        from modules.rendering import VerticalRenderer
        renderer = VerticalRenderer(self.config)
        rendered = renderer.render_clips(enriched, media_path)
        results["stages"]["rendering"] = {"rendered": len(rendered), "status": "complete"}

        elapsed = (datetime.now() - start).total_seconds()
        results["total_time"] = elapsed
        results["total_clips"] = len(rendered)
        results["status"] = "complete"

        self._save_results(results)
        logger.info(f"Pipeline complete: {len(rendered)} clips in {elapsed:.1f}s")
        return results

    def _merge_clips(self, voice_clips, ai_clips):
        all_clips = list(voice_clips)
        for ac in ai_clips:
            overlap = False
            for vc in voice_clips:
                if ac.start < vc.end and ac.end > vc.start:
                    overlap = True
                    break
            if not overlap:
                all_clips.append(ac)
        all_clips.sort(key=lambda c: c.start)
        merged = []
        for clip in all_clips:
            if merged and not clip.is_voice_triggered:
                last = merged[-1]
                if not last.is_voice_triggered and clip.start - last.end < self.config.clip.merge_gap_threshold:
                    last.end = max(last.end, clip.end)
                    last.score = max(last.score, clip.score)
                    continue
            merged.append(clip)
        logger.info(f"Merged {len(voice_clips)} voice + {len(ai_clips)} AI = {len(merged)} total")
        return merged

    def _generate_vod_id(self, vod_url):
        import hashlib
        return hashlib.sha256(vod_url.encode()).hexdigest()[:16]

    def _save_results(self, results):
        out = os.path.join(self.config.base_dir, self.config.output_dir, f"results_{results['vod_id']}.json")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w") as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Results saved to {out}")
