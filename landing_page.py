"""
Credit CPR Landing Page
Educational tool for learning about FCRA rights and credit repair
"""

import streamlit as st
import base64
import textwrap

def get_image_base64(image_path):
    """Convert image to base64 for embedding"""
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

def landing_page():
    """Display the landing page for Credit CPR"""
    
    # Get shield logo as base64
    shield_base64 = get_image_base64("assets/shield.png")
    
    # Hero Section with CSS
    st.markdown("""
    <style>
        /* Landing Page Specific Styles */
        .hero-section {
            background: linear-gradient(135deg, #1B3A5C 0%, #2E8B57 100%);
            padding: 4rem 2rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 3rem;
            color: white;
        }
        
        .hero-logo {
            margin-bottom: 2rem;
        }
        
        .hero-headline {
            font-size: 3.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
            line-height: 1.2;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .hero-subheadline {
            font-size: 2rem;
            color: #7CB342;
            margin-bottom: 1.5rem;
            font-style: italic;
        }
        
        .hero-description {
            font-size: 1.3rem;
            margin-bottom: 2rem;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
            line-height: 1.6;
        }
        
        .cta-buttons {
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-top: 2rem;
        }
        
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin: 3rem 0;
        }
        
        .feature-card {
            background: #f0f8f0;
            padding: 2rem;
            border-radius: 10px;
            border-left: 4px solid #2E8B57;
            text-align: center;
        }
        
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .feature-title {
            font-size: 1.3rem;
            font-weight: bold;
            color: #1B3A5C;
            margin-bottom: 0.5rem;
        }
        
        .feature-description {
            color: #555;
            line-height: 1.5;
        }
        
        .process-section {
            background: #f9f9f9;
            padding: 3rem 2rem;
            border-radius: 15px;
            margin: 3rem 0;
        }
        
        .process-title {
            text-align: center;
            font-size: 2.5rem;
            color: #1B3A5C;
            margin-bottom: 1rem;
        }
        
        .process-subtitle {
            text-align: center;
            font-size: 1.5rem;
            color: #2E8B57;
            font-weight: bold;
            margin-bottom: 3rem;
        }
        
        .process-steps {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }
        
        .process-step {
            text-align: center;
            padding: 2rem;
        }
        
        .step-number {
            background: linear-gradient(135deg, #2E8B57 0%, #7CB342 100%);
            color: white;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            font-weight: bold;
            margin: 0 auto 1rem;
        }
        
        .step-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .step-title {
            font-size: 1.5rem;
            font-weight: bold;
            color: #1B3A5C;
            margin-bottom: 0.5rem;
        }
        
        .step-description {
            color: #555;
            line-height: 1.6;
        }
        
        .educational-disclaimer {
            background: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 2rem 0;
            text-align: center;
        }
        
        .disclaimer-title {
            font-weight: bold;
            color: #856404;
            margin-bottom: 0.5rem;
        }
        
        .testimonial-section {
            margin: 3rem 0;
            text-align: center;
        }
        
        .testimonial-card {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin: 1rem;
        }
        
        .testimonial-text {
            font-style: italic;
            color: #333;
            margin-bottom: 1rem;
            font-size: 1.1rem;
        }
        
        .testimonial-author {
            font-weight: bold;
            color: #2E8B57;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Hero Section
    hero_html = f"""
    <div class="hero-section">
        <div class="hero-logo">
            <img src="data:image/png;base64,{shield_base64}" width="80" alt="Shield">
        </div>
        <h1 class="hero-headline">Revive. Repair. Rebuild!!!</h1>
        <h2 class="hero-subheadline">Your Credit, Your Future</h2>
        <p class="hero-description">
            <strong>Free educational tool</strong> that teaches you how to exercise your FCRA rights and dispute credit report errors yourself. 
            Learn what the credit bureaus don't want you to know.
        </p>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)
    
    # CTA Buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Learning (Free)", type="primary", use_container_width=True):
            st.session_state.show_landing = False
            st.rerun()
    
    # Educational Disclaimer
    st.markdown("""
    <div class="educational-disclaimer">
        <div class="disclaimer-title">📚 Educational Tool - Not a Credit Repair Service</div>
        <p style="margin: 0; color: #856404;">
            Credit CPR is a <strong>free educational resource</strong> that teaches you how to identify errors on your credit report 
            and exercise your rights under the Fair Credit Reporting Act (FCRA). You dispute errors yourself - we just teach you how.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Social Proof
    st.markdown("""
    <div class="testimonial-section">
        <h3 style="color: #1B3A5C; margin-bottom: 2rem;">Join Thousands Learning to Fix Their Credit</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="testimonial-card">
            <div class="testimonial-text">"Learned how to find 3 errors I never knew existed!"</div>
            <div class="testimonial-author">- Sarah M.</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="testimonial-card">
            <div class="testimonial-text">"The AI found duplicate accounts the bureaus missed"</div>
            <div class="testimonial-author">- Michael T.</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="testimonial-card">
            <div class="testimonial-text">"Finally understand my FCRA rights!"</div>
            <div class="testimonial-author">- Jennifer L.</div>
        </div>
        """, unsafe_allow_html=True)
    
 # How It Works: Sign It. Stamp It. Mail It.
 st.markdown(
    textwrap.dedent("""
    <div class="process-section">
      <h2 class="process-title">Learn How to Fix Your Credit in 3 Steps</h2>
      <h3 class="process-subtitle">Sign It. Stamp It. Mail It.</h3>

      <div class="process-steps">
        <div class="process-step">
          <div class="step-number">1</div>
          <div class="step-icon">📤</div>
          <h3 class="step-title">Upload & Learn</h3>
          <p class="step-description">
            Upload your credit report and our AI teaches you what to look for.
            Learn about FCRA violations, duplicate accounts, and obsolete information.
          </p>
        </div>

        <div class="process-step">
          <div class="step-number">2</div>
          <div class="step-icon">✍️</div>
          <h3 class="step-title">Generate & Sign</h3>
          <p class="step-description">
            Get professionally written dispute letter templates citing specific FCRA sections.
            Learn exactly what to say and how to say it.
          </p>
        </div>

        <div class="process-step">
          <div class="step-number">3</div>
          <div class="step-icon">📮</div>
          <h3 class="step-title">Mail & Track</h3>
          <p class="step-description">
            Learn the proper way to send disputes via certified mail.
            Understand your rights and the 30-day investigation timeline.
          </p>
        </div>
      </div>
    </div>
    """),
    unsafe_allow_html=True
 )
    
 # Features Grid
 st.markdown(
    "<h2 style='text-align: center; color: #1B3A5C; margin: 3rem 0 2rem;'>What You'll Learn</h2>",
    unsafe_allow_html=True
 )

 st.markdown(
    textwrap.dedent("""
    <div class="feature-grid">

      <div class="feature-card">
        <div class="feature-icon">🤖</div>
        <div class="feature-title">AI-Powered Education</div>
        <div class="feature-description">
          Learn what errors to look for with AI that analyzes your report for common FCRA violations
        </div>
      </div>

      <div class="feature-card">
        <div class="feature-icon">📜</div>
        <div class="feature-title">FCRA Rights Training</div>
        <div class="feature-description">
          Understand your legal rights under the Fair Credit Reporting Act and how to exercise them
        </div>
      </div>

      <div class="feature-card">
        <div class="feature-icon">✉️</div>
        <div class="feature-title">Letter Templates</div>
        <div class="feature-description">
          Get professionally written templates you can customize and send yourself
        </div>
      </div>

      <div class="feature-card">
        <div class="feature-icon">📊</div>
        <div class="feature-title">Credit Building Plan</div>
        <div class="feature-description">
          Learn proven strategies to build positive credit history and improve your score
        </div>
      </div>

      <div class="feature-card">
        <div class="feature-icon">🔒</div>
        <div class="feature-title">100% Private</div>
        <div class="feature-description">
          We don't store your credit report or personal data. Learn in complete privacy.
        </div>
      </div>

    </div>
    """),
    unsafe_allow_html=True
 )
    
    # FAQ Section
    st.markdown("<h2 style='text-align: center; color: #1B3A5C; margin: 3rem 0 2rem;'>Frequently Asked Questions</h2>", unsafe_allow_html=True)
    
    with st.expander("❓ Is this really free?"):
        st.write("""
        **Yes, 100% free!** Credit CPR is an educational tool designed to teach you how to exercise your FCRA rights. 
        Under federal law, you have the right to dispute credit report errors yourself at no cost. We simply provide 
        the education and templates to help you do it effectively.
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
    
    # Final CTA
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="hero-section" style="padding: 3rem 2rem;">
        <h2 style="font-size: 2.5rem; margin-bottom: 1rem;">Ready to Take Control of Your Credit?</h2>
        <p style="font-size: 1.2rem; margin-bottom: 2rem;">
            Start learning how to identify and dispute credit report errors today - completely free.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎓 Start Your Credit Education Now", type="primary", use_container_width=True, key="bottom_cta"):
            st.session_state.show_landing = False
            st.rerun()
    
    # Legal Footer
    st.markdown("""
    <div style="text-align: center; margin-top: 3rem; padding: 2rem; background: #f9f9f9; border-radius: 10px;">
        <p style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">
            <strong>Legal Notice:</strong> Credit CPR is an educational platform, not a credit repair organization. 
            We provide information and tools to help you exercise your rights under the Fair Credit Reporting Act (FCRA). 
            You are responsible for reviewing, customizing, and sending all dispute letters yourself.
        </p>
        <p style="font-size: 0.9rem; color: #666; margin: 0;">
            We do not guarantee specific results, provide legal advice, or repair credit on your behalf. 
            For legal advice, consult a licensed attorney.
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    landing_page()
