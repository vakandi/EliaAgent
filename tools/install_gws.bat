@echo off
:: Google Workspace CLI Installer for Windows
:: Run this script to install the gws command

echo ========================================
echo Google Workspace CLI Installer (Windows)
echo ========================================
echo.

:: Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "PYTHON_SCRIPT=%SCRIPT_DIR%\google_workspace.py"

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    exit /b 1
)

:: Create the gws.bat script
echo Creating gws.bat...

(
echo @echo off
echo :: Google Workspace CLI Wrapper
echo :: Usage: gws [command] [args^^^]
echo.
echo set "SCRIPT_DIR=C:\Users\vakandi\EliaAI\tools"
echo set "PYTHON_SCRIPT=%%SCRIPT_DIR%%\google_workspace.py"
echo.
echo :: Show usage
echo if "%%1"=="" (
echo     echo Google Workspace CLI
echo     echo.
echo     echo Usage: gws [command] [arguments]
echo     echo.
echo     echo Commands:
echo     echo   create-event    Create calendar event
echo     echo   create-task     Create task
echo     echo   list-events     List upcoming events
echo     echo   list-tasks      List tasks
echo     echo   help            Show this help
echo     exit /b 1
echo )
echo.
echo :: Parse command
echo if "%%1"=="create-event" (
echo     if "%%2"=="" (
echo         echo Error: create-event requires summary
echo         exit /b 1
echo     )
echo     python "%%PYTHON_SCRIPT%%" create-event %%2 %%3
echo     exit /b %%errorlevel%%
echo )
echo.
echo if "%%1"=="create-task" (
echo     if "%%2"=="" (
echo         echo Error: create-task requires title
echo         exit /b 1
echo     )
echo     python "%%PYTHON_SCRIPT%%" create-task %%2 %%3
echo     exit /b %%errorlevel%%
echo )
echo.
echo if "%%1"=="list-events" (
echo     python "%%PYTHON_SCRIPT%%" list-events
echo     exit /b %%errorlevel%%
echo )
echo.
echo if "%%1"=="list-tasks" (
echo     python "%%PYTHON_SCRIPT%%" list-tasks
echo     exit /b %%errorlevel%%
echo )
echo.
echo if "%%1"=="help" (
echo     echo Google Workspace CLI
echo     echo.
echo     echo Usage: gws [command] [arguments]
echo     echo.
echo     echo Commands:
echo     echo   create-event    Create calendar event
echo     echo   create-task     Create task
echo     echo   list-events     List upcoming events
echo     echo   list-tasks      List tasks
echo     echo   help            Show this help
echo     exit /b 0
echo )
echo.
echo echo Error: Unknown command '%%1'
echo exit /b 1
) > "%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\gws.bat"

:: Add to PATH if not already there
setx PATH "%PATH%;%USERPROFILE%\AppData\Local\Microsoft\WindowsApps" >nul 2>&1

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo The 'gws' command has been installed to:
echo %USERPROFILE%\AppData\Local\Microsoft\WindowsApps\gws.bat
echo.
echo Note: You may need to restart your terminal/IDE for the command to work.
echo.
echo Usage examples:
echo   gws create-event "Meeting Title" "Description"
echo   gws create-task "Task Title" "Notes"
echo   gws list-events
echo   gws list-tasks
echo.
echo Run 'gws help' for more information.
echo.

:: Verify installation
where gws >nul 2>&1
if errorlevel 1 (
    echo NOTE: Run 'gws' in a NEW terminal window to use the command.
    echo If it doesn''t work, try restarting your terminal/IDE.
)
