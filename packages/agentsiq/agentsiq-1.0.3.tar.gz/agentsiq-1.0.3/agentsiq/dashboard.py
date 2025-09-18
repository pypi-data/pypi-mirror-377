
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse,HTMLResponse,PlainTextResponse,RedirectResponse
import os,glob,html
from .agentops_metrics import summary_by_agent
from .decision_store import latest_decisions
from .router_manager import router_manager

DARK_CSS = """
body{background:#0b0f17;color:#e5e7eb;font-family:system-ui,Segoe UI,Arial,sans-serif;margin:0;padding:1rem}
a{color:#93c5fd}
.card{background:#111827;border:1px solid #1f2937;border-radius:12px;padding:16px;margin-bottom:16px;box-shadow:0 1px 0 #000}
table{width:100%;border-collapse:collapse;border:1px solid #1f2937;border-radius:12px;overflow:hidden}
th,td{padding:10px;border-bottom:1px solid #1f2937}
th{background:#0f172a;text-align:left}
tr:hover{background:#0f172a}
.badge{display:inline-block;padding:2px 8px;border-radius:999px;background:#1f2937}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}
small{color:#9ca3af}
.bar{height:8px;border-radius:4px;background:#1f2937;overflow:hidden}
.bar>span{display:block;height:100%;background:#60a5fa}
svg{display:block}
input[type=range]{width:200px}
label{display:block;margin:6px 0}
button{background:#1f2937;border:1px solid #374151;color:#e5e7eb;padding:6px 10px;border-radius:8px;cursor:pointer}
button:hover{background:#0f172a}
"""

app=FastAPI(title="AgentsIQ Dashboard")

@app.get("/")
def root():
    return HTMLResponse(f"""
<html><head><title>AgentsIQ Dashboard</title><style>{DARK_CSS}</style></head>
<body>
<div class='card'>
<h1>AgentsIQ Dashboard</h1>
<p><a href='/summary'>/summary</a> • <a href='/decisions'>/decisions</a> • <a href='/control'>/control</a> • <a href='/health'>/health</a> • <a href='/metrics'>/metrics</a> • <a href='/logs'>/logs</a></p>
</div>
</body></html>
""")

@app.get("/health")
def health():
    openai_key = bool(os.getenv("OPENAI_API_KEY"))
    anthropic_key = bool(os.getenv("ANTHROPIC_API_KEY"))
    google_key = bool(os.getenv("GOOGLE_API_KEY"))
    agentops_key = bool(os.getenv("AGENTOPS_API_KEY"))
    return JSONResponse({
        "openai": {"api_key_present": openai_key},
        "anthropic": {"api_key_present": anthropic_key},
        "gemini": {"api_key_present": google_key},
        "agentops": {"api_key_present": agentops_key}
    })

@app.get("/control")
def control():
    r = router_manager.get()
    w = r.weights
    options = "".join([f"<option {'selected' if r.strategy==s else ''}>{s}</option>" for s in ['smart','cheapest','fastest','hybrid']])
    page = f"""
<html><head><title>AgentsIQ Control</title><style>{DARK_CSS}</style></head>
<body>
<div class='card'><h2>Control Panel</h2>
<form method='post' action='/control'>
<label>Strategy: <select name='strategy'>{options}</select></label>
<label>Cost weight: <input type='range' name='w_cost' min='0' max='1' step='0.01' value='{w['cost']}'></label>
<label>Latency weight: <input type='range' name='w_latency' min='0' max='1' step='0.01' value='{w['latency']}'></label>
<label>Quality weight: <input type='range' name='w_quality' min='0' max='1' step='0.01' value='{w['quality']}'></label>
<p><button type='submit'>Apply</button> <a href='/summary'>View Summary</a></p>
</form>
<small>Changes affect this running process instantly. Consider committing updated weights to config.yaml if you like them.</small>
</div>
</body></html>
"""
    return HTMLResponse(page)

@app.post("/control")
async def control_apply(request: Request):
    form = await request.form()
    strategy = form.get("strategy","smart")
    w_cost = float(form.get("w_cost",0.6)); w_latency = float(form.get("w_latency",0.25)); w_quality = float(form.get("w_quality",0.15))
    r = router_manager.get()
    r.set_strategy(strategy); r.set_weights(w_cost,w_latency,w_quality)
    return RedirectResponse(url="/control", status_code=303)

