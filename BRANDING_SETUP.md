# 💚 Credit CPR - Branded Setup Guide

## 🎨 Your Branded Files

You now have a fully branded Credit CPR application with:

✅ **Custom logo** displayed in the header
✅ **Brand colors** (Green #2E8B57 and Navy #1B3A5C)
✅ **Custom tagline** "Bringing Your Credit Back to Life"
✅ **Styled theme** with Credit CPR colors throughout
✅ **Professional footer** with copyright

---

## 📁 File Structure

```
credit-repair-ai/
├── app.py                          # Branded main application
├── logo.png                        # Your Credit CPR logo
├── requirements.txt                # Python dependencies
├── .streamlit/
│   ├── secrets.toml               # Your API key (DO NOT commit to GitHub!)
│   └── config.toml                # Theme colors (rename from .streamlit_config.toml)
└── README.md                       # Setup instructions
```

---

## 🚀 Setup Instructions

### 1. Copy All Files to Your Project

```bash
cd /Users/mike/Desktop/credit-repair-ai

# Make sure you have these files:
# - app.py (updated branded version)
# - logo.png
# - .streamlit_config.toml (rename this!)
```

### 2. Rename Config File

```bash
# Create .streamlit folder if it doesn't exist
mkdir -p .streamlit

# Rename and move the config file
mv .streamlit_config.toml .streamlit/config.toml
```

### 3. Your secrets.toml Should Already Be There

```bash
# Verify it exists
cat .streamlit/secrets.toml

# Should show:
# ANTHROPIC_API_KEY = "sk-ant-..."
```

### 4. Test Locally

```bash
streamlit run app.py
```

**Open your browser** - you should see:
- ✅ Credit CPR logo at the top
- ✅ Green and navy color theme
- ✅ "Bringing Your Credit Back to Life" tagline
- ✅ Professional branded footer

---

## 🌐 Deploy to GitHub & Streamlit Cloud

### Step 1: Initialize Git

```bash
cd /Users/mike/Desktop/credit-repair-ai

# Initialize git
git init

# Add .gitignore to protect sensitive files
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.pyc
.Python
venv/
streamlit-env/

# Secrets - NEVER commit this!
.streamlit/secrets.toml

# OS
.DS_Store

# Test files
*.pdf
test_*
EOF

# Add all files (secrets.toml will be ignored)
git add .

# First commit
git commit -m "Initial commit - Credit CPR branded app"
```

### Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `credit-cpr`
3. Description: "Credit CPR - AI Credit Repair Assistant"
4. Make it **Public** (so Streamlit Cloud can access it)
5. **DON'T** initialize with README (we already have files)
6. Click "Create repository"

### Step 3: Push to GitHub

```bash
# Add GitHub as remote (replace YOUR-USERNAME)
git remote add origin https://github.com/YOUR-USERNAME/credit-cpr.git

# Push your code
git branch -M main
git push -u origin main
```

### Step 4: Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click "Sign in with GitHub"
3. Click "New app"
4. **Repository:** `YOUR-USERNAME/credit-cpr`
5. **Branch:** `main`
6. **Main file path:** `app.py`
7. Click "Advanced settings"
8. Under "Secrets" paste:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-your-key-here"
   ```
9. Click "Deploy!"

**Wait 2-3 minutes** and your app will be live at:
`https://YOUR-USERNAME-credit-cpr.streamlit.app`

---

## 🎨 Customization Options

### Change Colors

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#2E8B57"      # Main green - change this
backgroundColor = "#FFFFFF"    # White background
secondaryBackgroundColor = "#F0F8F0"  # Light tint
textColor = "#1B3A5C"         # Navy text - change this
```

### Add Your Own Domain

You can point your Hostinger domain to your Streamlit app:

1. In your Streamlit app settings, add your custom domain
2. In Hostinger DNS settings, add a CNAME record:
   - Type: `CNAME`
   - Name: `@` or `www`
   - Value: `YOUR-APP.streamlit.app`

---

## 📊 What Your Branded App Includes

### Header
- Credit CPR logo (centered)
- Brand tagline "Bringing Your Credit Back to Life"
- Professional gradient background (navy → green)

### Color Scheme
- **Primary Green:** #2E8B57 (from your logo)
- **Navy Blue:** #1B3A5C (from your logo)
- **Accent Green:** #7CB342 (bright green)

### Styled Elements
- Custom button colors (green gradient)
- Branded tabs with green highlights
- Professional footer with copyright
- Green-tinted backgrounds

### User Experience
- Clean, professional layout
- Consistent branding throughout
- Mobile-responsive design
- Easy-to-use interface

---

## 🔒 Security Reminders

**NEVER commit these files to GitHub:**
- ❌ `.streamlit/secrets.toml` (contains your API key)
- ❌ Credit report PDFs
- ❌ Any user data

**Safe to commit:**
- ✅ `app.py`
- ✅ `logo.png`
- ✅ `.streamlit/config.toml`
- ✅ `requirements.txt`
- ✅ `.gitignore`

---

## 💡 Next Steps

1. ✅ Test the branded app locally
2. ✅ Push to GitHub
3. ✅ Deploy to Streamlit Cloud
4. ✅ (Optional) Connect custom domain
5. ✅ Share with users!

---

## 🆘 Need Help?

**App not showing logo?**
- Make sure `logo.png` is in the same folder as `app.py`
- Check browser console for errors

**Colors not applying?**
- Make sure `.streamlit/config.toml` exists (not `.streamlit_config.toml`)
- Restart Streamlit after changing config

**Deployment issues?**
- Make sure `.gitignore` includes `secrets.toml`
- Verify logo.png is committed to GitHub
- Check Streamlit Cloud logs for errors

---

**Your branded Credit CPR app is ready to launch! 🚀**

*Bringing Your Credit Back to Life* 💚
