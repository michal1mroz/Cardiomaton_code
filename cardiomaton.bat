@echo off
setlocal enabledelayedexpansion

echo ============================================
echo  Cardiomaton Application Launcher
echo ============================================

python --version >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.11 or higher from: https://www.python.org/
    pause
    exit /b 1
)

for /f "tokens=1-4 delims=. " %%a in ('python --version') do (
    set "python_version=%%b.%%c.%%d"
)
echo Found Python version: %python_version%

echo.
echo Step 1: Installing dependencies...
call poetry install --no-root --with dev
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo Step 2: Building Cython extensions...
call poetry run build
if errorlevel 1 (
    echo ERROR: Failed to build Cython extensions!
    pause
    exit /b 1
)

echo.
echo Step 3: Starting Cardiomaton...
echo.
cd cardiomaton_code
call poetry run python main_with_front.py

echo.
if errorlevel 1 (
    echo Application exited with error code: %errorlevel%
) else (
    echo Application closed successfully.
)

echo.
pause