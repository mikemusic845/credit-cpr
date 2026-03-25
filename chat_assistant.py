"""
AI Chat Assistant for Credit CPR
- Paid plans only (basic, pro, premium)
- Free users see upgrade gate
- Context-aware credit coaching
- Session memory
- Smart quick prompts
"""

import os
from datetime import datetime
import streamlit as st


def _get_api_key() -> str:
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY", "")
    except Exception:
        key = ""
    if not key:
        key = os.getenv("ANTHROPIC_API_KEY", "")
    return key


def _extract_memory_candidate(user_input: str):
    text = user_input.strip()
    lower = text.lower()
    triggers = [
        "my score is", "my credit score is", "i was denied",
        "i have a collection", "i have collections", "i filed bankruptcy",
        "i missed a payment", "i have late payments", "i want to buy a house",
        "i want to buy a car", "my goal is", "i need to get approved",
    ]
    if any(t in lower for t in triggers):
        return text[:220]
    return None


def _summarize_credit_context(credit_data=None, errors=None) -> str:
    credit_data = credit_data or {}
    errors = errors or []

    accounts = credit_data.get("accounts", [])[:5]
    negatives = credit_data.get("negative_items", [])[:5]
    inquiries = credit_data.get("inquiries", [])[:5]
    public_records = credit_data.get("public_records", [])[:5]

    sections = [
        f"Accounts on file: {len(credit_data.get('accounts', []))}",
        f"Negative items: {len(credit_data.get('negative_items', []))}",
        f"Inquiries: {len(credit_data.get('inquiries', []))}",
        f"Public records: {len(credit_data.get('public_records', []))}",
        f"Errors detected: {len(errors)}",
    ]

    if accounts:
        lines = []
        for a in accounts:
            creditor = a.get("creditor") or a.get("name") or "Unknown"
            status = a.get("status", "unknown")
            balance = a.get("balance", "unknown")
            lines.append(f"- {creditor} | status: {status} | balance: {balance}")
        sections.append("Top accounts:\n" + "\n".join(lines))

    if negatives:
        lines = []
        for n in negatives:
            desc = n.get("description") or n.get("type") or "Negative item"
            date = n.get("date", "unknown date")
            lines.append(f"- {desc} | date: {date}")
        sections.append("Top negative items:\n" + "\n".join(lines))

    if errors:
        lines = []
        categories = []
        for e in errors[:6]:
            category = e.get("category", "Issue")
            if category not in categories:
                categories.append(category)
            desc = e.get("description", "No description")
            impact = e.get("potential_impact", "unknown")
            lines.append(f"- {category}: {desc} | potential impact: {impact}")
        sections.append("Detected issues:\n" + "\n".join(lines))
        if categories:
            sections.append("Issue categories: " + ", ".join(categories))

    return "\n\n".join(sections)


def get_system_prompt(credit_data=None, errors=None):
    user_plan = (st.session_state.get("user") or {}).get("plan", "free")
    chat_memory = st.session_state.get("chat_memory", [])

    base_prompt = """You are Credit CPR's AI Credit Specialist — a knowledgeable, friendly expert in:
- The Fair Credit Reporting Act (FCRA) and consumer rights
- Credit scoring (FICO, VantageScore) and what affects scores
- Dispute strategies and processes with Equifax, Experian, and TransUnion
- Debt validation, statute of limitations, and collections
- Credit building strategies (secured cards, authorized users, credit mix)
- Bankruptcy, charge-offs, collections, and how long items stay on reports

Your personality:
- Warm, encouraging, and empowering
- Use plain English
- Give specific, actionable advice
- Be concise but helpful
- Educational information only, not legal advice

Rules:
- Never tell users to lie or misrepresent facts
- Never promise a score increase or guaranteed result
- Recommend professional legal help for complex legal disputes
- Keep answers practical and personalized when context is available"""

    plan_context = f"\n\nCurrent user plan: {user_plan}."
    if user_plan == "basic":
        plan_context += " User has Basic paid access. Give solid coaching and actionable advice."
    else:
        plan_context += " User has Pro/Premium access. Give full deep-dive coaching and detailed next steps."

    memory_context = ""
    if chat_memory:
        memory_context = "\n\nRecent remembered user details:\n" + "\n".join(
            f"- {m}" for m in chat_memory[-5:]
        )

    credit_context = ""
    if credit_data or errors:
        credit_context = "\n\nCurrent user credit context:\n" + _summarize_credit_context(credit_data, errors)

    return base_prompt + plan_context + memory_context + credit_context


def _ensure_session_state():
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": (
                    "👋 Hi! I'm your Credit CPR AI Specialist. I can help you understand your credit rights, "
                    "explain dispute strategies, answer FCRA questions, and guide you on building better credit.\n\n"
                    "Ask me a question or use one of the quick prompts below."
                ),
                "timestamp": datetime.now().strftime("%I:%M %p"),
            }
        ]
    if "chat_memory" not in st.session_state:
        st.session_state.chat_memory = []
    if "pending_message" not in st.session_state:
        st.session_state.pending_message = None


def _append_message(role: str, content: str):
    st.session_state.chat_messages.append(
        {
            "role": role,
            "content": content,
            "timestamp": datetime.now().strftime("%I:%M %p"),
        }
    )


