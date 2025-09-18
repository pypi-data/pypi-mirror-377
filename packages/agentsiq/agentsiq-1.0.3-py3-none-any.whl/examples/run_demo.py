
from agentsiq.agent import Agent
from agentsiq.collab import Collab
from agentsiq.obs import init_agentops
init_agentops()
def retrieval(task: str) -> str: return "[retrieval] located 3 relevant sources."
def summarize(task: str) -> str: return "[summary] This is a short summary of the topic.]"
def main():
    researcher=Agent("Researcher","Finds information","openai:gpt-4o-mini",["retrieval"])
    analyst=Agent("Analyst","Summarizes info","anthropic:claude-3-haiku",["summarize"])
    collab=Collab([researcher,analyst],{"retrieval":retrieval,"summarize":summarize})
    task="Summarize recent advances in multi-agent AI frameworks and give a tiny python code example."
    out=collab.run(task)
    print("\nAGGREGATED OUTPUT\n==================\n", out["aggregated"])
    print("\nStart: python -m examples.serve_and_demo  -> single process with shared router + UI control")
if __name__=="__main__": main()
