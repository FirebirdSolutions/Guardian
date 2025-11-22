@echo off
REM Build Guardian Training Dataset
REM Combines instructions.jsonl + prompts.jsonl + outputs.jsonl

echo.
echo ========================================
echo   Build Guardian Training Dataset
echo ========================================
echo.
echo This script combines:
echo   - instructions.jsonl (system templates)
echo   - prompts.jsonl (user observations)
echo   - outputs.jsonl (expected responses)
echo.
echo Into: guardian-alpaca-built.jsonl
echo.

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Change to script directory
cd /d "%SCRIPT_DIR%"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.x from https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo Building dataset...
echo.

REM Run the build script
python build-dataset.py

echo.
if errorlevel 1 (
    echo.
    echo Build failed! Check error messages above.
    echo.
) else (
    echo.
    echo Build completed successfully!
    echo Output: guardian-alpaca-built.jsonl
    echo.
)

pause
