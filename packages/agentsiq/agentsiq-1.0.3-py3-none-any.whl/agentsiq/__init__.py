"""
AgentsIQ - Intelligent Multi-Model Router for LLM Selection

AgentsIQ automatically chooses the most cost-efficient, fastest, and highest-quality 
model for each task, supporting 10+ models including OpenAI, Anthropic, Google, 
Ollama (local), and Grok. Features comprehensive benchmarking with beautiful 
visualizations and real-time performance analytics.

Key Features:
- 🧠 Intelligent Selection: Multi-objective optimization
- 💰 Cost Optimization: Save up to 90% on API costs
- 🏠 Local Models: Full Ollama support for privacy
- 📊 Analytics: Real-time performance monitoring
- 🎯 Task-Aware: Different models for different tasks
- 🔧 Configurable: Adjust weights and strategies

Quick Start:
    from agentsiq.router import ModelRouter
    
    router = ModelRouter()
    model = router.select_model("Write a Python function")
    response, quality = router.call_model(model, "Write a Python function")
    print(f"Selected: {model}, Quality: {quality}")

Multi-Agent Collaboration:
    from agentsiq.agent import Agent
    from agentsiq.collab import Collab
    
    researcher = Agent("Researcher", "Finds information", "openai:gpt-4o-mini", ["retrieval"])
    analyst = Agent("Analyst", "Summarizes info", "anthropic:claude-3-haiku", ["summarize"])
    collab = Collab([researcher, analyst], {"retrieval": lambda _: "[retrieval] ok"})
    
    result = collab.run("Analyze the latest trends in AI")
"""

__version__ = "1.0.0"
__author__ = "AgentsIQ Team"
__email__ = "team@agentsiq.ai"
__license__ = "MIT"

# Core imports
from .router import ModelRouter
from .agent import Agent
from .collab import Collab
from .router_manager import router_manager
from .config_loader import load_config

# Optional imports (may fail if dependencies not installed)
try:
    from .dashboard import app
except ImportError:
    app = None

try:
    from .agentops import init_agentops
except ImportError:
    init_agentops = None

# Public API
__all__ = [
    "ModelRouter",
    "Agent", 
    "Collab",
    "router_manager",
    "load_config",
    "app",
    "init_agentops",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]