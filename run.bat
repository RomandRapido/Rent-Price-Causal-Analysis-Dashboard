@echo off
echo ============================================
echo   Rent-to-Price Dashboard Setup
echo ============================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check if virtual environment exists
if not exist "venv" (
    echo [1/4] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo       Virtual environment created successfully.
) else (
    echo [1/4] Virtual environment already exists. Skipping...
)

:: Activate virtual environment
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

:: Install/upgrade pip
echo [3/4] Installing dependencies...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo       Dependencies installed successfully.

:: Run the dashboard
echo [4/4] Starting dashboard...
echo.
echo ============================================
echo   Dashboard is starting...
echo   Open your browser to: http://localhost:8501
echo   Press Ctrl+C to stop the server
echo ============================================
echo.
streamlit run dashboard.py

:: Deactivate on exit
call venv\Scripts\deactivate.bat
pause