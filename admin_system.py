"""
Admin System for Credit CPR
Allows admins to:
- Use app for free (unlimited)
- Grant free access to users
- Create discount codes
- Upgrade/downgrade users manually
"""

import streamlit as st
import sqlite3
import auth
import secrets
from datetime import datetime, timedelta

# Admin emails (add your email here)
ADMIN_EMAILS = [
    "mikemusic845@gmail.com",  # CHANGE THIS TO YOUR EMAIL
]

def is_admin(email):
    """Check if user is an admin"""
    return email.lower() in [e.lower() for e in ADMIN_EMAILS]

def init_admin_tables():
    """Initialize admin-related database tables"""
    conn = sqlite3.connect(auth.DB_PATH)
    c = conn.cursor()
    
    # Discount codes table
    c.execute('''
        CREATE TABLE IF NOT EXISTS discount_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            discount_percent INTEGER,
            plan_override TEXT,
            uses_remaining INTEGER,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User overrides table (for manually granted access)
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_overrides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            override_type TEXT NOT NULL,
            reason TEXT,
            granted_by TEXT,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def grant_user_access(user_email, plan='premium', duration_days=None, reason=''):
    """Grant a user free access to a plan"""
    conn = sqlite3.connect(auth.DB_PATH)
    c = conn.cursor()
    
    # Get user
    c.execute('SELECT id FROM users WHERE email = ?', (user_email,))
    user = c.fetchone()
    
    if not user:
        conn.close()
        return False, "User not found"
    
    user_id = user[0]
    
    # Update user's plan
    c.execute('UPDATE users SET plan = ? WHERE id = ?', (plan, user_id))
    
    # Record the override
    expires_at = None
    if duration_days:
        expires_at = datetime.now() + timedelta(days=duration_days)
    
    admin_email = st.session_state.user.get('email', 'system')
    
    c.execute('''INSERT INTO user_overrides 
                 (user_id, override_type, reason, granted_by, expires_at) 
                 VALUES (?, ?, ?, ?, ?)''',
              (user_id, f'plan_{plan}', reason, admin_email, expires_at))
    
    conn.commit()
    conn.close()
    
    return True, f"✅ Granted {plan} access to {user_email}"

def create_discount_code(code, discount_percent=None, plan_override=None, uses=None, days_valid=None):
    """Create a discount code"""
    conn = sqlite3.connect(auth.DB_PATH)
    c = conn.cursor()
    
    expires_at = None
    if days_valid:
        expires_at = datetime.now() + timedelta(days=days_valid)
    
    try:
        c.execute('''INSERT INTO discount_codes 
                     (code, discount_percent, plan_override, uses_remaining, expires_at) 
                     VALUES (?, ?, ?, ?, ?)''',
                  (code.upper(), discount_percent, plan_override, uses, expires_at))
        conn.commit()
        conn.close()
        return True, f"✅ Created discount code: {code.upper()}"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Code already exists"

def apply_discount_code(user_id, code):
    """Apply a discount code to a user"""
    conn = sqlite3.connect(auth.DB_PATH)
    c = conn.cursor()
    
    # Get discount code
    c.execute('''SELECT id, discount_percent, plan_override, uses_remaining, expires_at 
                 FROM discount_codes WHERE code = ?''', (code.upper(),))
    discount = c.fetchone()
    
    if not discount:
        conn.close()
        return False, "Invalid code"
    
    discount_id, discount_percent, plan_override, uses_remaining, expires_at = discount
    
    # Check if expired
    if expires_at and datetime.fromisoformat(expires_at) < datetime.now():
        conn.close()
        return False, "Code expired"
    
    # Check uses remaining
    if uses_remaining is not None and uses_remaining <= 0:
        conn.close()
        return False, "Code has been fully used"
    
    # Apply the discount/plan
    if plan_override:
        # Grant free access to a plan
        c.execute('UPDATE users SET plan = ? WHERE id = ?', (plan_override, user_id))
        message = f"✅ Applied! You now have {plan_override} access"
    else:
        # TODO: Handle percentage discounts (would integrate with Stripe)
        message = f"✅ {discount_percent}% discount applied"
    
    # Decrement uses
    if uses_remaining is not None:
        c.execute('UPDATE discount_codes SET uses_remaining = uses_remaining - 1 WHERE id = ?', (discount_id,))
    
    conn.commit()
    conn.close()
    
    return True, message

def show_admin_panel():
    """Display admin control panel"""
    if not is_admin(st.session_state.user['email']):
        return
    
    st.markdown("---")
    st.markdown("## 🔧 Admin Panel")
    
    tab1, tab2, tab3 = st.tabs(["Grant Access", "Discount Codes", "User Management"])
    
    with tab1:
        st.markdown("### Grant User Access")
        
        with st.form("grant_access_form"):
            user_email = st.text_input("User Email")
            plan = st.selectbox("Plan", ["free", "basic", "pro", "premium"])
            duration = st.number_input("Duration (days, 0 = permanent)", min_value=0, value=0)
            reason = st.text_input("Reason (optional)")
            
            if st.form_submit_button("Grant Access"):
                if user_email:
                    duration_days = duration if duration > 0 else None
                    success, message = grant_user_access(user_email, plan, duration_days, reason)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
    
    with tab2:
        st.markdown("### Create Discount Code")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Option 1: Percentage Discount**")
            with st.form("discount_form"):
                code = st.text_input("Code", placeholder="SUMMER2024")
                discount = st.number_input("Discount %", min_value=0, max_value=100, value=20)
                uses = st.number_input("Max Uses (0 = unlimited)", min_value=0, value=0)
                days = st.number_input("Valid Days (0 = forever)", min_value=0, value=30)
                
                if st.form_submit_button("Create Discount Code"):
                    if code:
                        uses_val = uses if uses > 0 else None
                        days_val = days if days > 0 else None
                        success, message = create_discount_code(code, discount, None, uses_val, days_val)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
        
        with col2:
            st.markdown("**Option 2: Free Access Code**")
            with st.form("free_access_form"):
                code2 = st.text_input("Code", placeholder="FREEPRO", key="code2")
                plan2 = st.selectbox("Grant Plan", ["basic", "pro", "premium"])
                uses2 = st.number_input("Max Uses (0 = unlimited)", min_value=0, value=100, key="uses2")
                days2 = st.number_input("Valid Days (0 = forever)", min_value=0, value=30, key="days2")
                
                if st.form_submit_button("Create Free Access Code"):
                    if code2:
                        uses_val = uses2 if uses2 > 0 else None
                        days_val = days2 if days2 > 0 else None
                        success, message = create_discount_code(code2, None, plan2, uses_val, days_val)
                        if success:
                            st.success(message)
                            st.info(f"Share this code: **{code2.upper()}**")
                        else:
                            st.error(message)
    
    with tab3:
        st.markdown("### User Management")
        
        # Show all users
        conn = sqlite3.connect(auth.DB_PATH)
        c = conn.cursor()
        c.execute('SELECT email, plan, reports_analyzed, created_at FROM users ORDER BY created_at DESC LIMIT 50')
        users = c.fetchall()
        conn.close()
        
        if users:
            st.markdown(f"**Total Users: {len(users)}**")
            
            for user in users:
                email, plan, reports, created = user
                with st.expander(f"{email} - {plan} plan"):
                    st.write(f"Reports Analyzed: {reports}")
                    st.write(f"Joined: {created}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("Make Free", key=f"free_{email}"):
                            grant_user_access(email, 'free', reason='Admin override')
                            st.rerun()
                    with col2:
                        if st.button("Make Basic", key=f"basic_{email}"):
                            grant_user_access(email, 'basic', reason='Admin override')
                            st.rerun()
                    with col3:
                        if st.button("Make Pro", key=f"pro_{email}"):
                            grant_user_access(email, 'pro', reason='Admin override')
                            st.rerun()

def show_discount_code_input():
    """Show discount code input for users"""
    if st.session_state.user['plan'] == 'free':
        with st.expander("💎 Have a discount code?"):
            with st.form("apply_code_form"):
                code = st.text_input("Enter code", placeholder="SUMMER2024")
                if st.form_submit_button("Apply Code"):
                    if code:
                        user_id = st.session_state.user['id']
                        success, message = apply_discount_code(user_id, code)
                        if success:
                            st.success(message)
                            # Reload user data
                            st.session_state.user['plan'] = 'premium'  # Or whatever plan was granted
                            st.rerun()
                        else:
                            st.error(message)

# Initialize tables on import
init_admin_tables()
