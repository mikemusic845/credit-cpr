"""
Credit CPR Landing Page - Dark Mode Friendly Conversion Version
"""

import streamlit as st
from PIL import Image


def landing_page():
    """Display the upgraded landing page"""

    st.markdown("""
    <style>
    .lp-wrap {
        max-width: 1200px;
        margin: 0 auto;
    }
    .lp-hero {
        text-align: center;
        background: linear-gradient(135deg, #0f172a 0%, #14532d 100%);
        padding: 3rem 2rem;
        border-radius: 18px;
        color: white;
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 12px 40px rgba(0,0,0,0.25);
    }
    .lp-card {
        padding: 24px;
        border-radius: 18px;
        min-height: 560px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.18);
    }
    .lp-card, .lp-card * {
        color: #0f172a !important;
    }
    .lp-basic {
        background: #f8fafc;
        border: 1px solid #cbd5e1;
    }
    .lp-pro {
        background: #ecfdf5;
        border: 2px solid #22c55e;
    }
    .lp-premium {
        background: #fffbeb;
        border: 2px solid #facc15;
    }
    .lp-badge {
        text-align: center;
        color: white !important;
        background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
        padding: 0.5rem 0.75rem;
        border-radius: 10px;
        font-weight: 800;
        margin-bottom: 1rem;
    }
    .lp-price {
        font-size: 2.6rem;
        font-weight: 800;
        margin: 0.5rem 0;
        color: #15803d !important;
    }
    .lp-muted {
        color: #475569 !important;
    }
    .lp-strike {
        text-decoration: line-through;
        color: #64748b !important;
        margin-top: -0.25rem;
        margin-bottom: 0.75rem;
        font-size: 0.95rem;
    }
    .lp-ul {
        list-style: none;
        padding-left: 0;
        margin: 0;
        text-align: left;
    }
    .lp-ul li {
        padding: 0.45rem 0;
        line-height: 1.35;
    }
    .lp-subtle {
        font-size: 0.9rem;
        color: #cbd5e1 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='lp-wrap'>", unsafe_allow_html=True)

    # Logo
    try:
        shield = Image.open("assets/shield.png")
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            st.image(shield, width=110)
    except Exception:
        st.write("🛡️")

    # Hero
    st.markdown("""
    <div class='lp-hero'>
        <h1 style='font-size: 3rem; margin-bottom: 0.5rem;'>Fix Your Credit Yourself — The Smart Way</h1>
        <h2 style='font-size: 1.5rem; color: #86efac; font-style: italic; margin-top: 0;'>Find errors. Dispute them. Track your progress.</h2>
        <p style='font-size: 1.15rem; margin-top: 1rem;'>
            Upload your credit report and get a <strong>step-by-step plan, dispute letters, and AI guidance</strong> in minutes.
        </p>
        <p class='lp-subtle' style='margin-top: 1rem;'>No credit repair company needed. You stay in control.</p>
    </div>
    """, unsafe_allow_html=True)

    st.caption("📄 Works with Experian, Equifax, and TransUnion reports")
    st.warning("⚡ Most users find errors on their first report within minutes")

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🚀 Analyze My Credit Report Now", type="primary", use_container_width=True, key="hero_cta"):
            st.session_state.show_landing = False
            st.rerun()

    st.markdown("#### Trusted by people fixing their credit every day")
    st.markdown("---")

    # Social proof
    st.markdown("### What Our Users Say")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class='lp-card lp-basic' style='min-height:auto;'>
            <div style='color:#f59e0b !important; font-size:1.2rem; margin-bottom:0.5rem;'>⭐⭐⭐⭐⭐</div>
            <p style='font-style: italic; margin-bottom: 1rem;'>"Found 3 errors I never knew existed."</p>
            <p style='font-weight: 700; color:#15803d !important; margin:0;'>- Sarah M.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class='lp-card lp-basic' style='min-height:auto;'>
            <div style='color:#f59e0b !important; font-size:1.2rem; margin-bottom:0.5rem;'>⭐⭐⭐⭐⭐</div>
            <p style='font-style: italic; margin-bottom: 1rem;'>"The AI helped me understand what to dispute first."</p>
            <p style='font-weight: 700; color:#15803d !important; margin:0;'>- Michael T.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class='lp-card lp-basic' style='min-height:auto;'>
            <div style='color:#f59e0b !important; font-size:1.2rem; margin-bottom:0.5rem;'>⭐⭐⭐⭐⭐</div>
            <p style='font-style: italic; margin-bottom: 1rem;'>"Finally understand my FCRA rights."</p>
            <p style='font-weight: 700; color:#15803d !important; margin:0;'>- Jennifer L.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Why use
    st.markdown("## Why People Use Credit CPR")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        ❌ Stop paying credit repair companies hundreds of dollars

        ❌ Stop guessing what to dispute

        ❌ Stop waiting months with no plan

        ❌ Stop letting errors silently crush your score
        """)
    with c2:
        st.markdown("""
        ✅ Know EXACTLY what’s hurting your score

        ✅ Get step-by-step dispute strategy

        ✅ Track your progress in one place

        ✅ Take control of your credit journey today
        """)

    st.markdown("---")

    # 3 steps
    st.markdown("## Fix Your Credit in 3 Steps")
    st.markdown("### :green[Sign It. Stamp It. Mail It.]")

    steps = [
        ("1", "📤 Upload & Analyze", "Upload your credit report PDF. Our AI instantly scans for FCRA violations, duplicate accounts, errors, and obsolete information."),
        ("2", "✍️ Generate Dispute Letters", "Get professionally written dispute letters citing specific FCRA sections. Customized for each bureau — ready to sign and send."),
        ("3", "📊 Track & Win", "Track your disputes, log your score progress, get AI coaching, and follow up automatically. Your full credit repair system in one place."),
    ]

    for num, title, body in steps:
        c1, c2 = st.columns([1, 4])
        with c1:
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#16a34a 0%,#65a30d 100%);color:white;width:60px;height:60px;border-radius:50%;
            display:flex;align-items:center;justify-content:center;font-size:2rem;font-weight:bold;margin:0 auto;'>{num}</div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"### {title}")
            st.write(body)
        st.markdown("")

    st.markdown("---")

    # Features
    st.markdown("## Everything You Need to Fix Your Credit")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.success("**🤖 AI Credit Analysis**\n\nInstant scan of your report for errors, FCRA violations, and dispute opportunities")
        st.success("**📝 Dispute Letter Generator**\n\nProfessional letters citing specific FCRA sections — ready to mail in minutes")
    with c2:
        st.success("**📊 Score Tracker**\n\nLog and track your scores across all 3 bureaus")
        st.success("**📅 Dispute Tracker**\n\nTrack every dispute, follow-up dates, and resolutions")
    with c3:
        st.success("**💬 AI Credit Assistant**\n\nAsk anything about credit repair, FCRA rights, collections, and credit building")
        st.success("**🤖 AI Credit Coach**\n\nPersonalized action plans and progress coaching based on your profile")

    st.markdown("---")

    # Pricing
    st.markdown("## Choose Your Plan")
    st.markdown("### Take control of your credit — no middleman needed")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class='lp-card lp-basic'>
            <h3>🟦 Basic</h3>
            <div class='lp-price'>$19<span style='font-size:1rem;font-weight:500;'>/mo</span></div>
            <p class='lp-muted'>Perfect to get started fixing your credit</p>
            <hr>
            <ul class='lp-ul'>
                <li>✅ 1 AI credit analysis/month</li>
                <li>✅ Dispute letter generator</li>
                <li>✅ Credit education tools</li>
                <li>✅ 90-day action plan</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class='lp-card lp-pro'>
            <div class='lp-badge'>🔥 MOST POPULAR</div>
            <h3>🟩 Pro</h3>
            <div class='lp-price'>$29<span style='font-size:1rem;font-weight:500;'>/mo</span></div>
            <p style='color:#16a34a !important; font-weight:800; margin-bottom:0.25rem;'>🚀 Most users upgrade to Pro</p>
            <p class='lp-strike'>$79/mo value</p>
            <hr>
            <ul class='lp-ul'>
                <li>✅ Everything in Basic included</li>
                <li>✅ Unlimited credit analysis</li>
                <li>✅ Unlimited dispute letters</li>
                <li>✅ 💬 AI Credit Assistant (chat)</li>
                <li>✅ 📊 Score Tracker</li>
                <li>✅ 📅 Dispute Tracker</li>
                <li>✅ Email letters to bureaus</li>
            </ul>
            <div style='margin-top:20px;background:#16a34a;color:white !important;text-align:center;padding:12px 14px;border-radius:10px;font-weight:800;'>
                Upgrade to Pro
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class='lp-card lp-premium'>
            <h3>⭐ Premium</h3>
            <div class='lp-price'>$49<span style='font-size:1rem;font-weight:500;'>/mo</span></div>
            <p class='lp-muted'>Full AI coaching experience</p>
            <hr>
            <ul class='lp-ul'>
                <li>✅ Everything in Pro</li>
                <li>✅ 🤖 AI Credit Coach</li>
                <li>✅ Daily action plans</li>
                <li>✅ Progress check & analysis</li>
                <li>✅ Advanced AI insights</li>
                <li>✅ Priority support</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🚀 Analyze My Credit Report Now", type="primary", use_container_width=True, key="pricing_cta"):
            st.session_state.show_landing = False
            st.rerun()
    st.caption("Cancel anytime. No long-term contracts.")

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
        5. **Track progress** as your disputes move through the process
        """)

    with st.expander("❓ How fast can I see results?"):
        st.write("Credit bureaus have **30 days** to investigate disputes under the FCRA. Many users see movement within 30–45 days of sending their first dispute letter.")

    with st.expander("❓ Do you store my credit report?"):
        st.write("**No.** Your credit report is processed and never stored on our servers. Your privacy is protected.")

    with st.expander("❓ What if errors don't get removed?"):
        st.write("We teach you escalation strategies — including filing CFPB complaints and understanding your rights if bureaus fail to properly investigate.")

    with st.expander("❓ What makes Credit CPR different from other credit repair services?"):
        st.write("**You own the process.** No middleman charging $100–$200/month. You learn exactly what to do, why it works, and how to do it yourself — faster and smarter.")

    st.markdown("---")

    # Final CTA
    st.markdown("### Ready to Fix Your Credit the Smart Way?")
    st.write("Upload your report and see what’s really holding your score back — in minutes.")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🚀 Analyze My Credit Report Now", type="primary", use_container_width=True, key="bottom_cta"):
            st.session_state.show_landing = False
            st.rerun()

    st.markdown("---")
    st.caption("""
    **Legal Notice:** Credit CPR is an educational platform, not a credit repair organization.
    We provide information and tools to help you exercise your rights under the Fair Credit Reporting Act (FCRA).
    You are responsible for reviewing, customizing, and sending all dispute letters yourself.
    We do not guarantee specific results, provide legal advice, or repair credit on your behalf.
    For legal advice, consult a licensed attorney.
    """)

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    landing_page()
