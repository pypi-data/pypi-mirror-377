from typing import List,Dict,Callable
from .agent import Agent
from .router_manager import router_manager
from .agentops_metrics import record as record_metrics

class Collab:
    def __init__(self,agents:List[Agent],tools:Dict[str,Callable]=None):
        self.agents=agents; self.tools=tools or {}
    def run(self,task:str,mode:str="sequential"):
        router = router_manager.get()
        results=[]
        for agent in self.agents:
            entry=agent.act(task,router=router,tools=self.tools)
            record_metrics(entry,note=f"mode={mode}")
            results.append(entry)
        aggregated="\n---\n".join(r["response"] for r in results)
        return {"aggregated":aggregated,"results":results}
