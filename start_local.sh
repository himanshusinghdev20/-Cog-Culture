#!/bin/bash

# Fact-Check Agent - Quick Start Script
# This script sets up and runs the application

set -e

echo "🔍 Fact-Check Agent - Setup"
echo "=============================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION found"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated"

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt -q
echo "✅ Dependencies installed"

# Create .env file if needed
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  .env file not found"
    echo "Please create a .env file with your OpenAI API key:"
    echo ""
    echo "OPENAI_API_KEY=your_api_key_here"
    echo ""
    echo "You can get a free API key from: https://platform.openai.com/api-keys"
    echo ""
    read -p "Press Enter once you've created the .env file..."
fi

# Run tests (optional)
echo ""
read -p "Run tests? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧪 Running tests..."
    python3 test_app.py
    echo ""
fi

# Start app
echo "🚀 Starting Fact-Check Agent..."
echo "Open your browser to: http://localhost:8501"
echo ""

streamlit run streamlit_app.py
