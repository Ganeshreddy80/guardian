import json
import os
from turtle import st
from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# ── LLM SETUP (OpenRouter) ────────────────────────────────

# ── LLM SETUP (Multi-model via OpenRouter) ───────────────

analyst_llm = ChatOpenAI(
    model="anthropic/claude-3-haiku",
    temperature=0,
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY")
)

critic_llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    temperature=0,
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY")
)

from telegram_alert import send_alert



# ── TOOLS (Real Calculations) ─────────────────────────────

def is_wasteful(sub, overlapping_names):
    usage = int(sub.get("usage_days", 0))
    cost = sub["amount"]
    name = sub["source"]

    # Only evaluate overlapping tools strictly
    if name in overlapping_names:
        if usage == 0:
            return True
        if usage < 5 and cost > 700:
            return True
        if usage < 10:
            return True

    return False


def analyze_subscriptions(transactions: List[dict]) -> dict:
    subs = [t for t in transactions if t.get("category") == "subscription"]

    pm_tools = ["Notion Pro", "ClickUp", "Linear", "Asana"]

    overlapping = [s for s in subs if s.get("source") in pm_tools]
    overlapping_names = [s["source"] for s in overlapping]

    # Only apply waste logic to overlapping tools
    wasteful = [s for s in overlapping if is_wasteful(s, overlapping_names)]

    monthly_waste = sum(s["amount"] for s in wasteful)

    return {
        "total_subscriptions": len(subs),
        "overlapping_tools": overlapping_names,
        "wasteful_tools": [s["source"] for s in wasteful],
        "overlapping_count": len(overlapping),
        "monthly_waste": round(monthly_waste, 2),
        "six_month_waste": round(monthly_waste * 6, 2)
    }

def forecast_cashflow(transactions: List[dict]) -> dict:
    income = sum(t["amount"] for t in transactions
                 if t.get("type") == "income")
    expenses = sum(t["amount"] for t in transactions
                   if t.get("type") == "expense")
    net = income - expenses
    daily_burn = expenses / 30 if expenses > 0 else 1
    days_until_risk = int(net / daily_burn) if net > 0 else 0
    return {
        "total_income": round(income, 2),
        "total_expenses": round(expenses, 2),
        "net_position": round(net, 2),
        "daily_burn_rate": round(daily_burn, 2),
        "days_until_cash_risk": days_until_risk,
        "risk_level": (
            "HIGH" if days_until_risk < 20 else
            "MEDIUM" if days_until_risk < 40 else
            "LOW"
        )
    }

# ── STATE ─────────────────────────────────────────────────

class GUARDIANState(TypedDict):
    transactions: List[dict]
    monitor_output: Optional[dict]
    analyst_output: Optional[dict]
    tool_results: Optional[dict]
    confidence: float
    critique_approved: bool
    critique_reason: str
    decision: Optional[dict]
    iteration_count: int
    trace: List[str]

# ── STRUCTURED OUTPUT SCHEMAS ─────────────────────────────

class AnalystOutput(BaseModel):
    insight: str
    confidence: float
    recommended_action: str

class CritiqueOutput(BaseModel):
    approved: bool
    reason: str

class DecisionOutput(BaseModel):
    action: str
    projected_saving: float
    urgency: str
    message: str

# ── AGENT NODES ───────────────────────────────────────────

def monitor_node(state: GUARDIANState) -> GUARDIANState:
    txns = state["transactions"]
    subs = [t for t in txns if t.get("category") == "subscription"]
    state["monitor_output"] = {
        "subscription_count": len(subs),
        "flag": len(subs) >= 3
    }
    state["trace"].append(
        f"Monitor: Scanned {len(txns)} transactions. "
        f"Found {len(subs)} subscriptions. "
        f"Anomaly flag: {len(subs) >= 3}"
    )
    return state


