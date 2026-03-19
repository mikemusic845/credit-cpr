"""
AI Chat Assistant for Credit CPR
Answers credit questions, explains FCRA rights, gives personalized advice
"""

import streamlit as st
import os
from datetime import datetime


def get_system_prompt(credit_data=None, errors=None):
    """Build system prompt with user's credit context if available"""
    base_prompt = """You are Credit CPR's AI Credit Specialist — a knowledgeable, friendly expert in:
- The Fair Credit Reporting Act (FCRA) and consumer rights
- Credit scoring (FICO, VantageScore) and what affects scores
- Dispute strategies and processes with Equifax, Experian, and TransUnion
- Debt validation, statute of limitations, and collections
- Credit building strategies (secured cards, authorized users, credit mix)
- Bankruptcy, charge-offs, collections, and how long items stay on reports

Your personality:
- Warm, encouraging, and empowering — never condescending
- Use plain English, avoid jargon unless you explain it
- Give specific, actionable advice
- Always remind users you provide educational info, not legal advice
- Be concise but thorough — bullet points when helpful

IMPORTANT RULES:
- Never tell users to lie or misrepresent information
- Never promise specific score increases
- Always recommend consulting an attorney for complex legal matters
- This is educational information under FCRA Section 609"""

    if credit_data and errors:
        context = f"""

CURRENT USER CREDIT CONTEXT:
- Accounts on file: {len(credit_data.get('accounts', []))}
- Negative items: {len(credit_data.get('negative_items', []))}
- Public records: {len(credit_data.get('public_records', []))}
- Errors identified: {len(errors)}
- Error categories: {', '.join(set(e.get('category', '') for e in errors[:5]))}

Use this context to give personalized answers when relevant."""
        return base_prompt + context

    return base_prompt


def show_chat_assistant():
    """Main chat assistant UI"""

    st.header("💬 AI Credit Specialist")
    st.caption("Ask me anything about credit repair, FCRA rights, dispute strategies, and credit building.")

    # Initialize chat history
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": "👋 Hi! I'm your Credit CPR AI Specialist. I can help you understand your credit rights, explain dispute strategies, answer FCRA questions, and guide you on building credit.\n\nWhat can I help you with today?",
                "timestamp": datetime.now().strftime("%I:%M %p")
            }
        ]

    # Quick question buttons
    st.markdown("**Quick Questions:**")
    quick_cols = st.columns(3)
    quick_questions = [
        "How do I dispute an error?",
        "How long do negatives stay on my report?",
        "What's the fastest way to build credit?",
        "What is a 609 dispute letter?",
        "Can I remove a collection account?",
        "What rights do I have under FCRA?",
    ]

    for i, question in enumerate(quick_questions):
        col = quick_cols[i % 3]
        with col:
            if st.button(question, key=f"quick_{i}", use_container_width=True):
                st.session_state.pending_message = question

    st.divider()

    # Chat message display
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_messages:
            if msg["role"] == "assistant":
                with st.chat_message("assistant", avatar="🛡️"):
                    st.markdown(msg["content"])
                    st.caption(msg.get("timestamp", ""))
            else:
                with st.chat_message("user", avatar="👤"):
                    st.markdown(msg["content"])
                    st.caption(msg.get("timestamp", ""))

    # Handle pending message from quick buttons
    if 'pending_message' in st.session_state:
        user_input = st.session_state.pending_message
        del st.session_state.pending_message
        process_message(user_input)
        st.rerun()

    # Chat input
    user_input = st.chat_input("Ask a credit question...")
    if user_input:
        process_message(user_input)
        st.rerun()

    # Clear chat button
    if len(st.session_state.chat_messages) > 1:
        if st.button("🗑️ Clear Chat", use_container_width=False):
            st.session_state.chat_messages = [st.session_state.chat_messages[0]]
            st.rerun()


def process_message(user_input):
    """Process user message and get AI response"""
    # Add user message
    st.session_state.chat_messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime("%I:%M %p")
    })

    # Build messages for API
    credit_data = st.session_state.get('credit_data')
    errors = st.session_state.get('errors_found', [])
    system_prompt = get_system_prompt(credit_data, errors)

    # Build conversation history (last 10 messages to save tokens)
    history = st.session_state.chat_messages[-10:]
    api_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in history
        if m["role"] in ("user", "assistant")
    ]

    # Call Anthropic API
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=system_prompt,
            messages=api_messages
        )

        assistant_reply = response.content[0].text

    except Exception as e:
        assistant_reply = f"⚠️ I'm having trouble connecting right now. Please try again in a moment.\n\n*(Error: {str(e)})*"

    # Add assistant response
    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": assistant_reply,
        "timestamp": datetime.now().strftime("%I:%M %p")
    })
