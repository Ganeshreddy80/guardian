markdown
# 🛡️ GUARDIAN — Autonomous Financial Decision System

> Built for freelancers who lose money not from lack of income,
> but from lack of visibility.

GUARDIAN is a multi-agent financial decision system that monitors your
transactions, reasons about spending patterns, challenges its own conclusions,
and delivers verified decisions before money is wasted.

**Not a tracker. Not a dashboard. A reasoning system.**

---

## 🎬 Live Demo

👉 Live App: https://guardian-wwafsplqbv57hrhgnkhcp5.streamlit.app/ 
👉 Demo Video: https://youtu.be/558p5a4MkZs

![Dashboard](assets/dashboard.png)

> Real output from a live run:
> System rejected its first analysis, re-analysed with deeper
> evidence, and approved a decision at 90% confidence.

---

## 📊 Real System Output

 ⁠
Input: 7 transactions — Rs.85,000 income, Rs.4,440 expenses
Subscriptions detected: 3 (Notion Pro, ClickUp, Linear)

Monitor    → Found subscriptions and anomalies
Analyst 1  → Identified unnecessary spending
Critic     → REJECTED (insight lacked specific numbers)
Analyst 2  → Identified unnecessary spending with exact data
Critic     → APPROVED (strong confidence)

Final Confidence: 90% — approved after 2 iterations

Decision:  Cancel Notion Pro + ClickUp
Save:      Rs.11,640 over 6 months
Urgency:   HIGH
Impact:    Rs.1,940/month wasted


---

## 🧠 How It Works


Transactions (CSV / JSON / Manual)
↓
Monitor → Analyst → Critic → Decision


⁠ - Monitor detects anomalies
- Analyst builds financial insights
- Critic rejects weak reasoning
- Decision generates final action

Only high-confidence decisions are shown.

---

## 🚀 Features

- Multi-agent reasoning loop (Monitor → Analyst → Critic → Decision)
- Self-correcting AI (reject → improve → approve)
- Deterministic tool calculations (no LLM guessing)
- Live reasoning trace (step-by-step execution)
- CSV / JSON / manual input support
- Confidence evolution (0.80 → 0.90)
- Telegram alerts for high urgency
- Demo mode for safe public usage

---

## 🤖 Agent Architecture

| Agent    | Role                                   |
|----------|----------------------------------------|
| Monitor  | Detects anomalies                      |
| Analyst  | Builds insights and assigns confidence |
| Critic   | Validates or rejects reasoning         |
| Decision | Generates final action                 |

---

## 🔧 Tool Functions

**analyze_subscriptions(transactions)**
Detects wasteful subscriptions and calculates savings

**forecast_cashflow(transactions)**
Calculates burn rate and financial risk

---

## ▶️ Run Locally

 ⁠bash
git clone https://github.com/Ganeshreddy80/guardian.git
cd guardian

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Add your OpenRouter API key

streamlit run dashboard.py


---

## ⚙️ Environment Variables


OPENAI_API_KEY=your_openrouter_key
OPENAI_API_BASE=https://openrouter.ai/api/v1
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id


⁠ ---

## 📦 Requirements

 ⁠bash
pip install -r requirements.txt


---

## 📁 Project Structure


guardian/
├── guardian_core.py
├── dashboard.py
├── telegram_alert.py
├── requirements.txt
├── assets/
│   ├── dashboard.png
│   └── telegram.png
└── README.md


---

## 💬 What Makes This Different

Most finance apps track spending.

GUARDIAN challenges its own conclusions before acting.

If reasoning is weak → it rejects → re-analyzes → then decides.

This makes it a **decision system, not just a dashboard**.

---

## 🔮 Future Work

- Bank API integration (Razorpay / Plaid)
- Multi-user support
- Weekly automated analysis
- Mobile optimization

---

## 👨‍💻 Built By

**Ganesh Kumar Reddy**

---

## 📄 License

MIT License

