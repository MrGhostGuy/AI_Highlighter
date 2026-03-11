# Created by Jeff Hollaway
html = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Highlighter Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@400;600&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0a0a1a;color:#e0e0ff;font-family:Rajdhani,sans-serif;min-height:100vh}
.header{background:linear-gradient(135deg,#0a0a1a,#1a1a3a);padding:20px 30px;border-bottom:2px solid #00f0ff;display:flex;align-items:center;justify-content:space-between}
.header h1{font-family:Orbitron,sans-serif;color:#00f0ff;font-size:28px;text-shadow:0 0 20px rgba(0,240,255,0.5)}
.container{max-width:1200px;margin:0 auto;padding:30px}
.search-section{background:linear-gradient(135deg,#12122a,#1a1a3a);border:1px solid #00f0ff33;border-radius:12px;padding:30px;margin-bottom:30px}
.search-section h2{font-family:Orbitron,sans-serif;color:#00f0ff;margin-bottom:20px;font-size:20px}
.input-row{display:flex;gap:15px;margin-bottom:20px}
.input-row input{flex:1;background:#0a0a1a;border:1px solid #00f0ff55;border-radius:8px;padding:12px 18px;color:#e0e0ff;font-size:16px;font-family:Rajdhani;outline:none}
.input-row input:focus{border-color:#00f0ff}
.btn{background:linear-gradient(135deg,#00f0ff,#0088ff);color:#0a0a1a;border:none;border-radius:8px;padding:12px 28px;font-size:16px;font-weight:700;cursor:pointer;font-family:Rajdhani;transition:all 0.3s;text-transform:uppercase}
.btn:hover{transform:translateY(-2px);box-shadow:0 5px 20px rgba(0,240,255,0.4)}
.btn:disabled{opacity:0.5;cursor:not-allowed;transform:none}
.btn-analyze{background:linear-gradient(135deg,#ff006e,#ff4444)}
.vod-list{display:grid;gap:15px;margin-top:20px}
.vod-card{background:#0a0a1a;border:1px solid #ffffff15;border-radius:10px;padding:20px;display:flex;justify-content:space-between;align-items:center;transition:all 0.3s;cursor:pointer}
.vod-card:hover{border-color:#00f0ff;transform:translateX(5px)}
.vod-card.selected{border-color:#00ff88;background:#00ff8810}
.vod-card .vod-info h3{color:#fff;font-size:18px;margin-bottom:5px}
.vod-card .vod-info p{color:#888;font-size:14px}
.vod-card .vod-meta{text-align:right;color:#00f0ff;font-size:14px}
.progress-section{background:linear-gradient(135deg,#12122a,#1a1a3a);border:1px solid #00f0ff33;border-radius:12px;padding:30px;margin-bottom:30px;display:none}
.progress-section h2{font-family:Orbitron,sans-serif;color:#00f0ff;margin-bottom:20px}
.progress-bar-container{background:#0a0a1a;border-radius:20px;height:30px;overflow:hidden;margin-bottom:15px;border:1px solid #00f0ff33}
.progress-bar{height:100%;background:linear-gradient(90deg,#00f0ff,#00ff88);border-radius:20px;transition:width 0.5s;width:0%;display:flex;align-items:center;justify-content:center;font-weight:700;color:#0a0a1a;font-size:14px}
.stage-text{color:#00f0ff;font-size:18px;text-align:center;margin-top:10px}
.results-section{display:none}
.results-section h2{font-family:Orbitron,sans-serif;color:#00f0ff;margin-bottom:20px}
.clip-card{background:linear-gradient(135deg,#12122a,#1a1a3a);border:1px solid #00f0ff33;border-radius:12px;padding:25px;margin-bottom:20px}
.clip-card h3{color:#fff;font-size:20px;margin-bottom:10px}
.clip-card .clip-meta{display:flex;flex-wrap:wrap;gap:15px;margin-bottom:15px}
.clip-card .clip-meta span{background:#0a0a1a;padding:5px 12px;border-radius:6px;font-size:13px;color:#888}
.clip-card .clip-meta span.voice{border:1px solid #ff006e;color:#ff006e}
.clip-card .clip-meta span.high{border:1px solid #00ff88;color:#00ff88}
.clip-card .clip-meta span.medium{border:1px solid #ffaa00;color:#ffaa00}
.clip-card .summary{color:#bbb;font-size:15px;line-height:1.6;margin-bottom:15px}
.clip-card .score-bar{display:flex;align-items:center;gap:10px}
.clip-card .score-bar .bar{flex:1;background:#0a0a1a;height:8px;border-radius:4px;overflow:hidden}
.clip-card .score-bar .bar-fill{height:100%;border-radius:4px}
.clip-card .score-bar .score-label{color:#00f0ff;font-weight:700;min-width:50px}
.stats-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px;margin-bottom:30px}
.stat-card{background:linear-gradient(135deg,#12122a,#1a1a3a);border:1px solid #00f0ff33;border-radius:10px;padding:20px;text-align:center}
.stat-card .stat-value{font-family:Orbitron;font-size:32px;color:#00f0ff;margin-bottom:5px}
.stat-card .stat-label{color:#888;font-size:14px;text-transform:uppercase}
.log-section{background:#0a0a1a;border:1px solid #00f0ff33;border-radius:10px;padding:15px;margin-top:20px;max-height:200px;overflow-y:auto;font-family:monospace;font-size:13px;color:#00ff88}
.log-entry{padding:3px 0;border-bottom:1px solid #ffffff08}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}
.analyzing .stage-text{animation:pulse 1.5s infinite}
</style>
</head>
<body>
<div class="header"><h1>AI HIGHLIGHTER</h1><div style="color:#00ff88;font-size:14px">SYSTEM ONLINE</div></div>
<div class="container">
<div class="search-section">
<h2>SEARCH TWITCH VODs</h2>
<div class="input-row">
<input type="text" id="username" placeholder="Enter Twitch username..." value="">
<button class="btn" id="searchBtn" onclick="searchVods()">SEARCH</button>
</div>
<div id="vodList" class="vod-list"></div>
<div style="margin-top:20px;text-align:center;display:none" id="analyzeRow">
<button class="btn btn-analyze" id="analyzeBtn" onclick="analyzeVod()">ANALYZE SELECTED VOD</button>
</div>
</div>
<div class="progress-section" id="progressSection">
<h2>ANALYSIS IN PROGRESS</h2>
<div class="progress-bar-container"><div class="progress-bar" id="progressBar">0%</div></div>
<div class="stage-text" id="stageText">Initializing...</div>
<div class="log-section" id="logSection"></div>
</div>
<div class="results-section" id="resultsSection">
<h2>GENERATED HIGHLIGHTS</h2>
<div class="stats-row" id="statsRow"></div>
<div id="clipsList"></div>
</div>
</div>
<script>
let selectedVod=null,currentJobId=null,vods=[];
function log(m){const l=document.getElementById("logSection"),e=document.createElement("div");e.className="log-entry";e.textContent="["+new Date().toLocaleTimeString()+"] "+m;l.appendChild(e);l.scrollTop=l.scrollHeight}
function fmtTime(s){return Math.floor(s/60)+":"+String(Math.floor(s%60)).padStart(2,"0")}
async function searchVods(){
const u=document.getElementById("username").value.trim();
if(!u){alert("Enter a username");return}
document.getElementById("searchBtn").disabled=true;
document.getElementById("searchBtn").textContent="SEARCHING...";
log("Searching for Twitch user: "+u);
try{const r=await fetch("/api/v1/twitch/search",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({username:u})});
const d=await r.json();vods=d.vods||[];
const vl=document.getElementById("vodList");vl.innerHTML="";
if(vods.length===0){vl.innerHTML="<p style=color:#ff4444>No VODs found</p>";return}
log("Found "+vods.length+" VODs for "+u);
vods.forEach((v,i)=>{const c=document.createElement("div");c.className="vod-card";c.onclick=()=>selectVod(i);
c.innerHTML='<div class="vod-info"><h3>'+v.title+'</h3><p>VOD ID: '+v.vod_id+'</p></div><div class="vod-meta"><div>'+v.duration+'</div><div>'+v.date+'</div><div>'+v.game+'</div></div>';
vl.appendChild(c)});
}catch(e){log("Error: "+e.message)}
finally{document.getElementById("searchBtn").disabled=false;document.getElementById("searchBtn").textContent="SEARCH"}}
function selectVod(i){selectedVod=vods[i];document.querySelectorAll(".vod-card").forEach((c,j)=>{c.className=j===i?"vod-card selected":"vod-card"});
document.getElementById("analyzeRow").style.display="block";log("Selected VOD: "+selectedVod.title)}
async function analyzeVod(){
if(!selectedVod)return;
document.getElementById("analyzeBtn").disabled=true;
document.getElementById("progressSection").style.display="block";
document.getElementById("progressSection").className="progress-section analyzing";
log("Starting analysis of VOD: "+selectedVod.vod_id);
try{const r=await fetch("/api/v1/vods/analyze",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({twitch_vod_url:"https://twitch.tv/videos/"+selectedVod.vod_id,username:document.getElementById("username").value.trim()})});
const d=await r.json();currentJobId=d.job_id;log("Job created: "+currentJobId);pollJob();
}catch(e){log("Error: "+e.message)}}
async function pollJob(){
if(!currentJobId)return;
try{const r=await fetch("/api/v1/jobs/"+currentJobId);const d=await r.json();
const pct=Math.round((d.progress||0)*100);
document.getElementById("progressBar").style.width=pct+"%";
document.getElementById("progressBar").textContent=pct+"%";
document.getElementById("stageText").textContent=d.stage||"Processing...";
log(d.stage+" - "+pct+"%");
if(d.status==="completed"){log("Analysis complete!");document.getElementById("progressSection").className="progress-section";
document.getElementById("stageText").textContent="Analysis Complete!";fetchClips();return}
if(d.status==="failed"){log("FAILED: "+d.error);return}
setTimeout(pollJob,1500);
}catch(e){log("Poll error: "+e.message);setTimeout(pollJob,2000)}}
async function fetchClips(){
try{const r=await fetch("/api/v1/jobs/"+currentJobId+"/clips");const d=await r.json();const clips=d.clips||[];
log("Retrieved "+clips.length+" clips");
const rs=document.getElementById("resultsSection");rs.style.display="block";
const vc=clips.filter(c=>c.source==="voice_trigger").length;
document.getElementById("statsRow").innerHTML='<div class="stat-card"><div class="stat-value">'+clips.length+'</div><div class="stat-label">Total Clips</div></div><div class="stat-card"><div class="stat-value">'+vc+'</div><div class="stat-label">Voice Triggers</div></div><div class="stat-card"><div class="stat-value">'+(clips.length-vc)+'</div><div class="stat-label">AI Detected</div></div><div class="stat-card"><div class="stat-value">'+Math.round(clips.reduce((a,c)=>a+(c.score||0),0)/clips.length*100)+'%</div><div class="stat-label">Avg Score</div></div>';
const cl=document.getElementById("clipsList");cl.innerHTML="";
const colors=["#00f0ff","#00ff88","#ff006e","#ffaa00","#aa44ff"];
clips.forEach((c,i)=>{const pct=Math.round((c.score||0)*100);const qc=c.quality==="high"?"high":c.quality==="medium"?"medium":"";
const card=document.createElement("div");card.className="clip-card";
card.innerHTML='<h3>'+(c.title||"Clip "+(i+1))+'</h3><div class="clip-meta"><span>Start: '+fmtTime(c.start)+'</span><span>End: '+fmtTime(c.end)+'</span><span>Duration: '+Math.round(c.end-c.start)+'s</span>'+(c.source==="voice_trigger"?'<span class="voice">VOICE TRIGGER</span>':'<span>AI DETECTED</span>')+'<span class="'+qc+'">'+((c.quality||"medium")+" quality").toUpperCase()+'</span></div><div class="summary">'+(c.summary||"")+'</div><div class="score-bar"><span class="score-label">'+pct+'%</span><div class="bar"><div class="bar-fill" style="width:'+pct+'%;background:'+colors[i%colors.length]+'"></div></div></div>';
cl.appendChild(card)});
rs.scrollIntoView({behavior:"smooth"});
}catch(e){log("Error: "+e.message)}}
document.getElementById("username").addEventListener("keypress",e=>{if(e.key==="Enter")searchVods()});
</script>
</body></html>'''

with open('output/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Dashboard updated:', len(html), 'bytes')
