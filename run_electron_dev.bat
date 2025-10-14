@echo off
echo ========================================
echo   Pulox Desktop App - Development Mode
echo ========================================
echo.

echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)
echo   Python: OK

echo.
echo Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found! Please install Node.js 16+
    pause
    exit /b 1
)
echo   Node.js: OK

echo.
echo ========================================
echo   Starting Pulox...
echo ========================================
echo.
echo The app will:
echo   1. Start Python backend (port 8000)
echo   2. Launch Electron window
echo.
echo Press Ctrl+C to stop
echo.

cd webapp\electron
npm run dev

pause
