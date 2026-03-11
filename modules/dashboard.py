# Created by Jeff Hollaway

import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

FUTURISTIC_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;500;700&display=swap');
:root {
    --bg-primary: #0a0a1a;
    --bg-secondary: #12122a;
    --bg-card: #1a1a3e;
    --accent: #00f0ff;
    --accent-glow: rgba(0,240,255,0.3);
    --text-primary: #e0e0ff;
    --text-secondary: #8888aa;
    --success: #00ff88;
    --warning: #ffaa00;
    --danger: #ff4466;
    --gradient: linear-gradient(135deg, #00f0ff, #7b2fff);
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: 'Rajdhani', sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    min-height: 100vh;
    overflow-x: hidden;
}
.glow-text { text-shadow: 0 0 10px var(--accent-glow), 0 0 20px var(--accent-glow); }
.header {
    background: var(--bg-secondary);
    border-bottom: 2px solid var(--accent);
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4px 30px var(--accent-glow);
}
.header h1 {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.8rem;
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.status-badge {
    padding: 0.3rem 1rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.status-live { background: var(--success); color: #000; animation: pulse 2s infinite; }
.status-processing { background: var(--warning); color: #000; }
.status-idle { background: var(--text-secondary); color: #000; }
@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.7; } }
.container { max-width: 1400px; margin: 0 auto; padding: 2rem; }
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}
.stat-card {
    background: var(--bg-card);
    border: 1px solid rgba(0,240,255,0.15);
    border-radius: 12px;
    padding: 1.5rem;
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}
.stat-card:hover {
    border-color: var(--accent);
    box-shadow: 0 0 25px var(--accent-glow);
    transform: translateY(-2px);
}
.stat-card h3 { font-family:'Orbitron',sans-serif; font-size:0.8rem; color:var(--text-secondary); margin-bottom:0.5rem; text-transform:uppercase; letter-spacing:2px; }
.stat-card .value { font-family:'Orbitron',sans-serif; font-size:2.5rem; font-weight:900; color:var(--accent); }
.stat-card .sub { font-size:0.85rem; color:var(--text-secondary); margin-top:0.3rem; }
.clips-section { margin-top: 2rem; }
.clips-section h2 { font-family:'Orbitron',sans-serif; font-size:1.4rem; margin-bottom:1rem; border-left:3px solid var(--accent); padding-left:1rem; }
.clip-card {
    background: var(--bg-card);
    border: 1px solid rgba(0,240,255,0.1);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 1rem;
    align-items: center;
    transition: all 0.3s ease;
}
.clip-card:hover { border-color:var(--accent); box-shadow:0 0 15px var(--accent-glow); }
.clip-title { font-family:'Orbitron',sans-serif; font-size:1.1rem; margin-bottom:0.3rem; }
.clip-meta { color:var(--text-secondary); font-size:0.85rem; }
.clip-score {
    font-family:'Orbitron',sans-serif;
    font-size:1.5rem;
    font-weight:900;
    color: var(--accent);
    text-align: center;
}
.btn {
    font-family:'Rajdhani',sans-serif;
    font-weight:700;
    padding:0.6rem 1.5rem;
    border:2px solid var(--accent);
    background:transparent;
    color:var(--accent);
    border-radius:8px;
    cursor:pointer;
    text-transform:uppercase;
    letter-spacing:1px;
    transition:all 0.3s ease;
    text-decoration:none;
    display:inline-block;
}
.btn:hover { background:var(--accent); color:var(--bg-primary); box-shadow:0 0 20px var(--accent-glow); }
.btn-download { border-color:var(--success); color:var(--success); }
.btn-download:hover { background:var(--success); }
.btn-share { border-color:#7b2fff; color:#7b2fff; }
.btn-share:hover { background:#7b2fff; color:#fff; }
.qr-section { text-align:center; padding:2rem; }
.qr-section img { border:2px solid var(--accent); border-radius:12px; padding:10px; background:var(--bg-card); }
.mobile-note { font-size:0.9rem; color:var(--text-secondary); margin-top:1rem; }
@media (max-width: 768px) {
    .header h1 { font-size:1.2rem; }
    .stats-grid { grid-template-columns:1fr 1fr; }
    .stat-card .value { font-size:1.8rem; }
    .clip-card { grid-template-columns:1fr; }
    .container { padding:1rem; }
}
@media (max-width: 480px) {
    .stats-grid { grid-template-columns:1fr; }
    .header { flex-direction:column; gap:0.5rem; }
}
"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Highlighter Dashboard</title>
    <style>{css}</style>
</head>
<body>
    <div class="header">
        <h1 class="glow-text">AI HIGHLIGHTER</h1>
        <span class="status-badge status-{status}" id="statusBadge">{status_text}</span>
    </div>
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Clips</h3>
                <div class="value" id="totalClips">{total_clips}</div>
                <div class="sub">Generated highlights</div>
            </div>
            <div class="stat-card">
                <h3>Avg Score</h3>
                <div class="value" id="avgScore">{avg_score}</div>
                <div class="sub">Quality metric</div>
            </div>
            <div class="stat-card">
                <h3>VODs Processed</h3>
                <div class="value" id="vodsProcessed">{vods_processed}</div>
                <div class="sub">Analyzed streams</div>
            </div>
            <div class="stat-card">
                <h3>Voice Triggers</h3>
                <div class="value" id="voiceTriggers">{voice_triggers}</div>
                <div class="sub">Clip-that commands</div>
            </div>
        </div>
        <div class="clips-section">
            <h2>Recent Highlights</h2>
            {clips_html}
        </div>
        <div class="qr-section">
            <h2 style="margin-bottom:1rem; font-family:Orbitron,sans-serif;">Mobile Access</h2>
            <p class="mobile-note">Scan to view clips on your phone</p>
            <img src="data:image/png;base64,{qr_code}" alt="QR Code" style="margin-top:1rem;" />
            <p class="mobile-note" style="margin-top:0.5rem;">Dashboard URL: {dashboard_url}</p>
        </div>
    </div>
    <script>
        setInterval(async () => {{
            try {{
                const r = await fetch('/api/v1/health');
                const d = await r.json();
                document.getElementById('statusBadge').textContent = d.status;
            }} catch(e) {{ console.log('Health check failed'); }}
        }}, {refresh_interval}000);
    </script>
</body>
</html>"""

class DashboardGenerator:
    def __init__(self, config=None):
        self.config = config
        self.css = FUTURISTIC_CSS

    def generate_clip_html(self, clip):
        source_badge = "VOICE" if clip.get("source") == "voice_trigger" else "AI"
        return f"""
        <div class="clip-card">
            <div>
                <div class="clip-title">{clip.get("title","Untitled")}</div>
                <div class="clip-meta">
                    {clip.get("start",0):.1f}s - {clip.get("end",0):.1f}s |
                    Duration: {clip.get("duration",0):.1f}s |
                    Source: {source_badge} |
                    Quality: {clip.get("quality_rating","N/A")}
                </div>
                <div style="margin-top:0.8rem;">
                    <a href="/api/v1/clips/{clip.get("clip_id","")}/download" class="btn btn-download">Download</a>
                    <a href="/api/v1/clips/{clip.get("clip_id","")}/share" class="btn btn-share">Share</a>
                </div>
            </div>
            <div class="clip-score">{clip.get("score",0):.2f}</div>
        </div>"""

    def generate_dashboard(self, clips=None, stats=None, qr_code="", dashboard_url=""):
        clips = clips or []
        stats = stats or {}
        clips_html = "".join(self.generate_clip_html(c) for c in clips)
        if not clips_html:
            clips_html = "<p style=\"color:var(--text-secondary);text-align:center;padding:2rem;\">No clips generated yet. Start by analyzing a VOD.</p>"
        html = DASHBOARD_HTML.format(
            css=self.css,
            status=stats.get("status","idle"),
            status_text=stats.get("status","IDLE").upper(),
            total_clips=stats.get("total_clips",0),
            avg_score=f"{stats.get('avg_score',0):.2f}",
            vods_processed=stats.get("vods_processed",0),
            voice_triggers=stats.get("voice_triggers",0),
            clips_html=clips_html,
            qr_code=qr_code,
            dashboard_url=dashboard_url,
            refresh_interval=self.config.dashboard.auto_refresh_interval if self.config else 5
        )
        return html

    def save_dashboard(self, html, output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info(f"Dashboard saved to {output_path}")
