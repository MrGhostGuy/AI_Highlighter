
"""
AI Highlighter - Module 6: Vertical Rendering Engine
Renders clips as vertical 9:16 videos with captions.
Function: render_clip(vod_id, media_path, clip, transcript, title, style_preset) -> RenderedClip
Output: 1080x1920, H.264, AAC audio, 30/60fps
Layout: Main gameplay top 60%, cam bottom, captions in lower third safe zone
Captions: max 2 lines, max 42 chars/line, white text, dark outline, inside safe zones
"""
import os, logging, subprocess, uuid
from typing import List, Optional
logger = logging.getLogger(__name__)
try:
    from modules.models import RenderedClip, ClipCandidate, QualityRating, ClipSource
except ImportError:
    from models import RenderedClip, ClipCandidate, QualityRating, ClipSource

class RenderConfig:
    WIDTH = 1080
    HEIGHT = 1920
    CODEC = "libx264"
    AUDIO_CODEC = "aac"
    FPS = 30
    CRF = 18
    PRESET = "medium"
    CAPTION_FONT_SIZE = 48
    CAPTION_MAX_CHARS = 42
    CAPTION_MAX_LINES = 2
    CAPTION_COLOR = "white"
    CAPTION_OUTLINE = "black"
    CAPTION_Y_POSITION = 0.85
    SAFE_MARGIN = 50

class CaptionRenderer:
    def __init__(self, config):
        self.config = config
    def _wrap_text(self, text):
        words = text.split()
        lines, current = [], ""
        for word in words:
            if len(current) + len(word) + 1 <= self.config.CAPTION_MAX_CHARS:
                current = f"{current} {word}".strip()
            else:
                if current: lines.append(current)
                current = word
            if len(lines) >= self.config.CAPTION_MAX_LINES - 1 and len(current) + len(word) > self.config.CAPTION_MAX_CHARS:
                break
        if current: lines.append(current)
        return lines[:self.config.CAPTION_MAX_LINES]
    def generate_ass_subtitles(self, transcript, clip_start, clip_end, output_path):
        header = """[Script Info]
Title: AI Highlighter Captions
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,OutlineColour,Bold,Alignment,MarginV
Style: Default,Arial,48,&H00FFFFFF,&H00000000,1,2,200

[Events]
Format: Layer,Start,End,Style,Text
"""
        events = []
        for seg in transcript:
            if seg.end < clip_start or seg.start > clip_end: continue
            s = max(0, seg.start - clip_start)
            e = min(clip_end - clip_start, seg.end - clip_start)
            lines = self._wrap_text(seg.text)
            text = "\N".join(lines)
            sh,sm,ss = int(s//3600), int((s%3600)//60), s%60
            eh,em,es = int(e//3600), int((e%3600)//60), e%60
            events.append(f"Dialogue: 0,{sh}:{sm:02d}:{ss:05.2f},{eh}:{em:02d}:{es:05.2f},Default,{text}")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(header + "\n".join(events))
        return output_path

class VerticalRenderEngine:
    def __init__(self, config=None):
        self.config = config or RenderConfig()
        self.captions = CaptionRenderer(self.config)
    def render_clip(self, vod_id, media_path, clip, transcript, title, summary,
                    quality_rating, style_preset="default"):
        clip_id = str(uuid.uuid4())[:8]
        out_dir = os.path.join(os.path.dirname(media_path), "rendered_clips")
        os.makedirs(out_dir, exist_ok=True)
        output_path = os.path.join(out_dir, f"{vod_id}_{clip_id}.mp4")
        sub_path = os.path.join(out_dir, f"{vod_id}_{clip_id}.ass")
        self.captions.generate_ass_subtitles(transcript, clip.start, clip.end, sub_path)
        vf = (f"crop=ih*9/16:ih,scale={self.config.WIDTH}:{self.config.HEIGHT},"
              f"ass={sub_path}")
        cmd = ["ffmpeg", "-i", media_path,
               "-ss", str(clip.start), "-to", str(clip.end),
               "-vf", vf,
               "-c:v", self.config.CODEC, "-crf", str(self.config.CRF),
               "-preset", self.config.PRESET,
               "-c:a", self.config.AUDIO_CODEC, "-b:a", "128k",
               "-r", str(self.config.FPS),
               "-y", output_path]
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=600)
            logger.info(f"Rendered clip {clip_id} to {output_path}")
        except Exception as e:
            logger.error(f"Render failed: {e}")
            raise
        rendered = RenderedClip(
            id=clip_id, vod_id=vod_id, start=clip.start, end=clip.end,
            title=title, summary=summary, quality_rating=quality_rating,
            output_path=output_path, source=clip.source,
            format_spec={"resolution": f"{self.config.WIDTH}x{self.config.HEIGHT}",
                "codec": "H.264", "audio_codec": "AAC",
                "fps": self.config.FPS, "aspect_ratio": "9:16"})
        return rendered
