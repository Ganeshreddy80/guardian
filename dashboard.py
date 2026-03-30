import streamlit as st
import time
import json
import pandas as pd
from datetime import datetime
from guardian_core import guardian, DEMO_TRANSACTIONS, analyst_llm

# ── PAGE CONFIG ───────────────────────────────────────────

st.set_page_config(
    page_title="GUARDIAN",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ GUARDIAN — Financial Decision System")
st.caption("Autonomous financial co-pilot for freelancers")

# ── MEMORY HELPERS ────────────────────────────────────────

def save_run(decision):
    history = load_history()
    history.append({
        "date": datetime.now().strftime("%d %b %Y %I:%M %p"),
        "action": decision["action"],
        "saving": decision["projected_saving"],
        "urgency": decision["urgency"]
    })
    with open("history.json", "w") as f:
        json.dump(history, f)

def load_history():
    try:
        with open("history.json") as f:
            return json.load(f)
    except:
        return []

# ── SIDEBAR ───────────────────────────────────────────────

with st.sidebar:

    # Demo Mode Toggle
    demo_mode = st.toggle("🎭 Demo Mode", value=True)

    if demo_mode:
        st.session_state["transactions"] = DEMO_TRANSACTIONS
        st.info("Using demo data")
    else:
        st.header("📂 Upload Transactions")

        # Sample CSV download
        sample_csv = """id,type,amount,source,category,usage_days
t01,income,50000,Client A,freelance,0
t02,expense,950,Notion Pro,subscription,0
t03,expense,990,ClickUp,subscription,1
t04,expense,800,Linear,subscription,28
t05,expense,1200,Figma,tool,22
t06,expense,500,Food,personal,0
t07,income,35000,Client B,freelance,0
"""
        st.download_button(
            "📥 Download Sample CSV",
            sample_csv,
            "sample.csv",
            "text/csv"
        )

        uploaded = st.file_uploader("Upload CSV file", type="csv")
        if uploaded:
            df = pd.read_csv(uploaded)
            st.success(f"Loaded {len(df)} transactions")
            st.dataframe(df.head(5))
            st.session_state["transactions"] = df.to_dict(orient="records")
        else:
            if "transactions" not in st.session_state:
                st.session_state["transactions"] = DEMO_TRANSACTIONS

    st.divider()

    # Past Runs Memory
    st.header("📈 Past Runs")
    history = load_history()
    if history:
        for run in history[-3:][::-1]:
            urgency_icon = "🚨" if run["urgency"] == "HIGH" else "⚠️"
            st.write(f"{urgency_icon} **{run['date']}**")
            st.write(f"→ {run['action']}")
            st.write(f"→ ₹{run['saving']} saved")
            st.divider()
    else:
        st.caption("No runs yet. Click Run GUARDIAN.")

st.success("💡 Insight Preview: Subscription spending detected — potential savings opportunity identified.")

# ── LAYOUT — 4 PANELS ────────────────────────────────────

col1, col2 = st.columns([1, 2])
col3, col4 = st.columns([1, 2])

with col1:
    st.subheader("📥 Transactions")
    for t in st.session_state.get("transactions", DEMO_TRANSACTIONS):
        icon = "💰" if t.get("type") == "income" else "💸"
        with st.container():
            st.write(f"{icon} **{t['source']}**")
            st.caption(f"₹{t['amount']} • {t.get('category', 'uncategorized')}")

with col2:
    st.subheader("🧠 Live Reasoning Trace")
    trace_placeholder = st.empty()
    trace_placeholder.markdown("🔵 Waiting for analysis...")

with col3:
    st.subheader("📊 Confidence")
    confidence_placeholder = st.empty()

with col4:
    st.subheader("💡 Decision")
    decision_placeholder = st.empty()
    decision_placeholder.info("Run GUARDIAN to see your financial decision.")


st.info("💡 Click **Run GUARDIAN** to analyze transactions and get AI-powered financial insights.")

# ── RUN BUTTON ────────────────────────────────────────────

st.divider()
if st.button("🚀 Run GUARDIAN", type="primary", use_container_width=True):

    st.session_state["alert_sent"] = False

    # Show initial thinking state
    trace_placeholder.markdown("🧠 Analyzing transactions...")
    time.sleep(1)

    with st.spinner("Agents thinking..."):
        initial_state = {
            "transactions": st.session_state.get("transactions", DEMO_TRANSACTIONS),
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

    # Stream trace
    trace_lines = []
    for line in result["trace"]:
        trace_lines.append(line)
        time.sleep(0.2)
        color = "🔴" if "REJECTED" in line else "🟢" if "APPROVED" in line else "🔵"
        display = "\n\n".join(f"{color} {l}" for l in trace_lines)
        trace_placeholder.markdown(display)

    # Confidence
    final_conf = result["confidence"]
    with confidence_placeholder.container():
        st.progress(final_conf)
        if final_conf >= 0.80:
            st.success(
                f"✅ Final Confidence: {final_conf:.0%}\n\n"
                f"Critic approved after {result['iteration_count']} iterations"
            )
        else:
            st.error(
                f"❌ Confidence: {final_conf:.0%} — escalated to human review"
            )

    # Decision
    d = result.get("decision") or {}
    if d:
        with decision_placeholder.container():
            m1, m2 = st.columns(2)
            m1.metric("💰 Savings", f"₹{d.get('projected_saving', 0)}")
            m2.metric("⚠️ Urgency", d.get("urgency", "—"))
            st.success(d.get("action", ""))
            st.caption(d.get("message", ""))

        save_run(d)

        if d.get("urgency") == "HIGH" and not st.session_state.get("alert_sent"):
            try:
                from telegram_alert import send_alert
                send_alert(d)
                st.session_state["alert_sent"] = True
                st.toast("🚨 Telegram alert sent!", icon="📱")
            except Exception as e:
                st.warning(f"Telegram not configured: {e}")
    else:
        decision_placeholder.warning(
            "System escalated to human review — confidence too low after 3 iterations"
        )

    st.session_state["last_result"] = result

    st.caption("✅ Analysis complete. Review insights above or ask GUARDIAN questions below.")
    st.markdown("### 🚀 AI-powered financial co-pilot that detects waste, saves money, and guides decisions in real-time")
# ── CHATBOT ───────────────────────────────────────────────

st.divider()
st.subheader("💬 Ask GUARDIAN")

if "last_result" not in st.session_state:
    st.caption("Run GUARDIAN first to enable the chatbot.")
else:
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for msg in st.session_state["messages"]:
        st.chat_message("user").write(msg["user"])
        st.chat_message("assistant").write(msg["bot"])

    user_q = st.chat_input("Ask about your finances...")

    if user_q:
        result = st.session_state["last_result"]
        subs = result.get("tool_results", {}).get("subscriptions", {})
        d = result.get("decision", {})

        context = f"""You are GUARDIAN, an AI financial assistant.

Current analysis:
- Wasteful tools: {subs.get('wasteful_tools', [])}
- Monthly waste: ₹{subs.get('monthly_waste', 0)}
- 6-month waste: ₹{subs.get('six_month_waste', 0)}
- Decision: {d.get('action', 'N/A')}
- Savings: ₹{d.get('projected_saving', 0)}
- Urgency: {d.get('urgency', 'N/A')}

Answer using only this data. Be concise. Max 3 sentences.

User: {user_q}"""

        with st.spinner("Thinking..."):
            try:
                response = analyst_llm.invoke(context)
                bot_reply = response.content
            except Exception as e:
                bot_reply = "⚠️ Temporary issue. Please try again."

        st.session_state["messages"].append({
            "user": user_q,
            "bot": bot_reply
        })

        st.chat_message("user").write(user_q)
        st.chat_message("assistant").write(bot_reply)