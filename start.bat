@echo off
echo ============================================================
echo         Financial Analysis System - Quick Start
echo ============================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not detected, please install Python 3.8+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [Step 1/5] Checking Python environment...
python --version
echo.

REM Check virtual environment
if exist ".venv\Scripts\activate.bat" (
    echo [Step 2/5] Virtual environment detected, activating...
    call .venv\Scripts\activate.bat
    echo [OK] Virtual environment activated
    echo.
) else (
    echo [Step 2/5] Virtual environment not detected, skipped
    echo.
)

REM Check dependencies
echo [Step 3/5] Checking dependency packages...
pip show streamlit >nul 2>&1
if %errorlevel% neq 0 (
    echo Dependencies not detected, installing...
    echo.
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Dependency installation failed
        pause
        exit /b 1
    )
    echo.
    echo [OK] Dependencies installed
    echo.
) else (
    echo [OK] Dependencies already installed
    echo.
)

REM Create necessary directories
if not exist ".streamlit" mkdir ".streamlit"
if not exist "outputs" mkdir "outputs"

echo [Step 4/5] Starting application...
echo.

REM Start Streamlit app
echo ============================================================
echo Application is starting...
echo URL: http://localhost:8501
echo ============================================================
echo.
echo [Tip] Press Ctrl+C to stop the application
echo.

streamlit run app.py

REM If application exits abnormally
if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo [ERROR] Application startup failed
    echo ============================================================
    echo.
    echo Please check the following issues:
    echo 1. Ensure all dependencies are installed (pip install -r requirements.txt)
    echo 2. Ensure port 8501 is not in use
    echo 3. Check Python version (3.8+ required)
    echo.
    pause
    exit /b 1
)