@app.get("/summary")
def summary(json_mode: int = 0):
    data = summary_by_agent()
    if json_mode: return JSONResponse(data)
    rows = []
    for agent, info in data.items():
        series = info.get("series", []); pts = series[-40:] or [0]
        w,h=160,40; mx=max(pts) if max(pts)>0 else 1.0; step=w/max(1,len(pts)-1)
        path = " ".join([f"{i*step:.1f},{h-(v/mx)*h:.1f}" for i,v in enumerate(pts)])
        mix = ", ".join(f"{m}×{c}" for m,c in info.get("models",{}).items()) or "-"
        p50=info.get("p50",0.0); p90=info.get("p90",0.0); p99=info.get("p99",0.0)
        scale = mx if mx>0 else 1.0
        def wb(v): return max(2, int((v/scale)*160))
        bars = f"""
<div class='bar'><span style='width:{wb(p50)}px'></span></div>
<div class='bar' style='margin-top:4px'><span style='width:{wb(p90)}px'></span></div>
<div class='bar' style='margin-top:4px'><span style='width:{wb(p99)}px'></span></div>
"""
        rows.append(f"""
<tr>
<td>{html.escape(agent)}</td>
<td>{info['calls']}</td>
<td>{info['avg_latency']:.3f}s</td>
<td>{info['avg_confidence']:.2f}</td>
<td class='mono'>{html.escape(mix)}</td>
<td><svg width='{w}' height='{h}' viewBox='0 0 {w} {h}'><polyline fill='none' stroke='#60a5fa' stroke-width='2' points='{path}'/></svg></td>
<td>{bars}<small>P50 • P90 • P99</small></td>
</tr>
""")
    page = f"""
<html><head><title>AgentsIQ Summary</title><style>{DARK_CSS}</style></head>
<body>
<div class='card'><h2>Per-agent Performance</h2>
<p><a href='/control'>Open Control Panel</a></p>
<table>
<thead><tr><th>Agent</th><th>Calls</th><th>Avg Latency</th><th>Avg Conf.</th><th>Model Mix</th><th>Latency Sparkline</th><th>Percentiles</th></tr></thead>
<tbody>{''.join(rows) if rows else "<tr><td colspan='7'>No data yet.</td></tr>"}</tbody>
</table>
</div>
</body></html>
"""
    return HTMLResponse(page)

@app.get("/decisions")
def decisions(n: int = 20):
    rows = latest_decisions(n)
    def cell(v):
        if v is None: return ""
        s = html.escape(str(v)); return s[:160] + ("…" if len(s)>160 else "")
    html_rows = []
    for r in rows[::-1]:
        chosen = r.get("chosen"); strategy = r.get("strategy"); agent = r.get("agent")
        est_cost = r.get("est_cost_chosen"); saved_next = r.get("est_cost_saved_vs_next_best"); saved_gpt4 = r.get("est_cost_saved_vs_gpt4o")
        tokens = r.get("tokens_total_est"); scored = r.get("scored", [])[:3]
        top_details = "<br>".join([f"{i+1}. {cell(s.get('model'))} (score={round(s.get('score',0),3)}, est_cost=${s.get('est_cost')})" for i,s in enumerate(scored)])
        html_rows.append(f"""
<tr>
<td>{cell(agent)}</td>
<td><span class='badge'>{cell(strategy)}</span></td>
<td><b class='mono'>{cell(chosen)}</b></td>
<td class='mono'>${cell(est_cost)}</td>
<td class='mono'>${cell(saved_next)}</td>
<td class='mono'>${cell(saved_gpt4)}</td>
<td class='mono'>{cell(tokens)}</td>
<td>{top_details}</td>
<td title='{cell(r.get('task'))}' class='mono'>{cell(r.get('task'))}</td>
</tr>
""")
    page = f"""
<html><head><title>AgentsIQ Decisions</title><style>{DARK_CSS}</style></head>
<body>
<div class='card'><h2>Routing Decisions (newest first)</h2>
<table>
<thead><tr><th>Agent</th><th>Strategy</th><th>Chosen</th><th>Est Cost</th><th>Saved vs Next</th><th>Saved vs GPT-4o</th><th>Est Tokens</th><th>Top Candidates</th><th>Task</th></tr></thead>
<tbody>{''.join(html_rows) if html_rows else "<tr><td colspan='9'>No decisions yet.</td></tr>"}</tbody>
</table>
</div>
</body></html>
"""
    return HTMLResponse(page)

@app.get("/decisions.json")
def decisions_json(n: int = 20):
    return JSONResponse(latest_decisions(n))

@app.get("/logs")
def logs():
    files=sorted(glob.glob("logs/*.jsonl"))
    if not files: return JSONResponse({"message":"No logs yet."})
    latest=files[-1]
    with open(latest,"r",encoding="utf-8") as f: return PlainTextResponse(f.read(),media_type="text/plain")

@app.get("/metrics")
def metrics():
    path="agentops_records/metrics.csv"
    if not os.path.exists(path): return JSONResponse({"message":"No metrics yet."})
    with open(path,"r",encoding="utf-8") as f: return PlainTextResponse(f.read(),media_type="text/plain")
