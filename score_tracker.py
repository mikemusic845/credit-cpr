"""
Credit Score Tracker for Credit CPR
Uses PostgreSQL (Supabase) for persistent storage
"""

import streamlit as st
from datetime import datetime
import auth  # Uses auth.get_conn()


def log_score(user_id, score, bureau, note=""):
    conn = auth.get_conn()
    c = conn.cursor()
    c.execute(
        'INSERT INTO score_history (user_id, score, bureau, note) VALUES (%s, %s, %s, %s)',
        (user_id, score, bureau, note)
    )
    conn.commit()
    conn.close()


def get_score_history(user_id, bureau=None):
    conn = auth.get_conn()
    c = conn.cursor()
    if bureau and bureau != "All":
        c.execute(
            'SELECT score, bureau, note, logged_at FROM score_history WHERE user_id = %s AND bureau = %s ORDER BY logged_at ASC',
            (user_id, bureau)
        )
    else:
        c.execute(
            'SELECT score, bureau, note, logged_at FROM score_history WHERE user_id = %s ORDER BY logged_at ASC',
            (user_id,)
        )
    rows = c.fetchall()
    conn.close()
    return rows


def get_score_color(score):
    if score >= 800:
        return "#2E8B57", "Exceptional"
    elif score >= 740:
        return "#7CB342", "Very Good"
    elif score >= 670:
        return "#FFC107", "Good"
    elif score >= 580:
        return "#FF9800", "Fair"
    else:
        return "#F44336", "Poor"


def show_score_tracker():
    user_id = st.session_state.user['id']

    st.header("📊 Credit Score Tracker")
    st.caption("Log your scores from all three bureaus and track your progress over time.")

    with st.expander("➕ Log New Score", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            bureau = st.selectbox("Bureau", ["Equifax", "Experian", "TransUnion"], key="score_bureau")
        with col2:
            score = st.number_input("Score", min_value=300, max_value=850, value=650, step=1, key="score_input")
        with col3:
            note = st.text_input("Note (optional)", placeholder="e.g. After dispute resolved", key="score_note")

        color, label = get_score_color(score)
        st.markdown(f"""
        <div style='background: {color}20; border-left: 4px solid {color};
                    padding: 0.75rem 1rem; border-radius: 6px; margin: 0.5rem 0;'>
            <strong style='color: {color}; font-size: 1.2rem;'>{score}</strong>
            <span style='color: #666; margin-left: 0.5rem;'>— {label}</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("💾 Save Score", type="primary", use_container_width=True):
            log_score(user_id, score, bureau, note)
            st.success(f"✅ {bureau} score of {score} saved!")
            st.rerun()

    history = get_score_history(user_id)

    if not history:
        st.info("👆 Log your first score above to start tracking your progress!")
        return

    st.subheader("📈 Current Scores")
    bureaus = ["Equifax", "Experian", "TransUnion"]
    latest = {}
    for row in reversed(history):
        b = row[1]
        if b not in latest:
            latest[b] = row

    score_cols = st.columns(3)
    for i, bureau_name in enumerate(bureaus):
        with score_cols[i]:
            if bureau_name in latest:
                s = latest[bureau_name][0]
                color, label = get_score_color(s)
                logged_at = latest[bureau_name][3]
                date_str = logged_at.strftime("%Y-%m-%d") if hasattr(logged_at, 'strftime') else str(logged_at)[:10]
                st.markdown(f"""
                <div style='background: {color}15; border: 2px solid {color};
                            border-radius: 12px; padding: 1.5rem; text-align: center;'>
                    <div style='font-size: 0.85rem; color: #666; margin-bottom: 0.25rem;'>{bureau_name}</div>
                    <div style='font-size: 2.5rem; font-weight: bold; color: {color};'>{s}</div>
                    <div style='font-size: 0.85rem; color: {color};'>{label}</div>
                    <div style='font-size: 0.75rem; color: #999; margin-top: 0.5rem;'>{date_str}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background: #f5f5f5; border: 2px dashed #ccc;
                            border-radius: 12px; padding: 1.5rem; text-align: center;'>
                    <div style='font-size: 0.85rem; color: #666;'>{bureau_name}</div>
                    <div style='font-size: 1.5rem; color: #ccc; margin: 0.5rem 0;'>—</div>
                    <div style='font-size: 0.75rem; color: #999;'>Not logged yet</div>
                </div>
                """, unsafe_allow_html=True)

    st.subheader("📉 Score History")
    filter_bureau = st.selectbox("Filter by bureau", ["All", "Equifax", "Experian", "TransUnion"], key="filter_bureau")
    filtered = get_score_history(user_id, filter_bureau)

    if len(filtered) >= 2:
        first_score = filtered[0][0]
        last_score = filtered[-1][0]
        change = last_score - first_score
        change_symbol = "+" if change >= 0 else ""
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Starting Score", first_score)
        with col2:
            st.metric("Current Score", last_score, delta=f"{change_symbol}{change} pts")
        with col3:
            st.metric("Entries Logged", len(filtered))

    with st.expander("📋 Full History"):
        for row in reversed(filtered):
            score_val, bureau_name, note_text, logged_at = row
            color, label = get_score_color(score_val)
            date_str = logged_at.strftime("%Y-%m-%d") if hasattr(logged_at, 'strftime') else str(logged_at)[:10]
            st.markdown(f"""
            <div style='display: flex; align-items: center; padding: 0.5rem;
                        border-bottom: 1px solid #eee; gap: 1rem;'>
                <span style='color: {color}; font-weight: bold; font-size: 1.1rem; min-width: 50px;'>{score_val}</span>
                <span style='background: {color}20; color: {color}; padding: 2px 8px;
                             border-radius: 4px; font-size: 0.8rem;'>{bureau_name}</span>
                <span style='color: #666; font-size: 0.85rem;'>{date_str}</span>
                <span style='color: #888; font-size: 0.85rem; font-style: italic;'>{note_text or ""}</span>
            </div>
            """, unsafe_allow_html=True)

    with st.expander("📚 Credit Score Ranges Reference"):
        ranges = [
            ("800-850", "Exceptional", "#2E8B57", "Best rates, easiest approvals"),
            ("740-799", "Very Good", "#7CB342", "Above average, great rates"),
            ("670-739", "Good", "#FFC107", "Near or above average"),
            ("580-669", "Fair", "#FF9800", "Below average, higher rates"),
            ("300-579", "Poor", "#F44336", "Difficulty getting approved"),
        ]
        for r, label, color, desc in ranges:
            st.markdown(f"""
            <div style='display: flex; align-items: center; gap: 1rem; padding: 0.4rem 0;'>
                <span style='color: {color}; font-weight: bold; min-width: 90px;'>{r}</span>
                <span style='background: {color}20; color: {color}; padding: 2px 10px;
                             border-radius: 4px; min-width: 100px; text-align: center;'>{label}</span>
                <span style='color: #666; font-size: 0.9rem;'>{desc}</span>
            </div>
            """, unsafe_allow_html=True)
