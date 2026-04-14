@echo off
REM manage_cron.bat - EliaAI Cron Manager (Windows)
REM Uses PowerShell background monitor instead of cron
REM
REM ADAPTATION NOTES:
REM   Windows has no native cron. This uses a PowerShell background
REM   scheduler that runs trigger_opencode.bat at configured intervals.
REM
REM   Config is stored in: %AGENT_DIR%\.cron_config.json
REM   Monitor process: EliaAI_CronMonitor (managed via Windows Task)
REM
REM COMMANDS:
REM   install          Install/update standard interval-based scheduler
REM   install-morning  Install/update morning scheduler (MORNING_PROMPT.md)
REM   uninstall        Remove all EliaAI cron jobs
REM   uninstall-morning Remove only morning scheduler
REM   show             Show current scheduler status
REM
REM OPTIONS:
REM   --interval      Interval: 20min, 30min, 1h, 2h, 3h, 4h (default: 1h)
REM   --start         Start hour 0-23 (default: 11)
REM   --end           End hour 0-23 (default: 21)
REM   --morning-hour  Morning run hour 0-23 (default: 10)
REM
REM EXAMPLES:
REM   manage_cron.bat install
REM   manage_cron.bat install --interval 2h --start 10 --end 22
REM   manage_cron.bat install-morning --morning-hour 8
REM   manage_cron.bat uninstall
REM   manage_cron.bat show

setlocal EnableDelayedExpansion

set "AGENT_DIR=%~dp0"
set "CONFIG_FILE=%AGENT_DIR%.cron_config.json"
set "MORNING_CONFIG_FILE=%AGENT_DIR%.cron_morning_config.json"
set "MONITOR_SCRIPT=%AGENT_DIR%cron_monitor.ps1"
set "START_MONITOR_BAT=%AGENT_DIR%start_cron_monitor.bat"

REM ─── Color variables (empty = plain text, set codes for ANSI-capable terminals) ───
set "CYAN="
set "YELLOW="
set "GREEN="
set "RED="
for /f %%A in ('powershell -Command "[console]::OutputEncoding.CodePage" 2^>nul') do set "CODEPAGE=%%A"
if defined CODEPAGE if !CODEPAGE! geq 65001 (
    set "CYAN=94"
    set "YELLOW=93"
    set "GREEN=92"
    set "RED=91"
)

REM Default settings
set "DEFAULT_INTERVAL=1h"
set "DEFAULT_START_HOUR=11"
set "DEFAULT_END_HOUR=21"
set "DEFAULT_MORNING_HOUR=10"

goto :main

:log
echo [INFO] %~1
goto :eof

:ok
echo [OK] %~1
goto :eof

:warn
echo [WARN] %~1
goto :eof

:error
echo [ERROR] %~1 >&2
goto :eof

:cecho
REM Echo helper - prints all text arguments (color codes not implemented)
echo %*
goto :eof

REM ─── Usage ────────────────────────────────────────────────────────────────
:show_usage
echo Usage: manage_cron.bat [command] [OPTIONS]
echo.
echo Commands:
echo   install           Install/update standard interval scheduler
echo   install-morning  Install/update morning scheduler
echo   uninstall         Remove all EliaAI schedulers
echo   uninstall-morning Remove only morning scheduler
echo   show             Show current scheduler status
echo.
echo Options:
echo   --interval      Interval: 20min, 30min, 1h, 2h, 3h, 4h ^(default: 1h^)
echo   --start         Start hour 0-23 ^(default: 11^)
echo   --end           End hour 0-23 ^(default: 21^)
echo   --morning-hour  Morning hour 0-23 ^(default: 10^)
echo   -h, --help      Show this help
echo.
echo Examples:
echo   manage_cron.bat install
echo   manage_cron.bat install --interval 2h --start 10 --end 22
echo   manage_cron.bat install-morning --morning-hour 8
echo   manage_cron.bat show
echo.
echo NOTE: Windows uses PowerShell background scheduler instead of cron.
echo   The monitor runs in background and triggers EliaAI at intervals.
exit /b 0

REM ─── Get interval in minutes ─────────────────────────────────────────────
:get_interval_minutes
set "IVAL_MINUTES=60"
if /i "%~1"=="20min" set "IVAL_MINUTES=20"
if /i "%~1"=="30min" set "IVAL_MINUTES=30"
if /i "%~1"=="1h" set "IVAL_MINUTES=60"
if /i "%~1"=="2h" set "IVAL_MINUTES=120"
if /i "%~1"=="3h" set "IVAL_MINUTES=180"
if /i "%~1"=="4h" set "IVAL_MINUTES=240"
exit /b 0

REM ─── Kill existing monitor ────────────────────────────────────────────────
:kill_monitor
tasklist /fi "imagename eq powershell.exe" /fo list 2>nul | findstr /i "cron_monitor" >nul
if !ERRORLEVEL!==0 (
    taskkill /f /im powershell.exe 2>nul
    timeout /t 1 >nul 2>&1
)
tasklist /fi "imagename eq EliaAI_CronMonitor*" /fo list 2>nul | findstr /i "EliaAI_CronMonitor" >nul
if !ERRORLEVEL!==0 (
    taskkill /f /fi "windowtitle eq EliaAI_CronMonitor*" 2>nul
)
exit /b 0