def _build_quick_questions():
    quick_questions = [
        "How do I dispute an error?",
        "How long do negatives stay on my report?",
        "What's the fastest way to build credit?",
        "What is a 609 dispute letter?",
        "Can I remove a collection account?",
        "What rights do I have under FCRA?",
    ]
    errors = st.session_state.get("errors_found", [])
    if errors:
        issue_name = errors[0].get("category", "issue")
        quick_questions.append(f"What should I dispute first based on my {issue_name.lower()}?")
        quick_questions.append("What should my next 30 days look like based on my report?")
    return quick_questions[:8]


def show_chat_assistant():
    _ensure_session_state()

    user_plan = (st.session_state.get("user") or {}).get("plan", "free")
    is_paid = user_plan in ("basic", "pro", "premium")

    st.header("💬 AI Credit Specialist")
    st.caption("Ask about credit repair, FCRA rights, dispute strategy, collections, and credit-building.")

    # Show quick questions for everyone — clicking triggers upgrade for free users
    st.markdown("**Suggested Questions:**")
    quick_questions = _build_quick_questions()
    cols = st.columns(2 if len(quick_questions) <= 4 else 3)

    for i, question in enumerate(quick_questions):
        col = cols[i % len(cols)]
        with col:
            if st.button(question, key=f"quick_{i}", use_container_width=True):
                if not is_paid:
                    st.session_state.show_upgrade = True
                    st.session_state.upgrade_source = "chat"
                    st.rerun()
                else:
                    st.session_state.pending_message = question
                    st.rerun()

    st.divider()

    # Free user gate
    if not is_paid:
        st.markdown("""
        <div style="
            padding: 32px;
            border-radius: 14px;
            background: linear-gradient(135deg, #f0f8f0 0%, #e8f5e9 100%);
            border: 2px solid #2E8B57;
            text-align: center;
            box-shadow: 0 8px 24px rgba(46,139,87,0.15);
            margin: 20px 0;
        ">
            <h3 style="margin-bottom: 10px; color: #1B3A5C;">🔒 AI Chat is a Paid Feature</h3>
            <p style="margin-bottom: 16px; color: #444;">
                Get personalized credit guidance, dispute strategy help,<br>
                and report-aware coaching from your AI Credit Specialist.
            </p>
            <p style="color: #666; font-size: 0.9rem;">Available on Basic ($19/mo), Pro ($29/mo), and Premium plans</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Upgrade to Unlock AI Chat", type="primary", use_container_width=True):
            st.session_state.show_upgrade = True
            st.session_state.upgrade_source = "chat"
            st.rerun()

        st.markdown("### 💡 What you can ask with a paid plan:")
        st.markdown(
            "- What should I dispute first?\n"
            "- Which item is hurting me the most?\n"
            "- What is the fastest safe way to build my score?\n"
            "- What should I do in the next 30 days?\n"
            "- Should I pay or dispute this collection?"
        )
        return

    # Paid users only below this line
    if user_plan == "basic":
        st.success("🔵 Basic Plan Active")
    else:
        st.success("⭐ Pro/Premium Plan Active")

    for msg in st.session_state.chat_messages:
        avatar = "🛡️" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            st.caption(msg.get("timestamp", ""))

    if st.session_state.pending_message:
        user_input = st.session_state.pending_message
        st.session_state.pending_message = None
        process_message(user_input)
        st.rerun()

    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            "Your question",
            placeholder="Ask a credit question...",
            label_visibility="collapsed",
            key="chat_input_box",
        )
    with col2:
        send_clicked = st.button("Send 💬", use_container_width=True, type="primary")

    if send_clicked and user_input and user_input.strip():
        process_message(user_input.strip())
        st.rerun()

    st.markdown("### 💡 Good things to ask")
    st.markdown(
        "- What should I dispute first?\n"
        "- Which item is hurting me the most?\n"
        "- What is the fastest safe way to build my score?\n"
        "- What should I do in the next 30 days?\n"
        "- Should I pay or dispute this collection?"
    )

    if len(st.session_state.chat_messages) > 1:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_messages = [st.session_state.chat_messages[0]]
            st.session_state.chat_memory = []
            st.rerun()


def process_message(user_input: str):
    _append_message("user", user_input)

    memory_candidate = _extract_memory_candidate(user_input)
    if memory_candidate and memory_candidate not in st.session_state.chat_memory:
        st.session_state.chat_memory.append(memory_candidate)

    credit_data = st.session_state.get("credit_data")
    errors = st.session_state.get("errors_found", [])
    system_prompt = get_system_prompt(credit_data, errors)

    history = st.session_state.chat_messages[-10:]
    api_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in history
        if m["role"] in ("user", "assistant")
    ]

    api_key = _get_api_key()
    if not api_key:
        _append_message(
            "assistant",
            "⚠️ I'm not connected right now because the Anthropic API key is missing. Please add ANTHROPIC_API_KEY to Render environment variables.",
        )
        return

    try:
        from anthropic import Anthropic

        with st.spinner("🤖 Thinking..."):
            client = Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-3-5-sonnet-latest",
                max_tokens=1024,
                system=system_prompt,
                messages=api_messages,
            )

        assistant_reply = response.content[0].text

        lower = user_input.lower()
        if "dispute letter" in lower or "write a dispute" in lower:
            assistant_reply += "\n\n📄 Ready to generate one? Jump to the **Dispute Letters** tab!"
        if "plan" in lower or "next 30 days" in lower or "what should i do" in lower:
            assistant_reply += "\n\n📈 Check the **Credit Plan** tab for your full 90-day action plan!"

    except Exception as e:
        assistant_reply = (
            "⚠️ I'm having trouble connecting right now. Please try again in a moment.\n\n"
            f"*(Error: {str(e)})*"
        )

    _append_message("assistant", assistant_reply)
