Here is your complete README. Copy this entirely and replace your current README.md.

```markdown
# 🛡️ GUARDIAN — Autonomous Financial Decision System

> Built for freelancers who lose money not from lack of income, but from lack of visibility.

GUARDIAN is a deep multi-agent AI system that monitors your financial activity, reasons about patterns, challenges its own conclusions, and delivers decisions — before the money is gone.

**Not a tracker. Not a dashboard. A reasoning system.**

---

## 🎬 Demo



![Dashboard](assets/dashboard.png)



> Watch the system reject its own first analysis, retrieve more evidence, and approve a stronger conclusion — autonomously.

---

## 🧠 How It Works

```

Transactions (CSV / JSON / Manual)
↓
Monitor Agent — detects anomalies
↓
Analyst Agent — builds hypothesis using real tool calculations
↓
Critic Agent — rejects if confidence < 0.80
↓
Analyst Agent — retrieves deeper evidence, re-analyses
↓
Critic Agent — approves at 0.90 confidence
↓
Decision Agent — ranked actions + projected savings
↓
Streamlit Dashboard + Telegram Alert 📱

```

This loop — reject → improve → approve — is what makes GUARDIAN a deep agent system, not a script.

---

## 🚀 Features

- **Multi-agent reasoning loop** — Monitor → Analyst → Critic → Decision
- **Self-correcting AI** — rejects weak conclusions before acting
- **Deterministic tool calculations** — savings calculated by code, not guessed by LLM
- **Historical memory** — compares current patterns against past behaviour
- **Three input methods** — upload CSV, upload JSON, or enter manually
- **Live reasoning trace** — watch every agent step stream in real time
- **Confidence evolution** — visual indicator from rejection to approval
- **Telegram alerts** — autonomous notification when high-urgency action detected
- **Demo mode** — safe public usage without exposing API keys

---

## 🤖 Agent Architecture

| Agent | Role |
|---|---|
| **Monitor** | Scans transactions, flags anomalies, routes to analyst |
| **Analyst** | Calls tool functions, builds hypothesis, assigns confidence score |
| **Critic** | Evaluates against evidence rubric, approves or rejects |
| **Decision** | Generates ranked actions using verified tool output only |

The Orchestrator is LangGraph itself — managing state transitions and routing between agents.

---

## 🔧 Tool Functions

These run as deterministic Python functions — not LLM guesses.

**`analyze_subscriptions(transactions)`**
Identifies overlapping subscriptions, flags tools with under 5 usage days, calculates monthly and six-month waste.

**`forecast_cashflow(transactions)`**
Computes net position, daily burn rate, and days until cash risk window based on income and expense patterns.

---

## 📊 Demo Result

```

Input: 7 freelance transactions including 3 overlapping project management subscriptions

Analyst iteration 1: Confidence 0.80 → Critic REJECTED
Reason: No specific cost breakdown referenced

Analyst iteration 2: Confidence 0.90 → Critic APPROVED  
Reason: Specific tools identified, waste calculated, cashflow risk quantified

Decision: Cancel Notion Pro + ClickUp
Savings: ₹11,640 over 6 months
Risk window: 18 days

```

---

## 🛡️ Demo Mode

GUARDIAN supports a built-in demo mode for safe public sharing.

- Public deployment uses demo data — no real API calls made
- Full AI reasoning works locally with your own API key
- Input validation prevents malformed data from reaching agents
- No financial data is stored beyond your local session

---

## ▶️ Run Locally

```bash
# Clone
git clone https://github.com/Ganeshreddy80/guardian.git
cd guardian

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Add your API key
cp .env.example .env
# Edit .env and add your OpenRouter API key

# Run
streamlit run dashboard.py
```

---

## ⚙️ Environment Variables

Create a `.env` file with the following:

```
OPENAI_API_KEY=your_openrouter_key_here
OPENAI_API_BASE=https://openrouter.ai/api/v1
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key_here
LANGCHAIN_PROJECT=guardian
```

---

## 📁 Project Structure

```

guardian/
├── guardian\_core.py        # LangGraph agents + tool functions
├── dashboard.py            # Streamlit UI with upload support
├── input\_handler.py        # CSV / JSON / manual input parsing
├── memory\_store.py         # Historical context and RAG layer
├── main.py                 # FastAPI backend
├── requirements.txt
├── .env.example
├── sample\_transactions.csv
└── assets/
    ├── dashboard.png
    └── telegram.png

```

---

## 📦 Requirements

```

langgraph
langchain
langchain-openai
streamlit
fastapi
uvicorn
pydantic
pandas
python-dotenv
langsmith

```

---

## 🏗️ Tech Stack

| Layer | Tool |
|---|---|
| Agent Orchestration | LangGraph |
| LLM | GPT-4o-mini via OpenRouter |
| Backend API | FastAPI |
| Dashboard | Streamlit |
| Alerts | Telegram Bot API |
| Observability | LangSmith |
| Memory | JSON with historical retrieval |

---

## 💬 What Makes This Different

Most financial tools answer: *"How much did you spend?"*

GUARDIAN answers: *"What should you do about it — and here is the verified reasoning behind that recommendation."*

The Critic Agent is the key differentiator. No recommendation reaches the user until it has been challenged and approved against an evidence rubric. A system that knows when its own reasoning is insufficient — and corrects it before acting — is not a tracking tool. It is a decision system.

---

## 🔮 Roadmap

- [ ] Plaid / Razorpay API integration for real bank data
- [ ] Multi-user support with authentication
- [ ] Weekly scheduled analysis with persistent database
- [ ] Mobile-optimised interface
- [ ] Expanded tool library (tax estimation, invoice tracking)

---

## 👨‍💻 Built By

**Ganesh Kumar Reddy** — Student transitioning to freelancing, building AI systems that solve real problems.

Built for: **AI + Robotics Hackathon 2026**

---

## 📄 License

MIT License — use freely, build on top, give credit.
```

---

## Now Do These Four Things

```bash
# 1. Create .env.example (safe to commit — no real keys)
echo "OPENAI_API_KEY=your_openrouter_key_here" > .env.example
echo "OPENAI_API_BASE=https://openrouter.ai/api/v1" >> .env.example
echo "LANGCHAIN_TRACING_V2=true" >> .env.example
echo "LANGCHAIN_API_KEY=your_langsmith_key_here" >> .env.example

# 2. Create requirements.txt
pip freeze > requirements.txt

# 3. Make sure .env is in .gitignore
echo ".env" >> .gitignore
echo "guardian_memory.json" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore

# 4. Add screenshots to assets folder
mkdir assets
# Take a screenshot of your dashboard and save as assets/dashboard.png
# Take a screenshot of your Telegram alert and save as assets/telegram.png

# 5. Commit everything
git add .
git commit -m "Production ready: multi-input system, memory layer, reasoning trace UI, Telegram alerts, clean README"
git push
```

---

Come back and say **"README done"** and the Discord and LinkedIn posts get written immediately — formatted specifically to get attention from technical judges and developers.