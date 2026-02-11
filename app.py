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
from datetime import datetime
import PyPDF2

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
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f8f0;
        border-radius: 8px 8px 0 0;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2E8B57 0%, #7CB342 100%);
        color: white;
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
        st.error("⚠️ **API Key Not Found!**")
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
        st.error(f"⚠️ Invalid API key format. Key should start with 'sk-ant-' but yours starts with '{api_key[:7]}'")
        st.stop()
    
    # Try to import and initialize Anthropic
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        return client
    except ImportError:
        st.error("⚠️ Anthropic library not installed properly!")
        st.info("Run this command: `pip install anthropic`")
        st.stop()
    except Exception as e:
        st.error(f"⚠️ Error initializing Anthropic client: {str(e)}")
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
    # Credit CPR Branded Header
    st.markdown("""
    <div class="main-header">
        <div class="logo-container">
            <img src="data:image/png;base64,{}" width="400" alt="Credit CPR Logo">
        </div>
        <h1 class="hero-title">Credit CPR - AI Credit Repair Assistant</h1>
        <p class="hero-tagline">Bringing Your Credit Back to Life</p>
        <p class="hero-subtext">Analyze credit reports, identify FCRA violations, and generate professional dispute letters — powered by AI.</p>
    </div>
    """.format(get_logo_base64()), unsafe_allow_html=True)
    
    # Critical disclaimer
    with st.expander("⚠️ IMPORTANT LEGAL NOTICE - READ BEFORE USING", expanded=True):
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
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px;">
                <img src="assets/shield.png" width="28">
                <h2 style="margin: 0;">Your Information</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.caption("Used to personalize dispute letters")
        
        user_name = st.text_input("Full Legal Name", value=st.session_state.user_info.get('name', ''))
        user_address = st.text_area("Current Address", value=st.session_state.user_info.get('address', ''))
        user_ssn = st.text_input("Last 4 of SSN (Optional)", max_chars=4, value=st.session_state.user_info.get('ssn_last4', ''))
        user_dob = st.text_input("Date of Birth (MM/DD/YYYY)", value=st.session_state.user_info.get('dob', ''))
        
        if st.button("💾 Save Info"):
            st.session_state.user_info = {
                'name': user_name,
                'address': user_address,
                'ssn_last4': user_ssn,
                'dob': user_dob
            }
            st.success("✅ Information saved!")
        
        st.divider()
        st.caption("💡 **Tip:** Fill this out before uploading your report")
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["📤 Upload & Analyze", "📝 Dispute Letters", "📈 Credit Building Plan"])
    
    with tab1:
        st.header("Step 1: Upload Your Credit Report")
        st.info("📄 Upload a PDF from Equifax, Experian, TransUnion, or AnnualCreditReport.com")
        
        uploaded_file = st.file_uploader("Choose your credit report PDF", type=['pdf'])
        
        if uploaded_file is not None:
            with st.spinner("📖 Reading PDF..."):
                raw_text = extract_text_from_pdf(uploaded_file)
            
            if raw_text:
                st.success("✅ PDF loaded successfully!")
                
                with st.expander("📄 View extracted text (first 1000 characters)"):
                    st.text(raw_text[:1000] + "...")
                
                if st.button("🔍 Analyze Credit Report with AI", type="primary", use_container_width=True):
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
                    st.warning("⚠️ Please fill in your information in the sidebar first")
                else:
                    client = get_anthropic_client()
                    
                    with st.spinner("✍️ AI is writing your dispute letter..."):
                        letter_text = generate_dispute_letter(
                            selected_error,
                            st.session_state.user_info,
                            bureau,
                            client
                        )
                    
                    st.success("✅ Letter generated!")
                    
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
                
                st.success("✅ Your plan is ready!")
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
    
    # Footer
    st.markdown("""
    <hr style="margin-top: 40px; margin-bottom: 20px;">

    <div style="text-align: center; padding-bottom: 10px;">

        <img src="assets/shield.png" width="28" style="margin-bottom: 8px;">

        <h3 style="margin-bottom: 5px;">
            Credit CPR – AI Credit Repair Assistant
        </h3>

        <p style="font-weight: 600; margin-bottom: 8px;">
            Bringing Your Credit Back to Life
        </p>

        <p style="font-size: 13px; opacity: 0.75;">
            Built to help you exercise your FCRA rights | Not affiliated with any credit bureau
        </p>

        <p style="font-size: 13px; opacity: 0.75;">
            ⚠️ This tool does not store your credit report or personal information
        </p>

        <p style="margin-top: 1rem; font-size: 13px; font-weight: 600;">
            © 2026 Credit CPR. All rights reserved.
        </p>
 
    </div>
    """, unsafe_allow_html=True)
   

if __name__ == "__main__":
    main()
