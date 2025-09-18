
import os, yaml
DEFAULT = {
  "settings": {
    "router": {
      "strategy": "smart",
      "weights": {"cost": 0.60, "latency": 0.25, "quality": 0.15},
      "profiles": {
        "openai:gpt-4o-mini": {"cost": 0.15, "latency": 0.8, "quality": 0.75},
        "openai:gpt-4o": {"cost": 5.00, "latency": 1.0, "quality": 0.95},
        "anthropic:claude-3-haiku": {"cost": 0.25, "latency": 0.7, "quality": 0.80},
        "google:gemini-pro": {"cost": 0.125, "latency": 0.6, "quality": 0.78},
        "ollama:llama3.1:8b": {"cost": 0.0, "latency": 0.3, "quality": 0.82},
        "ollama:llama3.1:70b": {"cost": 0.0, "latency": 0.5, "quality": 0.88},
        "ollama:qwen2.5:7b": {"cost": 0.0, "latency": 0.25, "quality": 0.80},
        "ollama:qwen2.5:72b": {"cost": 0.0, "latency": 0.4, "quality": 0.85},
        "grok:grok-2": {"cost": 0.20, "latency": 0.9, "quality": 0.90},
        "grok:grok-2-vision": {"cost": 0.25, "latency": 1.1, "quality": 0.92}
      }
    }
  }
}
def load_config(path: str = "config.yaml"):
    if not os.path.exists(path): return DEFAULT
    try:
        with open(path, "r", encoding="utf-8") as f: data = yaml.safe_load(f) or {}
        res = DEFAULT.copy(); res.update(data)
        d_router = DEFAULT["settings"]["router"]
        s_router = (data.get("settings") or {}).get("router") or {}
        merged = {
            "strategy": s_router.get("strategy", d_router["strategy"]),
            "weights": s_router.get("weights", d_router["weights"]),
            "profiles": s_router.get("profiles", d_router["profiles"]),
        }
        if "settings" not in res: res["settings"] = {}
        res["settings"]["router"] = merged
        return res
    except Exception:
        return DEFAULT
