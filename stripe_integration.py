"""
Stripe Payment Integration for Credit CPR
Handles subscriptions, checkouts, and webhooks
"""

import streamlit as st
import stripe
import os

# Stripe Configuration
try:
    STRIPE_PUBLISHABLE_KEY = st.secrets.get("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_SECRET_KEY = st.secrets.get("STRIPE_SECRET_KEY", "")
    STRIPE_PRICE_BASIC = st.secrets.get("STRIPE_PRICE_BASIC", "")
    STRIPE_PRICE_PRO = st.secrets.get("STRIPE_PRICE_PRO", "")
except:
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PRICE_BASIC = os.getenv("STRIPE_PRICE_BASIC", "")
    STRIPE_PRICE_PRO = os.getenv("STRIPE_PRICE_PRO", "")

# Set Stripe API key
stripe.api_key = STRIPE_SECRET_KEY

def create_checkout_session(price_id, user_email, success_url, cancel_url):
    """Create a Stripe Checkout session for subscription"""
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=user_email,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=cancel_url,
            metadata={
                'user_email': user_email
            }
        )
        return checkout_session.url, None
    except Exception as e:
        return None, str(e)

def create_customer_portal_session(customer_id, return_url):
    """Create a Stripe Customer Portal session for managing subscription"""
    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return portal_session.url, None
    except Exception as e:
        return None, str(e)

def get_customer_by_email(email):
    """Get Stripe customer by email"""
    try:
        customers = stripe.Customer.list(email=email, limit=1)
        if customers.data:
            return customers.data[0]
        return None
    except Exception as e:
        print(f"Error getting customer: {e}")
        return None

def get_customer_subscription(customer_id):
    """Get active subscription for a customer"""
    try:
        subscriptions = stripe.Subscription.list(
            customer=customer_id,
            status='active',
            limit=1
        )
        if subscriptions.data:
            return subscriptions.data[0]
        return None
    except Exception as e:
        print(f"Error getting subscription: {e}")
        return None

def show_upgrade_options():
    """Display upgrade options for free tier users"""
    st.markdown("### 🚀 Upgrade to Unlock More Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f0f8f0 0%, #e8f5e9 100%); 
        padding: 2rem; border-radius: 15px; border: 2px solid #2E8B57; text-align: center;'>
            <h3 style='color: #1B3A5C;'>🟦 Credit CPR Basic</h3>
            <div style='font-size: 2.5rem; font-weight: bold; color: #2E8B57; margin: 1rem 0;'>
                $19<span style='font-size: 1rem;'>/month</span>
            </div>
            <hr style='border: 1px solid #2E8B57; margin: 1.5rem 0;'>
            <ul style='list-style: none; padding: 0; text-align: left;'>
                <li style='padding: 0.5rem 0;'>✅ Unlimited AI analysis</li>
                <li style='padding: 0.5rem 0;'>✅ Identify errors & violations</li>
                <li style='padding: 0.5rem 0;'>✅ Educational explanations</li>
                <li style='padding: 0.5rem 0;'>✅ Limited dispute templates</li>
                <li style='padding: 0.5rem 0;'>✅ Email support</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔥 Upgrade to Basic - $19/mo", type="primary", use_container_width=True, key="upgrade_basic"):
            start_checkout(STRIPE_PRICE_BASIC, "basic")
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); 
        padding: 2rem; border-radius: 15px; border: 3px solid #2E8B57; 
        box-shadow: 0 4px 15px rgba(46, 139, 87, 0.3); text-align: center;'>
            <div style='background: #2E8B57; color: white; text-align: center; 
            padding: 0.5rem; border-radius: 5px; margin-bottom: 1rem; font-weight: bold;'>
                MOST POPULAR
            </div>
            <h3 style='color: #1B3A5C;'>🟩 Credit CPR Pro</h3>
            <div style='font-size: 2.5rem; font-weight: bold; color: #2E8B57; margin: 1rem 0;'>
                $29<span style='font-size: 1rem;'>/month</span>
            </div>
            <hr style='border: 1px solid #2E8B57; margin: 1.5rem 0;'>
            <ul style='list-style: none; padding: 0; text-align: left;'>
                <li style='padding: 0.5rem 0;'>✅ <strong>Everything in Basic</strong></li>
                <li style='padding: 0.5rem 0;'>✅ Unlimited dispute templates</li>
                <li style='padding: 0.5rem 0;'>✅ Advanced AI insights</li>
                <li style='padding: 0.5rem 0;'>✅ Personalized roadmap</li>
                <li style='padding: 0.5rem 0;'>✅ Priority support</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("⭐ Upgrade to Pro - $29/mo", type="primary", use_container_width=True, key="upgrade_pro"):
            start_checkout(STRIPE_PRICE_PRO, "pro")

