"""
Authentication System for Credit CPR
Uses PostgreSQL (Supabase) for persistent storage
"""

import streamlit as st
import hashlib
import secrets
from datetime import datetime
import os

# Database connection
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL", "")


def get_conn():
    """Get a database connection"""
    return psycopg2.connect(DATABASE_URL, sslmode='require')


def init_database():
    """Initialize the database tables"""
    conn = get_conn()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            plan TEXT DEFAULT 'free',
            reports_analyzed INTEGER DEFAULT 0,
            disputes_purchased INTEGER DEFAULT 0
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS analysis_history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            report_name TEXT,
            errors_found INTEGER,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS dispute_letters (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            bureau TEXT,
            error_description TEXT,
            status TEXT DEFAULT 'draft',
            purchased BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS score_history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            bureau TEXT NOT NULL,
            note TEXT,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS dispute_reminders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            bureau TEXT NOT NULL,
            dispute_description TEXT,
            sent_date TEXT NOT NULL,
            follow_up_date TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt + pwd_hash.hex()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    salt = password_hash[:32]
    stored_hash = password_hash[32:]
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return pwd_hash.hex() == stored_hash


def create_user(email: str, password: str) -> tuple:
    """Create a new user account"""
    try:
        conn = get_conn()
        c = conn.cursor()
        password_hash = hash_password(password)
        c.execute('INSERT INTO users (email, password_hash) VALUES (%s, %s)', (email, password_hash))
        conn.commit()
        conn.close()
        return True, "Account created successfully!"
    except psycopg2.errors.UniqueViolation:
        return False, "Email already exists"
    except Exception as e:
        return False, f"Error: {str(e)}"


def authenticate_user(email: str, password: str) -> tuple:
    """Authenticate user and return user data"""
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute(
            'SELECT id, email, password_hash, plan, reports_analyzed, disputes_purchased FROM users WHERE email = %s',
            (email,)
        )
        user = c.fetchone()
        conn.close()

        if user and verify_password(password, user[2]):
            return True, {
                'id': user[0],
                'email': user[1],
                'plan': user[3],
                'reports_analyzed': user[4],
                'disputes_purchased': user[5]
            }
        return False, {}
    except Exception as e:
        return False, {}


def get_user_stats(user_id: int) -> dict:
    """Get user statistics"""
    conn = get_conn()
    c = conn.cursor()

    c.execute('SELECT COUNT(*) FROM analysis_history WHERE user_id = %s', (user_id,))
    analyses = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM dispute_letters WHERE user_id = %s AND purchased = TRUE', (user_id,))
    disputes = c.fetchone()[0]

    c.execute('SELECT plan, reports_analyzed, disputes_purchased FROM users WHERE id = %s', (user_id,))
    user_data = c.fetchone()
    conn.close()

    return {
        'total_analyses': analyses,
        'total_disputes': disputes,
        'plan': user_data[0],
        'reports_analyzed': user_data[1],
        'disputes_purchased': user_data[2]
    }


def can_analyze_report(user_id: int) -> tuple:
    """Check if user can analyze another report"""
    stats = get_user_stats(user_id)

    if stats['plan'] in ('premium', 'pro', 'basic'):
        return True, "Unlimited analyses"

    if stats['reports_analyzed'] >= 1:
        return False, "Free tier limit reached (1 report). Upgrade for unlimited analyses."

    return True, f"You have {1 - stats['reports_analyzed']} analysis remaining"


def record_analysis(user_id: int, report_name: str, errors_found: int):
    """Record a credit report analysis"""
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        'INSERT INTO analysis_history (user_id, report_name, errors_found) VALUES (%s, %s, %s)',
        (user_id, report_name, errors_found)
    )
    c.execute('UPDATE users SET reports_analyzed = reports_analyzed + 1 WHERE id = %s', (user_id,))
    conn.commit()
    conn.close()


def save_dispute_letter(user_id: int, bureau: str, error_description: str) -> int:
    """Save a dispute letter"""
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        'INSERT INTO dispute_letters (user_id, bureau, error_description) VALUES (%s, %s, %s) RETURNING id',
        (user_id, bureau, error_description)
    )
    letter_id = c.fetchone()[0]
    conn.commit()
    conn.close()
    return letter_id


def purchase_dispute_letter(user_id: int, letter_id: int):
    """Mark dispute letter as purchased"""
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        'UPDATE dispute_letters SET purchased = TRUE, status = %s WHERE id = %s AND user_id = %s',
        ('ready', letter_id, user_id)
    )
    c.execute('UPDATE users SET disputes_purchased = disputes_purchased + 1 WHERE id = %s', (user_id,))
    conn.commit()
    conn.close()


