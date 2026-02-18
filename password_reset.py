"""
Password Reset System for Credit CPR
Handles forgot password flow with email verification
"""

import streamlit as st
import sqlite3
import auth
import secrets
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def init_reset_table():
    """Initialize password reset tokens table"""
    conn = sqlite3.connect(auth.DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def generate_reset_token(email):
    """Generate a password reset token for a user"""
    conn = sqlite3.connect(auth.DB_PATH)
    c = conn.cursor()
    
    # Check if user exists
    c.execute('SELECT id FROM users WHERE email = ?', (email,))
    user = c.fetchone()
    
    if not user:
        conn.close()
        return None, "No account found with that email"
    
    user_id = user[0]
    
    # Generate token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=1)  # Token expires in 1 hour
    
    # Save token
    c.execute('INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (?, ?, ?)',
              (user_id, token, expires_at))
    
    conn.commit()
    conn.close()
    
    return token, None

def verify_reset_token(token):
    """Verify a password reset token"""
    conn = sqlite3.connect(auth.DB_PATH)
    c = conn.cursor()
    
    c.execute('''SELECT user_id, expires_at, used FROM password_reset_tokens 
                 WHERE token = ?''', (token,))
    result = c.fetchone()
    
    conn.close()
    
    if not result:
        return None, "Invalid reset token"
    
    user_id, expires_at, used = result
    
    if used:
        return None, "This reset link has already been used"
    
    if datetime.fromisoformat(expires_at) < datetime.now():
        return None, "This reset link has expired"
    
    return user_id, None

def reset_password(token, new_password):
    """Reset password using a valid token"""
    user_id, error = verify_reset_token(token)
    
    if error:
        return False, error
    
    # Hash new password
    password_hash = auth.hash_password(new_password)
    
    conn = sqlite3.connect(auth.DB_PATH)
    c = conn.cursor()
    
    # Update password
    c.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
    
    # Mark token as used
    c.execute('UPDATE password_reset_tokens SET used = 1 WHERE token = ?', (token,))
    
    conn.commit()
    conn.close()
    
    return True, "Password reset successfully!"

def send_reset_email(email, token):
    """Send password reset email (placeholder - requires email configuration)"""
    # For now, just return the reset link
    # In production, you'd send this via SendGrid, Mailgun, etc.
    
    reset_url = f"https://credit-cpr.onrender.com/?reset_token={token}"
    # For localhost: f"http://localhost:8501/?reset_token={token}"
    
    return reset_url

def show_forgot_password_link():
    """Show 'Forgot Password?' link on login page"""
    if st.button("🔑 Forgot Password?", key="forgot_password_link", help="Reset your password"):
        st.session_state.show_forgot_password = True
        st.rerun()

def show_forgot_password_form():
    """Show the forgot password form"""
    st.markdown("## Reset Your Password")
    st.write("Enter your email address and we'll send you a reset link.")
    
    with st.form("forgot_password_form"):
        email = st.text_input("Email Address", key="reset_email")
        submit = st.form_submit_button("Send Reset Link", use_container_width=True)
        
        if submit:
            if not email or '@' not in email:
                st.error("Please enter a valid email address")
            else:
                token, error = generate_reset_token(email)
                
                if error:
                    st.warning("If an account exists with this email, a reset link will be sent.")
                    # Don't reveal if email exists or not (security)
                else:
                    reset_url = send_reset_email(email, token)
                    
                    st.success("✅ Password reset link generated!")
                    st.info("**Copy this link to reset your password:**")
                    st.code(reset_url, language=None)
                    st.caption("⚠️ This link expires in 1 hour")
                    
                    # In production with email configured:
                    # st.success("✅ Password reset link sent to your email!")
                    # st.info("Check your inbox and click the link to reset your password.")
    
    if st.button("← Back to Sign In"):
        st.session_state.show_forgot_password = False
        st.rerun()

def show_reset_password_form(token):
    """Show the password reset form"""
    st.markdown("## Set New Password")
    
    # Verify token first
    user_id, error = verify_reset_token(token)
    
    if error:
        st.error(f"❌ {error}")
        st.info("Please request a new password reset link.")
        if st.button("← Back to Sign In"):
            # Clear the token from URL
            st.query_params.clear()
            st.rerun()
        return
    
    with st.form("reset_password_form"):
        new_password = st.text_input("New Password", type="password", key="new_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_new_password")
        
        st.caption("Password must be at least 8 characters")
        
        submit = st.form_submit_button("Reset Password", use_container_width=True)
        
        if submit:
            if len(new_password) < 8:
                st.error("Password must be at least 8 characters")
            elif new_password != confirm_password:
                st.error("Passwords don't match")
            else:
                success, message = reset_password(token, new_password)
                
                if success:
                    st.success("✅ Password reset successfully!")
                    st.info("You can now sign in with your new password.")
                    
                    # Clear the token from URL
                    st.query_params.clear()
                    
                    # Auto-login or redirect to login
                    if st.button("Sign In Now", use_container_width=True):
                        st.rerun()
                else:
                    st.error(f"❌ {message}")

def handle_password_reset_flow():
    """Handle password reset flow on page load"""
    # Check for reset token in URL
    try:
        params = st.query_params
    except AttributeError:
        params = st.experimental_get_query_params()
    
    # Handle both dict and direct access
    reset_token = None
    if isinstance(params, dict):
        reset_token = params.get('reset_token', [None])[0] if 'reset_token' in params else None
    else:
        reset_token = params.get('reset_token', None)
    
    if reset_token:
        show_reset_password_form(reset_token)
        return True
    
    return False

# Initialize table on import
init_reset_table()
