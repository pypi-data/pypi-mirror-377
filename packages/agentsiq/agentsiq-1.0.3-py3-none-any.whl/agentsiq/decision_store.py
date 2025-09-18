
import os, json, time
DECISION_DIR = os.path.join(os.getcwd(), "logs"); os.makedirs(DECISION_DIR, exist_ok=True)
DECISIONS_PATH = os.path.join(DECISION_DIR, "decisions.json")
def _load():
    if not os.path.exists(DECISIONS_PATH): return []
    try:
        with open(DECISIONS_PATH, "r", encoding="utf-8") as f: return json.load(f) or []
    except Exception: return []
def _save(data):
    with open(DECISIONS_PATH, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)
def record_decision(entry: dict):
    data = _load(); entry["ts"] = time.time(); data.append(entry); _save(data)
def latest_decisions(n=20): return _load()[-n:]
def all_decisions(): return _load()
