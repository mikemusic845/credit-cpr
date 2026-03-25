"""
AI Credit Repair Specialist - MVP
A tool to analyze credit reports and generate dispute letters using AI
"""

import streamlit as st
import json
import os
from io import BytesIO
from docx import Document
from docx.shared import Pt, Inches
from datetime import datetime, timedelta
import PyPDF2
import base64
import auth  # Authentication system

def get_shield_base64():
    with open("assets/shield.png", "rb") as f:
        return base64.b64encode(f.read()).decode()

# Page config
st.set_page_config(
    page_title="Credit CPR - AI Credit Repair Assistant",
    page_icon="assets/shield.png",
    layout="wide",
    initial_sidebar_state="expanded"
    )

st.markdown("""
<style>

/* Fix tab background conflicts without overriding theme */
button[data-baseweb="tab"] {
    background-color: transparent !important;
}

button[data-baseweb="tab"] p {
    color: inherit !important;
}

button[data-baseweb="tab"][aria-selected="true"] p {
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'errors_found' not in st.session_state:
    st.session_state.errors_found = []
if 'credit_data' not in st.session_state:
    st.session_state.credit_data = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}

    # Custom CSS for Credit CPR branding
st.markdown("""
<style>
    /* Credit CPR Color Theme */
    :root {
        --primary-color: #2E8B57;  /* Green from logo */
        --secondary-color: #1B3A5C;  /* Navy blue from logo */
        --accent-color: #7CB342;  /* Bright green */
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1B3A5C 0%, #2E8B57 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }
    
    .hero-title {
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .hero-tagline {
        color: #7CB342;
        font-size: 1.5rem;
        font-style: italic;
        margin: 0.5rem 0;
    }
    
    .hero-subtext {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
        margin-top: 1rem;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #2E8B57 0%, #7CB342 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: transform 0.2s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(46, 139, 87, 0.4);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f0f8f0;
        border-left: 4px solid #2E8B57;
    }
    
    /* Tab styling - Fixed with borders */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f8f0;
        border-radius: 8px 8px 0 0;
        border-top: 2px solid #2E8B57;
        border-left: 2px solid #2E8B57;
        border-right: 2px solid #2E8B57;
        border-bottom: none;
        padding: 12px 20px;
        white-space: nowrap;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2E8B57 0%, #7CB342 100%);
        color: white;
        border-top: 2px solid #1B3A5C;
        border-left: 2px solid #1B3A5C;
        border-right: 2px solid #1B3A5C;
    }
    
    /* Footer */
    .credit-cpr-footer {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        border-top: 2px solid #2E8B57;
        color: #1B3A5C;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Anthropic client
def get_anthropic_client():
    # Try multiple ways to get the API key
    api_key = None
    
    # Method 1: Streamlit secrets
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    except:
        pass
    
    # Method 2: Environment variable
    if not api_key:
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Check if we got a valid key
    if not api_key or api_key == "":
        st.error("**API Key Not Found!**")
        st.info("""
        Please set up your Anthropic API key using ONE of these methods:
        
        **Method 1: Streamlit Secrets (Recommended)**
        1. Create folder: `.streamlit` 
        2. Create file: `.streamlit/secrets.toml`
        3. Add this line:
        ```
        ANTHROPIC_API_KEY = "sk-ant-your-key-here"
        ```
        
        **Method 2: Environment Variable**
        Run this before starting the app:
        ```
        export ANTHROPIC_API_KEY="sk-ant-your-key-here"
        ```
        
        **Get your API key:** https://console.anthropic.com/
        """)
        st.stop()
    
    # Validate key format
    if not api_key.startswith("sk-ant-"):
        st.error(f"Invalid API key format. Key should start with 'sk-ant-' but yours starts with '{api_key[:7]}'")
        st.stop()
    
    # Try to import and initialize Anthropic
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        return client
    except ImportError:
        st.error("Anthropic library not installed properly!")
        st.info("Run this command: `pip install anthropic`")
        st.stop()
    except Exception as e:
        st.error(f"Error initializing Anthropic client: {str(e)}")
        st.info("Try reinstalling: `pip install --upgrade anthropic`")
        st.stop()

# PDF Parser
def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

# AI Functions
def parse_credit_report_with_ai(raw_text, client):
    """Use AI to structure the credit report data"""
    prompt = f"""Analyze this credit report text and extract key information into a structured JSON format.

Extract:
1. Personal Information (name, addresses, SSN if present, DOB)
2. Accounts (creditor name, account number, balance, status, payment history)
3. Inquiries (company name, date)
4. Public Records (bankruptcies, collections, judgments)
5. Negative Items (late payments, charge-offs, etc.)

Credit Report Text:
{raw_text[:15000]}  

Return ONLY valid JSON with this structure:
{{
  "personal_info": {{"name": "", "addresses": [], "ssn_last4": "", "dob": ""}},
  "accounts": [{{"creditor": "", "account_num": "", "balance": 0, "status": "", "payment_history": ""}}],
  "inquiries": [{{"company": "", "date": ""}}],
  "public_records": [{{"type": "", "status": "", "date": ""}}],
  "negative_items": [{{"description": "", "date": ""}}]
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        # Extract JSON from response
        response_text = message.content[0].text
        # Clean up any markdown code blocks
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        return json.loads(response_text)
    except:
        # Return basic structure if parsing fails
        return {
            "personal_info": {"name": "Unable to parse", "addresses": [], "ssn_last4": "", "dob": ""},
            "accounts": [],
            "inquiries": [],
            "public_records": [],
            "negative_items": []
        }

def analyze_for_errors(credit_data, client):
    """Analyze credit report for errors and FCRA violations"""
    prompt = f"""You are a credit repair specialist. Analyze this credit report data for errors and FCRA violations.

Credit Report Data:
{json.dumps(credit_data, indent=2)}

Identify:
1. Personal information errors (wrong name, address, SSN, DOB)
2. Duplicate accounts (same debt listed multiple times)
3. Accounts that may not belong to the user
4. Incorrect balances or limits
5. Obsolete information (debts older than 7 years, bankruptcies older than 10 years)
6. Unauthorized hard inquiries
7. Inaccurate payment history
8. Medical debt under $500 (should be removed per 2023 rules)
9. Any other FCRA violations

For EACH error found, return JSON in this format:
{{
  "errors": [
    {{
      "id": "ERR001",
      "category": "Account Error",
      "severity": "High/Medium/Low",
      "description": "Brief description of the error",
      "fcra_violation": "Specific FCRA section violated",
      "affected_item": "Account or item name",
      "dispute_strategy": "How to dispute this",
      "success_likelihood": 75,
      "potential_impact": "Points impact if removed"
    }}
  ]
}}

Return ONLY valid JSON."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        response_text = message.content[0].text
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        result = json.loads(response_text)
        return result.get("errors", [])
    except:
        return []

def generate_dispute_letter(error, user_info, bureau_name, client):
    """Generate a personalized dispute letter"""
    prompt = f"""Generate a professional credit dispute letter for the following error:

Error Details:
{json.dumps(error, indent=2)}

User Information:
Name: {user_info.get('name', 'John Doe')}
Address: {user_info.get('address', '123 Main St, City, ST 12345')}
SSN Last 4: {user_info.get('ssn_last4', 'XXXX')}
DOB: {user_info.get('dob', 'MM/DD/YYYY')}

Bureau: {bureau_name}

Generate a complete dispute letter that:
1. Uses proper business letter format
2. Cites specific FCRA sections (particularly Section 611 and 1681e(b))
3. Clearly describes the error
4. Requests investigation within 30 days
5. Demands correction or deletion
6. Maintains professional, assertive tone
7. Mentions sending via certified mail
8. Requests written confirmation

Return the complete letter text."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text

def create_letter_docx(letter_text, filename="dispute_letter.docx"):
    """Create a downloadable Word document"""
    doc = Document()
    
    # Set margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
    
    # Add content
    for line in letter_text.split('\n'):
        p = doc.add_paragraph(line)
        p.style.font.size = Pt(12)
        p.style.font.name = 'Times New Roman'
    
    # Save to BytesIO
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def get_logo_base64():
    """Convert logo to base64 for embedding in HTML"""
    import base64
    try:
        with open("logo.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

def generate_credit_plan(credit_data, errors, client):
    """Generate a personalized 90-day credit building plan"""
    prompt = f"""Create a personalized 90-day credit building action plan based on this credit profile:

Credit Data Summary:
- Number of accounts: {len(credit_data.get('accounts', []))}
- Negative items: {len(credit_data.get('negative_items', []))}
- Errors found: {len(errors)}
- Public records: {len(credit_data.get('public_records', []))}

Errors to dispute:
{json.dumps(errors[:5], indent=2)}

Create a practical, actionable 90-day plan with:
1. Month 1: Immediate actions (dispute letters, basic cleanup)
2. Month 2: Building positive history (payment strategies, authorized user, secured card)
3. Month 3: Optimization (credit limit increases, follow-ups)

Include specific weekly action items, tips for credit mix, and budget recommendations.
Format it clearly with headers and bullet points."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text

# Main App UI
def main():
    # Initialize session states
    if 'show_landing' not in st.session_state:
        st.session_state.show_landing = True
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    # Show landing page first (if not authenticated)
    if st.session_state.show_landing and not st.session_state.authenticated:
        from landing_page import landing_page
        landing_page()
        return
    
    # Show login if not authenticated
    if not st.session_state.authenticated:
        auth.show_login_page()
        return
    
    # Show user dashboard in sidebar
    auth.show_user_dashboard()

    # Admin panel for admins
    import admin_system
    if admin_system.is_admin(st.session_state.user['email']):
        admin_system.show_admin_panel()
   
    # Handle upgrade modal
    import stripe_integration
    
    # Check for checkout success/cancel
    stripe_integration.handle_checkout_success()
    
    # Show upgrade modal if requested
    if st.session_state.get('show_upgrade', False):
        st.markdown("## 🚀 Choose Your Plan")
        stripe_integration.show_upgrade_options()
        
        if st.button("← Back to Dashboard"):
            st.session_state.show_upgrade = False
            st.rerun()
        
        st.stop()  # Don't show main app
    
    # Show subscription management if requested
    if st.session_state.get('show_manage', False):
        st.markdown("## 🔧 Manage Your Subscription")
        stripe_integration.show_manage_subscription()
        
        if st.button("← Back to Dashboard"):
            st.session_state.show_manage = False
            st.rerun()
        
        st.stop()  # Don't show main app
    # Credit CPR Branded Header
    st.markdown("""
    <div class="main-header">
        <div class="logo-container">
            <img src="data:image/png;base64,{}" width="400" alt="Credit CPR Logo">
        </div>
        <h1 class="hero-title">Credit CPR - AI Credit Repair Assistant</h1>
        <p class="hero-tagline">Bringing Your Credit Back to Life</p>
        <p class="hero-subtext">Analyze credit reports, identify FCRA violations, and generate professional dispute letters - powered by AI.</p>
    </div>
    """.format(get_logo_base64()), unsafe_allow_html=True)
    
    # Critical disclaimer
    with st.expander("IMPORTANT LEGAL NOTICE - READ BEFORE USING", expanded=True):
        st.warning("""
        **THIS TOOL PROVIDES EDUCATIONAL INFORMATION ONLY**
        
        This application is NOT:
        - Legal advice or a substitute for an attorney
        - A credit repair organization (as defined by CRORA)
        - A guarantee of specific results
        - Financial advice
        
        We do NOT:
        - Charge fees for credit repair services
        - Make promises about outcomes
        - Store your credit report or personal data
        - Advise you to make false statements
        
        You have the right to dispute inaccurate information yourself for FREE under the Fair Credit Reporting Act (FCRA).
        
        For legal matters, consult a licensed attorney. This tool helps you understand your rights and exercise them yourself.
        """)
    
    # Sidebar for user information
    with st.sidebar:
        col1, col2 = st.columns([1, 4])

        with col1:
            st.image("assets/shield.png", width=26)

        with col2:
            st.markdown("### Your Information")

        st.caption("Used to personalize dispute letters")

        user_name = st.text_input("Full Legal Name", value=st.session_state.user_info.get('name', ''))
        user_address = st.text_area("Current Address", value=st.session_state.user_info.get('address', ''))
        user_ssn = st.text_input("Last 4 of SSN (Optional)", max_chars=4, value=st.session_state.user_info.get('ssn_last4', ''))
        user_dob = st.text_input("Date of Birth (MM/DD/YYYY)", value=st.session_state.user_info.get('dob', ''))
        
        if st.button("Save Information", use_container_width=True):
            st.session_state.user_info = {
                'name': user_name,
                'address': user_address,
                'ssn_last4': user_ssn,
                'dob': user_dob
            }
            st.success("[OK] Information saved!")
        
        st.divider()
        st.caption("💡 **Tip:** Fill this out before uploading your report")
    
    # Main content area
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📤 Upload & Analyze",
        "📝 Dispute Letters",
        "📈 Credit Plan",
        "💬 AI Assistant",
        "📊 Score Tracker",
        "📅 Dispute Tracker",
        "🤖 AI Credit Coach"
    ])
    
    with tab1:
        st.header("Step 1: Upload Your Credit Report")
        st.info("📄 Upload a PDF from Equifax, Experian, TransUnion, or AnnualCreditReport.com")
        
        uploaded_file = st.file_uploader("Choose your credit report PDF", type=['pdf'])
        
        if uploaded_file is not None:
            with st.spinner("📖 Reading PDF..."):
                raw_text = extract_text_from_pdf(uploaded_file)
            
            if raw_text:
                st.success("[OK] PDF loaded successfully!")
                
                with st.expander("📄 View extracted text (first 1000 characters)"):
                    st.text(raw_text[:1000] + "...")
                
                if st.button("🔍 Analyze Credit Report with AI", type="primary", use_container_width=True):
                    # CHECK USAGE LIMITS
                    user_id = st.session_state.user['id']
                    can_analyze, message = auth.can_analyze_report(user_id)
                    
                    if not can_analyze:
                        st.error(message)
                        
                        import stripe_integration
                        if st.button("🚀 Upgrade to Basic ($19/mo) or Pro ($29/mo)", type="primary", use_container_width=True):
                           st.session_state.show_upgrade = True
                           st.rerun()
        
                        st.stop()
                    
                    st.info(message)  # Show remaining analyses
                    
                    client = get_anthropic_client()
                    
                    # Parse the report
                    with st.spinner("🤖 AI is structuring your credit report data..."):
                        credit_data = parse_credit_report_with_ai(raw_text, client)
                        st.session_state.credit_data = credit_data
                    
                    st.success("✅ Report structured!")
                    
                    # Show parsed data
                    with st.expander("📊 Structured Credit Data"):
                        st.json(credit_data)
                    
                    # Analyze for errors
                    with st.spinner("🔍 Analyzing for errors and FCRA violations..."):
                        errors = analyze_for_errors(credit_data, client)
                        st.session_state.errors_found = errors
                        st.session_state.analysis_complete = True
                    
                    # RECORD THE ANALYSIS
                    auth.record_analysis(user_id, uploaded_file.name, len(errors))
                    
                    if errors:
                        st.balloons()
                        st.success(f"🎯 Found {len(errors)} potential issues to dispute!")
                    else:
                        st.info("No obvious errors detected, but you can still review your report manually.")
        
        # Display errors if analysis is complete
        if st.session_state.analysis_complete and st.session_state.errors_found:
            st.divider()
            st.header("🎯 Errors & Issues Found")
            
            for idx, error in enumerate(st.session_state.errors_found):
                severity_color = {
                    "High": "🔴",
                    "Medium": "🟡", 
                    "Low": "🟢"
                }.get(error.get('severity', 'Medium'), "⚪")
                
                with st.expander(f"{severity_color} {error.get('category', 'Error')} - {error.get('description', 'Unknown issue')[:80]}..."):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Severity:** {error.get('severity', 'N/A')}")
                        st.write(f"**Category:** {error.get('category', 'N/A')}")
                        st.write(f"**Affected Item:** {error.get('affected_item', 'N/A')}")
                    
                    with col2:
                        st.write(f"**Success Likelihood:** {error.get('success_likelihood', 'N/A')}%")
                        st.write(f"**Potential Impact:** {error.get('potential_impact', 'N/A')}")
                    
                    st.write(f"**Description:** {error.get('description', 'No description')}")
                    st.write(f"**FCRA Violation:** {error.get('fcra_violation', 'N/A')}")
                    st.write(f"**Dispute Strategy:** {error.get('dispute_strategy', 'N/A')}")
    
    with tab2:
        st.header("📝 Generate Dispute Letters")
        
        if not st.session_state.analysis_complete:
            st.info("👈 Please upload and analyze a credit report first")
        elif not st.session_state.errors_found:
            st.info("No errors were found to dispute")
        else:
            st.write(f"**{len(st.session_state.errors_found)} errors ready to dispute**")
            
            # Bureau selection
            bureau = st.selectbox(
                "Select Credit Bureau",
                ["Equifax", "Experian", "TransUnion"]
            )
            
            # Error selection
            error_options = [
                f"{e.get('category', 'Error')} - {e.get('description', 'Unknown')[:60]}" 
                for e in st.session_state.errors_found
            ]
            
            selected_error_idx = st.selectbox(
                "Select Error to Dispute",
                range(len(error_options)),
                format_func=lambda x: error_options[x]
            )
            
            selected_error = st.session_state.errors_found[selected_error_idx]
            
            # Show error details
            with st.expander("📋 Error Details"):
                st.json(selected_error)
            
            # Generate letter button
            if st.button("✍️ Generate Dispute Letter", type="primary", use_container_width=True):
                if not st.session_state.user_info.get('name'):
                    st.warning("Please fill in your information in the sidebar first")
                else:
                    client = get_anthropic_client()
                    
                    with st.spinner("✍️ AI is writing your dispute letter..."):
                        letter_text = generate_dispute_letter(
                            selected_error,
                            st.session_state.user_info,
                            bureau,
                            client
                        )
                    
                    st.success("[OK] Letter generated!")
                    
                    # Display letter
                    st.text_area("Your Dispute Letter", letter_text, height=400)
                    
                    # Download button
                    doc_buffer = create_letter_docx(letter_text)
                    st.download_button(
                        label="📥 Download as Word Document",
                        data=doc_buffer,
                        file_name=f"dispute_letter_{bureau}_{datetime.now().strftime('%Y%m%d')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                    
                    st.divider()
                    st.info("""
                    **Next Steps:**
                    1. Review the letter carefully
                    2. Gather supporting documents (if any)
                    3. Print and sign the letter
                    4. Send via **Certified Mail** with return receipt
                    5. Keep copies of everything
                    6. Bureau has 30 days to investigate
                    """)
    
    with tab3:
        st.header("📈 Your Credit Building Plan")
        
        if not st.session_state.analysis_complete:
            st.info("👈 Please upload and analyze a credit report first")
        else:
            if st.button("🚀 Generate My 90-Day Action Plan", type="primary", use_container_width=True):
                client = get_anthropic_client()
                
                with st.spinner("🤖 AI is creating your personalized credit plan..."):
                    plan = generate_credit_plan(
                        st.session_state.credit_data,
                        st.session_state.errors_found,
                        client
                    )
          
                st.success("[OK] Your plan is ready!")
                st.markdown(plan)
                
                # Download plan
                plan_buffer = create_letter_docx(plan, "credit_building_plan.docx")
                st.download_button(
                    label="📥 Download Plan as Word Document",
                    data=plan_buffer,
                    file_name=f"credit_plan_{datetime.now().strftime('%Y%m%d')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
                
    with tab4:
        from chat_assistant import show_chat_assistant
        show_chat_assistant()

    with tab5:
        st.header("📊 Credit Score Tracker")

        user_plan = (st.session_state.get("user") or {}).get("plan", "free")
        is_paid = user_plan in ("basic", "pro", "premium")

        if not is_paid:
            st.info("🔒 Upgrade to track and monitor your credit scores over time.")
            if st.button("🚀 Upgrade Now", use_container_width=True, key="upgrade_score"):
                st.session_state.show_upgrade = True
                st.session_state.upgrade_source = "score_tracker"
                st.rerun()
            st.stop()

        import sqlite3
        conn = sqlite3.connect(auth.DB_PATH)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS score_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                bureau TEXT,
                score INTEGER,
                note TEXT,
                logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

        # --- Log New Score ---
        with st.expander("➕ Log New Score", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                bureau = st.selectbox("Bureau", ["Experian", "Equifax", "TransUnion"])
            with col2:
                score = st.number_input("Score", min_value=300, max_value=850, value=650)
            with col3:
                note = st.text_input("Note (optional)", placeholder="e.g. After dispute")

            def score_color(s):
                if s >= 800: return "#2E8B57", "Exceptional"
                elif s >= 740: return "#7CB342", "Very Good"
                elif s >= 670: return "#FFC107", "Good"
                elif s >= 580: return "#FF9800", "Fair"
                else: return "#F44336", "Poor"

            sc, sl = score_color(score)
            st.markdown(f"<div style='background:{sc}20;border-left:4px solid {sc};padding:0.5rem 1rem;border-radius:6px;'><strong style='color:{sc};font-size:1.2rem;'>{score}</strong> <span style='color:#666;'>— {sl}</span></div>", unsafe_allow_html=True)

            if st.button("💾 Save Score", type="primary", use_container_width=True):
                c.execute("INSERT INTO score_history (user_id, bureau, score, note) VALUES (?, ?, ?, ?)",
                          (st.session_state.user["id"], bureau, score, note))
                conn.commit()
                st.success(f"✅ {bureau} score of {score} saved!")
                st.rerun()

        # --- Fetch all scores ---
        c.execute("SELECT bureau, score, note, logged_at FROM score_history WHERE user_id = ? ORDER BY logged_at ASC",
                  (st.session_state.user["id"],))
        rows = c.fetchall()
        conn.close()

        if not rows:
            st.info("👆 Log your first score above to start tracking!")
        else:
            # --- Current scores per bureau ---
            st.subheader("📈 Current Scores")
            latest = {}
            for row in reversed(rows):
                if row[0] not in latest:
                    latest[row[0]] = row

            score_cols = st.columns(3)
            for i, bname in enumerate(["Experian", "Equifax", "TransUnion"]):
                with score_cols[i]:
                    if bname in latest:
                        s = latest[bname][1]
                        sc, sl = score_color(s)
                        st.markdown(f"""
                        <div style='background:{sc}15;border:2px solid {sc};border-radius:12px;padding:1.2rem;text-align:center;'>
                            <div style='font-size:0.8rem;color:#666;'>{bname}</div>
                            <div style='font-size:2.2rem;font-weight:bold;color:{sc};'>{s}</div>
                            <div style='font-size:0.8rem;color:{sc};'>{sl}</div>
                            <div style='font-size:0.7rem;color:#999;'>{str(latest[bname][3])[:10]}</div>
                        </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style='background:#f5f5f5;border:2px dashed #ccc;border-radius:12px;padding:1.2rem;text-align:center;'>
                            <div style='font-size:0.8rem;color:#666;'>{bname}</div>
                            <div style='font-size:1.5rem;color:#ccc;'>—</div>
                            <div style='font-size:0.7rem;color:#999;'>Not logged</div>
                        </div>""", unsafe_allow_html=True)

            # --- Progress metrics ---
            if len(rows) >= 2:
                st.divider()
                st.subheader("📉 Progress")
                first_s = rows[0][1]
                last_s = rows[-1][1]
                change = last_s - first_s
                sym = "+" if change >= 0 else ""
                m1, m2, m3 = st.columns(3)
                m1.metric("Starting Score", first_s)
                m2.metric("Latest Score", last_s, delta=f"{sym}{change} pts")
                m3.metric("Entries Logged", len(rows))

            # --- Chart ---
            st.divider()
            st.subheader("📊 Score Over Time")
            filter_b = st.selectbox("Filter by bureau", ["All", "Experian", "Equifax", "TransUnion"], key="filter_bureau")

            chart_rows = [r for r in rows if filter_b == "All" or r[0] == filter_b]

            if len(chart_rows) >= 2:
                import json
                chart_data = [{"date": str(r[3])[:10], "score": r[1], "bureau": r[0]} for r in chart_rows]
                dates = [d["date"] for d in chart_data]
                scores = [d["score"] for d in chart_data]

                # Build simple line chart with HTML/SVG
                min_s = max(300, min(scores) - 20)
                max_s = min(850, max(scores) + 20)
                w, h = 600, 200
                pts = []
                for i, (d, s) in enumerate(zip(dates, scores)):
                    x = int(40 + (i / max(len(scores)-1, 1)) * (w - 60))
                    y = int(h - 20 - ((s - min_s) / max(max_s - min_s, 1)) * (h - 40))
                    pts.append((x, y, d, s))

                polyline = " ".join([f"{x},{y}" for x, y, _, _ in pts])
                dots = "".join([f'<circle cx="{x}" cy="{y}" r="5" fill="#2E8B57"><title>{d}: {s}</title></circle>' for x, y, d, s in pts])
                labels = "".join([f'<text x="{x}" y="{h-2}" font-size="9" text-anchor="middle" fill="#999">{d[5:]}</text>' for x, y, d, s in pts])

                svg = f"""<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="width:100%;border:1px solid #eee;border-radius:8px;background:#fafafa;">
                    <polyline points="{polyline}" fill="none" stroke="#2E8B57" stroke-width="2.5"/>
                    {dots}{labels}
                    <text x="10" y="20" font-size="10" fill="#999">{max_s}</text>
                    <text x="10" y="{h-20}" font-size="10" fill="#999">{min_s}</text>
                </svg>"""
                st.markdown(svg, unsafe_allow_html=True)
            else:
                st.info("Log at least 2 scores to see your progress chart.")

            # --- AI Insights ---
            st.divider()
            st.subheader("🤖 AI Score Insights")
            if len(rows) >= 1:
                last_score_val = rows[-1][1]
                sc, sl = score_color(last_score_val)
                if last_score_val < 580:
                    st.error(f"Your latest score of **{last_score_val}** is in the **Poor** range. Focus on: paying on time, disputing errors, and reducing collections.")
                elif last_score_val < 670:
                    st.warning(f"Your latest score of **{last_score_val}** is **Fair**. Key moves: dispute any errors, keep utilization under 30%, and avoid new hard inquiries.")
                elif last_score_val < 740:
                    st.info(f"Your latest score of **{last_score_val}** is **Good**. To reach Very Good: keep accounts open, mix credit types, and keep balances low.")
                elif last_score_val < 800:
                    st.success(f"Your latest score of **{last_score_val}** is **Very Good**! You're close to Exceptional. Maintain on-time payments and low utilization.")
                else:
                    st.success(f"🏆 Your latest score of **{last_score_val}** is **Exceptional**! You have access to the best rates available.")

            # --- Full history ---
            with st.expander("📋 Full Score History"):
                for row in reversed(rows):
                    sc, sl = score_color(row[1])
                    st.markdown(f"""<div style='display:flex;align-items:center;padding:0.4rem;border-bottom:1px solid #eee;gap:1rem;'>
                        <span style='color:{sc};font-weight:bold;min-width:45px;'>{row[1]}</span>
                        <span style='background:{sc}20;color:{sc};padding:2px 8px;border-radius:4px;font-size:0.8rem;'>{row[0]}</span>
                        <span style='color:#666;font-size:0.85rem;'>{str(row[3])[:10]}</span>
                        <span style='color:#888;font-size:0.85rem;font-style:italic;'>{row[2] or ""}</span>
                    </div>""", unsafe_allow_html=True)

    with tab6:
        st.header("📅 Dispute Tracker & Tools")

        user_plan_t6 = (st.session_state.get("user") or {}).get("plan", "free")
        is_paid_t6 = user_plan_t6 in ("basic", "pro", "premium")

        if not is_paid_t6:
            st.markdown("""
            <div style='padding:32px;border-radius:14px;background:linear-gradient(135deg,#f0f8f0 0%,#e8f5e9 100%);
                        border:2px solid #2E8B57;text-align:center;box-shadow:0 8px 24px rgba(46,139,87,0.15);margin:20px 0;'>
                <h3 style='color:#1B3A5C;'>🔒 Dispute Tracker is a Paid Feature</h3>
                <p style='color:#444;margin-bottom:8px;'>Track disputes, get automatic follow-up alerts, and email letters directly to credit bureaus.</p>
                <p style='color:#666;font-size:0.9rem;'>Available on Basic ($19/mo), Pro ($29/mo), and Premium plans</p>
            </div>""", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("- 📋 Track all disputes in one place\n- 🔔 Automatic 30-day follow-up alerts\n- ⚠️ Overdue dispute notifications")
            with col2:
                st.markdown("- 📬 Email letters directly to bureaus\n- ✅ Mark disputes as resolved\n- 📊 Dispute stats dashboard")
            if st.button("🚀 Upgrade to Unlock Dispute Tracker", type="primary", use_container_width=True, key="upgrade_disputes"):
                st.session_state.show_upgrade = True
                st.session_state.upgrade_source = "dispute_tracker"
                st.rerun()
        else:
            import sqlite3
            import smtplib
            import ssl
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            conn = sqlite3.connect(auth.DB_PATH)
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS dispute_reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    bureau TEXT,
                    dispute_description TEXT,
                    sent_date TEXT,
                    follow_up_date TEXT,
                    status TEXT DEFAULT 'pending'
                )
            """)
            conn.commit()

            dtab1, dtab2, dtab3 = st.tabs(["📋 My Disputes", "➕ Add Dispute", "📬 Email a Letter"])

            with dtab1:
                c.execute(
                    "SELECT id, bureau, dispute_description, sent_date, follow_up_date, status FROM dispute_reminders WHERE user_id = ? ORDER BY follow_up_date ASC",
                    (st.session_state.user["id"],)
                )
                rows = c.fetchall()

                if not rows:
                    st.info("No disputes tracked yet. Use the **Add Dispute** tab to get started!")
                else:
                    today = datetime.now().date()
                    overdue = [r for r in rows if r[5] == 'pending' and datetime.strptime(r[4], "%Y-%m-%d").date() < today]
                    due_soon = [r for r in rows if r[5] == 'pending' and 0 <= (datetime.strptime(r[4], "%Y-%m-%d").date() - today).days <= 7]
                    upcoming = [r for r in rows if r[5] == 'pending' and (datetime.strptime(r[4], "%Y-%m-%d").date() - today).days > 7]
                    resolved = [r for r in rows if r[5] == 'resolved']

                    if overdue:
                        st.error(f"⚠️ {len(overdue)} dispute(s) are OVERDUE for follow-up!")
                    if due_soon:
                        st.warning(f"🔔 {len(due_soon)} dispute(s) need follow-up within the next 7 days.")

                    s1, s2, s3, s4 = st.columns(4)
                    s1.metric("Total", len(rows))
                    s2.metric("⚠️ Overdue", len(overdue))
                    s3.metric("🔔 Due Soon", len(due_soon))
                    s4.metric("✅ Resolved", len(resolved))

                    st.divider()

                    def show_dispute_row(row, alert_type):
                        rid, bureau, desc, sent, followup, status = row
                        follow_date = datetime.strptime(followup, "%Y-%m-%d").date()
                        days_diff = (follow_date - today).days
                        if alert_type == "overdue":
                            border, icon = "#F44336", "🔴"
                            time_label = f"{abs(days_diff)} days overdue"
                        elif alert_type == "due_soon":
                            border, icon = "#FF9800", "🟡"
                            time_label = f"Follow-up in {days_diff} days"
                        elif alert_type == "upcoming":
                            border, icon = "#2E8B57", "🟢"
                            time_label = f"Follow-up in {days_diff} days"
                        else:
                            border, icon = "#9E9E9E", "✅"
                            time_label = "Resolved"
                        st.markdown(f"""
                        <div style='border-left:4px solid {border};padding:0.75rem 1rem;background:{border}10;border-radius:0 8px 8px 0;margin:0.4rem 0;'>
                            <div style='display:flex;justify-content:space-between;'><strong>{icon} {bureau}</strong><span style='font-size:0.8rem;color:#666;'>{time_label}</span></div>
                            <div style='color:#444;margin:0.25rem 0;'>{desc}</div>
                            <div style='font-size:0.75rem;color:#999;'>Sent: {sent} | Follow-up: {followup}</div>
                        </div>""", unsafe_allow_html=True)
                        if status == 'pending':
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("✅ Resolved", key=f"resolve_{rid}", use_container_width=True):
                                    conn2 = sqlite3.connect(auth.DB_PATH)
                                    conn2.execute("UPDATE dispute_reminders SET status = 'resolved' WHERE id = ?", (rid,))
                                    conn2.commit()
                                    conn2.close()
                                    st.rerun()
                            with col2:
                                if st.button("🗑️ Delete", key=f"delete_{rid}", use_container_width=True):
                                    conn2 = sqlite3.connect(auth.DB_PATH)
                                    conn2.execute("DELETE FROM dispute_reminders WHERE id = ?", (rid,))
                                    conn2.commit()
                                    conn2.close()
                                    st.rerun()

                    if overdue:
                        st.markdown("### ⚠️ Overdue")
                        for r in overdue: show_dispute_row(r, "overdue")
                    if due_soon:
                        st.markdown("### 🔔 Due This Week")
                        for r in due_soon: show_dispute_row(r, "due_soon")
                    if upcoming:
                        st.markdown("### 📅 Upcoming")
                        for r in upcoming: show_dispute_row(r, "upcoming")
                    if resolved:
                        with st.expander(f"✅ Resolved ({len(resolved)})"):
                            for r in resolved: show_dispute_row(r, "resolved")

            with dtab2:
                st.subheader("➕ Add New Dispute")
                bureau_d = st.selectbox("Bureau", ["Experian", "Equifax", "TransUnion"], key="dispute_bureau")
                description = st.text_area("Dispute Description", placeholder="e.g. Incorrect late payment on Capital One")
                col1, col2 = st.columns(2)
                with col1:
                    sent_date = st.date_input("Date Letter Sent", datetime.now())
                with col2:
                    follow_up = st.date_input("Follow-up Date", datetime.now() + timedelta(days=35))
                st.caption("💡 Bureaus have 30 days to respond. We recommend following up at day 35.")
                if st.button("💾 Save Dispute", type="primary", use_container_width=True):
                    if description:
                        c.execute(
                            "INSERT INTO dispute_reminders (user_id, bureau, dispute_description, sent_date, follow_up_date) VALUES (?, ?, ?, ?, ?)",
                            (st.session_state.user["id"], bureau_d, description, str(sent_date), str(follow_up))
                        )
                        conn.commit()
                        st.success("✅ Dispute saved!")
                        st.rerun()
                    else:
                        st.warning("Please enter a dispute description.")

            with dtab3:
                st.subheader("📬 Email Dispute Letter")
                if not st.session_state.get('analysis_complete') or not st.session_state.get('errors_found'):
                    st.info("👈 Please upload and analyze a credit report first.")
                else:
                    BUREAU_EMAILS = {"Equifax": "disputeinfo@equifax.com", "Experian": "disputes@experian.com", "TransUnion": "transunion@transunion.com"}
                    col1, col2 = st.columns(2)
                    with col1:
                        sender_email = st.text_input("Your Gmail", placeholder="you@gmail.com", key="sender_email")
                    with col2:
                        sender_password = st.text_input("App Password", type="password", placeholder="16-char password", key="sender_pass")
                    bureau_e = st.selectbox("Bureau", ["Equifax", "Experian", "TransUnion"], key="email_bureau")
                    error_options = [f"{e.get('category','Error')} - {e.get('description','')[:60]}" for e in st.session_state.errors_found]
                    selected_idx = st.selectbox("Select Error", range(len(error_options)), format_func=lambda x: error_options[x], key="email_error_idx")
                    selected_error = st.session_state.errors_found[selected_idx]
                    if st.button("✍️ Generate Letter", type="primary", use_container_width=True):
                        if not st.session_state.user_info.get('name'):
                            st.warning("Please fill in your personal info in the sidebar first.")
                        else:
                            client = get_anthropic_client()
                            with st.spinner("✍️ Generating..."):
                                letter = generate_dispute_letter(selected_error, st.session_state.user_info, bureau_e, client)
                            st.session_state.email_letter = letter
                            st.session_state.email_bureau_name = bureau_e
                            st.success("✅ Letter ready!")
                    if st.session_state.get('email_letter'):
                        letter = st.session_state.email_letter
                        bureau_name = st.session_state.email_bureau_name
                        st.text_area("📄 Preview (editable)", letter, height=250, key="email_preview")
                        col1, col2 = st.columns(2)
                        with col1:
                            send_to_bureau = st.checkbox(f"Send to {bureau_name}", value=True)
                        with col2:
                            send_copy = st.checkbox("Send copy to me", value=True)
                        if st.button("📤 Send", type="primary", use_container_width=True):
                            if not sender_email or not sender_password:
                                st.error("Please enter your Gmail credentials.")
                            else:
                                final_letter = st.session_state.get('email_preview', letter)
                                subject = f"Credit Report Dispute - {st.session_state.user_info.get('name', 'Consumer')}"
                                success_count = 0
                                def send_email_fn(to, subj, body):
                                    try:
                                        msg = MIMEMultipart()
                                        msg['From'] = sender_email; msg['To'] = to; msg['Subject'] = subj
                                        msg.attach(MIMEText(body, 'plain'))
                                        ctx = ssl.create_default_context()
                                        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=ctx) as srv:
                                            srv.login(sender_email, sender_password)
                                            srv.sendmail(sender_email, to, msg.as_string())
                                        return True, "Sent!"
                                    except smtplib.SMTPAuthenticationError:
                                        return False, "Auth failed. Use a Gmail App Password."
                                    except Exception as e:
                                        return False, str(e)
                                with st.spinner("📤 Sending..."):
                                    if send_to_bureau:
                                        ok, msg = send_email_fn(BUREAU_EMAILS[bureau_name], subject, final_letter)
                                        if ok: success_count += 1; st.success(f"✅ Sent to {bureau_name}!")
                                        else: st.error(f"❌ {msg}")
                                    if send_copy:
                                        ok, msg = send_email_fn(sender_email, f"[COPY] {subject}", final_letter)
                                        if ok: success_count += 1; st.success("✅ Copy sent!")
                                        else: st.error(f"❌ {msg}")
                                if success_count > 0:
                                    today_str = datetime.now().strftime("%Y-%m-%d")
                                    followup_str = (datetime.now() + timedelta(days=35)).strftime("%Y-%m-%d")
                                    c.execute("INSERT INTO dispute_reminders (user_id, bureau, dispute_description, sent_date, follow_up_date) VALUES (?, ?, ?, ?, ?)",
                                              (st.session_state.user["id"], bureau_name, selected_error.get('description', 'Dispute'), today_str, followup_str))
                                    conn.commit()
                                    st.info(f"🔔 Follow-up reminder set for {followup_str}")
            conn.close()

    with tab7:
        st.header("🤖 AI Credit Coach")
        st.caption("Your personalized AI coach — daily action steps, progress insights, and smart credit guidance.")

        user_plan_t7 = (st.session_state.get("user") or {}).get("plan", "free")
        is_paid_t7 = user_plan_t7 in ("basic", "pro", "premium")

        if not is_paid_t7:
            st.markdown("""
            <div style='padding:32px;border-radius:14px;background:linear-gradient(135deg,#f0f8f0 0%,#e8f5e9 100%);
                        border:2px solid #2E8B57;text-align:center;box-shadow:0 8px 24px rgba(46,139,87,0.15);margin:20px 0;'>
                <h3 style='color:#1B3A5C;'>🔒 AI Credit Coach is a Paid Feature</h3>
                <p style='color:#444;'>Get a personalized daily action plan, smart insights, and step-by-step coaching.</p>
                <p style='color:#666;font-size:0.9rem;'>Available on Basic ($19/mo), Pro ($29/mo), and Premium plans</p>
            </div>""", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("- 📅 Personalized 30-day action plan\n- 🎯 Daily focus — one action at a time\n- 🤖 AI-powered credit coaching")
            with col2:
                st.markdown("- 📊 Progress check & analysis\n- 💡 Smart insights based on your report\n- 🏆 Score improvement roadmap")
            if st.button("🚀 Upgrade to Unlock AI Credit Coach", type="primary", use_container_width=True, key="upgrade_coach"):
                st.session_state.show_upgrade = True
                st.session_state.upgrade_source = "ai_coach"
                st.rerun()
        else:
            if user_plan_t7 == "basic":
                st.success("🔵 Basic Plan Active")
            else:
                st.success("⭐ Pro/Premium Plan Active")

            has_report = st.session_state.get('analysis_complete', False)
            credit_data = st.session_state.get('credit_data', {})
            errors = st.session_state.get('errors_found', [])

            coach_tab1, coach_tab2, coach_tab3 = st.tabs(["📅 My Action Plan", "🎯 Today's Focus", "📊 Progress Check"])

            with coach_tab1:
                st.subheader("Your Personalized 30-Day Action Plan")
                if not has_report:
                    st.info("👈 Upload and analyze a credit report first for a personalized plan.")
                else:
                    if st.button("🤖 Generate My Action Plan", type="primary", use_container_width=True):
                        client = get_anthropic_client()
                        with st.spinner("🤖 Building your plan..."):
                            prompt = f"""You are an expert credit coach. Create a detailed 30-day credit improvement plan.
Credit Profile: Accounts: {len(credit_data.get('accounts', []))}, Negatives: {len(credit_data.get('negative_items', []))}, Errors: {len(errors)}, Top Issues: {", ".join([e.get('category','') for e in errors[:3]])}
Create week-by-week plan: Week 1 immediate actions, Week 2 momentum, Week 3 optimization, Week 4 review.
Be specific, actionable, encouraging. Use clear headers and bullet points."""
                            response = client.messages.create(model="claude-3-5-sonnet-latest", max_tokens=2000, messages=[{"role": "user", "content": prompt}])
                            st.session_state.coach_plan = response.content[0].text
                    if st.session_state.get('coach_plan'):
                        st.markdown(st.session_state.coach_plan)
                        plan_buffer = create_letter_docx(st.session_state.coach_plan)
                        st.download_button("📥 Download Action Plan", data=plan_buffer,
                                           file_name=f"credit_action_plan_{datetime.now().strftime('%Y%m%d')}.docx",
                                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                           use_container_width=True)

            with coach_tab2:
                st.subheader("🎯 Today's Focus")
                if not has_report:
                    st.info("👈 Upload and analyze a credit report first.")
                else:
                    if st.button("🔄 Get Today's Action", type="primary", use_container_width=True):
                        client = get_anthropic_client()
                        with st.spinner("🤖 Getting your daily focus..."):
                            top_error = errors[0] if errors else None
                            prompt = f"""Credit coach: Give ONE specific actionable task for today.
Top issue: {top_error.get('category', 'N/A') if top_error else 'None'} - {top_error.get('description', '') if top_error else ''}
Give: 1) Today's action (specific), 2) Why it matters, 3) How to do it (steps), 4) Time required, 5) Expected impact. One task only."""
                            response = client.messages.create(model="claude-3-5-sonnet-latest", max_tokens=600, messages=[{"role": "user", "content": prompt}])
                            st.session_state.todays_focus = response.content[0].text
                    if st.session_state.get('todays_focus'):
                        st.markdown(st.session_state.todays_focus)
                        if st.button("✅ Mark as Done", type="primary"):
                            st.success("🎉 Great work! Come back tomorrow for your next action.")
                            st.balloons()
                            del st.session_state.todays_focus

            with coach_tab3:
                st.subheader("📊 Progress Check")
                import sqlite3 as _sqlite3
                conn3 = _sqlite3.connect(auth.DB_PATH)
                c3 = conn3.cursor()
                c3.execute("SELECT COUNT(*) FROM score_history WHERE user_id = ?", (st.session_state.user["id"],))
                score_count = c3.fetchone()[0]
                c3.execute("SELECT COUNT(*) FROM dispute_reminders WHERE user_id = ?", (st.session_state.user["id"],))
                dispute_count = c3.fetchone()[0]
                c3.execute("SELECT COUNT(*) FROM dispute_reminders WHERE user_id = ? AND status = 'resolved'", (st.session_state.user["id"],))
                resolved_count = c3.fetchone()[0]
                conn3.close()

                p1, p2, p3, p4 = st.columns(4)
                p1.metric("Scores Logged", score_count)
                p2.metric("Disputes Filed", dispute_count)
                p3.metric("Resolved", resolved_count)
                p4.metric("Errors Found", len(errors) if has_report else "—")

                st.divider()
                if score_count > 0 or dispute_count > 0:
                    if st.button("🤖 Get Progress Analysis", type="primary", use_container_width=True):
                        client = get_anthropic_client()
                        with st.spinner("Analyzing your progress..."):
                            prompt = f"""Credit coach: Give encouraging progress report.
Stats: Scores logged: {score_count}, Disputes filed: {dispute_count}, Resolved: {resolved_count}, Errors identified: {len(errors) if has_report else 0}
Give: 1) Progress assessment, 2) What's working, 3) Next priority, 4) Encouragement. Personal and uplifting."""
                            response = client.messages.create(model="claude-3-5-sonnet-latest", max_tokens=600, messages=[{"role": "user", "content": prompt}])
                            st.markdown(response.content[0].text)
                else:
                    st.info("Start logging scores and filing disputes to see your progress analysis here!")


    # Footer
    st.markdown(
        """
        <hr style="margin-top: 40px; margin-bottom: 20px;">

        <div style="text-align: center;">

        <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 10px;">
            <img src="data:image/png;base64,{}" width="32">
            <h3 style="margin: 0;">
                Credit CPR - AI Credit Repair Assistant
            </h3>
        </div>

        <p style="font-weight: 600; margin-bottom: 8px;">
            Bringing Your Credit Back to Life
        </p>

        <p style="font-size: 13px; opacity: 0.75;">
            Built to help you exercise your FCRA rights | Not affiliated with any credit bureau
        </p>

        <p style="font-size: 13px; opacity: 0.75;">
            This tool does not store your credit report or personal information
        </p>

        <p style="margin-top: 1rem; font-size: 13px; font-weight: 600;">
            © 2026 Credit CPR. All rights reserved.
        </p>

        </div>
        """.format(get_shield_base64()),
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
