@echo off
echo ========================================
echo   Pulox - Install Electron Dependencies
echo ========================================
echo.

echo Step 1: Installing Python dependencies...
echo ----------------------------------------
echo Installing minimal dependencies for Electron app...
pip install -r requirements-electron.txt
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install Python dependencies
    echo.
    echo Try installing manually:
    echo   pip install openai-whisper fastapi uvicorn[standard] python-multipart
    echo.
    pause
    exit /b 1
)
echo   Python deps: OK

echo.
echo Step 2: Installing Node.js dependencies...
echo ----------------------------------------
cd webapp\electron
call npm install
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install Node.js dependencies
    pause
    exit /b 1
)
echo   Node.js deps: OK

cd ..\..

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo To run the app:
echo   1. Double-click: run_electron_dev.bat
echo   2. Or run: cd webapp\electron && npm run dev
echo.
pause
