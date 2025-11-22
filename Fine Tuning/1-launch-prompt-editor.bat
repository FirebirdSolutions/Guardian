@echo off
REM Guardian Prompt Editor Launcher
REM Lightweight editor for managing training prompts

echo.
echo ========================================
echo   Guardian Prompt Editor (Lightweight)
echo ========================================
echo.
echo This editor allows you to:
echo   - Create and edit user prompts
echo   - Select output templates by category/risk
echo   - Link prompts to instruction templates
echo   - Save changes to prompts.jsonl
echo.
echo Opening editor in your default browser...
echo.

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Launch the HTML file in default browser
start "" "%SCRIPT_DIR%prompt-editor.html"

echo.
echo Editor launched successfully!
echo.
echo Instructions:
echo 1. Click "Load All Files" to load existing data
echo 2. Select a prompt from the list or create new
echo 3. Edit the prompt text
echo 4. Select an output template from the right panel
echo 5. Click "Save Prompts" when done
echo 6. Use "Build Dataset" script to generate training file
echo.
echo Press any key to exit this window...
pause >nul
