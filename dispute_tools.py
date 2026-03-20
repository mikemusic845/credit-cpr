"""
Dispute Email Sender & Reminder System for Credit CPR
Uses PostgreSQL (Supabase) for persistent storage
"""

import streamlit as st
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
import auth  # Uses auth.get_conn()

BUREAU_EMAILS = {
    "Equifax": "disputeinfo@equifax.com",
    "Experian": "disputes@experian.com",
    "TransUnion": "transunion@transunion.com"
}

BUREAU_ADDRESSES = {
    "Equifax": "Equifax Information Services LLC\nP.O. Box 740256\nAtlanta, GA 30374-0256",
    "Experian": "Experian\nP.O. Box 4500\nAllen, TX 75013",
    "TransUnion": "TransUnion LLC Consumer Dispute Center\nP.O. Box 2000\nChester, PA 19016"
}


def save_reminder(user_id, bureau, description, sent_date, follow_up_date):
    conn = auth.get_conn()
    c = conn.cursor()
    c.execute(
        '''INSERT INTO dispute_reminders
           (user_id, bureau, dispute_description, sent_date, follow_up_date)
           VALUES (%s, %s, %s, %s, %s) RETURNING id''',
        (user_id, bureau, description, sent_date, follow_up_date)
    )
    reminder_id = c.fetchone()[0]
    conn.commit()
    conn.close()
    return reminder_id


def get_reminders(user_id):
    conn = auth.get_conn()
    c = conn.cursor()
    c.execute(
        '''SELECT id, bureau, dispute_description, sent_date, follow_up_date, status, notes
           FROM dispute_reminders WHERE user_id = %s ORDER BY follow_up_date ASC''',
        (user_id,)
    )
    rows = c.fetchall()
    conn.close()
    return rows


def update_reminder_status(reminder_id, status, notes=""):
    conn = auth.get_conn()
    c = conn.cursor()
    c.execute(
        'UPDATE dispute_reminders SET status = %s, notes = %s WHERE id = %s',
        (status, notes, reminder_id)
    )
    conn.commit()
    conn.close()


