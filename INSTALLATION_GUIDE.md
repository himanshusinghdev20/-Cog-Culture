# Installation & Setup Guide

## System Requirements

- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 500MB free space
- **Internet**: Required for API calls

---

## Option 1: Automated Setup (Recommended)

### Windows
```bash
start_local.bat
```

### macOS/Linux
```bash
chmod +x start_local.sh
./start_local.sh
```

**What the script does:**
1. ✅ Checks Python installation
2. ✅ Creates virtual environment
3. ✅ Installs dependencies
4. ✅ Sets up .env file
5. ✅ Runs tests (optional)
6. ✅ Starts the app

---

## Option 2: Manual Setup

### Step 1: Create Virtual Environment

**Windows (Command Prompt):**
```bash
python -m venv venv
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` prefix in your terminal.

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment

**Windows/macOS/Linux:**
```bash
# Create .env file
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
```

### Step 4: Test Installation

```bash
python test_app.py
```

Expected output:
```
✅ Python 3.11 found
✅ pdfplumber imported
✅ OpenAI imported
✅ duckduckgo_search imported
✅ streamlit imported
```

### Step 5: Run Application

```bash
streamlit run streamlit_app.py
```

Your app will open at: **http://localhost:8501**

---

## Getting OpenAI API Key

1. Go to: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (appears once)
4. Paste into `.env` file:
   ```
   OPENAI_API_KEY=sk-...
   ```
5. Save and restart app

**Free Trial:**
- Initial credit: $5
- Valid for 3 months
- No auto-charge

**Costs:**
- Text extraction/verification: $0.01-0.05 per PDF
- Free tier sufficient for testing

---

## Troubleshooting Installation

### "Python not found"
- **Windows**: Install from https://python.org (check "Add to PATH")
- **macOS**: `brew install python3`
- **Linux**: `sudo apt-get install python3`
- **Verify**: `python --version` or `python3 --version`

### "pip not found"
```bash
python -m pip install --upgrade pip
```

### "Virtual environment not working"
```bash
# Windows
python -m venv venv --clear
venv\Scripts\activate.bat

# macOS/Linux
python3 -m venv venv --clear
source venv/bin/activate
```

### "ModuleNotFoundError"
```bash
# Ensure venv is activated (should see "(venv)" in terminal)
pip install -r requirements.txt --upgrade
```

### "Streamlit not starting"
```bash
# Try running without cached files
streamlit run streamlit_app.py --logger.level=debug
```

### "OPENAI_API_KEY not found"
1. Check if `.env` file exists in project root
2. Verify key is added: `OPENAI_API_KEY=sk-...`
3. Restart Streamlit: `Ctrl+C` then rerun

---

## Dependency Details

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | 1.28+ | Web interface |
| pdfplumber | 0.10+ | PDF extraction |
| openai | 1.3+ | GPT API access |
| duckduckgo-search | 3.9+ | Web search |
| python-dotenv | 1.0+ | Environment config |

### Optional Dependencies

- `google-search-results` - Google Search API
- `selenium` - Advanced web scraping
- `beautifulsoup4` - HTML parsing
- `requests` - HTTP client

---

## Verify Deployment

### Local Test
```bash
# Test PDF extraction
python -c "from pdf_extractor import PDFExtractor; print('✅ OK')"

# Test claim extraction
python -c "from claim_extractor import ClaimExtractor; print('✅ OK')"

# Test fact verification
python -c "from fact_verifier import FactVerifier; print('✅ OK')"
```

### Quick Functional Test
1. Upload a test PDF
2. Click "Verify Claims"
3. Check results display

---

## Uninstall / Clean Up

### Remove Virtual Environment
```bash
# Windows
rmdir /s venv

# macOS/Linux
rm -rf venv
```

### Remove Cache Files
```bash
# Delete Streamlit cache
rm -rf .streamlit/

# Delete Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
```

---

## Advanced Configuration

### Custom Python Version
```bash
python3.11 -m venv venv
```

### Specify Exact Package Versions
Edit `requirements.txt` with specific versions:
```
streamlit==1.28.1
openai==1.3.7
```

### System-wide Installation (Not Recommended)
```bash
pip install -r requirements.txt --user
```

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Add OpenAI API key
3. ✅ Run `test_app.py` to verify
4. ✅ Upload sample PDF
5. ✅ Deploy to cloud

See [QUICKSTART.md](QUICKSTART.md) for next steps.

---

## Support

**Still having issues?**
1. Check [QUICKSTART.md](QUICKSTART.md)
2. Review [deployment.md](deployment.md)
3. Check [ARCHITECTURE.md](ARCHITECTURE.md)