REM ─── Write standard config ────────────────────────────────────────────────
:write_config
set "IVAL=%~1"
set "START=%~2"
set "END=%~3"

call :get_interval_minutes !IVAL!

(
    echo {
    echo   "type": "standard",
    echo   "interval_minutes": !IVAL_MINUTES!,
    echo   "interval_label": "!IVAL!",
    echo   "start_hour": !START!,
    echo   "end_hour": !END!,
    echo   "agent_dir": "%AGENT_DIR:\=\\%",
    echo   "trigger_script": "%AGENT_DIR%trigger_opencode.bat",
    echo   "log_dir": "%AGENT_DIR%logs",
    echo   "enabled": true,
    echo   "last_run": "",
    echo   "next_run": ""
    echo }
) > "!CONFIG_FILE!"
exit /b 0

REM ─── Write morning config ────────────────────────────────────────────────
:write_morning_config
set "MORNING_H=%~1"

(
    echo {
    echo   "type": "morning",
    echo   "morning_hour": !MORNING_H!,
    echo   "agent_dir": "%AGENT_DIR:\=\\%",
    echo   "trigger_script": "%AGENT_DIR%trigger_morning.bat",
    echo   "log_dir": "%AGENT_DIR%logs",
    echo   "enabled": true,
    echo   "last_run": "",
    echo   "next_run": ""
    echo }
) > "!MORNING_CONFIG_FILE!"
exit /b 0

REM ─── Validate hours ───────────────────────────────────────────────────────
:validate_hours
set "H=%~1"
set "MIN=%~2"
set "MAX=%~3"
if !H! LSS !MIN! (
    call :error "Hour must be !MIN!^-!MAX! (got: !H!)"
    exit /b 1
)
if !H! GTR !MAX! (
    call :error "Hour must be !MIN!^-!MAX! (got: !H!)"
    exit /b 1
)
exit /b 0

REM ─── Install standard scheduler ──────────────────────────────────────────
:do_install
call :log "Installing EliaAI standard scheduler..."

call :write_config "!IVAL!" "!START!" "!END!"

REM Kill existing monitor
call :kill_monitor

REM Start new monitor
call :start_monitor

call :ok "Standard scheduler installed"
call :log "Interval: !IVAL! (every !IVAL_MINUTES! minutes)"
call :log "Active hours: !START!:00 - !END!:00"
call :log "Monitor PID will be shown by the monitor"
exit /b 0

REM ─── Install morning scheduler ────────────────────────────────────────────
:do_install_morning
call :log "Installing EliaAI morning scheduler..."

call :write_morning_config !MORNING_H!

REM Kill existing morning monitor
tasklist /fi "imagename eq powershell.exe" /fo list 2>nul | findstr /i "cron_monitor" >nul
if !ERRORLEVEL!==0 (
    taskkill /f /im powershell.exe 2>nul
    timeout /t 1 >nul 2>&1
)

REM Start morning monitor
call :start_morning_monitor

call :ok "Morning scheduler installed"
call :log "Morning run time: !MORNING_H!:00"
exit /b 0

REM ─── Start standard monitor ──────────────────────────────────────────────
:start_monitor
if not exist "!MONITOR_SCRIPT!" (
    call :error "cron_monitor.ps1 not found: !MONITOR_SCRIPT!"
    exit /b 1
)

call :log "Starting EliaAI cron monitor..."
powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File "!MONITOR_SCRIPT!" "!CONFIG_FILE!" 2>nul
exit /b 0

REM ─── Start morning monitor ────────────────────────────────────────────────
:start_morning_monitor
if not exist "!MONITOR_SCRIPT!" (
    call :error "cron_monitor.ps1 not found: !MONITOR_SCRIPT!"
    exit /b 1
)

call :log "Starting EliaAI morning cron monitor..."
powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File "!MONITOR_SCRIPT!" "!MORNING_CONFIG_FILE!" 2>nul
exit /b 0

REM ─── Uninstall all ────────────────────────────────────────────────────────
:do_uninstall
call :log "Removing EliaAI schedulers..."

call :kill_monitor

if exist "!CONFIG_FILE!" (
    del "!CONFIG_FILE!" >nul 2>&1
    call :ok "Standard scheduler removed"
)

if exist "!MORNING_CONFIG_FILE!" (
    del "!MORNING_CONFIG_FILE!" >nul 2>&1
    call :ok "Morning scheduler removed"
)

REM Also try Task Scheduler
schtasks /query /tn "EliaAI_Cron" 2>nul | findstr /i "EliaAI" >nul
if !ERRORLEVEL!==0 (
    schtasks /delete /tn "EliaAI_Cron" /f >nul 2>&1
    call :ok "Task Scheduler job removed"
)

