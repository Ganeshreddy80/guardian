import streamlit as st
import time
from guardian_core import guardian, DEMO_TRANSACTIONS

# ── PAGE CONFIG ───────────────────────────────────────────

st.set_page_config(
    page_title="GUARDIAN",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ GUARDIAN — Financial Decision System")
st.caption("Autonomous financial co-pilot for freelancers")

# ── LAYOUT — 4 PANELS ────────────────────────────────────

col1, col2 = st.columns([1, 2])
col3, col4 = st.columns([1, 2])

# Panel 1 — Transaction Feed
with col1:
    st.subheader("📥 Transactions")
    for t in DEMO_TRANSACTIONS:
        icon = "💰" if t["type"] == "income" else "💸"
        st.write(f"{icon} {t['source']} — ₹{t['amount']}")

# Panel 2 — Reasoning Trace (main panel)
with col2:
    st.subheader("🧠 Live Reasoning Trace")
    trace_placeholder = st.empty()

# Panel 3 — Confidence Evolution
with col3:
    st.subheader("📊 Confidence")
    confidence_placeholder = st.empty()

# Panel 4 — Final Decision
with col4:
    st.subheader("💡 Decision")
    decision_placeholder = st.empty()

# ── RUN BUTTON ────────────────────────────────────────────

st.divider()
if st.button("🚀 Run GUARDIAN", type="primary", use_container_width=True):

    with st.spinner("Agents thinking..."):

        initial_state = {
            "transactions":      DEMO_TRANSACTIONS,
            "monitor_output":    None,
            "analyst_output":    None,
            "tool_results":      None,
            "confidence":        0.0,
            "critique_approved": False,
            "critique_reason":   "",
            "decision":          None,
            "iteration_count":   0,
            "trace":             []
        }

        result = guardian.invoke(initial_state)

    # Stream trace lines one by one with delay
    trace_lines = []
    for line in result["trace"]:
        trace_lines.append(line)
        time.sleep(0.4)

        # Color logic — amber on reject, green on approve
        if "REJECTED" in line:
            color = "🔴"
        elif "APPROVED" in line:
            color = "🟢"
        else:
            color = "🔵"

        display = "\n\n".join(
            f"{color} {l}" for l in trace_lines
        )
        trace_placeholder.markdown(display)

    # Confidence evolution panel
    final_conf = result["confidence"]
    if final_conf >= 0.80:
        confidence_placeholder.success(
            f"✅ Final Confidence: {final_conf:.0%}\n\n"
            f"Critic approved after {result['iteration_count']} iterations"
        )
    else:
        confidence_placeholder.error(
            f"❌ Confidence: {final_conf:.0%} — escalated to human review"
        )

    # Decision panel
    if result["decision"]:
        d = result["decision"]
        decision_placeholder.success(
            f"**Action:** {d['action']}\n\n"
            f"**Save:** ₹{d['projected_saving']}\n\n"
            f"**Urgency:** {d['urgency']}\n\n"
            f"**Message:** {d['message']}"
        )
    else:
        decision_placeholder.warning(
            "System escalated to human review — confidence too low after 3 iterations"
        )
