
import os, re, statistics as stats, requests, json
from dotenv import load_dotenv
from .decision_store import record_decision
from .config_loader import load_config
load_dotenv()
_openai_client=None; _anthropic_client=None; _gemini_ready=None; _grok_client=None
def _get_openai_client():
    global _openai_client
    if _openai_client is None:
        try:
            from openai import OpenAI
            _openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except Exception: _openai_client = False
    return _openai_client
def _get_anthropic_client():
    global _anthropic_client
    if _anthropic_client is None:
        try:
            import anthropic
            _anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        except Exception: _anthropic_client = False
    return _anthropic_client
def _ensure_gemini():
    global _gemini_ready
    if _gemini_ready is None:
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY")); _gemini_ready = True
        except Exception: _gemini_ready = False
    return _gemini_ready

def _get_grok_client():
    global _grok_client
    if _grok_client is None:
        try:
            api_key = os.getenv("GROK_API_KEY")
            if api_key:
                _grok_client = {"api_key": api_key, "base_url": "https://api.x.ai/v1"}
            else:
                _grok_client = False
        except Exception: _grok_client = False
    return _grok_client

def _call_ollama(model_name: str, prompt: str):
    """Call Ollama API for local models"""
    try:
        model = model_name.split(":", 1)[1]  # Remove 'ollama:' prefix
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2, "num_predict": 500}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", ""), 0.8
        else:
            return f"[OLLAMA ERROR {response.status_code}] {prompt[:180]}", 0.6
    except Exception as e:
        return f"[OLLAMA MOCK {model_name}] {prompt[:180]}", 0.7

