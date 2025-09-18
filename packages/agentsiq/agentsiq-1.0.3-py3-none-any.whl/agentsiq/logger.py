
import os, json, time
LOG_DIR=os.path.join(os.getcwd(),"logs"); os.makedirs(LOG_DIR,exist_ok=True)
LOG_FILE=os.path.join(LOG_DIR,f"explain_{int(time.time())}.jsonl")
def explain_log(entry:dict):
    with open(LOG_FILE,"a",encoding="utf-8") as f: f.write(json.dumps(entry,ensure_ascii=False)+"\n")