call :ok "All EliaAI schedulers removed"
exit /b 0

REM ─── Uninstall morning only ───────────────────────────────────────────────
:do_uninstall_morning
call :log "Removing EliaAI morning scheduler..."

if exist "!MORNING_CONFIG_FILE!" (
    del "!MORNING_CONFIG_FILE!" >nul 2>&1
    call :ok "Morning scheduler removed"
)

tasklist /fi "imagename eq powershell.exe" /fo list 2>nul | findstr /i "cron_monitor" >nul
if !ERRORLEVEL!==0 (
    taskkill /f /im powershell.exe 2>nul
)
call :ok "Morning scheduler and monitor stopped"
exit /b 0

REM ─── Show status ─────────────────────────────────────────────────────────
:do_show
echo.
echo =============================================================
call :cecho %CYAN%    EliaAI Scheduler Status
echo =============================================================
echo.

REM Check standard config
if exist "!CONFIG_FILE!" (
    call :ok "Standard scheduler: INSTALLED"
    findstr /r "interval_label start_hour end_hour" "!CONFIG_FILE!" 2>nul
    REM Parse and display
    for /f "tokens=2" %%a in ('findstr "interval_label" "!CONFIG_FILE!" 2^>nul') do (
        set "IVAL_DISP=%%a"
        set "IVAL_DISP=!IVAL_DISP:,=!
        call :log "  Interval: !IVAL_DISP!"
    )
    for /f "tokens=2" %%a in ('findstr "start_hour" "!CONFIG_FILE!" 2^>nul') do set "START_DISP=%%a"
    for /f "tokens=2" %%a in ('findstr "end_hour" "!CONFIG_FILE!" 2^>nul') do set "END_DISP=%%a"
    call :log "  Active hours: !START_DISP!:00 - !END_DISP!:00"
) else (
    call :warn "Standard scheduler: NOT INSTALLED"
)

echo.

REM Check morning config
if exist "!MORNING_CONFIG_FILE!" (
    call :ok "Morning scheduler: INSTALLED"
    for /f "tokens=2" %%a in ('findstr "morning_hour" "!MORNING_CONFIG_FILE!" 2^>nul') do set "MORN_DISP=%%a"
    call :log "  Morning run time: !MORN_DISP!:00"
) else (
    call :warn "Morning scheduler: NOT INSTALLED"
)

echo.

REM Check if monitor is running
tasklist /fi "imagename eq powershell.exe" /fo list 2>nul | findstr /i "cron_monitor" >nul
if !ERRORLEVEL!==0 (
    call :ok "Cron monitor process: RUNNING"
) else (
    call :warn "Cron monitor process: NOT RUNNING"
    call :info "Run: manage_cron.bat install"
)

echo.
echo =============================================================
exit /b 0

REM ─── Parse args ───────────────────────────────────────────────────────────
:parse_args
set "COMMAND="
set "IVAL=%DEFAULT_INTERVAL%"
set "START=%DEFAULT_START_HOUR%"
set "END=%DEFAULT_END_HOUR%"
set "MORNING_H=%DEFAULT_MORNING_HOUR%"

:parse_loop
if "%~1"=="" goto :parse_done

if /i "%~1"=="-h" goto :show_usage
if /i "%~1"=="--help" goto :show_usage

REM Commands
echo %~1 | findstr /i /r "^install$ ^install-morning$ ^uninstall$ ^uninstall-morning$ ^show$" >nul
if !ERRORLEVEL!==0 (
    set "COMMAND=%~1"
    shift
    goto :parse_loop
)

REM Options
echo %~1 | findstr /i "--interval" >nul
if !ERRORLEVEL!==0 (
    set "IVAL=%~2"
    shift
    shift
    goto :parse_loop
)

echo %~1 | findstr /i "--start" >nul
if !ERRORLEVEL!==0 (
    set "START=%~2"
    shift
    shift
    goto :parse_loop
)

echo %~1 | findstr /i "--end" >nul
if !ERRORLEVEL!==0 (
    set "END=%~2"
    shift
    shift
    goto :parse_loop
)

echo %~1 | findstr /i "--morning-hour" >nul
if !ERRORLEVEL!==0 (
    set "MORNING_H=%~2"
    shift
    shift
    goto :parse_loop
)

shift
goto :parse_loop

:parse_done

REM ─── Main dispatch ────────────────────────────────────────────────────────
:main
if "%~1"=="" goto :show_usage
call :parse_args %*

REM Dispatch
if /i "!COMMAND!"=="install" (
    call :do_install
) else if /i "!COMMAND!"=="install-morning" (
    call :do_install_morning
) else if /i "!COMMAND!"=="uninstall" (
    call :do_uninstall
) else if /i "!COMMAND!"=="uninstall-morning" (
    call :do_uninstall_morning
) else if /i "!COMMAND!"=="show" (
    call :do_show
) else (
    call :error "Unknown command: !COMMAND!"
    call :show_usage
    exit /b 1
)

endlocal
exit /b 0