def _call_grok(model_name: str, prompt: str):
    """Call Grok API"""
    client = _get_grok_client()
    if not client:
        return f"[GROK MOCK {model_name}] {prompt[:180]}", 0.7
    
    try:
        model = model_name.split(":", 1)[1]  # Remove 'grok:' prefix
        headers = {
            "Authorization": f"Bearer {client['api_key']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 500
        }
        
        response = requests.post(
            f"{client['base_url']}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            return content, 0.85
        else:
            return f"[GROK ERROR {response.status_code}] {prompt[:180]}", 0.6
    except Exception as e:
        return f"[GROK MOCK {model_name}] {prompt[:180]}", 0.7
def _estimate_tokens(text:str)->int: return max(16, int(len(text)/4))
def _traits(task:str):
    t = task.lower()
    return {
        "is_code": any(k in t for k in ("code","python","algorithm","implement")),
        "is_summary": any(k in t for k in ("summarize","summary","tl;dr","short")),
        "has_math": bool(re.search(r"\b\d+\s*[\+\-\*/^]", t)),
    }
class ModelRouter:
    def __init__(self, strategy: str = None, profiles=None, weights=None):
        cfg = load_config(); rcfg = cfg.get("settings",{}).get("router",{})
        self.strategy = strategy or rcfg.get("strategy","smart")
        self.profiles = profiles or rcfg.get("profiles",{})
        self.weights = weights or rcfg.get("weights",{"cost":0.60,"latency":0.25,"quality":0.15})
    def reload(self):
        cfg = load_config(); rcfg = cfg.get("settings",{}).get("router",{})
        self.strategy = rcfg.get("strategy", self.strategy)
        self.profiles = rcfg.get("profiles", self.profiles)
        self.weights  = rcfg.get("weights",  self.weights)
        return {"strategy": self.strategy, "weights": self.weights, "profiles": list(self.profiles.keys())}
    def set_strategy(self, s:str):
        self.strategy = s; return self.strategy
    def set_weights(self, cost:float=None, latency:float=None, quality:float=None):
        w = self.weights.copy()
        if cost is not None: w["cost"]=float(cost)
        if latency is not None: w["latency"]=float(latency)
        if quality is not None: w["quality"]=float(quality)
        self.weights = w; return self.weights
    def _score(self, model, tokens_in, traits):
        p = self.profiles.get(model, {"cost":1.0,"latency":1.0,"quality":0.7})
        tokens_out = min(1500, int(tokens_in*2.0)); tokens_total = tokens_in + tokens_out
        est_cost = p["cost"] * (tokens_total/1000.0)
        quality = p.get("quality",0.75)
        if traits["is_code"] and "openai" in model: quality += 0.05
        if traits["is_summary"] and "anthropic" in model: quality += 0.05
        if "gemini" in model and not traits["is_code"]: quality += 0.02
        quality = max(0.6, min(0.98, quality))
        costs=[v["cost"] for v in self.profiles.values()]; lats=[v["latency"] for v in self.profiles.values()]
        c_med=stats.median(costs); l_med=stats.median(lats)
        cost_norm = p["cost"]/max(1e-6, c_med); lat_norm  = p["latency"]/max(1e-6, l_med); qual_norm = 1.0 - quality
        objective = (self.weights["cost"]*cost_norm + self.weights["latency"]*lat_norm + self.weights["quality"]*qual_norm)
        why = {"profile": p, "traits": traits, "tokens_in": tokens_in, "tokens_out_est": tokens_out, "tokens_total_est": tokens_total,
               "est_cost": round(est_cost, 6), "norms": {"cost_norm": cost_norm, "lat_norm": lat_norm, "qual_norm": qual_norm},
               "weights": self.weights, "objective": objective}
        return objective, why
    def select_model(self, task, preferred:str="", agent_name:str="", role:str=""):
        tokens = _estimate_tokens(task); traits=_traits(task); candidates = list(self.profiles.keys())
        if self.strategy == "cheapest": chosen = min(candidates, key=lambda m: self.profiles[m]["cost"])
        elif self.strategy == "fastest": chosen = min(candidates, key=lambda m: self.profiles[m]["latency"])
        elif self.strategy == "hybrid":
            if traits["is_code"]: chosen = "openai:gpt-4o"
            elif traits["is_summary"]: chosen = "anthropic:claude-3-haiku"
            else: chosen = "openai:gpt-4o-mini"
        else:
            scored = []
            for m in candidates:
                s, why = self._score(m, tokens, traits); scored.append((m, s, why))
            scored.sort(key=lambda x: x[1]); chosen = scored[0][0]
        if preferred and preferred in self.profiles and self.strategy == "smart":
            def sc(m): return self._score(m, tokens, traits)[0]
            if sc(preferred) <= sc(chosen) * 1.08: chosen = preferred
        record = {"agent":agent_name,"role":role,"task":task[:300],"strategy":self.strategy,"traits":traits,"preferred":preferred,"chosen":chosen}
        if self.strategy == "smart":
            scored_rows = [{"model":m,"score":s,**why} for m,s,why in scored]; scored_rows.sort(key=lambda x: x["score"])
            record["scored"] = scored_rows; chosen_row = scored_rows[0]; next_best_row = scored_rows[1] if len(scored_rows)>1 else chosen_row
            baseline = "openai:gpt-4o"; baseline_row = next((r for r in scored_rows if r["model"]==baseline), None)
            record["est_cost_chosen"] = chosen_row["est_cost"]; record["tokens_total_est"] = chosen_row["tokens_total_est"]
            record["est_cost_next_best"] = next_best_row["est_cost"]
            record["est_cost_saved_vs_next_best"] = round(next_best_row["est_cost"] - chosen_row["est_cost"],6)
            record["est_cost_baseline_gpt4o"] = baseline_row["est_cost"] if baseline_row else None
            if baseline_row: record["est_cost_saved_vs_gpt4o"] = round(baseline_row["est_cost"] - chosen_row["est_cost"],6)
        record_decision(record); return chosen
    def call_model(self, model_name: str, prompt: str):
        if model_name.startswith("openai:"):
            client=_get_openai_client(); model=model_name.split(":",1)[1]
            if client:
                try:
                    resp=client.chat.completions.create(model=model,messages=[{"role":"user","content":prompt}],temperature=0.2,max_tokens=500)
                    return resp.choices[0].message.content, 0.85
                except Exception: pass
            return f"[OPENAI MOCK {model}] "+prompt[:180], 0.75
        if model_name.startswith("anthropic:"):
            client=_get_anthropic_client(); model=model_name.split(":",1)[1]
            if client:
                try:
                    resp=client.messages.create(model=model,max_tokens=500,messages=[{"role":"user","content":prompt}])
                    try: txt="".join([b.text for b in resp.content])
                    except Exception: txt=str(resp)
                    return txt, 0.83
                except Exception: pass
            return f"[ANTHROPIC MOCK {model}] "+prompt[:180], 0.74
        if model_name.startswith("google:"):
            ok=_ensure_gemini(); model=model_name.split(":",1)[1]
            if ok:
                try:
                    import google.generativeai as genai
                    gm=genai.GenerativeModel(model)
                    resp=gm.generate_content(prompt)
                    txt=getattr(resp,"text",None) or (resp.candidates[0].content.parts[0].text if getattr(resp,"candidates",None) else "")
                    return txt, 0.8
                except Exception: pass
            return f"[GEMINI MOCK {model}] "+prompt[:180], 0.73
        if model_name.startswith("ollama:"):
            return _call_ollama(model_name, prompt)
        if model_name.startswith("grok:"):
            return _call_grok(model_name, prompt)
        return f"[MOCK {model_name}] "+prompt[:180], 0.7
