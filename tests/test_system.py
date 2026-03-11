# Created by Jeff Hollaway
from modules.models import ClipSource

import unittest
import os
import json
from dataclasses import asdict

class TestDataModels(unittest.TestCase):
    def test_vod_creation(self):
        from modules.models import Vod
        v = Vod(id="v1", twitch_vod_id="123", source_url="https://twitch.tv/v/123", duration_seconds=3600.0, status="pending")
        self.assertEqual(v.id, "v1")
        self.assertEqual(v.duration_seconds, 3600.0)
        v.validate()

    def test_transcript_segment(self):
        from modules.models import TranscriptSegment
        ts = TranscriptSegment(vod_id="v1", start=10.0, end=15.0, text="Hello world", confidence=0.95)
        self.assertEqual(ts.duration, 5.0)
        self.assertGreater(ts.confidence, 0.5)
        ts.validate()

    def test_transcript_segment_invalid(self):
        from modules.models import TranscriptSegment
        ts = TranscriptSegment(vod_id="v1", start=15.0, end=10.0, text="bad", confidence=0.9)
        with self.assertRaises(AssertionError):
            ts.validate()

    def test_feature_vector(self):
        from modules.models import FeatureVector
        fv = FeatureVector(vod_id="v1", timestamp=30.0, audio_energy=0.8, audio_spike=True, motion_intensity=0.5, scene_change=False, chat_hype=0.6, semantic_importance=0.7)
        fv.validate()

    def test_clip_candidate(self):
        from modules.models import ClipCandidate
        cc = ClipCandidate(vod_id="v1", start=100.0, end=160.0, score=0.85, source="ai", reason="High engagement")
        self.assertEqual(cc.duration, 60.0)
        self.assertFalse(cc.is_voice_triggered)
        cc.validate()

    def test_voice_triggered_clip(self):
        from modules.models import ClipCandidate
        cc = ClipCandidate(vod_id="v1", start=50.0, end=80.0, score=1.0, source=ClipSource.VOICE_TRIGGER, reason="clip that")
        self.assertTrue(cc.is_voice_triggered)
        self.assertEqual(cc.duration, 30.0)

    def test_clip_length_constraints(self):
        from modules.models import ClipCandidate
        short = ClipCandidate(vod_id="v1", start=0.0, end=20.0, score=0.5, source="ai", reason="test")
        self.assertEqual(short.duration, 20.0)
        long_clip = ClipCandidate(vod_id="v1", start=0.0, end=130.0, score=0.5, source="ai", reason="test")
        self.assertGreater(long_clip.duration, 120)

class TestScoringWeights(unittest.TestCase):
    def test_weights_sum_to_one(self):
        from modules.config import ScoringConfig
        sc = ScoringConfig()
        total = sc.audio_weight + sc.chat_weight + sc.visual_weight + sc.semantic_weight
        self.assertAlmostEqual(total, 1.0, places=2)

    def test_custom_weights(self):
        from modules.config import ScoringConfig
        sc = ScoringConfig(audio_weight=0.4, chat_weight=0.2, visual_weight=0.2, semantic_weight=0.2)
        total = sc.audio_weight + sc.chat_weight + sc.visual_weight + sc.semantic_weight
        self.assertAlmostEqual(total, 1.0, places=2)

class TestClipRules(unittest.TestCase):
    def test_min_length(self):
        from modules.config import ClipConfig
        cc = ClipConfig()
        self.assertGreaterEqual(cc.min_length, 30)

    def test_max_length(self):
        from modules.config import ClipConfig
        cc = ClipConfig()
        self.assertLessEqual(cc.max_length, 120)

    def test_merge_gap(self):
        from modules.config import ClipConfig
        cc = ClipConfig()
        self.assertGreater(cc.merge_gap_threshold, 0)

class TestConfiguration(unittest.TestCase):
    def test_default_config(self):
        from modules.config import PipelineConfig
        pc = PipelineConfig()
        pc.validate()

    def test_render_dimensions(self):
        from modules.config import RenderConfig
        rc = RenderConfig()
        self.assertEqual(rc.WIDTH, 1080)
        self.assertEqual(rc.HEIGHT, 1920)
        self.assertEqual(rc.aspect_ratio, "9:16")

    def test_dashboard_config(self):
        from modules.config import DashboardConfig
        dc = DashboardConfig()
        self.assertEqual(dc.theme, "futuristic")
        self.assertTrue(dc.enable_qr_code)
        self.assertTrue(dc.mobile_responsive)

class TestVoiceClipping(unittest.TestCase):
    def test_trigger_detection(self):
        triggers = ["clip that", "save that", "highlight that", "last couple minutes"]
        text = "wow that was amazing clip that please"
        found = any(t in text.lower() for t in triggers)
        self.assertTrue(found)

    def test_no_trigger(self):
        triggers = ["clip that", "save that", "highlight that"]
        text = "just a normal conversation"
        found = any(t in text.lower() for t in triggers)
        self.assertFalse(found)

if __name__ == "__main__":
    unittest.main()