def send_dispute_email(sender_email, sender_password, recipient_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        return True, "Email sent successfully!"
    except smtplib.SMTPAuthenticationError:
        return False, "Authentication failed. Use a Gmail App Password, not your regular password."
    except Exception as e:
        return False, str(e)


def show_email_sender():
    st.header("📬 Email Dispute Letters")
    st.caption("Send your dispute letters directly to credit bureaus via email.")

    if not st.session_state.get('analysis_complete') or not st.session_state.get('errors_found'):
        st.info("👈 Please upload and analyze a credit report first to generate dispute letters.")
        return

    with st.expander("⚙️ Email Setup Instructions", expanded=False):
        st.markdown("""
        **To send emails, you need a Gmail App Password:**
        1. Go to your Google Account → Security
        2. Enable **2-Step Verification**
        3. Go to **App Passwords** → Create one for "Mail"
        4. Copy the 16-character password and paste below

        ⚠️ Never use your regular Gmail password — always use an App Password.
        Your credentials are never stored.
        """)

    col1, col2 = st.columns(2)
    with col1:
        sender_email = st.text_input("Your Gmail Address", placeholder="you@gmail.com", key="sender_email")
    with col2:
        sender_password = st.text_input("Gmail App Password", type="password", placeholder="16-character app password", key="sender_password")

    bureau = st.selectbox("Select Bureau", ["Equifax", "Experian", "TransUnion"], key="email_bureau")
    error_options = [
        f"{e.get('category', 'Error')} - {e.get('description', 'Unknown')[:60]}"
        for e in st.session_state.errors_found
    ]
    selected_idx = st.selectbox("Select Error to Dispute", range(len(error_options)),
                                 format_func=lambda x: error_options[x], key="email_error_idx")
    selected_error = st.session_state.errors_found[selected_idx]

    st.info(f"📮 **{bureau} Mailing Address:**\n\n{BUREAU_ADDRESSES[bureau]}")

    if st.button("✍️ Generate Letter for Email", type="primary", use_container_width=True):
        if not st.session_state.user_info.get('name'):
            st.warning("Please fill in your personal information in the sidebar first.")
        else:
            from app import generate_dispute_letter, get_anthropic_client
            client = get_anthropic_client()
            with st.spinner("✍️ Generating dispute letter..."):
                letter_text = generate_dispute_letter(
                    selected_error,
                    st.session_state.user_info,
                    bureau,
                    client
                )
            st.session_state.email_letter_text = letter_text
            st.session_state.email_bureau = bureau
            st.session_state.email_error_desc = selected_error.get('description', 'Dispute')
            st.success("✅ Letter ready!")

    if st.session_state.get('email_letter_text'):
        letter_text = st.session_state.email_letter_text
        bureau_used = st.session_state.get('email_bureau', bureau)
        st.text_area("📄 Letter Preview (editable)", letter_text, height=300, key="email_letter_preview")

        subject = f"Credit Report Dispute - {st.session_state.user_info.get('name', 'Consumer')}"
        col1, col2 = st.columns(2)
        with col1:
            send_to_bureau = st.checkbox(f"Send to {bureau_used} ({BUREAU_EMAILS[bureau_used]})", value=True)
        with col2:
            send_copy_to_self = st.checkbox("Send copy to myself", value=True)

        if st.button("📤 Send Dispute Letter", type="primary", use_container_width=True):
            if not sender_email or not sender_password:
                st.error("Please enter your Gmail credentials above.")
            else:
                final_letter = st.session_state.get('email_letter_preview', letter_text)
                success_count = 0

                with st.spinner("📤 Sending..."):
                    if send_to_bureau:
                        ok, msg = send_dispute_email(sender_email, sender_password, BUREAU_EMAILS[bureau_used], subject, final_letter)
                        if ok:
                            success_count += 1
                            st.success(f"✅ Sent to {bureau_used}!")
                        else:
                            st.error(f"❌ Failed: {msg}")

                    if send_copy_to_self:
                        ok, msg = send_dispute_email(sender_email, sender_password, sender_email, f"[COPY] {subject}", final_letter)
                        if ok:
                            success_count += 1
                            st.success("✅ Copy sent to you!")
                        else:
                            st.error(f"❌ Failed to send copy: {msg}")

                if success_count > 0:
                    sent_date = datetime.now().strftime("%Y-%m-%d")
                    follow_up_date = (datetime.now() + timedelta(days=35)).strftime("%Y-%m-%d")
                    save_reminder(st.session_state.user['id'], bureau_used,
                                  st.session_state.get('email_error_desc', 'Dispute'), sent_date, follow_up_date)
                    st.info(f"🔔 Follow-up reminder set for {follow_up_date} (35 days from today)")


def show_reminders():
    user_id = st.session_state.user['id']

    st.header("🔔 Dispute Follow-Up Reminders")
    st.caption("Bureaus have 30 days to investigate — follow up if you don't hear back.")

    with st.expander("➕ Add Manual Reminder"):
        col1, col2 = st.columns(2)
        with col1:
            r_bureau = st.selectbox("Bureau", ["Equifax", "Experian", "TransUnion"], key="r_bureau")
            r_description = st.text_input("Dispute Description", placeholder="e.g. Incorrect late payment on Chase", key="r_desc")
        with col2:
            r_sent = st.date_input("Date Letter Sent", datetime.now(), key="r_sent")
            r_followup = st.date_input("Follow-Up Date", datetime.now() + timedelta(days=35), key="r_followup")

        if st.button("💾 Save Reminder", use_container_width=True):
            if r_description:
                save_reminder(user_id, r_bureau, r_description,
                              r_sent.strftime("%Y-%m-%d"), r_followup.strftime("%Y-%m-%d"))
                st.success("✅ Reminder saved!")
                st.rerun()
            else:
                st.warning("Please enter a dispute description.")

    reminders = get_reminders(user_id)

    if not reminders:
        st.info("No reminders yet. Send a dispute letter and a reminder will be created automatically!")
        return

    today = datetime.now().date()
    overdue = [r for r in reminders if r[5] == 'pending' and datetime.strptime(str(r[4])[:10], "%Y-%m-%d").date() < today]
    upcoming = [r for r in reminders if r[5] == 'pending' and datetime.strptime(str(r[4])[:10], "%Y-%m-%d").date() >= today]
    completed = [r for r in reminders if r[5] != 'pending']

    if overdue:
        st.error(f"⚠️ {len(overdue)} Overdue Follow-Up(s)")
        for r in overdue:
            show_reminder_card(r, "overdue")
    if upcoming:
        st.subheader(f"📅 Upcoming ({len(upcoming)})")
        for r in upcoming:
            show_reminder_card(r, "upcoming")
    if completed:
        with st.expander(f"✅ Completed ({len(completed)})"):
            for r in completed:
                show_reminder_card(r, "completed")


def show_reminder_card(reminder, reminder_type):
    r_id, bureau, description, sent_date, follow_up_date, status, notes = reminder
    today = datetime.now().date()
    follow_up = datetime.strptime(str(follow_up_date)[:10], "%Y-%m-%d").date()
    days_until = (follow_up - today).days

    if reminder_type == "overdue":
        border_color, icon = "#F44336", "🔴"
        days_text = f"{abs(days_until)} days overdue"
    elif reminder_type == "upcoming":
        border_color = "#FF9800" if days_until <= 7 else "#2E8B57"
        icon = "🟡" if days_until <= 7 else "🟢"
        days_text = f"in {days_until} days" if days_until > 0 else "today"
    else:
        border_color, icon = "#9E9E9E", "✅"
        days_text = status

    st.markdown(f"""
    <div style='border-left: 4px solid {border_color}; padding: 0.75rem 1rem;
                background: {border_color}10; border-radius: 0 8px 8px 0; margin: 0.5rem 0;'>
        <div style='display: flex; justify-content: space-between;'>
            <strong>{icon} {bureau}</strong> — {description}
            <span style='font-size: 0.8rem; color: #666;'>{days_text}</span>
        </div>
        <div style='font-size: 0.8rem; color: #888; margin-top: 0.25rem;'>
            Sent: {str(sent_date)[:10]} | Follow-up: {str(follow_up_date)[:10]}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if reminder_type != "completed":
        col1, col2, col3 = st.columns([2, 1, 1])
        with col2:
            if st.button("✅ Resolved", key=f"resolve_{r_id}", use_container_width=True):
                update_reminder_status(r_id, "resolved")
                st.rerun()
        with col3:
            if st.button("❌ No Response", key=f"no_response_{r_id}", use_container_width=True):
                update_reminder_status(r_id, "no_response")
                st.rerun()
