
import threading, time
from agentsiq.agent import Agent
from agentsiq.collab import Collab
from agentsiq.obs import init_agentops
from agentsiq.dashboard import app
import uvicorn

init_agentops()

def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

def run_demo_tasks():
    researcher=Agent("Researcher","Finds information","openai:gpt-4o-mini",["retrieval"])
    analyst=Agent("Analyst","Summarizes info","anthropic:claude-3-haiku",["summarize"])
    collab=Collab([researcher,analyst],tools={"retrieval":lambda _: "[retrieval] ok", "summarize":lambda _: "[summary] ok"})
    tasks=[
        "Summarize the key ideas of retrieval-augmented generation.",
        "Write a tiny Python function to reverse a list.",
        "Give a TL;DR of multi-agent coordination strategies.",
    ]
    for t in tasks:
        out=collab.run(t)
        print("\n--- DEMO OUTPUT ---\n", out["aggregated"][:200], "...")
        time.sleep(0.5)

if __name__ == "__main__":
    t=threading.Thread(target=start_server, daemon=True); t.start()
    time.sleep(1.0)
    print("Dashboard at http://127.0.0.1:8000  (Control: /control)")
    run_demo_tasks()
    # keep alive
    while True: time.sleep(5)
