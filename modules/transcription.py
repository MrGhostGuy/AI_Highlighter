# Created by Jeff Hollaway

"""
AI Highlighter - Module 1: Transcription Engine
Uses Whisper ASR with overlapping windows.
Function: transcribe_vod(vod_id, media_path) -> List[TranscriptSegment]
"""
import os, re, logging, subprocess
from typing import List, Tuple, Optional
logger = logging.getLogger(__name__)
try:
    from modules.models import TranscriptSegment
except ImportError:
    from models import TranscriptSegment

class TranscriptionConfig:
    WHISPER_MODEL = "large-v2"
    CHUNK_DURATION = 30.0
    OVERLAP = 5.0
    MIN_CONFIDENCE = 0.4
    SAMPLE_RATE = 16000
    LANGUAGE = "en"

class AudioExtractor:
    @staticmethod
    def extract(media_path, output_path, sr=16000):
        if not os.path.exists(media_path):
            raise FileNotFoundError(f"Media not found: {media_path}")
        cmd = ["ffmpeg","-i",media_path,"-ac","1","-ar",str(sr),"-vn","-y",output_path]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

class WhisperASR:
    def __init__(self, config):
        self.config = config
        self._model = None
    def load(self):
        try:
            import whisper
            self._model = whisper.load_model(self.config.WHISPER_MODEL)
        except ImportError:
            logger.warning("Whisper not installed")
    def transcribe(self, audio_path, offset=0.0):
        if not self._model: return []
        result = self._model.transcribe(audio_path, language=self.config.LANGUAGE, word_timestamps=True)
        return [{"start": s["start"]+offset, "end": s["end"]+offset,
                 "text": s["text"].strip(), "confidence": s.get("avg_logprob",0)}
                for s in result.get("segments",[])]

class SegmentMerger:
    @staticmethod
    def normalize(text):
        return re.sub(r"\s+", " ", text.strip().lower())
    @staticmethod
    def similarity(t1, t2):
        w1, w2 = set(t1.lower().split()), set(t2.lower().split())
        if not w1 or not w2: return 0.0
        return len(w1 & w2) / len(w1 | w2)
    def merge(self, segments, threshold=0.7):
        if not segments: return []
        segs = sorted(segments, key=lambda s: s["start"])
        merged = [segs[0]]
        for s in segs[1:]:
            last = merged[-1]
            if last["end"] > s["start"]:
                if self.similarity(last["text"], s["text"]) > threshold:
                    if s.get("confidence",0) > last.get("confidence",0):
                        merged[-1] = s
                    continue
                mid = (last["end"] + s["start"]) / 2
                last["end"] = mid
                s["start"] = mid
            merged.append(s)
        return merged

class TranscriptionEngine:
    def __init__(self, config=None):
        self.config = config or TranscriptionConfig()
        self.extractor = AudioExtractor()
        self.asr = WhisperASR(self.config)
        self.merger = SegmentMerger()
    def initialize(self):
        self.asr.load()
    def _chunks(self, duration):
        chunks, start = [], 0.0
        step = self.config.CHUNK_DURATION - self.config.OVERLAP
        while start < duration:
            chunks.append((start, min(start + self.config.CHUNK_DURATION, duration)))
            start += step
        return chunks
    def transcribe_vod(self, vod_id, media_path):
        audio = media_path.rsplit(".",1)[0] + "_audio.wav"
        self.extractor.extract(media_path, audio, self.config.SAMPLE_RATE)
        try:
            r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                "-of","default=noprint_wrappers=1:nokey=1",media_path],
                capture_output=True, text=True, check=True)
            dur = float(r.stdout.strip())
        except: dur = 3600.0
        all_segs = []
        for cs, ce in self._chunks(dur):
            chunk_f = f"{audio}.chunk_{cs:.0f}_{ce:.0f}.wav"
            subprocess.run(["ffmpeg","-i",audio,"-ss",str(cs),"-to",str(ce),"-y",chunk_f], capture_output=True)
            all_segs.extend(self.asr.transcribe(chunk_f, offset=cs))
            if os.path.exists(chunk_f): os.remove(chunk_f)
        merged = self.merger.merge(all_segs)
        result = []
        for s in merged:
            if s.get("confidence",0) < self.config.MIN_CONFIDENCE and not s["text"].strip(): continue
            txt = self.merger.normalize(s["text"])
            if not txt: continue
            seg = TranscriptSegment(vod_id=vod_id, start=round(s["start"],2),
                end=round(s["end"],2), text=txt,
                confidence=round(max(0,min(1,s.get("confidence",0.5))),3))
            result.append(seg)
        result.sort(key=lambda s: s.start)
        if os.path.exists(audio): os.remove(audio)
        return result