def get_user_disputes(user_id: int):
    """Get all dispute letters for a user"""
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        '''SELECT id, bureau, error_description, status, purchased, created_at
           FROM dispute_letters WHERE user_id = %s ORDER BY created_at DESC''',
        (user_id,)
    )
    disputes = c.fetchall()
    conn.close()
    return disputes


def update_user_plan(user_id: int, plan: str):
    """Update a user's plan"""
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE users SET plan = %s WHERE id = %s', (plan, user_id))
    conn.commit()
    conn.close()
    # Update session state if this is the current user
    if st.session_state.get('user') and st.session_state.user['id'] == user_id:
        st.session_state.user['plan'] = plan


def get_all_users():
    """Get all users (admin only)"""
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id, email, plan, reports_analyzed, disputes_purchased, created_at FROM users ORDER BY created_at DESC')
    users = c.fetchall()
    conn.close()
    return users


# Streamlit Auth UI Components

def show_login_page():
    """Display login/signup page with Google Auth"""
    try:
        from google_auth import show_login_page_with_google
        show_login_page_with_google()
    except ImportError:
        show_login_page_original()


def show_login_page_original():
    """Display login/signup page (original version)"""
    st.markdown("## Welcome to Credit CPR")
    st.write("Sign in to access your AI-powered credit repair assistant")

    tab1, tab2 = st.tabs(["Sign In", "Create Account"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submit = st.form_submit_button("Sign In", use_container_width=True)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔑 Forgot Password?", use_container_width=True):
                st.session_state.show_forgot_password = True
                st.rerun()

        if submit:
            if not email or not password:
                st.error("Please enter both email and password")
            else:
                success, user_data = authenticate_user(email, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user = user_data
                    st.success("✅ Logged in successfully!")
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password")

    with tab2:
        with st.form("signup_form"):
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
            st.caption("Password must be at least 8 characters")
            agree = st.checkbox("I agree that Credit CPR is an educational assistant, not a credit repair service")
            submit = st.form_submit_button("Create Account", use_container_width=True)

        if submit:
            if not agree:
                st.error("Please agree to the terms")
            elif len(new_password) < 8:
                st.error("Password must be at least 8 characters")
            elif new_password != confirm_password:
                st.error("Passwords don't match")
            elif not new_email or '@' not in new_email:
                st.error("Please enter a valid email")
            else:
                success, message = create_user(new_email, new_password)
                if success:
                    st.success("✅ Account created! Please sign in.")
                else:
                    st.error(f"❌ {message}")


def show_user_dashboard():
    """Display user dashboard in sidebar"""
    user = st.session_state.user
    # Always fetch fresh stats from DB
    stats = get_user_stats(user['id'])

    # Keep session state in sync
    st.session_state.user['plan'] = stats['plan']

    with st.sidebar:
        st.markdown(f"### 👤 {user['email']}")

        if stats['plan'] in ('pro', 'premium'):
            st.success("⭐ Pro Plan")
        elif stats['plan'] == 'basic':
            st.info("🔵 Basic Plan")
        else:
            st.info("📦 Free Tier")

        st.markdown("---")
        st.markdown("**📊 Your Usage**")

        if stats['plan'] == 'free':
            st.write(f"Reports Analyzed: {stats['reports_analyzed']}/1")
            if stats['reports_analyzed'] >= 1:
                st.warning("⚠️ Free tier limit reached")
            import stripe_integration
            if st.button("🚀 Upgrade Now", use_container_width=True, type="primary"):
                st.session_state.show_upgrade = True
                st.rerun()
        else:
            st.write(f"Reports Analyzed: {stats['reports_analyzed']}")
            import stripe_integration
            if st.button("🔧 Manage Subscription", use_container_width=True):
                st.session_state.show_manage = True
                st.rerun()

        st.write(f"Disputes Purchased: {stats['disputes_purchased']}")
        st.markdown("---")

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.show_landing = True
            st.rerun()


def require_auth(func):
    """Decorator to require authentication"""
    def wrapper(*args, **kwargs):
        if not st.session_state.get('authenticated', False):
            show_login_page()
            return
        return func(*args, **kwargs)
    return wrapper


# Initialize database on import
try:
    init_database()
except Exception as e:
    st.error(f"Database connection error: {str(e)}")
