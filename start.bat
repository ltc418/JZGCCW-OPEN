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
echo Checking if pip is available...
where pip >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip not found, cannot install dependencies
    echo Please install pip: https://pip.pypa.io/en/stable/installing/
    pause
    exit /b 1
)

echo Checking if streamlit is installed...
python -c "import streamlit" 2>nul
if %errorlevel% neq 0 (
    echo Dependencies not detected, installing...
    echo.
    echo Installing Python packages...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Dependency installation failed
        echo.
        echo Please try:
        echo 1. Update pip: python -m pip install --upgrade pip
        echo 2. Clean cache: pip cache purge
        echo 3. Install manually: pip install -r requirements.txt
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

REM Verify openpyxl installation
echo [Step 3.1/5] Verifying critical dependencies...
python -c "import openpyxl" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] openpyxl not found, reinstalling...
    pip install openpyxl
)
echo [OK] Critical dependencies verified
echo.

REM Create necessary directories
echo [Step 4/5] Creating necessary directories...
if not exist ".streamlit" mkdir ".streamlit"
if not exist "outputs" mkdir "outputs"
echo [OK] Directories created
echo.

REM Start Streamlit app
echo [Step 5/5] Starting application...
echo.

echo ============================================================
echo Application is starting...
echo URL: http://localhost:8501
echo ============================================================
echo.
echo [Tip] Press Ctrl+C to stop the application
echo.

REM Start app
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
    echo 4. Check if there are any import errors in app.py
    echo.
    echo For help, run: python check_dependencies.py
    echo.
    pause
    exit /b 1
)