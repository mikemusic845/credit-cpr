"""
Credit CPR Landing Page - Pure Streamlit Version
No HTML - All native Streamlit components
"""

import streamlit as st
from PIL import Image

def landing_page():
    """Display the landing page using only Streamlit components"""
    
    # Hero Section
    st.markdown("---")
    
    # Try to load shield logo
    try:
        shield = Image.open("assets/shield.png")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.image(shield, width=120)
    except:
        st.write("🛡️")
    
    # Hero headline
    st.markdown("""
        <div style='text-align: center; background: linear-gradient(135deg, #1B3A5C 0%, #2E8B57 100%); 
        padding: 3rem 2rem; border-radius: 15px; color: white; margin-bottom: 2rem;'>
            <h1 style='font-size: 3rem; margin-bottom: 0.5rem;'>Revive. Repair. Rebuild.</h1>
            <h2 style='font-size: 1.8rem; color: #7CB342; font-style: italic;'>Your Credit, Your Future</h2>
            <p style='font-size: 1.2rem; margin-top: 1rem;'>
                <strong>AI-powered educational assistant</strong> that equips you to exercise your FCRA rights<br>
                and dispute credit report errors yourself.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # CTA Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Get Started", type="primary", use_container_width=True, key="hero_cta"):
            st.session_state.show_landing = False
            st.rerun()
    
    st.markdown("---")
    
    # Educational Disclaimer
    st.warning("📚 **Educational Assistant - Not a Credit Repair Service**\n\nCredit CPR is an **AI-powered educational assistant** that teaches you how to identify errors on your credit report and exercise your rights under the Fair Credit Reporting Act (FCRA). You dispute errors yourself - we equip you with the knowledge and tools.")
    
    # Social Proof
    st.markdown("### Join Thousands Learning to Fix Their Credit")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("💬 *\"Learned how to find 3 errors I never knew existed!\"*\n\n**- Sarah M.**")
    
    with col2:
        st.info("💬 *\"The AI found duplicate accounts the bureaus missed\"*\n\n**- Michael T.**")
    
    with col3:
        st.info("💬 *\"Finally understand my FCRA rights!\"*\n\n**- Jennifer L.**")
    
    st.markdown("---")
    
    # Process Section - Sign It. Stamp It. Mail It.
    st.markdown("## Learn How to Fix Your Credit in 3 Steps")
    st.markdown("### :green[Sign It. Stamp It. Mail It.]")
    
    # Step 1
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #2E8B57 0%, #7CB342 100%); 
            color: white; width: 60px; height: 60px; border-radius: 50%; 
            display: flex; align-items: center; justify-content: center; 
            font-size: 2rem; font-weight: bold; margin: 0 auto;'>1</div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📤 Upload & Learn")
        st.write("Upload your credit report and our AI teaches you what to look for. Learn about FCRA violations, duplicate accounts, and obsolete information.")
    
    st.markdown("")
    
    # Step 2
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #2E8B57 0%, #7CB342 100%); 
            color: white; width: 60px; height: 60px; border-radius: 50%; 
            display: flex; align-items: center; justify-content: center; 
            font-size: 2rem; font-weight: bold; margin: 0 auto;'>2</div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### ✍️ Generate & Sign")
        st.write("Get professionally written dispute letter templates citing specific FCRA sections. Learn exactly what to say and how to say it.")
    
    st.markdown("")
    
    # Step 3
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #2E8B57 0%, #7CB342 100%); 
            color: white; width: 60px; height: 60px; border-radius: 50%; 
            display: flex; align-items: center; justify-content: center; 
            font-size: 2rem; font-weight: bold; margin: 0 auto;'>3</div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📮 Mail & Track")
        st.write("Learn the proper way to send disputes via certified mail. Understand your rights and the 30-day investigation timeline.")
    
    st.markdown("---")
    
    # What You'll Learn
    st.markdown("## What You'll Learn")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("**🤖 AI-Powered Education**\n\nLearn what errors to look for with AI that analyzes your report for common FCRA violations")
        st.success("**🔒 100% Private**\n\nWe don't store your credit report or personal data. Learn in complete privacy.")
    
    with col2:
        st.success("**📜 FCRA Rights Training**\n\nUnderstand your legal rights under the Fair Credit Reporting Act and how to exercise them")
        st.success("**📊 Credit Building Plan**\n\nLearn proven strategies to build positive credit history and improve your score")
    
    with col3:
        st.success("**✉️ Letter Templates**\n\nGet professionally written templates you can customize and send yourself")
        st.success("**⚡ Instant Analysis**\n\nAI analyzes your credit report in seconds, identifying errors you might miss")
    
    st.markdown("---")
    
    # FAQ Section
    st.markdown("## Frequently Asked Questions")
    
    with st.expander("❓ How does Credit CPR work?"):
        st.write("""
        Credit CPR is an AI-powered educational assistant that teaches you how to exercise your FCRA rights. 
        Under federal law, you have the right to dispute credit report errors yourself. Credit CPR equips you with 
        the knowledge, tools, and templates to do it effectively - putting you in control of your credit repair journey.
        """)
    
    with st.expander("❓ Is this a credit repair company?"):
        st.write("""
        **No.** Credit CPR is an educational platform that teaches you how to repair your own credit. We don't repair 
        your credit for you - we teach you how to do it yourself, which is your legal right under the FCRA. This means 
        you're not subject to Credit Repair Organizations Act (CRORA) restrictions, and you can start immediately.
        """)
    
    with st.expander("❓ How does it work?"):
        st.write("""
        1. **Upload your credit report** (PDF from any bureau)
        2. **AI analyzes it** and teaches you what errors to look for
        3. **Generate dispute letters** using our professional templates
        4. **Learn how to mail them** properly via certified mail
        5. **Track your disputes** and understand the 30-day timeline
        """)
    
    with st.expander("❓ Do you store my credit report?"):
        st.write("""
        **No.** Your credit report is processed in your browser only and is never saved to our servers. We take your 
        privacy seriously. Once you close your browser, your data is gone.
        """)
    
    with st.expander("❓ Will this actually improve my credit score?"):
        st.write("""
        **It can!** If your credit report contains errors (which studies show up to 79% do), successfully disputing 
        them can improve your score. However, we're an educational tool - we teach you the process, but results depend 
        on whether errors exist on your report and how bureaus respond to your disputes.
        """)
    
    with st.expander("❓ How long does the dispute process take?"):
        st.write("""
        Credit bureaus have **30 days** to investigate disputes under the FCRA. You'll learn the entire timeline and 
        what to expect at each stage. Many people see results within 30-45 days of mailing their first dispute letter.
        """)
    
    with st.expander("❓ What if the bureaus don't respond?"):
        st.write("""
        We teach you your rights! If bureaus don't respond within 30 days or fail to properly investigate, you'll learn 
        about follow-up strategies, including filing complaints with the CFPB (Consumer Financial Protection Bureau) and 
        understanding your right to sue under FCRA Section 616.
        """)
    
    st.markdown("---")
    
    # Final CTA
    st.markdown("### Ready to Take Control of Your Credit?")
    st.write("Start identifying and disputing credit report errors today with AI-powered assistance.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎓 Start Your Credit Repair Journey", type="primary", use_container_width=True, key="bottom_cta"):
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
