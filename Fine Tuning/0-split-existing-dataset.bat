@echo off
REM Split Guardian Dataset
REM Splits guardian-alpaca.jsonl into modular components

echo.
echo ========================================
echo   Split Guardian Dataset
echo ========================================
echo.
echo This script splits guardian-alpaca.jsonl into:
echo   - instructions.jsonl (system templates)
echo   - prompts.jsonl (user observations)
echo   - outputs.jsonl (expected responses)
echo.
echo WARNING: This will OVERWRITE existing split files!
echo.

set /p CONTINUE="Continue? (Y/N): "
if /i not "%CONTINUE%"=="Y" (
    echo Cancelled.
    pause
    exit /b 0
)

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

REM Check if guardian-alpaca.jsonl exists
if not exist "guardian-alpaca.jsonl" (
    echo ERROR: guardian-alpaca.jsonl not found!
    echo Please make sure the file is in the same directory.
    echo.
    pause
    exit /b 1
)

echo.
echo Splitting dataset...
echo.

REM Run the split script
python split-dataset.py

echo.
if errorlevel 1 (
    echo.
    echo Split failed! Check error messages above.
    echo.
) else (
    echo.
    echo Split completed successfully!
    echo Files created:
    echo   - instructions.jsonl
    echo   - prompts.jsonl
    echo   - outputs.jsonl
    echo.
    echo You can now use the prompt editor to manage your data.
    echo.
)

pause
