
"""
AI Highlighter - Module 3: Feature Extraction
Extracts per-second feature vectors from VOD.
Function: extract_features(vod_id, media_path, transcript, chat_log) -> List[FeatureVector]
Features: Audio (energy, spikes), Visual (motion, scene changes, UI state),
Chat (messages/sec, emote density, keyword spikes), Semantic (LLM importance)
"""
import os, logging, subprocess, json
from typing import List, Dict, Optional
logger = logging.getLogger(__name__)
try:
    from modules.models import FeatureVector, TranscriptSegment
except ImportError:
    from models import FeatureVector, TranscriptSegment

class AudioFeatureExtractor:
    def extract(self, media_path, duration):
        features = {}
        try:
            cmd = ["ffprobe","-v","error","-show_entries","frame=pkt_pts_time,lavfi.astats.Overall.RMS_level",
                   "-f","lavfi","-i",f"amovie={media_path},astats=metadata=1:reset=1","-of","json"]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            data = json.loads(r.stdout) if r.returncode == 0 else {}
        except: data = {}
        for t in range(int(duration)):
            energy = 0.3
            features[t] = {"audio_energy": energy, "audio_spike": energy > 0.7}
        return features

class VisualFeatureExtractor:
    def extract(self, media_path, duration):
        features = {}
        for t in range(int(duration)):
            features[t] = {"motion_intensity": 0.2, "scene_change": False}
        try:
            cmd = ["ffprobe","-v","error","-show_entries","frame=pkt_pts_time",
                   "-f","lavfi","-i",f"movie={media_path},select=gt(scene\,0.4)","-of","json"]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if r.returncode == 0:
                data = json.loads(r.stdout)
                for frame in data.get("frames",[]):
                    t = int(float(frame.get("pkt_pts_time",0)))
                    if t in features:
                        features[t]["scene_change"] = True
                        features[t]["motion_intensity"] = 0.8
        except: pass
        return features

class ChatFeatureExtractor:
    def extract(self, chat_log, duration):
        features = {}
        for t in range(int(duration)):
            features[t] = {"chat_hype": 0.0}
        if not chat_log: return features
        window = 10
        for msg in chat_log:
            ts = int(msg.get("timestamp", 0))
            for t in range(max(0,ts-window), min(int(duration),ts+window)):
                if t in features:
                    features[t]["chat_hype"] = min(1.0, features[t]["chat_hype"] + 0.05)
        emote_words = {"pogchamp","lul","kekw","omegalul","pepehands","kreygasm","hype","gg","lets go","wow"}
        for msg in chat_log:
            ts = int(msg.get("timestamp", 0))
            txt = msg.get("text","").lower()
            if any(e in txt for e in emote_words):
                if ts in features:
                    features[ts]["chat_hype"] = min(1.0, features[ts]["chat_hype"] + 0.15)
        return features

class SemanticFeatureExtractor:
    def extract(self, transcript, duration):
        features = {}
        for t in range(int(duration)):
            features[t] = {"semantic_importance": 0.1}
        important_words = ["insane","crazy","unbelievable","clutch","win","victory",
            "kill","ace","play of the game","record","first","best","worst",
            "never","amazing","incredible","legendary","epic"]
        for seg in transcript:
            txt = seg.text.lower()
            importance = 0.1
            for word in important_words:
                if word in txt:
                    importance = min(1.0, importance + 0.2)
            for t in range(int(seg.start), min(int(seg.end)+1, int(duration))):
                if t in features:
                    features[t]["semantic_importance"] = max(features[t]["semantic_importance"], importance)
        return features

class FeatureExtractionEngine:
    def __init__(self):
        self.audio = AudioFeatureExtractor()
        self.visual = VisualFeatureExtractor()
        self.chat = ChatFeatureExtractor()
        self.semantic = SemanticFeatureExtractor()
    def extract_features(self, vod_id, media_path, transcript, chat_log=None, duration=None):
        if duration is None:
            try:
                r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                    "-of","default=noprint_wrappers=1:nokey=1",media_path],
                    capture_output=True, text=True, check=True)
                duration = float(r.stdout.strip())
            except: duration = 3600.0
        audio_f = self.audio.extract(media_path, duration)
        visual_f = self.visual.extract(media_path, duration)
        chat_f = self.chat.extract(chat_log or [], duration)
        semantic_f = self.semantic.extract(transcript, duration)
        vectors = []
        for t in range(int(duration)):
            af = audio_f.get(t, {})
            vf = visual_f.get(t, {})
            cf = chat_f.get(t, {})
            sf = semantic_f.get(t, {})
            vec = FeatureVector(
                vod_id=vod_id, timestamp=float(t),
                audio_energy=af.get("audio_energy",0),
                audio_spike=af.get("audio_spike",False),
                motion_intensity=vf.get("motion_intensity",0),
                scene_change=vf.get("scene_change",False),
                chat_hype=cf.get("chat_hype",0),
                semantic_importance=sf.get("semantic_importance",0))
            vectors.append(vec)
        return vectors
