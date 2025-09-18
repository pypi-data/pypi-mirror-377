# AgentsIQ Architecture Documentation

## 🏗️ System Overview

AgentsIQ is an intelligent multi-model router that automatically selects the most cost-efficient, fastest, and highest-quality model for each task. The system uses sophisticated multi-objective optimization to make routing decisions in real-time.

## 🧠 Intelligent Model Selection Process

### Core Selection Algorithm

The `router.select_model()` method uses a **multi-objective optimization** approach to choose the best model for each task:

```python
from agentsiq.router import ModelRouter

router = ModelRouter()
model = router.select_model("Write a Python function to sort a list")
response, quality = router.call_model(model, "Write a Python function to sort a list")
print(f"Selected: {model}, Quality: {quality}")
```

### Step-by-Step Selection Process

#### 1. **Task Analysis**
```python
# Your example: "Write a Python function to sort a list"
tokens = _estimate_tokens(task)  # Estimates ~25 tokens
traits = _traits(task)           # Analyzes task characteristics
```

**Task Traits Detection:**
```python
def _traits(task: str):
    t = task.lower()
    return {
        "is_code": any(k in t for k in ("code","python","algorithm","implement")),
        "is_summary": any(k in t for k in ("summarize","summary","tl;dr","short")),
        "has_math": bool(re.search(r"\b\d+\s*[\+\-\*/^]", t)),
    }
```

For the example: `{"is_code": True, "is_summary": False, "has_math": False}`

#### 2. **Strategy Selection**

The router supports 4 strategies:

- **`cheapest`**: Always picks the lowest-cost model
- **`fastest`**: Always picks the lowest-latency model  
- **`hybrid`**: Rule-based selection (code → GPT-4o, summary → Claude, else → GPT-4o-mini)
- **`smart`** (default): **Multi-objective optimization**

#### 3. **Smart Strategy - Multi-Objective Scoring**

For the `smart` strategy, each model gets scored using this formula:

```python
def _score(self, model, tokens_in, traits):
    # 1. Get model profile (cost, latency, quality)
    p = self.profiles.get(model, {"cost":1.0,"latency":1.0,"quality":0.7})
    
    # 2. Estimate token usage
    tokens_out = min(1500, int(tokens_in*2.0))
    tokens_total = tokens_in + tokens_out
    est_cost = p["cost"] * (tokens_total/1000.0)
    
    # 3. Adjust quality based on task traits
    quality = p.get("quality",0.75)
    if traits["is_code"] and "openai" in model: quality += 0.05      # OpenAI excels at code
    if traits["is_summary"] and "anthropic" in model: quality += 0.05  # Claude excels at summaries
    if "gemini" in model and not traits["is_code"]: quality += 0.02    # Gemini good for general tasks
    quality = max(0.6, min(0.98, quality))
    
    # 4. Normalize metrics relative to all models
    costs = [v["cost"] for v in self.profiles.values()]
    lats = [v["latency"] for v in self.profiles.values()]
    c_med = stats.median(costs)
    l_med = stats.median(lats)
    
    cost_norm = p["cost"]/max(1e-6, c_med)
    lat_norm = p["latency"]/max(1e-6, l_med)
    qual_norm = 1.0 - quality  # Lower is better
    
    # 5. Calculate weighted objective function
    objective = (self.weights["cost"]*cost_norm + 
                self.weights["latency"]*lat_norm + 
                self.weights["quality"]*qual_norm)
    
    return objective, why
```

#### 4. **Weighted Decision Making**

The default weights are: `{"cost": 0.60, "latency": 0.25, "quality": 0.15}`

This means:
- **60%** weight on cost optimization
- **25%** weight on speed
- **15%** weight on quality

#### 5. **Model Selection**

```python
# Score all models
scored = []
for model in candidates:
    score, why = self._score(model, tokens, traits)
    scored.append((model, score, why))

# Sort by score (lower is better)
scored.sort(key=lambda x: x[1])
chosen = scored[0][0]  # Pick the best scoring model
```

### Example: Code Task Selection

For `"Write a Python function to sort a list"`:

1. **Traits**: `{"is_code": True, "is_summary": False, "has_math": False}`
2. **Tokens**: ~25 tokens estimated
3. **Quality Boost**: OpenAI models get +0.05 quality boost for code tasks
4. **Scoring**: Each model scored on cost/latency/quality with 60/25/15 weights
5. **Selection**: Model with lowest objective score wins

**Example Result:**
```python
# Might select "ollama:qwen2.5:7b" because:
# - Cost: $0.00 (excellent)
# - Latency: 0.25s (very fast)  
# - Quality: 0.80 + 0.05 = 0.85 (good for code)
# - Total score: 0.60*0 + 0.25*0.25 + 0.15*0.15 = 0.0625 (lowest)
```

## 🏗️ System Components

### Core Components

1. **ModelRouter**: Central routing engine with intelligent selection
2. **Agent**: Individual AI agents with specific roles and capabilities
3. **Collab**: Multi-agent collaboration framework
4. **RouterManager**: Singleton pattern for shared router instances
5. **DecisionStore**: Records and tracks routing decisions
6. **Dashboard**: Real-time monitoring and control interface

### Model Providers

- **OpenAI**: GPT-4o, GPT-4o-mini
- **Anthropic**: Claude-3-Haiku
- **Google**: Gemini-Pro
- **Ollama**: Llama3.1 (8B/70B), Qwen2.5 (7B/72B)
- **Grok**: Grok-2, Grok-2-Vision

### Configuration System

- **config.yaml**: Model profiles, weights, and routing strategies
- **Environment Variables**: API keys and service configurations
- **Dynamic Reloading**: Real-time configuration updates

## 🔄 Data Flow

1. **Task Input** → Task analysis and trait detection
2. **Model Scoring** → Multi-objective optimization across all models
3. **Selection** → Best model chosen based on weighted scores
4. **Execution** → Model called with task
5. **Response** → Result returned with quality metrics
6. **Logging** → Decision recorded for analytics

## 🎯 Key Benefits

1. **🎯 Task-Aware**: Different models excel at different tasks
2. **💰 Cost-Optimized**: Prioritizes cheaper models when quality is sufficient
3. **⚡ Speed-Conscious**: Considers response time in decision
4. **📊 Data-Driven**: Uses actual model profiles and performance data
5. **🔧 Configurable**: Weights can be adjusted via config or control panel

## 🔧 Configuration

### Model Profiles
```yaml
profiles:
  openai:gpt-4o-mini: { cost: 0.15,  latency: 0.8, quality: 0.75 }
  openai:gpt-4o:      { cost: 5.00,  latency: 1.0, quality: 0.95 }
  anthropic:claude-3-haiku: { cost: 0.25, latency: 0.7, quality: 0.80 }
  google:gemini-pro:  { cost: 0.125, latency: 0.6, quality: 0.78 }
  ollama:llama3.1:8b: { cost: 0.0,   latency: 0.3, quality: 0.82 }
  ollama:llama3.1:70b: { cost: 0.0,  latency: 0.5, quality: 0.88 }
  ollama:qwen2.5:7b:  { cost: 0.0,   latency: 0.25, quality: 0.80 }
  ollama:qwen2.5:72b: { cost: 0.0,   latency: 0.4, quality: 0.85 }
  grok:grok-2:        { cost: 0.20,  latency: 0.9, quality: 0.90 }
  grok:grok-2-vision: { cost: 0.25,  latency: 1.1, quality: 0.92 }
```

### Routing Weights
```yaml
weights: { cost: 0.60, latency: 0.25, quality: 0.15 }
```

### Strategies
- `smart`: Multi-objective optimization (default)
- `cheapest`: Always lowest cost
- `fastest`: Always lowest latency
- `hybrid`: Rule-based selection

## 📊 Analytics & Monitoring

- **AgentOps Integration**: Real-time performance tracking
- **Decision Logging**: Complete rationale for each selection
- **Cost Analysis**: Savings vs baseline models
- **Performance Metrics**: Response times, quality scores, usage patterns
- **Dashboard**: Live monitoring and control interface

## 🚀 Future Enhancements

- **Dynamic Weight Adjustment**: ML-based weight optimization
- **Model Performance Learning**: Adaptive quality scoring
- **Task-Specific Profiles**: Specialized model configurations
- **Load Balancing**: Multi-instance routing
- **Custom Metrics**: User-defined optimization criteria