def analyst_node(state: GUARDIANState) -> GUARDIANState:
    iteration = state["iteration_count"] + 1
    txns = state["transactions"]

    # Run real tool calculations
    sub_results = analyze_subscriptions(txns)
    cash_results = forecast_cashflow(txns)
    state["tool_results"] = {
        "subscriptions": sub_results,
        "cashflow": cash_results
    }

    if iteration == 1:
        data_context = (
            f"{sub_results['overlapping_count']} overlapping tools found. "
            f"Tools confirmed as wasteful (under 5 usage days): "
            f"{sub_results.get('wasteful_tools', [])}. "
        )
    else:
        data_context = (
            f"DETAILED DATA: "
            f"{sub_results['overlapping_count']} overlapping tools found: "
            f"{sub_results['overlapping_tools']}. "
            f"Monthly waste: ₹{sub_results['monthly_waste']}. "
            f"Six month waste: ₹{sub_results['six_month_waste']}. "
            f"Cash risk in {cash_results['days_until_cash_risk']} days. "
            f"Risk level: {cash_results['risk_level']}."
        )

    prompt = f"""
You are a financial analyst.

STRICT RULES (NO EXCEPTIONS):
- Return ONLY valid JSON
- No explanation
- No text before or after JSON
- No markdown

JSON FORMAT:
{{
  "insight": "string with ₹ values",
  "confidence": number (0.0 to 1.0),
  "recommended_action": "clear action"
}}

DATA:
Wasteful tools: {sub_results.get('wasteful_tools', [])}
Monthly waste: ₹{sub_results['monthly_waste']}
Six month waste: ₹{sub_results['six_month_waste']}
Cash risk: {cash_results['days_until_cash_risk']} days
"""

    # Call Claude
    raw = analyst_llm.invoke(prompt).content

    import json
    raw = raw.replace("```json", "").replace("```", "").strip()

    result_json = json.loads(raw)
    result = AnalystOutput(**result_json)

    state["analyst_output"] = {
        "insight": result.insight,
        "confidence": result.confidence,
        "recommended_action": result.recommended_action
    }

    state["confidence"] = result.confidence
    state["iteration_count"] += 1

    state["trace"].append(
        f"Analyst (iteration {iteration}): "
        f"Confidence {result.confidence:.2f} | "
        f"{result.insight[:60]}..."
    )

    return state

def critic_node(state: GUARDIANState) -> GUARDIANState:
    analyst = state["analyst_output"]
    confidence = analyst["confidence"]
    tool_results = state["tool_results"]

    has_specific_amount = tool_results["subscriptions"]["monthly_waste"] > 0
    has_action = len(analyst["recommended_action"]) > 10
    meets_threshold = confidence >= 0.75

    prompt = f"""You are a financial critic agent.

Analyst insight: {analyst['insight']}
Confidence score: {confidence}
Has specific waste amount calculated: {has_specific_amount}
Has actionable recommendation: {has_action}
Required confidence threshold: 0.80

Evaluate strictly:
- Confidence must be >= 0.80
- Insight must reference specific numbers
- Recommendation must be actionable

If ANY condition fails → reject and state exactly what is missing."""

    structured_llm = critic_llm.with_structured_output(CritiqueOutput)
    result = structured_llm.invoke(prompt)

    # Hard override — threshold is non-negotiable
    if not meets_threshold:
        result.approved = False
        result.reason = (
            f"Confidence {confidence:.2f} below 0.80 threshold. "
            "Insufficient evidence. Requesting detailed tool analysis."
        )

    state["critique_approved"] = result.approved
    state["critique_reason"] = result.reason
    status = "APPROVED ✅" if result.approved else "REJECTED ❌"

    state["trace"].append(
        f"Critic: {status} | {result.reason[:70]}"
    )
    return state


def decision_node(state: GUARDIANState) -> GUARDIANState:
    sub = state["tool_results"]["subscriptions"]
    cash = state["tool_results"]["cashflow"]

    wasteful = sub["wasteful_tools"]
    saving = sub["six_month_waste"]

    # Handle no waste case
    if not wasteful:
        state["decision"] = {
            "action": "No cancellations needed",
            "projected_saving": 0,
            "urgency": "LOW",
            "message": "All subscriptions are actively used. No action required."
        }
        return state

    # Proper decision
    urgency = (
        "HIGH" if saving > 10000 else
        "MEDIUM" if saving > 3000 else
        "LOW"
    )

    state["decision"] = {
        "action": f"Cancel {', '.join(wasteful)}",
        "projected_saving": saving,
        "urgency": urgency,
        "message": (
            f"Cancel {', '.join(wasteful)} — "
            f"low usage detected. "
            f"Saves ₹{saving} over 6 months."
        )
    }

    state["trace"].append(
        f"Decision: Cancel {wasteful} | Save ₹{saving} | Urgency: {urgency}"
    )

    return state
