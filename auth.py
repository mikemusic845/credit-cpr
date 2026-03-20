"""
Authentication System for Credit CPR
Handles user signup, login, and session management
"""

import streamlit as st
import sqlite3
import hashlib
import secrets
from datetime import datetime
import os

# Database setup
DB_PATH = "users.db"

def init_database():
    """Initialize the user database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            plan TEXT DEFAULT 'free',
            reports_analyzed INTEGER DEFAULT 0,
            disputes_purchased INTEGER DEFAULT 0
        )
    ''')
    
    # Analysis history table
    c.execute('''
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            report_name TEXT,
            errors_found INTEGER,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Dispute letters table
    c.execute('''
        CREATE TABLE IF NOT EXISTS dispute_letters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            bureau TEXT,
            error_description TEXT,
            status TEXT DEFAULT 'draft',
            purchased BOOLEAN DEFAULT 0,
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

def create_user(email: str, password: str) -> tuple[bool, str]:
    """Create a new user account"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        password_hash = hash_password(password)
        c.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)', (email, password_hash))
        
        conn.commit()
        conn.close()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        return False, "Email already exists"
    except Exception as e:
        return False, f"Error: {str(e)}"

def authenticate_user(email: str, password: str) -> tuple[bool, dict]:
    """Authenticate user and return user data"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('SELECT id, email, password_hash, plan, reports_analyzed, disputes_purchased FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()
        
        if user and verify_password(password, user[2]):
            user_data = {
                'id': user[0],
                'email': user[1],
                'plan': user[3],
                'reports_analyzed': user[4],
                'disputes_purchased': user[5]
            }
            return True, user_data
        return False, {}
    except Exception as e:
        return False, {}

def get_user_stats(user_id: int) -> dict:
    """Get user statistics"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get analysis count
    c.execute('SELECT COUNT(*) FROM analysis_history WHERE user_id = ?', (user_id,))
    analyses = c.fetchone()[0]
    
    # Get dispute count
    c.execute('SELECT COUNT(*) FROM dispute_letters WHERE user_id = ? AND purchased = 1', (user_id,))
    disputes = c.fetchone()[0]
    
    # Get user plan
    c.execute('SELECT plan, reports_analyzed, disputes_purchased FROM users WHERE id = ?', (user_id,))
    user_data = c.fetchone()
    
    conn.close()
    
    return {
        'total_analyses': analyses,
        'total_disputes': disputes,
        'plan': user_data[0],
        'reports_analyzed': user_data[1],
        'disputes_purchased': user_data[2]
    }

def can_analyze_report(user_id: int) -> tuple[bool, str]:
    """Check if user can analyze another report"""
    stats = get_user_stats(user_id)
    
    if stats['plan'] == 'premium':
        return True, "Unlimited analyses"
    
    # Free tier: 1 report only
    if stats['reports_analyzed'] >= 1:
        return False, "Free tier limit reached (1 report). Upgrade for unlimited analyses."
    
    return True, f"You have {1 - stats['reports_analyzed']} analysis remaining"

def record_analysis(user_id: int, report_name: str, errors_found: int):
    """Record a credit report analysis"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Add to history
    c.execute('INSERT INTO analysis_history (user_id, report_name, errors_found) VALUES (?, ?, ?)',
              (user_id, report_name, errors_found))
    
    # Update user's report count
    c.execute('UPDATE users SET reports_analyzed = reports_analyzed + 1 WHERE id = ?', (user_id,))
    
    conn.commit()
    conn.close()

def save_dispute_letter(user_id: int, bureau: str, error_description: str) -> int:
    """Save a dispute letter (not purchased yet)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('INSERT INTO dispute_letters (user_id, bureau, error_description) VALUES (?, ?, ?)',
              (user_id, bureau, error_description))
    
    letter_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return letter_id

def purchase_dispute_letter(user_id: int, letter_id: int):
    """Mark dispute letter as purchased"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('UPDATE dispute_letters SET purchased = 1, status = ? WHERE id = ? AND user_id = ?',
              ('ready', letter_id, user_id))
    c.execute('UPDATE users SET disputes_purchased = disputes_purchased + 1 WHERE id = ?', (user_id,))
    
    conn.commit()
    conn.close()

def get_user_disputes(user_id: int):
    """Get all dispute letters for a user"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''SELECT id, bureau, error_description, status, purchased, created_at 
                 FROM dispute_letters WHERE user_id = ? ORDER BY created_at DESC''', (user_id,))
    
    disputes = c.fetchall()
    conn.close()
    
    return disputes

# Streamlit Auth UI Components
def show_login_page():
    """Display login/signup page with Google Auth"""
    try:
        from google_auth import show_login_page_with_google
        show_login_page_with_google()
    except ImportError:
        # Fallback to regular login if Google auth not available
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
    stats = get_user_stats(user['id'])
    
    with st.sidebar:
        st.markdown(f"### 👤 {user['email']}")
        
        # Plan badge
        if stats['plan'] == 'premium':
            st.success("⭐ Premium Plan")
        else:
            st.info("📦 Free Tier")
        
        st.markdown("---")
        
        # Usage stats
        st.markdown("**📊 Your Usage**")
        
        if stats['plan'] == 'free':
            st.write(f"Reports Analyzed: {stats['reports_analyzed']}/1")
            if stats['reports_analyzed'] >= 1:
                st.warning("⚠️ Free tier limit reached")
                
                # ADD THIS: Upgrade button
                import stripe_integration
                if st.button("🚀 Upgrade Now", use_container_width=True, type="primary"):
                    st.session_state.show_upgrade = True
                    st.rerun()
        else:
            st.write(f"Reports Analyzed: {stats['reports_analyzed']}")
            
            # ADD THIS: Manage subscription button
            import stripe_integration
            if st.button("🔧 Manage Subscription", use_container_width=True):
                st.session_state.show_manage = True
                st.rerun()
        
        st.write(f"Disputes Purchased: {stats['disputes_purchased']}")
        
        st.markdown("---")
        
        # Logout button
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
init_database()
