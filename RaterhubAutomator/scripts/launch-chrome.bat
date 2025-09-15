@echo off
setlocal enabledelayedexpansion

REM This script launches Google Chrome with remote debugging enabled on port 9222.
REM It is used by the RaterHub Automator to connect and control the browser via Selenium.

REM Set temp directory for Chrome user data.
REM Reads the path from config.json first, falls back to a default if not found.
set "TEMP_DIR="
for /f "delims=" %%i in ('python get_config_value.py chrome_user_data_dir') do set "TEMP_DIR=%%i"

if not defined TEMP_DIR (
    REM Fallback to a default location in the user's temp directory if config value is missing or script fails
    set "TEMP_DIR=%USERPROFILE%\AppData\Local\Temp\chrome_debug_automator"
    echo Warning: Could not read chrome_user_data_dir from config.json. Using default: %TEMP_DIR%
)


REM Create temp directory if it doesn't exist
if not exist "%TEMP_DIR%" (
    echo Creating Chrome debug directory: %TEMP_DIR%
    mkdir "%TEMP_DIR%"
    if errorlevel 1 (
        echo Error: Failed to create directory %TEMP_DIR%
        pause
        exit /b 1
    )
)

REM Get Chrome executable path from config.json
REM Reads the path from config.json first, falls back to common locations if not found.
set "CHROME_EXE="
for /f "delims=" %%i in ('python get_config_value.py chrome_path') do set "CHROME_EXE=%%i"

REM Fallback to trying multiple common paths if config value is missing or script fails
if not defined CHROME_EXE (
    echo Warning: Could not read chrome_path from config.json. Trying common locations...
    set "CHROME_PATHS[0]=C:\Program Files\Google\Chrome\Application\chrome.exe"
    set "CHROME_PATHS[1]=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    set "CHROME_PATHS[2]=%USERPROFILE%\AppData\Local\Google\Chrome\Application\chrome.exe"

    for /L %%i in (0,1,2) do (
        if exist "!CHROME_PATHS[%%i]!" (
            set "CHROME_EXE=!CHROME_PATHS[%%i]!"
            goto :found_chrome
        )
    )

    echo Error: Chrome executable not found in config or common locations.
    echo Please install Google Chrome or update the config.json file.
    pause
    exit /b 1
) else (
    REM Check if the path from config exists
    if not exist "%CHROME_EXE%" (
        echo Error: Chrome executable path from config does not exist: %CHROME_EXE%
        echo Please update the config.json file.
        pause
        exit /b 1
    )
    :found_chrome
    echo Found Chrome at: %CHROME_EXE%
)

echo Using user data directory: %TEMP_DIR%
echo Starting Chrome with remote debugging on port 9222...

REM Start Chrome with debugging enabled
REM --remote-debugging-port=9222: Enables remote debugging on port 9222, allowing Selenium to connect.
REM --user-data-dir="%TEMP_DIR%": Specifies a separate user profile directory to avoid interfering with the main profile.
REM --profile-directory="DebugProfile": Uses a specific profile within the user data directory.
REM --remote-allow-origins=*: Allows connections from any origin (necessary for remote debugging).
REM --no-first-run: Prevents the first-run experience.
REM --disable-infobars: Disables infobars (like "Chrome is being controlled by automated test software").
REM --disable-extensions: Disables browser extensions which can sometimes interfere with automation.
start "" "%CHROME_EXE%" ^
    --remote-debugging-port=9222 ^
    --user-data-dir="%TEMP_DIR%" ^
    --profile-directory="DebugProfile" ^
    --remote-allow-origins=* ^
    --no-first-run ^
    --disable-infobars ^
    --disable-extensions

if errorlevel 1 (
    echo Error: Failed to start Chrome
    pause
    exit /b 1
)

echo Chrome started successfully!
echo You can now run the RaterHub Automator
pause
exit /b 0