# ── ROUTING ───────────────────────────────────────────────

def route_after_critic(state: GUARDIANState) -> str:
    # Force fallback after max iterations
    if state["iteration_count"] >= 3:
        state["critique_approved"] = True
        state["trace"].append("Critic fallback: Forced approval after 3 attempts")
        return "decide"

    # If rejected → re-run analyst
    if not state["critique_approved"]:
        return "reanalyse"

    # If approved → proceed
    return "decide"
# ── GRAPH ASSEMBLY ────────────────────────────────────────

graph = StateGraph(GUARDIANState)
graph.add_node("monitor",  monitor_node)
graph.add_node("analyst",  analyst_node)
graph.add_node("critic",   critic_node)
graph.add_node("decision", decision_node)

graph.set_entry_point("monitor")
graph.add_edge("monitor", "analyst")
graph.add_edge("analyst", "critic")
graph.add_conditional_edges(
    "critic",
    route_after_critic,
    {
        "reanalyse": "analyst",
        "decide":    "decision",
        "escalate":  END
    }
)
graph.add_edge("decision", END)

guardian = graph.compile()

# ── DEMO TRANSACTIONS ─────────────────────────────────────

DEMO_TRANSACTIONS = [
    {"id": "t01", "type": "income",  "amount": 50000,
     "source": "Client A",   "category": "freelance",    "usage_days": 0},
    {"id": "t02", "type": "expense", "amount": 950,
     "source": "Notion Pro", "category": "subscription", "usage_days": 0},
    {"id": "t03", "type": "expense", "amount": 990,
     "source": "ClickUp",    "category": "subscription", "usage_days": 1},
    {"id": "t04", "type": "expense", "amount": 800,
     "source": "Linear",     "category": "subscription", "usage_days": 28},
    {"id": "t05", "type": "expense", "amount": 1200,
     "source": "Figma",      "category": "tool",         "usage_days": 22},
    {"id": "t06", "type": "expense", "amount": 500,
     "source": "Food",       "category": "personal",     "usage_days": 0},
    {"id": "t07", "type": "income",  "amount": 35000,
     "source": "Client B",   "category": "freelance",    "usage_days": 0},
]

# ── RUN ───────────────────────────────────────────────────

if __name__ == "__main__":
    send_alert({
        "action": "Test Telegram",
        "projected_saving": 5000,
        "urgency": "HIGH",
        "message": "If you see this, integration works."
    })
    initial_state: GUARDIANState = {
        "transactions": DEMO_TRANSACTIONS,
        "monitor_output": None,
        "analyst_output": None,
        "tool_results": None,
        "confidence": 0.0,
        "critique_approved": False,
        "critique_reason": "",
        "decision": None,
        "iteration_count": 0,
        "trace": []
    }

    result = guardian.invoke(initial_state)
    if result.get("decision") and result["decision"]["urgency"] == "HIGH" and not st.session_state.get("alert_sent"):
        send_alert(result["decision"])
        st.session_state["alert_sent"] = True

    print("📋 REASONING TRACE:")
    print("-" * 55)
    for line in result["trace"]:
        print(f"  → {line}")

    print(f"\n📊 FINAL CONFIDENCE: {result['confidence']:.2f}")
    print(f"✅ APPROVED: {result['critique_approved']}")

    if result["decision"]:
        d = result["decision"]
        print("\n💡 FINAL DECISION:")
        print(f"   Action:  {d['action']}")
        print(f"   Saving:  ₹{d['projected_saving']}")
        print(f"   Urgency: {d['urgency']}")
        print(f"   Message: {d['message']}")