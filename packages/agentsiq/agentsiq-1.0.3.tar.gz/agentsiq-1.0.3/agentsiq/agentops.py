import os, csv, json, time
REC_DIR = os.path.join(os.getcwd(), 'agentops_records')
os.makedirs(REC_DIR, exist_ok=True)
CSV_PATH = os.path.join(REC_DIR, 'metrics.csv')
if not os.path.exists(CSV_PATH):
    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['ts','agent','task_id','model','confidence','latency','note'])

def record_metrics(entry: dict, note: str = ''):
    ts = time.time()
    with open(CSV_PATH, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow([ts, entry.get('agent'), entry.get('id'), entry.get('model_used'), entry.get('confidence'), entry.get('latency'), note])
    # mirror JSON
    with open(os.path.join(REC_DIR, f"run_{entry.get('id')}.json"), 'w', encoding='utf-8') as jf:
        json.dump(entry, jf, ensure_ascii=False, indent=2)
