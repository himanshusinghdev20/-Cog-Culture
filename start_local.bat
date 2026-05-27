@echo off
REM Fact-Check Agent - Quick Start Script for Windows
REM This script sets up and runs the application

echo.
echo 🔍 Fact-Check Agent - Setup
echo ==============================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% found
echo.

REM Create virtual environment
if not exist "venv\" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated
echo.

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt -q
echo ✅ Dependencies installed
echo.

REM Create .env file if needed
if not exist ".env" (
    echo ⚠️  .env file not found
    echo.
    echo Please create a .env file with your OpenAI API key:
    echo.
    echo OPENAI_API_KEY=your_api_key_here
    echo.
    echo You can get a free API key from: https://platform.openai.com/api-keys
    echo.
    pause
)

REM Run tests (optional)
set /p run_tests="Run tests? (y/n): "
if /i "%run_tests%"=="y" (
    echo.
    echo 🧪 Running tests...
    python test_app.py
    echo.
)

REM Start app
echo 🚀 Starting Fact-Check Agent...
echo Open your browser to: http://localhost:8501
echo.

streamlit run streamlit_app.py
pause
