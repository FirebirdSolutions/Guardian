@echo off
REM Guardian Alpaca Editor Launcher
REM This script launches the HTML editor in your default browser

echo.
echo ========================================
echo   Guardian Alpaca Editor
echo ========================================
echo.
echo Opening editor in your default browser...
echo.

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Launch the HTML file in default browser
start "" "%SCRIPT_DIR%guardian-editor.html"

echo.
echo Editor launched successfully!
echo.
echo Instructions:
echo 1. Click "Choose File" and select guardian-alpaca.jsonl
echo 2. Click "Load File" to load the entries
echo 3. Edit, create, or delete entries as needed
echo 4. Click "Download JSONL" to save your changes
echo.
echo Press any key to exit this window...
pause >nul
