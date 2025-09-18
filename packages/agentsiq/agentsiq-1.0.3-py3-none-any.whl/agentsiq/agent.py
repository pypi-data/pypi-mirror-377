
import time, uuid
from .logger import explain_log
from .governance import check_permission
class Agent:
    def __init__(self, name, role, model: str = "", allowed_tools=None):
        self.name=name; self.role=role; self.model=model or ""; self.allowed_tools=allowed_tools or []
    def can_use_tool(self, tool_name): return check_permission(self, tool_name)
    def act(self, task, router, tools=None):
        start=time.time(); tools=tools or {}; used_tool=None; tool_output=None
        for t in self.allowed_tools:
            if f"use:{t}" in task.lower() and t in tools:
                used_tool=t; tool_output=tools[t](task); break
        model_to_use=None
        if tool_output is None:
            model_to_use=router.select_model(task, preferred=self.model, agent_name=self.name, role=self.role)
            response,conf=router.call_model(model_to_use, task)
        else:
            response,conf=tool_output,0.9
        entry={"agent":self.name,"role":self.role,"task":task,"response":response,               "model_used":model_to_use if tool_output is None else f"tool:{used_tool}",               "confidence":conf,"latency":time.time()-start,"id":str(uuid.uuid4())}
        explain_log(entry); return entry
