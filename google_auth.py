"""
Google OAuth for Streamlit - Working Implementation
Uses streamlit-oauth for proper Google Sign-In
"""

import streamlit as st
import requests
import os
from urllib.parse import urlencode

# Google OAuth Configuration
try:
    GOOGLE_CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
except:
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

# OAuth URLs
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# Your app URLs (change for production)
REDIRECT_URI = "http://localhost:8501"  # Change to your domain
# For production: REDIRECT_URI = "https://credit-cpr.onrender.com"

def get_google_auth_url():
    """Generate Google OAuth URL"""
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

def exchange_code_for_token(code):
    """Exchange authorization code for access token"""
    data = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    
    response = requests.post(GOOGLE_TOKEN_URL, data=data)
    return response.json()

def get_user_info(access_token):
    """Get user info from Google"""
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(GOOGLE_USER_INFO_URL, headers=headers)
    return response.json()

def handle_google_callback():
    """Handle OAuth callback from Google"""
    # Check if we have a code in the URL
    params = st.query_params
    
    if 'code' in params:
        code = params['code']
        
        try:
            # Exchange code for token
            token_data = exchange_code_for_token(code)
            
            if 'access_token' in token_data:
                # Get user info
                user_info = get_user_info(token_data['access_token'])
                
                # Create or login user
                email = user_info.get('email')
                name = user_info.get('name', '')
                
                if email:
                    # Check if user exists or create new user
                    import auth
                    import sqlite3
                    
                    conn = sqlite3.connect(auth.DB_PATH)
                    c = conn.cursor()
                    
                    # Check if user exists
                    c.execute('SELECT id, email, plan, reports_analyzed, disputes_purchased FROM users WHERE email = ?', (email,))
                    user = c.fetchone()
                    
                    if user:
                        # User exists - log them in
                        user_data = {
                            'id': user[0],
                            'email': user[1],
                            'plan': user[2],
                            'reports_analyzed': user[3],
                            'disputes_purchased': user[4]
                        }
                        st.session_state.authenticated = True
                        st.session_state.user = user_data
                        st.success(f"✅ Signed in with Google as {email}")
                    else:
                        # Create new user
                        import secrets
                        random_password = secrets.token_urlsafe(32)
                        password_hash = auth.hash_password(random_password)
                        
                        c.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)', (email, password_hash))
                        user_id = c.lastrowid
                        conn.commit()
                        
                        user_data = {
                            'id': user_id,
                            'email': email,
                            'plan': 'free',
                            'reports_analyzed': 0,
                            'disputes_purchased': 0
                        }
                        st.session_state.authenticated = True
                        st.session_state.user = user_data
                        st.success(f"✅ Account created with Google! Welcome {name}!")
                    
                    conn.close()
                    
                    # Clear the code from URL
                    st.query_params.clear()
                    st.rerun()
                else:
                    st.error("Could not get email from Google")
            else:
                st.error("Failed to get access token from Google")
                
        except Exception as e:
            st.error(f"Error during Google sign-in: {str(e)}")
        
        # Clear the code parameter
        st.query_params.clear()

def show_google_login_button():
    """Show Google Sign-In button"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        return
    
    # Custom styled Google button
    google_auth_url = get_google_auth_url()
    
    st.markdown(f"""
    <div style='text-align: center; margin: 20px 0;'>
        <a href='{google_auth_url}' target='_self' style='text-decoration: none;'>
            <div style='
                display: inline-flex;
                align-items: center;
                justify-content: center;
                padding: 12px 24px;
                background: white;
                border: 2px solid #ddd;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 500;
                color: #333;
                transition: all 0.2s;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            '>
                <svg width="20" height="20" viewBox="0 0 20 20" style="margin-right: 12px;">
                    <path fill="#4285F4" d="M19.6 10.23c0-.82-.1-1.42-.25-2.05H10v3.72h5.5c-.15.96-.74 2.31-2.04 3.22v2.45h3.16c1.89-1.73 2.98-4.3 2.98-7.34z"/>
                    <path fill="#34A853" d="M13.46 15.13c-.83.59-1.96 1-3.46 1-2.64 0-4.88-1.74-5.68-4.15H1.07v2.52C2.72 17.75 6.09 20 10 20c2.7 0 4.96-.89 6.62-2.42l-3.16-2.45z"/>
                    <path fill="#FBBC05" d="M3.99 10c0-.69.12-1.35.32-1.97V5.51H1.07A9.973 9.973 0 000 10c0 1.61.39 3.14 1.07 4.49l3.24-2.52c-.2-.62-.32-1.28-.32-1.97z"/>
                    <path fill="#EA4335" d="M10 3.88c1.88 0 3.13.81 3.85 1.48l2.84-2.76C14.96.99 12.7 0 10 0 6.09 0 2.72 2.25 1.07 5.51l3.24 2.52C5.12 5.62 7.36 3.88 10 3.88z"/>
                </svg>
                Sign in with Google
            </div>
        </a>
    </div>
    
    <div style='text-align: center; margin: 20px 0; color: #666;'>
        <span style='background: white; padding: 0 10px; position: relative; z-index: 1;'>or</span>
        <hr style='margin-top: -12px; border: 1px solid #ddd;'>
    </div>
    """, unsafe_allow_html=True)

def show_login_page_with_google():
    """Display login/signup page with Google Auth"""
    
    # Handle Google OAuth callback
    handle_google_callback()
    
    st.markdown("## Welcome to Credit CPR")
    st.write("Sign in to access your AI-powered credit repair assistant")
    
    # Google Sign-In button
    show_google_login_button()
    
    # Regular email/password tabs
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
                    import auth
                    success, user_data = auth.authenticate_user(email, password)
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
                    import auth
                    success, message = auth.create_user(new_email, new_password)
                    if success:
                        st.success("✅ Account created! Please sign in.")
                    else:
                        st.error(f"❌ {message}")
