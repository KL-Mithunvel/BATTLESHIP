@echo off
setlocal enabledelayedexpansion

echo.
echo  ============================================
echo   BATTLESHIP -- Project Setup
echo  ============================================
echo.

REM ── Check Python ──────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found.
    echo         Install Python 3.10+ from https://python.org
    echo         Make sure to check "Add Python to PATH" during install.
    pause & exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo [OK] %%v

REM ── Check Node.js ─────────────────────────────
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found.
    echo         Install Node.js 18+ from https://nodejs.org
    pause & exit /b 1
)
for /f "tokens=*" %%v in ('node --version') do echo [OK] Node.js %%v
for /f "tokens=*" %%v in ('npm --version')  do echo [OK] npm %%v

echo.
echo  --- Backend setup ---
echo.

REM Create virtual environment in project root
if exist .venv (
    echo [SKIP] .venv already exists, skipping creation
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause & exit /b 1
    )
    echo [OK] Virtual environment created
)

REM Install Python requirements
call .venv\Scripts\activate.bat
echo Installing Python packages...
pip install --quiet --upgrade pip
pip install --quiet -r backend\requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install Python requirements.
    echo         Check backend\requirements.txt and your internet connection.
    pause & exit /b 1
)
echo [OK] Python packages installed

REM Run tests
echo.
echo  --- Running tests ---
echo.
python -m pytest backend\tests\ -v
if errorlevel 1 (
    echo.
    echo [WARNING] Some tests failed. The game may still work, but check the output above.
    echo.
) else (
    echo.
    echo [OK] All tests passed.
    echo.
)

echo.
echo  --- Frontend setup ---
echo.

cd frontend

echo Installing Node packages...
npm install
if errorlevel 1 (
    echo [ERROR] Failed to install Node packages.
    echo         Check your internet connection and that Node 18+ is installed.
    pause & exit /b 1
)
echo [OK] Node packages installed

cd ..

echo.
echo  ============================================
echo   Setup complete!
echo  ============================================
echo.
echo   To start the game, run:
echo.
echo     python run.py
echo.
echo   That's it. The browser will open automatically.
echo.
echo   For LAN play, share your local IP with friends.
echo   Find it with: ipconfig  (look for IPv4 Address)
echo  ============================================
echo.
pause
