FROM python:3.11-slim

WORKDIR /app

# Update pip, setuptools, and wheel first
RUN pip install --upgrade pip setuptools wheel

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies with no-build-isolation
RUN pip install --no-cache-dir --only-binary :all: -r requirements.txt || pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create .streamlit directory
RUN mkdir -p .streamlit

# Create streamlit config
RUN echo "[theme]\n \
primaryColor = '#6c63ff'\n \
backgroundColor = '#ffffff'\n \
secondaryBackgroundColor = '#f8f9fa'\n \
textColor = '#262730'\n \
\n \
[client]\n \
showErrorDetails = true\n \
\n \
[server]\n \
port = 8501\n \
headless = true\n \
runOnSave = false" > .streamlit/config.toml

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run streamlit
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--logger.level=info"]
