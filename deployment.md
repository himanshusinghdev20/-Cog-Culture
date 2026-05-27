# Fact-Check Agent - Deployment Guide

## Option 1: Streamlit Cloud (Recommended - Easy & Free)

### Prerequisites
- GitHub account
- Streamlit Cloud account (free at https://streamlit.io/cloud)

### Steps

1. **Push code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/fact-check-agent.git
   git push -u origin main
   ```

2. **Create Streamlit Cloud App**
   - Go to https://share.streamlit.io/
   - Click "New app"
   - Select your GitHub repo, branch (main), and file (streamlit_app.py)
   - Click "Deploy"

3. **Add Secrets**
   - In Streamlit Cloud dashboard, go to your app settings
   - Add secrets:
     ```
     OPENAI_API_KEY = "your_key_here"
     ```

4. **Share URL**
   - Your app will be live at: `https://share.streamlit.io/[username]/fact-check-agent`

---

## Option 2: Render (Alternative - Also Free)

### Steps

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 8501
   
   CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501"]
   ```

2. **Create render.yaml**
   ```yaml
   services:
     - type: web
       name: fact-check-agent
       env: python
       plan: free
       pythonVersion: 3.11
       buildCommand: pip install -r requirements.txt
       startCommand: streamlit run streamlit_app.py --server.port $PORT
       envVars:
         - key: OPENAI_API_KEY
           scope: run
           value: your_key_here
   ```

3. **Push to GitHub and Deploy**
   - Connect GitHub repo to Render
   - Deploy automatically

---

## Option 3: Vercel (For Advanced Setup)

Requires converting to Next.js + API routes (more complex).

---

## Testing the Deployment

1. Visit your live URL
2. Upload a test PDF
3. Click "Verify Claims"
4. Check results display correctly

---

## Troubleshooting

### App takes too long to load
- First load with dependencies takes ~30 seconds on free tier
- Subsequent loads are faster

### Fact verification returns no results
- Check internet connectivity
- Verify API keys are set correctly
- DuckDuckGo search may be rate-limited; try again later

### PDF upload fails
- Max file size: 200MB
- Ensure PDF is not corrupted
- Try a different PDF

### Missing OPENAI_API_KEY
- Generate free API key at https://platform.openai.com/api-keys
- Add to Streamlit secrets
- Restart app

---

## Free Tier Limitations

### Streamlit Cloud
- 1 free app
- Sleeps after 30 mins of inactivity
- No email support

### Render
- Free tier apps spin down after 15 mins of inactivity
- Limited compute resources

### Workarounds
- Use paid tiers for production
- Set up monitors to keep app alive
- Cache validation results

---

## Environment Variables Needed

```
OPENAI_API_KEY=sk-... (required for AI extraction)
GOOGLE_API_KEY=... (optional, for Google Search)
GOOGLE_SEARCH_ENGINE_ID=... (optional, for Google Search)
```

---

## Monitoring & Logging

Check deployment logs:
- **Streamlit Cloud**: App settings → View logs
- **Render**: Dashboard → Select service → Logs

Look for:
- API key issues
- Timeout errors
- Rate limiting messages
