@echo off
REM This script is the main launcher for the RaterHub Automator.
REM It allows the user to choose between running the GUI, CLI, or a setup check.

REM Set Google Cloud Project ID (used for Vertex AI authentication).
REM This should match the project configured for Vertex AI.
set GOOGLE_CLOUD_PROJECT=raterhubautomation

REM Display current configuration and options
echo RaterHub Automator Launcher
echo ============================
echo Google Cloud Project: %GOOGLE_CLOUD_PROJECT%
echo.

:choice_loop
REM Prompt user to choose how to run the automator
echo Choose how to run the automator:
echo 1. GUI Application (Recommended)
echo 2. Command Line Interface
echo 3. Setup Check
echo.
set /p choice="Enter your choice (1-3): "

REM Validate user input
if "%choice%"=="1" (
    echo Starting GUI application...
    REM Execute the GUI script
    python automator_gui.py
    goto :end_script
) else if "%choice%"=="2" (
    echo Starting command line interface...
    REM Execute the CLI script (main.py is the CLI entry point)
    python main.py
    goto :end_script
) else if "%choice%"=="3" (
    echo Running setup check...
    REM Execute a basic setup check
    python -c "import sys; print('Python version:', sys.version); import selenium, PIL, PySimpleGUI; print('All required packages are installed')"
    goto :end_script
) else (
    REM Invalid input - display error and loop back for input
    echo Invalid choice. Please enter 1, 2, or 3.
    echo.
    goto :choice_loop
)

:end_script
REM Pause to keep the console window open after execution
pause
exit /b 0
