@echo off
REM start_cron_monitor.bat - Launch PowerShell cron monitor as background service
REM
REM This starts the EliaAI cron monitor in a hidden PowerShell window.
REM The monitor runs continuously and triggers EliaAI at configured intervals.
REM
REM Usage:
REM   start_cron_monitor.bat           Start standard monitor
REM   start_cron_monitor.bat morning  Start morning-only monitor

setlocal EnableDelayedExpansion

set "AGENT_DIR=%~dp0"
set "CONFIG_FILE=%AGENT_DIR%.cron_config.json"
set "MORNING_CONFIG_FILE=%AGENT_DIR%.cron_morning_config.json"
set "MONITOR_SCRIPT=%AGENT_DIR%cron_monitor.ps1"

if /i "%~1"=="morning" (
    if not exist "!MORNING_CONFIG_FILE!" (
        echo [ERROR] Morning config not found. Run: manage_cron.bat install-morning
        exit /b 1
    )
    set "TARGET_CONFIG=!MORNING_CONFIG_FILE!"
    echo Starting EliaAI Morning Cron Monitor...
) else (
    if not exist "!CONFIG_FILE!" (
        echo [ERROR] Standard config not found. Run: manage_cron.bat install
        exit /b 1
    )
    set "TARGET_CONFIG=!CONFIG_FILE!"
    echo Starting EliaAI Standard Cron Monitor...
)

if not exist "!MONITOR_SCRIPT!" (
    echo [ERROR] cron_monitor.ps1 not found in: !AGENT_DIR!
    exit /b 1
)

REM Launch PowerShell monitor in hidden window
REM Using -WindowStyle Hidden + start to detach from console
powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File "!MONITOR_SCRIPT!" "!TARGET_CONFIG!" >nul 2>&1

REM Give it a moment to start
timeout /t 2 >nul 2>&1

REM Check if it's running
powershell -Command "Get-Process powershell | Where-Object { $_.MainWindowTitle -like '*EliaAI*' -or $_.CommandLine -like '*cron_monitor*' }" >nul 2>&1
if !ERRORLEVEL!==0 (
    echo [OK] EliaAI Cron Monitor started successfully
    echo [OK] Use: manage_cron.bat show
    echo [OK] Stop with: manage_cron.bat uninstall
) else (
    REM Try alternative - check task list
    tasklist /fi "imagename eq powershell.exe" /fo list 2>nul | findstr /i "cron_monitor" >nul
    if !ERRORLEVEL!==0 (
        echo [OK] EliaAI Cron Monitor started ^(process found^)
    ) else (
        echo [WARN] Monitor may not have started. Check with: manage_cron.bat show
        echo.
        echo If issues persist, try manually:
        echo   powershell -ExecutionPolicy Bypass -File "!MONITOR_SCRIPT!" "!TARGET_CONFIG!"
    )
)

endlocal
