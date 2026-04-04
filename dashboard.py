import html
import time

import streamlit as st

from guardian_core import DEMO_TRANSACTIONS, guardian
from input_handler import get_summary, parse_csv, parse_json, parse_manual


st.set_page_config(page_title="GUARDIAN", page_icon="🛡️", layout="wide")


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #0b1018;
            --panel: #101722;
            --panel-soft: #151d29;
            --border: rgba(255, 255, 255, 0.08);
            --text: #f4f6fb;
            --muted: #9ca8bc;
            --success-bg: rgba(22, 89, 55, 0.62);
            --success-border: rgba(84, 214, 135, 0.22);
            --success-text: #5bf08f;
            --danger-bg: rgba(118, 32, 45, 0.35);
            --danger-border: rgba(255, 110, 129, 0.22);
            --danger-text: #ff8da1;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(64, 84, 126, 0.16), transparent 28%),
                radial-gradient(circle at top right, rgba(37, 97, 78, 0.16), transparent 24%),
                var(--bg);
            color: var(--text);
        }

        [data-testid="stAppViewContainer"] {
            background: transparent;
        }

        [data-testid="stSidebar"] {
            background: #272834;
            border-right: 1px solid rgba(255, 255, 255, 0.06);
        }

        [data-testid="stSidebar"] .block-container {
            padding-top: 1.6rem;
            padding-bottom: 1.5rem;
        }

        .block-container {
            max-width: 1500px;
            padding-top: 1.4rem;
            padding-bottom: 2rem;
        }

        h1, h2, h3, h4, p, label, span, div {
            font-family: "Avenir Next", "Helvetica Neue", "Segoe UI", sans-serif;
        }

        .guardian-sidebar-title {
            font-size: 1.9rem;
            font-weight: 700;
            color: var(--text);
            margin: 0 0 0.85rem 0;
        }

        .guardian-divider {
            height: 1px;
            background: rgba(255, 255, 255, 0.08);
            margin: 1.4rem 0 1.5rem;
        }

        .guardian-hero-kicker {
            color: var(--muted);
            font-size: 1rem;
            margin-bottom: 0.65rem;
        }

        .guardian-hero-title {
            color: var(--text);
            font-size: clamp(2rem, 3vw, 3.25rem);
            line-height: 1.1;
            font-weight: 800;
            margin: 0 0 1.2rem 0;
            letter-spacing: -0.03em;
        }

        .guardian-banner {
            background: linear-gradient(90deg, rgba(20, 72, 46, 0.92), rgba(24, 82, 51, 0.82));
            border: 1px solid rgba(92, 227, 146, 0.12);
            border-radius: 14px;
            color: #58ee92;
            font-size: 1rem;
            font-weight: 700;
            padding: 1rem 1.2rem;
            margin: 0.15rem 0 1.35rem 0;
        }

        .guardian-metric {
            padding: 0.4rem 0 1.2rem;
        }

        .guardian-metric__label {
            color: var(--text);
            opacity: 0.92;
            font-size: 0.98rem;
            margin-bottom: 0.45rem;
        }

        .guardian-metric__value {
            color: var(--text);
            font-size: clamp(2.2rem, 3vw, 3rem);
            line-height: 1;
            font-weight: 500;
            letter-spacing: -0.04em;
        }

        .guardian-panel {
            background: linear-gradient(180deg, rgba(17, 24, 36, 0.9), rgba(12, 18, 27, 0.95));
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 1.2rem 1.2rem 1.15rem;
            min-height: 250px;
            box-shadow: 0 18px 36px rgba(0, 0, 0, 0.18);
        }

        .guardian-panel--success {
            background: linear-gradient(180deg, rgba(20, 72, 46, 0.9), rgba(19, 65, 43, 0.92));
            border-color: var(--success-border);
        }

        .guardian-panel--danger {
            background: linear-gradient(180deg, rgba(98, 31, 41, 0.48), rgba(65, 24, 32, 0.72));
            border-color: var(--danger-border);
        }

        .guardian-panel__title {
            color: var(--text);
            font-size: 1.2rem;
            font-weight: 800;
            margin-bottom: 0.95rem;
            letter-spacing: -0.02em;
        }

        .guardian-panel__body {
            color: var(--text);
            font-size: 1rem;
        }

        .guardian-empty {
            color: var(--muted);
            line-height: 1.7;
            padding-top: 0.1rem;
        }

        .guardian-table-wrap {
            overflow-x: auto;
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }

        .guardian-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.96rem;
        }

        .guardian-table th {
            text-align: left;
            color: var(--muted);
            font-weight: 600;
            padding: 0.9rem 0.8rem;
            background: rgba(255, 255, 255, 0.04);
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }

        .guardian-table td {
            color: var(--text);
            padding: 0.82rem 0.8rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }

        .guardian-table tr:last-child td {
            border-bottom: none;
        }

        .guardian-table td:nth-child(3) {
            text-align: right;
            font-variant-numeric: tabular-nums;
        }

        .guardian-trace-item {
            color: var(--text);
            line-height: 1.65;
            margin-bottom: 0.8rem;
        }

        .guardian-trace-item:last-child {
            margin-bottom: 0;
        }

        .guardian-trace-item--danger {
            color: #ffc0cb;
        }

        .guardian-trace-item--success {
            color: #a6ffbf;
        }

        .guardian-stat {
            font-size: clamp(2rem, 3vw, 2.8rem);
            font-weight: 800;
            letter-spacing: -0.04em;
            color: var(--success-text);
            margin-bottom: 0.8rem;
        }

        .guardian-panel--danger .guardian-stat {
            color: var(--danger-text);
        }

        .guardian-copy {
            font-size: 1rem;
            color: rgba(244, 246, 251, 0.96);
            line-height: 1.8;
        }

        .guardian-copy strong {
            color: var(--text);
        }

        .stButton > button {
            border-radius: 12px;
            border: none;
            background: #ff4d57;
            color: white;
            font-weight: 700;
            min-height: 3rem;
        }

        .stButton > button:hover {
            background: #ff5d66;
            color: white;
        }

        .stRadio > label,
        .stFileUploader label,
        .stDownloadButton label,
        .stNumberInput label,
        .stTextInput label,
        .stSlider label,
        .stSelectbox label {
            color: var(--text) !important;
        }

        [data-testid="stMarkdownContainer"] p {
            color: inherit;
        }

        [data-testid="stAlert"] {
            border-radius: 14px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def escape(value: object) -> str:
    return html.escape(str(value))


def panel(title: str, body: str, variant: str = "") -> str:
    variant_class = f" guardian-panel--{variant}" if variant else ""
    return (
        f'<section class="guardian-panel{variant_class}">'
        f'<div class="guardian-panel__title">{escape(title)}</div>'
        f'<div class="guardian-panel__body">{body}</div>'
        f"</section>"
    )


def metric_card(label: str, value: str) -> str:
    return (
        '<div class="guardian-metric">'
        f'<div class="guardian-metric__label">{escape(label)}</div>'
        f'<div class="guardian-metric__value">{escape(value)}</div>'
        "</div>"
    )


def format_amount(value: object) -> str:
    try:
        return f"{float(value):,.0f}".replace(",", "")
    except (TypeError, ValueError):
        return str(value)


def render_transactions_panel(transactions: list[dict] | None) -> str:
    if not transactions:
        return panel(
            "📥 Transactions",
            '<div class="guardian-empty">Load data using the sidebar to preview your transactions here.</div>',
        )

    columns = ["source", "type", "amount", "category"]
    header_html = "".join(f"<th>{escape(col)}</th>" for col in columns)

    rows = []
    for txn in transactions:
        row = "".join(
            (
                f"<td>{escape(txn.get('source', '—'))}</td>"
                f"<td>{escape(txn.get('type', '—'))}</td>"
                f"<td>{escape(format_amount(txn.get('amount', '—')))}</td>"
                f"<td>{escape(txn.get('category', '—'))}</td>"
            )
        )
        rows.append(f"<tr>{row}</tr>")

    body = (
        '<div class="guardian-table-wrap">'
        '<table class="guardian-table">'
        f"<thead><tr>{header_html}</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
        "</div>"
    )
    return panel("📥 Transactions", body)


def trace_item(raw_line: str) -> tuple[str, str]:
    if raw_line.startswith("Monitor:"):
        return "🔍 Monitoring → Found subscriptions & anomalies", ""
    if raw_line.startswith("Analyst"):
        return "🧠 Analysis → Identified unnecessary spending", ""
    if "REJECTED" in raw_line:
        reason = raw_line.split("|", 1)[1].strip() if "|" in raw_line else raw_line
        return f"🔵 Critic: REJECTED ❌ | {reason}", "danger"
    if "APPROVED" in raw_line:
        return "🛡️ Critic → Approved (strong confidence)", "success"
    if raw_line.startswith("Decision:"):
        return "🎯 Decision → Taking action to save money", ""
    return raw_line, ""


def render_trace_panel(trace_lines: list[str] | None) -> str:
    if not trace_lines:
        return panel(
            "🧠 Live Reasoning Trace",
            '<div class="guardian-empty">Trace will appear here when you run GUARDIAN.</div>',
        )

    items = []
    for raw_line in trace_lines:
        label, state = trace_item(raw_line)
        state_class = f" guardian-trace-item--{state}" if state else ""
        items.append(
            f'<div class="guardian-trace-item{state_class}">{escape(label)}</div>'
        )
    return panel("🧠 Live Reasoning Trace", "".join(items))


def render_confidence_panel(result: dict | None) -> str:
    if not result:
        return panel(
            "📊 Confidence",
            '<div class="guardian-empty">Confidence score appears here after GUARDIAN finishes its review.</div>',
        )

    confidence = result["confidence"]
    iterations = result["iteration_count"]

    if result["critique_approved"]:
        body = (
            f'<div class="guardian-stat">✅ {confidence:.0%} Confidence</div>'
            f'<div class="guardian-copy">Approved after {iterations} iteration'
            f"{'s' if iterations != 1 else ''}<br><br>"
            "Evidence threshold: 0.80 met</div>"
        )
        return panel("📊 Confidence", body, "success")

    body = (
        f'<div class="guardian-stat">❌ {confidence:.0%} Confidence</div>'
        f'<div class="guardian-copy">Could not reach threshold after {iterations} iteration'
        f"{'s' if iterations != 1 else ''}<br><br>"
        "Escalated to human review</div>"
    )
    return panel("📊 Confidence", body, "danger")


def render_decision_panel(result: dict | None) -> str:
    if not result:
        return panel(
            "💡 Decision",
            '<div class="guardian-empty">Final decision appears here after the analysis is approved.</div>',
        )

    decision = result.get("decision")
    if not decision:
        body = (
            '<div class="guardian-copy">System could not reach a confident decision.<br><br>'
            "Please review the trace and decide manually.</div>"
        )
        return panel("💡 Decision", body, "danger")

    body = (
        f'<div class="guardian-copy"><strong>{escape(decision["action"])}</strong><br><br>'
        f'💰 Save: ₹{decision["projected_saving"]:,.0f}<br><br>'
        f'⚠️ Urgency: {escape(decision["urgency"])}<br><br>'
        f'💬 {escape(decision["message"])}</div>'
    )
    variant = "success" if decision["projected_saving"] > 0 else ""
    return panel("💡 Decision", body, variant)


def render_hero() -> None:
    st.markdown(
        """
        <div class="guardian-hero-kicker">
            Upload your financial data and get autonomous AI-powered decisions
        </div>
        <div class="guardian-hero-title">
            💡 AI that challenges its own financial decisions before showing them
        </div>
        <div class="guardian-banner">
            🔥 You are wasting ₹1940/month without realizing it
        </div>
        """,
        unsafe_allow_html=True,
    )


inject_styles()

if "transactions" not in st.session_state:
    st.session_state.transactions = None
if "result" not in st.session_state:
    st.session_state.result = None


with st.sidebar:
    st.markdown(
        '<div class="guardian-sidebar-title">📂 Input Your Data</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="guardian-divider"></div>', unsafe_allow_html=True)

    input_method = st.radio(
        "Choose input method:",
        ["📁 Upload CSV", "📋 Upload JSON", "✏️ Enter Manually", "🧪 Use Demo Data"],
        index=3,
    )

    st.markdown('<div class="guardian-divider"></div>', unsafe_allow_html=True)
    transactions = None
    error_msg = None

    if input_method == "📁 Upload CSV":
        st.markdown("**Expected columns:** type, amount, source, category, usage_days")

        sample_csv = """id,type,amount,source,category,usage_days
t01,income,50000,Client A,freelance,0
t02,expense,950,Notion Pro,subscription,0
t03,expense,990,ClickUp,subscription,1
t04,expense,800,Linear,subscription,28
t05,expense,1200,Figma,tool,22
t06,expense,500,Food,personal,0"""

        st.download_button(
            "⬇️ Download Sample CSV",
            sample_csv,
            "sample_transactions.csv",
            "text/csv",
        )

        uploaded = st.file_uploader("Upload your CSV", type=["csv"])
        if uploaded:
            valid, msg, parsed = parse_csv(uploaded)
            if valid:
                transactions = parsed
                st.success(f"✅ {len(parsed)} transactions loaded")
            else:
                error_msg = msg

    elif input_method == "📋 Upload JSON":
        st.markdown("**Format:** List of transaction objects")

        sample_json = """[
  {"type": "income", "amount": 50000,
   "source": "Client A", "category": "freelance", "usage_days": 0},
  {"type": "expense", "amount": 950,
   "source": "Notion Pro", "category": "subscription", "usage_days": 0}
]"""
        st.download_button(
            "⬇️ Download Sample JSON",
            sample_json,
            "sample_transactions.json",
            "application/json",
        )

        uploaded = st.file_uploader("Upload your JSON", type=["json"])
        if uploaded:
            valid, msg, parsed = parse_json(uploaded)
            if valid:
                transactions = parsed
                st.success(f"✅ {len(parsed)} transactions loaded")
            else:
                error_msg = msg

    elif input_method == "✏️ Enter Manually":
        st.markdown("**Add your transactions below:**")

        if "manual_rows" not in st.session_state:
            st.session_state.manual_rows = [{}]

        num_rows = st.number_input(
            "Number of transactions",
            min_value=1,
            max_value=20,
            value=3,
        )

        manual_data = []
        for index in range(num_rows):
            st.markdown(f"**Transaction {index + 1}**")
            col1, col2 = st.columns(2)
            with col1:
                txn_type = st.selectbox(
                    "Type",
                    ["expense", "income"],
                    key=f"type_{index}",
                )
                amount = st.number_input(
                    "Amount (₹)",
                    min_value=1,
                    value=500,
                    key=f"amount_{index}",
                )
            with col2:
                source = st.text_input(
                    "Source/Name",
                    value="",
                    key=f"source_{index}",
                    placeholder="e.g. Notion Pro",
                )
                category = st.selectbox(
                    "Category",
                    ["subscription", "freelance", "tool", "personal", "other"],
                    key=f"category_{index}",
                )
            usage = st.slider(
                "Usage days this month",
                0,
                31,
                0,
                key=f"usage_{index}",
            )
            st.markdown('<div class="guardian-divider"></div>', unsafe_allow_html=True)
            if source:
                manual_data.append(
                    {
                        "type": txn_type,
                        "amount": amount,
                        "source": source,
                        "category": category,
                        "usage_days": usage,
                    }
                )

        if manual_data:
            valid, msg, parsed = parse_manual(manual_data)
            if valid:
                transactions = parsed
                st.success(f"✅ {len(parsed)} transactions ready")
            else:
                error_msg = msg

    else:
        transactions = DEMO_TRANSACTIONS
        st.success(f"✅ {len(DEMO_TRANSACTIONS)} demo transactions loaded")
        st.caption("Using pre-built freelancer scenario")

    if error_msg:
        st.error(f"❌ {error_msg}")

    if transactions:
        st.session_state.transactions = transactions

    st.markdown('<div class="guardian-divider"></div>', unsafe_allow_html=True)

    run_disabled = st.session_state.transactions is None
    run_clicked = st.button(
        "🚀 Run GUARDIAN",
        type="primary",
        use_container_width=True,
        disabled=run_disabled,
    )

    if run_disabled:
        st.caption("⬆️ Load data first to enable")


render_hero()

active_transactions = st.session_state.transactions

if active_transactions:
    summary = get_summary(active_transactions)
    metric_columns = st.columns(4)
    metric_values = [
        ("Total Transactions", str(summary["total_transactions"])),
        ("Total Income", f"₹{summary['total_income']:,.0f}"),
        ("Total Expenses", f"₹{summary['total_expenses']:,.0f}"),
        ("Subscriptions Found", str(summary["subscription_count"])),
    ]
    for column, (label, value) in zip(metric_columns, metric_values):
        with column:
            st.markdown(metric_card(label, value), unsafe_allow_html=True)

    st.markdown('<div class="guardian-divider"></div>', unsafe_allow_html=True)


top_left, top_right = st.columns([1.05, 1.3], gap="large")
bottom_left, bottom_right = st.columns(2, gap="large")

with top_left:
    st.markdown(render_transactions_panel(active_transactions), unsafe_allow_html=True)

with top_right:
    trace_placeholder = st.empty()

with bottom_left:
    confidence_placeholder = st.empty()

with bottom_right:
    decision_placeholder = st.empty()


def paint_dashboard(result: dict | None) -> None:
    trace_placeholder.markdown(
        render_trace_panel(result["trace"] if result else None),
        unsafe_allow_html=True,
    )
    confidence_placeholder.markdown(
        render_confidence_panel(result),
        unsafe_allow_html=True,
    )
    decision_placeholder.markdown(
        render_decision_panel(result),
        unsafe_allow_html=True,
    )


paint_dashboard(st.session_state.result)

if run_clicked and active_transactions:
    st.session_state.result = None
    paint_dashboard(None)

    with st.spinner("GUARDIAN is thinking..."):
        initial_state = {
            "transactions": active_transactions,
            "monitor_output": None,
            "analyst_output": None,
            "tool_results": None,
            "confidence": 0.0,
            "critique_approved": False,
            "critique_reason": "",
            "decision": None,
            "iteration_count": 0,
            "trace": [],
        }
        result = guardian.invoke(initial_state)
        st.session_state.result = result

    streamed_trace = []
    for line in result["trace"]:
        streamed_trace.append(line)
        trace_placeholder.markdown(
            render_trace_panel(streamed_trace),
            unsafe_allow_html=True,
        )
        time.sleep(0.2)

    confidence_placeholder.markdown(
        render_confidence_panel(result),
        unsafe_allow_html=True,
    )
    decision_placeholder.markdown(
        render_decision_panel(result),
        unsafe_allow_html=True,
    )
