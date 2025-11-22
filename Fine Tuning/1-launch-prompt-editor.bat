@echo off
REM Guardian Prompt Editor Launcher - Enhanced Version
REM Composable output builder with checkboxes

echo.
echo ========================================
echo   Guardian Prompt Editor - ENHANCED
echo ========================================
echo.
echo This editor allows you to:
echo   - Create and edit user prompts
echo   - Build outputs with checkboxes (tool calls + sections)
echo   - Browse and select from existing output templates
echo   - Link prompts to instruction templates
echo   - Save changes to prompts.jsonl and outputs.jsonl
echo.
echo NEW: Composable output builder with:
echo   - Tool call checkboxes (get_crisis_resources, log_incident, etc.)
echo   - Section checkboxes (RISK LEVEL, PATTERNS, ACTION, etc.)
echo   - Live preview of composed output
echo.
echo Opening enhanced editor in your default browser...
echo.

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Launch the enhanced HTML file in default browser
start "" "%SCRIPT_DIR%prompt-editor-enhanced.html"

echo.
echo Editor launched successfully!
echo.
echo Instructions:
echo 1. Click "Load Files" to load existing data
echo 2. Select a prompt or click "New Prompt"
echo 3. Edit prompt text and link to output template
echo 4. OR click "New Output" to build custom output with checkboxes
echo 5. Click "Save All" when done
echo 6. Run "Build Dataset" script to generate training file
echo.
echo Press any key to exit this window...
pause >nul