def start_checkout(price_id, plan_name):
    """Initiate Stripe Checkout"""
    user_email = st.session_state.user['email']
    
    # Create success and cancel URLs
    success_url = "http://localhost:8501/?checkout=success"  # Change to your domain in production
    cancel_url = "http://localhost:8501/?checkout=cancel"
    
    checkout_url, error = create_checkout_session(price_id, user_email, success_url, cancel_url)
    
    if checkout_url:
        st.success(f"✅ Redirecting to checkout for {plan_name.title()} plan...")
        st.markdown(f'<meta http-equiv="refresh" content="0;url={checkout_url}">', unsafe_allow_html=True)
        st.markdown(f"[Click here if not redirected automatically]({checkout_url})")
    else:
        st.error(f"❌ Error creating checkout: {error}")

def show_manage_subscription():
    """Show subscription management for paid users"""
    user_email = st.session_state.user['email']
    
    # Get customer
    customer = get_customer_by_email(user_email)
    
    if customer:
        # Get subscription
        subscription = get_customer_subscription(customer.id)
        
        if subscription:
            st.success(f"✅ Active Subscription: {subscription.items.data[0].price.nickname or 'Premium'}")
            st.write(f"Status: {subscription.status}")
            st.write(f"Renews: {subscription.current_period_end}")
            
            if st.button("🔧 Manage Subscription (Cancel, Update Card, etc.)", use_container_width=True):
                return_url = "http://localhost:8501"  # Change to your domain in production
                portal_url, error = create_customer_portal_session(customer.id, return_url)
                
                if portal_url:
                    st.markdown(f'<meta http-equiv="refresh" content="0;url={portal_url}">', unsafe_allow_html=True)
                    st.markdown(f"[Click here to manage subscription]({portal_url})")
                else:
                    st.error(f"Error: {error}")
        else:
            st.info("No active subscription found")
    else:
        st.info("No customer record found")

def update_user_plan_from_stripe(user_email, plan):
    """Update user's plan in database after successful payment"""
    import auth
    import sqlite3
    
    conn = sqlite3.connect(auth.DB_PATH)
    c = conn.cursor()
    
    c.execute('UPDATE users SET plan = ? WHERE email = ?', (plan, user_email))
    conn.commit()
    conn.close()
    
    # Update session state
    if st.session_state.get('user') and st.session_state.user['email'] == user_email:
        st.session_state.user['plan'] = plan

def handle_checkout_success():
    """Handle successful checkout"""
    # Get session_id from URL
    params = st.query_params
    
    if 'session_id' in params:
        session_id = params['session_id']
        
        try:
            # Retrieve the session to get details
            session = stripe.checkout.Session.retrieve(session_id)
            user_email = session.metadata.get('user_email') or session.customer_email
            
            # Determine plan based on price_id
            price_id = session.line_items.data[0].price.id if hasattr(session, 'line_items') else None
            
            if price_id == STRIPE_PRICE_BASIC:
                plan = 'basic'
            elif price_id == STRIPE_PRICE_PRO:
                plan = 'pro'
            else:
                plan = 'premium'  # Default
            
            # Update user's plan
            update_user_plan_from_stripe(user_email, plan)
            
            st.success("🎉 Payment successful! Your account has been upgraded!")
            st.balloons()
            
            # Clear the URL parameter
            st.query_params.clear()
            st.rerun()
            
        except Exception as e:
            st.error(f"Error processing payment: {e}")

# Check for checkout success on page load
if 'checkout' in st.query_params:
    if st.query_params['checkout'] == 'success':
        handle_checkout_success()
    elif st.query_params['checkout'] == 'cancel':
        st.warning("Payment cancelled. You can upgrade anytime!")
        st.query_params.clear()
