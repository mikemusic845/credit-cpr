"""
Credit CPR Landing Page - Upgraded for Conversion
"""

import streamlit as st
from PIL import Image


def landing_page():
    """Display the upgraded landing page"""

    # Hero Section
    try:
        shield = Image.open("assets/shield.png")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.image(shield, width=120)
    except:
        st.write("🛡️")

    st.markdown("""
    <div style='text-align: center; background: linear-gradient(135deg, #1B3A5C 0%, #2E8B57 100%);
    padding: 3rem 2rem; border-radius: 15px; color: white; margin-bottom: 2rem;'>
        <h1 style='font-size: 2.8rem; margin-bottom: 0.5rem;'>
            Fix Your Credit Yourself — The Smart Way
        </h1>
        <h2 style='font-size: 1.5rem; color: #7CB342; font-style: italic;'>
            Find errors. Dispute them. Track your progress.
        </h2>
        <p style='font-size: 1.2rem; margin-top: 1rem;'>
            Upload your credit report and get a <strong>step-by-step plan, dispute letters, and AI guidance</strong> in minutes.
        </p>
        <p style='font-size: 0.9rem; opacity: 0.8; margin-top: 1rem;'>
            No credit repair company needed. You stay in control.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Hero CTA
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Analyze My Credit Report Now", type="primary", use_container_width=True, key="hero_cta"):
            st.session_state.show_landing = False
            st.rerun()

    st.caption("📄 Works with Experian, Equifax, and TransUnion reports")
    st.warning("⚡ Most users find errors on their first report within minutes")
    st.markdown("#### Trusted by people fixing their credit every day")

    st.markdown("---")

    # Social Proof
    st.markdown("### What Our Users Say")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style='background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
            <div style='color: #FFD700; font-size: 1.2rem; margin-bottom: 0.5rem;'>⭐⭐⭐⭐⭐</div>
            <p style='font-style: italic; color: #333; margin-bottom: 1rem;'>"Found 3 errors I never knew existed. Score went up 47 points!"</p>
            <p style='font-weight: bold; color: #2E8B57; margin: 0;'>- Sarah M.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style='background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
            <div style='color: #FFD700; font-size: 1.2rem; margin-bottom: 0.5rem;'>⭐⭐⭐⭐⭐</div>
            <p style='font-style: italic; color: #333; margin-bottom: 1rem;'>"The AI found duplicate accounts the bureaus missed. Saved me thousands."</p>
            <p style='font-weight: bold; color: #2E8B57; margin: 0;'>- Michael T.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style='background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
            <div style='color: #FFD700; font-size: 1.2rem; margin-bottom: 0.5rem;'>⭐⭐⭐⭐⭐</div>
            <p style='font-style: italic; color: #333; margin-bottom: 1rem;'>"Finally understand my FCRA rights. No more paying $150/mo to a repair company!"</p>
            <p style='font-weight: bold; color: #2E8B57; margin: 0;'>- Jennifer L.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Why People Use Credit CPR
    st.markdown("## Why People Use Credit CPR")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ❌ Stop paying credit repair companies hundreds of dollars
        
        ❌ Stop guessing what to dispute
        
        ❌ Stop waiting months with no plan
        
        ❌ Stop letting errors silently crush your score
        """)
    with col2:
        st.markdown("""
        ✅ Know EXACTLY what's hurting your score
        
        ✅ Get step-by-step dispute strategy
        
        ✅ Track your progress in one place
        
        ✅ Take control of your credit journey today
        """)

    st.markdown("---")

    # How It Works
    st.markdown("## Fix Your Credit in 3 Steps")
    st.markdown("### :green[Sign It. Stamp It. Mail It.]")

    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("<div style='background:linear-gradient(135deg,#2E8B57 0%,#7CB342 100%);color:white;width:60px;height:60px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:2rem;font-weight:bold;margin:0 auto;'>1</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("### 📤 Upload & Analyze")
        st.write("Upload your credit report PDF. Our AI instantly scans for FCRA violations, duplicate accounts, errors, and obsolete information.")

    st.markdown("")

    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("<div style='background:linear-gradient(135deg,#2E8B57 0%,#7CB342 100%);color:white;width:60px;height:60px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:2rem;font-weight:bold;margin:0 auto;'>2</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("### ✍️ Generate Dispute Letters")
        st.write("Get professionally written dispute letters citing specific FCRA sections. Customized for each bureau — ready to sign and send.")

    st.markdown("")

    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("<div style='background:linear-gradient(135deg,#2E8B57 0%,#7CB342 100%);color:white;width:60px;height:60px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:2rem;font-weight:bold;margin:0 auto;'>3</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("### 📊 Track & Win")
        st.write("Track your disputes, log your score progress, get AI coaching, and follow up automatically. Your full credit repair system in one place.")

    st.markdown("---")

    # Features
    st.markdown("## Everything You Need to Fix Your Credit")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success("**🤖 AI Credit Analysis**\n\nInstant scan of your report for errors, FCRA violations, and disputes opportunities")
        st.success("**📝 Dispute Letter Generator**\n\nProfessional letters citing specific FCRA sections — ready to mail in minutes")
    with col2:
        st.success("**📊 Score Tracker**\n\nLog and track your scores across all 3 bureaus with progress charts and AI insights")
        st.success("**📅 Dispute Tracker**\n\nTrack every dispute, get automatic 30-day follow-up alerts, mark resolutions")
    with col3:
        st.success("**💬 AI Credit Assistant**\n\nAsk anything about credit repair, FCRA rights, collections, and credit building")
        st.success("**🤖 AI Credit Coach**\n\nPersonalized daily action plans and progress coaching based on your profile")

    st.markdown("---")

    # Pricing
    st.markdown("## Choose Your Plan")
    st.markdown("### Take control of your credit — no middleman needed")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style='padding:2rem;border:2px solid #ccc;border-radius:12px;text-align:center;height:100%;'>
            <h3 style='color:#1B3A5C;'>🟦 Basic</h3>
            <div style='font-size:2.5rem;font-weight:bold;color:#2E8B57;margin:1rem 0;'>$19<span style='font-size:1rem;font-weight:normal;'>/mo</span></div>
            <p style='color:#666;'>Perfect to get started fixing your credit</p>
            <hr>
            <ul style='text-align:left;list-style:none;padding:0;'>
                <li style='padding:0.4rem 0;'>✅ 1 AI credit analysis/month</li>
                <li style='padding:0.4rem 0;'>✅ Dispute letter generator</li>
                <li style='padding:0.4rem 0;'>✅ Credit education tools</li>
                <li style='padding:0.4rem 0;'>✅ 90-day action plan</li>
                <li style='padding:0.4rem 0;'>⚪ Score Tracker (Pro+)</li>
                <li style='padding:0.4rem 0;'>⚪ Dispute Tracker (Pro+)</li>
                <li style='padding:0.4rem 0;'>⚪ AI Assistant (Pro+)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='padding:2rem;border:3px solid #2E8B57;border-radius:12px;text-align:center;background:#e8f5e9;height:100%;'>
            <div style='background:#2E8B57;color:white;padding:0.4rem;border-radius:5px;font-weight:bold;margin-bottom:1rem;'>🔥 MOST POPULAR</div>
            <h3 style='color:#1B3A5C;'>🟩 Pro</h3>
            <div style='font-size:2.5rem;font-weight:bold;color:#2E8B57;margin:1rem 0;'>$29<span style='font-size:1rem;font-weight:normal;'>/mo</span></div>
            <p style='color:#444;'><strong>Everything you need to fix your credit faster</strong></p>
            <hr style='border-color:#2E8B57;'>
            <ul style='text-align:left;list-style:none;padding:0;'>
                <li style='padding:0.4rem 0;'>✅ <strong>Unlimited</strong> credit analysis</li>
                <li style='padding:0.4rem 0;'>✅ Unlimited dispute letters</li>
                <li style='padding:0.4rem 0;'>✅ 💬 AI Credit Assistant (chat)</li>
                <li style='padding:0.4rem 0;'>✅ 📊 Score Tracker + charts</li>
                <li style='padding:0.4rem 0;'>✅ 📅 Dispute Tracker + alerts</li>
                <li style='padding:0.4rem 0;'>✅ Email letters to bureaus</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style='padding:2rem;border:2px solid #FFD700;border-radius:12px;text-align:center;height:100%;'>
            <h3 style='color:#1B3A5C;'>⭐ Premium</h3>
            <div style='font-size:2.5rem;font-weight:bold;color:#2E8B57;margin:1rem 0;'>$49<span style='font-size:1rem;font-weight:normal;'>/mo</span></div>
            <p style='color:#666;'>Full AI coaching experience</p>
            <hr>
            <ul style='text-align:left;list-style:none;padding:0;'>
                <li style='padding:0.4rem 0;'>✅ Everything in Pro</li>
                <li style='padding:0.4rem 0;'>✅ 🤖 AI Credit Coach</li>
                <li style='padding:0.4rem 0;'>✅ Daily action plans</li>
                <li style='padding:0.4rem 0;'>✅ Progress check & analysis</li>
                <li style='padding:0.4rem 0;'>✅ Advanced AI insights</li>
                <li style='padding:0.4rem 0;'>✅ Priority support</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Analyze My Credit Report Now", type="primary", use_container_width=True, key="pricing_cta"):
            st.session_state.show_landing = False
            st.rerun()

    st.markdown("---")

    # FAQ
    st.markdown("## Frequently Asked Questions")

    with st.expander("❓ Is this a credit repair company?"):
        st.write("**No.** Credit CPR is an educational platform that teaches you how to repair your own credit. You stay in full control — no middleman, no monthly fees to a repair company. This is your legal right under the FCRA.")

    with st.expander("❓ How does it work?"):
        st.write("""
        1. **Upload your credit report** (PDF from any bureau)
        2. **AI analyzes it** and finds errors, violations, and dispute opportunities
        3. **Generate dispute letters** citing specific FCRA sections
        4. **Mail them** via certified mail and track everything in the app
        5. **Watch your score improve** as disputes get resolved
        """)

    with st.expander("❓ How fast can I see results?"):
        st.write("Credit bureaus have **30 days** to investigate disputes under the FCRA. Many users see results within 30-45 days of sending their first dispute letter.")

    with st.expander("❓ Do you store my credit report?"):
        st.write("**No.** Your credit report is processed and never stored on our servers. Your privacy is protected.")

    with st.expander("❓ What if errors don't get removed?"):
        st.write("We teach you escalation strategies — including filing CFPB complaints and understanding your right to sue under FCRA Section 616 if bureaus fail to properly investigate.")

    with st.expander("❓ What makes Credit CPR different from other credit repair services?"):
        st.write("**You own the process.** No middleman charging $100-$200/month. You learn exactly what to do, why it works, and how to do it yourself — permanently. Credit CPR gives you the tools, knowledge, and AI to do it faster and smarter.")

    st.markdown("---")

    # Final CTA
    st.markdown("### Ready to Fix Your Credit the Smart Way?")
    st.write("Upload your report and see what's really holding your score back — in minutes.")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Analyze My Credit Report Now", type="primary", use_container_width=True, key="bottom_cta"):
            st.session_state.show_landing = False
            st.rerun()

    st.markdown("---")

    # Legal Footer
    st.caption("""
    **Legal Notice:** Credit CPR is an educational platform, not a credit repair organization.
    We provide information and tools to help you exercise your rights under the Fair Credit Reporting Act (FCRA).
    You are responsible for reviewing, customizing, and sending all dispute letters yourself.
    We do not guarantee specific results, provide legal advice, or repair credit on your behalf.
    For legal advice, consult a licensed attorney.
    """)


if __name__ == "__main__":
    landing_page()
