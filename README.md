# 🔍 Fact-Check Agent

An automated fact-checking web application that analyzes PDFs, extracts claims, and verifies them against live web data.

## 🎯 Features

- **PDF Analysis**: Upload and extract text from PDF documents
- **AI-Powered Claim Extraction**: Intelligent identification of factual claims using OpenAI GPT
- **Web Verification**: Search web for evidence to verify claims
- **Detailed Reporting**: Categorize claims as Verified, Unverified, or No Evidence
- **Export Results**: Download verification reports as JSON or CSV
- **Live Deployment**: Deploy-ready with Streamlit Cloud, Render, or Vercel

## 🚀 Quick Start

### Local Development

1. **Clone and Setup**
   ```bash
   cd fact-check-agent
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Run Application**
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Access Web Interface**
   - Open http://localhost:8501

### Deploy to Cloud

#### Streamlit Cloud (Easiest)
1. Push code to GitHub
2. Go to https://share.streamlit.io/
3. Connect your repository
4. Add OPENAI_API_KEY in app secrets
5. Deploy!

#### Render
1. Create `render.yaml` ✓ (already included)
2. Push to GitHub
3. Connect Render to your repo
4. Deploy!

See [deployment.md](deployment.md) for detailed instructions.

## 📋 Project Structure

```
fact-check-agent/
├── streamlit_app.py          # Main web interface
├── pdf_extractor.py          # PDF parsing and text extraction
├── claim_extractor.py        # AI-powered claim identification
├── fact_verifier.py          # Web search and verification
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
├── Dockerfile                # For container deployment
├── render.yaml              # Render deployment config
├── deployment.md            # Deployment guide
└── README.md               # This file
```

## 🔧 Configuration

### Required Environment Variables

```env
OPENAI_API_KEY=sk-...  # OpenAI API key for claim extraction
```

### Optional Environment Variables

```env
GOOGLE_API_KEY=...             # For Google Search API
GOOGLE_SEARCH_ENGINE_ID=...    # For Google Search custom search
```

## 📊 How It Works

1. **Upload PDF**: User uploads a document
2. **Extract Text**: PDF parser extracts all readable text
3. **Identify Claims**: AI analyzes text and identifies factual claims
   - Statistics and numbers
   - Dates and historical events
   - Financial figures
   - Technical specifications
4. **Verify Claims**: System searches web for supporting evidence
5. **Report Results**: Categorize as:
   - ✅ **VERIFIED**: Multiple sources confirm the claim
   - ⚠️ **UNVERIFIED**: Claim not clearly verified or contradicted
   - ❌ **NO_EVIDENCE**: No information found on web
6. **Export**: Download detailed report as JSON/CSV

## 🧪 Testing

### Test with Sample PDFs

1. Create a PDF with:
   - Correct facts (e.g., "The Earth is approximately 4.54 billion years old")
   - Outdated statistics (e.g., "As of 2010, the world population was...")
   - Clearly false claims (e.g., "The Moon is 10,000 km from Earth")

2. Upload and verify
3. Check that correct facts are verified
4. Check that false claims show "No Evidence"

### Example Test Claims

- "Apple's market cap is $2.8 trillion" (check if current)
- "Python was created in 1991" (should verify)
- "The Atlantic Ocean has 2 million islands" (should be flagged)

## 🔐 Security Considerations

- PDFs are processed temporarily and deleted after analysis
- No data is stored on server
- API keys stored in environment variables only
- Use HTTPS in production
- Set rate limits on API endpoints if deployed

## 📈 Performance Tips

- **Streamlit Cloud**: First load ~30 seconds (dependencies), subsequent < 5 seconds
- **Caching**: Search results are cached to reduce API calls
- **Batch Processing**: Process up to 50 claims per upload

## 🐛 Troubleshooting

### "OPENAI_API_KEY not found"
- Add to `.env` file locally
- Add to Streamlit secrets in cloud deployment
- Free trial key available at https://platform.openai.com/api-keys

### PDF extraction fails
- Ensure PDF is not password-protected
- Try OCR-based PDF if scanned document
- Check file size (max recommended: 200MB)

### Verification takes too long
- Normal for 15+ claims (rate limiting)
- Can adjust max claims in sidebar
- Free tier search may be delayed

### No evidence found for correct claims
- Web search is limited by search engine results
- Try rephrasing the claim
- Add author/date for more specific searches

## 📝 License

MIT License - feel free to use and modify

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Better claim extraction (custom ML models)
- Fact database integration (Wikipedia, Snopes)
- Multi-language support
- Citation parsing
- Academic paper verification

## 📧 Support

For issues or questions:
1. Check [deployment.md](deployment.md)
2. Review troubleshooting section above
3. Check Streamlit documentation: https://docs.streamlit.io/

---

**Built with ❤️ using Streamlit, OpenAI, and DuckDuckGo**
