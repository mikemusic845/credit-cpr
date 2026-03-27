import streamlit as st

def landing_page():
    st.markdown("<h1 style='text-align:center;'>Choose Your Plan</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>Take control of your credit — no middleman needed</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    # BASIC
    with col1:
        st.markdown("""
        <div style='padding:20px;border-radius:15px;border:1px solid #ddd;background-color:#f9f9f9;'>
            <h3>🟦 Basic</h3>
            <h2>$19/mo</h2>
            <p>Perfect to get started fixing your credit</p>
            <hr>
            <ul style='text-align:left;list-style:none;padding:0;'>
                <li>✅ 1 AI credit analysis/month</li>
                <li>✅ Dispute letter generator</li>
                <li>✅ Credit education tools</li>
                <li>✅ 90-day action plan</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # PRO
    with col2:
        st.markdown("""
        <div style='padding:20px;border-radius:15px;border:2px solid #22c55e;background-color:#e6f4ea;'>
            <p style='text-align:center;color:#16a34a;font-weight:bold;'>🔥 MOST POPULAR</p>
            <h3>🟩 Pro</h3>
            <h2>$29/mo</h2>
            <p><strong>Everything in Basic, plus powerful automation</strong></p>
            <hr>
            <ul style='text-align:left;list-style:none;padding:0;'>
                <li>✅ Everything in Basic included</li>
                <li>✅ Unlimited credit analysis</li>
                <li>✅ Unlimited dispute letters</li>
                <li>✅ 💬 AI Credit Assistant (chat)</li>
                <li>✅ 📊 Score Tracker</li>
                <li>✅ 📅 Dispute Tracker</li>
                <li>✅ Email letters to bureaus</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # PREMIUM
    with col3:
        st.markdown("""
        <div style='padding:20px;border-radius:15px;border:2px solid gold;background-color:#fffbe6;'>
            <h3>⭐ Premium</h3>
            <h2>$49/mo</h2>
            <p>Full AI coaching experience</p>
            <hr>
            <ul style='text-align:left;list-style:none;padding:0;'>
                <li>✅ Everything in Pro</li>
                <li>✅ 🤖 AI Credit Coach</li>
                <li>✅ Daily action plans</li>
                <li>✅ Progress check & analysis</li>
                <li>✅ Advanced AI insights</li>
                <li>✅ Priority support</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.button("🚀 Analyze My Credit Report Now", use_container_width=True)
