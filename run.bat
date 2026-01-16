@echo off
echo ===========================================
echo   AI Study Buddy - Build & Run Script
echo ===========================================
echo.
echo [1/2] Checking and Installing Dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to install dependencies. Check your internet connection.
    pause
    exit /b %errorlevel%
)
echo.
echo [2/2] Starting AI Study Buddy Server...
echo.
echo Open your browser to: http://127.0.0.1:5000
echo.
python app.py
pause
