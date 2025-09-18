# AgentsIQ Architecture Diagram

## 🏗️ System Architecture Overview

```mermaid
graph TB
    subgraph "User Input"
        A[Task Request] --> B[Task Analysis]
    end
    
    subgraph "Intelligent Router"
        B --> C[Traits Detection]
        C --> D[Token Estimation]
        D --> E[Model Scoring]
        E --> F[Multi-Objective Optimization]
        F --> G[Model Selection]
    end
    
    subgraph "Model Providers"
        H[OpenAI<br/>GPT-4o, GPT-4o-mini]
        I[Anthropic<br/>Claude-3-Haiku]
        J[Google<br/>Gemini-Pro]
        K[Ollama<br/>Llama3.1, Qwen2.5]
        L[Grok<br/>Grok-2, Grok-2-Vision]
    end
    
    subgraph "Scoring Engine"
        M[Cost Analysis<br/>Weight: 60%]
        N[Latency Analysis<br/>Weight: 25%]
        O[Quality Analysis<br/>Weight: 15%]
        P[Task-Specific Boosts]
    end
    
    subgraph "Output & Analytics"
        Q[Response Generation]
        R[Quality Metrics]
        S[Decision Logging]
        T[AgentOps Analytics]
    end
    
    G --> H
    G --> I
    G --> J
    G --> K
    G --> L
    
    E --> M
    E --> N
    E --> O
    E --> P
    
    H --> Q
    I --> Q
    J --> Q
    K --> Q
    L --> Q
    
    Q --> R
    Q --> S
    Q --> T
    
    style A fill:#e1f5fe
    style G fill:#c8e6c9
    style Q fill:#fff3e0
    style T fill:#f3e5f5
```

## 🔄 Decision Flow Diagram

```mermaid
flowchart TD
    A["Task: Write Python function"] --> B[Analyze Task]
    B --> C{Task Traits}
    C -->|"is_code: true"| D[Code Task Detected]
    C -->|"is_summary: false"| E[Not Summary Task]
    C -->|"has_math: false"| F[No Math Detected]
    
    D --> G["Estimate Tokens: ~25"]
    E --> G
    F --> G
    
    G --> H[Score All Models]
    H --> I[Apply Quality Boosts]
    I --> J["OpenAI +0.05 for code"]
    J --> K[Calculate Weighted Scores]
    
    K --> L["Cost: 60% weight"]
    K --> M["Latency: 25% weight"]
    K --> N["Quality: 15% weight"]
    
    L --> O[Select Best Model]
    M --> O
    N --> O
    
    O --> P["ollama:qwen2.5:7b<br/>Score: 0.0625"]
    P --> Q[Execute Task]
    Q --> R["Return Response + Quality"]
    
    style A fill:#e3f2fd
    style P fill:#c8e6c9
    style R fill:#fff3e0
```

## 🏢 Component Architecture

```mermaid
graph LR
    subgraph "AgentsIQ Core"
        A[ModelRouter]
        B[Agent]
        C[Collab]
        D[RouterManager]
    end
    
    subgraph "Configuration"
        E["config.yaml"]
        F["Environment Variables"]
        G["Dynamic Weights"]
    end
    
    subgraph "Analytics"
        H[DecisionStore]
        I[AgentOps]
        J[Dashboard]
        K[Benchmark]
    end
    
    subgraph "External APIs"
        L["OpenAI API"]
        M["Anthropic API"]
        N["Google API"]
        O["Ollama API"]
        P["Grok API"]
    end
    
    A --> E
    A --> F
    A --> G
    A --> H
    A --> I
    
    B --> A
    C --> A
    D --> A
    
    A --> L
    A --> M
    A --> N
    A --> O
    A --> P
    
    H --> J
    I --> J
    K --> J
    
    style A fill:#ffeb3b
    style J fill:#4caf50
    style L fill:#2196f3
    style M fill:#ff9800
    style N fill:#4caf50
    style O fill:#9c27b0
    style P fill:#f44336
```

## 📊 Model Selection Matrix

| Model | Cost/1K | Latency | Quality | Best For |
|-------|---------|---------|---------|----------|
| **Ollama Qwen2.5:7b** | $0.00 | 0.25s | 0.80 | Fast, local inference |
| **Ollama Llama3.1:8b** | $0.00 | 0.30s | 0.82 | Balanced local model |
| **Google Gemini-Pro** | $0.125 | 0.60s | 0.78 | General purpose |
| **Anthropic Claude-3-Haiku** | $0.25 | 0.70s | 0.80 | Summarization |
| **OpenAI GPT-4o-mini** | $0.15 | 0.80s | 0.75 | Code generation |
| **Grok Grok-2** | $0.20 | 0.90s | 0.90 | Creative writing |
| **OpenAI GPT-4o** | $5.00 | 1.00s | 0.95 | Complex reasoning |

## 🎯 Optimization Strategy

The intelligent selection uses a **weighted objective function**:

```
Score = (Cost_Weight × Cost_Normalized) + 
        (Latency_Weight × Latency_Normalized) + 
        (Quality_Weight × Quality_Normalized)

Where:
- Cost_Weight = 0.60 (60%)
- Latency_Weight = 0.25 (25%)  
- Quality_Weight = 0.15 (15%)
```

**Task-Specific Quality Boosts:**
- OpenAI models: +0.05 for code tasks
- Anthropic models: +0.05 for summarization tasks
- Google models: +0.02 for general tasks (non-code)

This ensures optimal model selection based on task requirements while maintaining cost efficiency.
