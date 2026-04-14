@echo off
REM backup_config.bat - Backup all OpenCode + oh-my-opencode configs (Windows)
REM
REM ADAPTATION NOTES:
REM   This is the Windows version of backup_config.sh
REM   Key changes from macOS:
REM   - No shebang needed
REM   - Use %USERPROFILE% instead of ~
REM   - Use %APPDATA% instead of ~/.config
REM   - Use mkdir dir 2>nul & if not exist dir mkdir dir pattern
REM   - Use set VAR=value instead of VAR=value
REM   - Use %VAR% instead of ${VAR}
REM   - Use cmd /c for command substitution
REM   - Use 7z or PowerShell for ZIP creation
REM
REM PREREQUISITES (install one):
REM   - 7-Zip: https://www.7-zip.org/
REM   - PowerShell 5+ (Windows 10+ has it built-in)
REM   - Git for Windows (includes bash/zip)

setlocal EnableDelayedExpansion

REM ─── Configuration ─────────────────────────────────────────────────────────
set "SCRIPT_DIR=%~dp0"
set "BACKUP_DIR=%SCRIPT_DIR%backups"
set "OPENCODE_CONFIG_DIR=%APPDATA%\opencode"

REM Detect timestamp
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set "TS=%%a%%b%%c"
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set "TS=%TS%_%%a%%b"
set "TIMESTAMP=%TS%"
set "BACKUP_FILENAME=elia_config_backup_%TIMESTAMP%.zip"
set "BACKUP_PATH=%BACKUP_DIR%\%BACKUP_FILENAME%"

REM ─── Logging helpers ───────────────────────────────────────────────────────
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "CYAN=[96m"
set "NC=[0m"

goto :main

:color_echo
REM call :color_echo %GREEN% "message"
for /f "delims=" %%a in ('echo %~1%~2%') do echo %%a
goto :eof

:log
echo [%TIME%] %~1
goto :eof

:info
call :color_echo %CYAN% [INFO] %~1
goto :eof

:warn
call :color_echo %YELLOW% [WARN] %~1
goto :eof

:err
call :color_echo %RED% [ERROR] %~1
goto :eof

:ok
call :color_echo %GREEN% [OK] %~1
goto :eof

REM ─── Show usage ────────────────────────────────────────────────────────────
:show_usage
echo Usage: backup_config.bat [--output PATH]
echo.
echo Options:
echo   --output PATH   Custom backup output path
echo   -h, --help      Show this help
echo.
echo Backup includes:
echo   - %%APPDATA%%\opencode\ (all files, agents, skills, plugins, themes, docs)
echo   - %%APPDATA%%\opencode\commands\ (custom commands directory)
echo   - %%APPDATA%%\opencode\command (custom command file)
echo   - oh-my-opencode npm package (if installed)
exit /b 0

:main
echo.
echo =============================================================
echo   EliaAI Config Backup  (Windows)
echo =============================================================
echo.

REM ─── Parse arguments ───────────────────────────────────────────────────────
if "%~1"=="-h" goto :show_usage
if "%~1"=="--help" goto :show_usage

set "CUSTOM_OUTPUT="
if "%~1"=="--output" (
    set "CUSTOM_OUTPUT=%~2"
    set "BACKUP_PATH=%CUSTOM_OUTPUT%"
    for %%P in ("%BACKUP_PATH%") do set "BACKUP_DIR=%%~dpP"
)

REM ─── Check prerequisites ────────────────────────────────────────────────────
call :log "Checking prerequisites..."

if exist "%OPENCODE_CONFIG_DIR%" (
    call :ok "OpenCode config found: %OPENCODE_CONFIG_DIR%"
    set "OPENCODE_INSTALLED=true"
) else (
    call :warn "OpenCode config directory not found: %OPENCODE_CONFIG_DIR%"
    call :info "OpenCode may not be installed. This is OK for backup purposes."
    set "OPENCODE_INSTALLED=false"
)

REM ─── Check OpenCode CLI ────────────────────────────────────────────────────
call :log "Checking OpenCode installation..."
where opencode >nul 2>&1
if !ERRORLEVEL!==0 (
    for /f "delims=" %%v in ('opencode --version 2^>^&1 ^| findstr /r "^[0-9]"') do set "OV=%%v"
    call :ok "OpenCode CLI found: !OV!"
    set "OPENCODE_CLI_FOUND=true"
) else (
    call :warn "OpenCode CLI not found in PATH"
    call :info "To install OpenCode:"
    call :info "  Option 1: scoop install opencode"
    call :info "  Option 2: npm install -g opencode"
    call :info "  Option 3: Download from https://opencode.ai/"
    set "OPENCODE_CLI_FOUND=false"
)

REM ─── Check oh-my-opencode ──────────────────────────────────────────────────
call :log "Checking oh-my-opencode installation..."
where oh-my-opencode >nul 2>&1
if !ERRORLEVEL!==0 (
    for /f "delims=" %%v in ('oh-my-opencode --version 2^>^&1 ^| findstr /r "^[0-9]"') do set "OMOV=%%v"
    call :ok "oh-my-opencode found: !OMOV!"
    set "OMO_INSTALLED=true"

    REM Find npm package path
    where npm >nul 2>&1
    if !ERRORLEVEL!==0 (
        for /f "delims=" %%p in ('npm root -g 2^>nul') do set "NPM_GLOBAL=%%p"
        set "OMO_PKG_DIR=!NPM_GLOBAL!\oh-my-opencode"
    ) else (
        set "OMO_PKG_DIR="
    )
) else (
    call :warn "oh-my-opencode not found in PATH"
    call :info "To install oh-my-opencode:"
    call :info "  Option 1 (WSL recommended): wsl -e bunx oh-my-opencode install"
    call :info "  Option 2: npm install -g oh-my-opencode"
    set "OMO_INSTALLED=false"
    set "OMO_PKG_DIR="
)

REM ─── Create backup directory ───────────────────────────────────────────────
call :log "Creating backup directory..."
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
call :ok "Backup directory: %BACKUP_DIR%"

REM ─── Create staging directory ───────────────────────────────────────────────
set "STAGING_DIR=%BACKUP_DIR%\.staging_%RANDOM%"
call :log "Creating staging directory..."
if not exist "%STAGING_DIR%" mkdir "%STAGING_DIR%"
if not exist "%STAGING_DIR%\opencode_config" mkdir "%STAGING_DIR%\opencode_config"
if not exist "%STAGING_DIR%\oh-my-opencode_pkg" mkdir "%STAGING_DIR%\oh-my-opencode_pkg"

REM ─── Backup OpenCode config ────────────────────────────────────────────────
if "%OPENCODE_INSTALLED%"=="true" (
    call :log "Backing up %%APPDATA%%\opencode\ ..."
    xcopy /s /e /y "%OPENCODE_CONFIG_DIR%\*" "%STAGING_DIR%\opencode_config\" >nul 2>&1
    if !ERRORLEVEL!==0 (
        for /f %%c in ('dir /s /b "%STAGING_DIR%\opencode_config\*.json" "%STAGING_DIR%\opencode_config\*.md" 2^>nul ^| find /c /v ""') do set "FILE_COUNT=%%c"
        call :ok "Backed up !FILE_COUNT! files from %%APPDATA%%\opencode\"
    ) else (
        call :warn "No files found to backup"
        set "FILE_COUNT=0"
    )
) else (
    call :warn "Skipping opencode config backup (directory not found)"
    set "FILE_COUNT=0"
)

REM ─── Backup oh-my-opencode npm package ────────────────────────────────────
set "OMO_FILE_COUNT=0"
if not "%OMO_PKG_DIR%"=="" (
    if exist "!OMO_PKG_DIR!" (
        call :log "Backing up oh-my-opencode npm package..."
        xcopy /s /e /y "!OMO_PKG_DIR!\*" "%STAGING_DIR%\oh-my-opencode_pkg\" >nul 2>&1
        if !ERRORLEVEL!==0 (
            for /f %%c in ('dir /s /b "%STAGING_DIR%\oh-my-opencode_pkg\*.json" 2^>nul ^| find /c /v ""') do set "OMO_FILE_COUNT=%%c"
            call :ok "Backed up !OMO_FILE_COUNT! files from oh-my-opencode npm package"
        )
    )
) else (
    call :warn "oh-my-opencode npm package location not found"
)

REM ─── Save backup metadata ──────────────────────────────────────────────────
call :log "Saving backup metadata..."
(
    echo # EliaAI Config Backup Info
    echo # Generated: %DATE% %TIME%
    echo # Host: %COMPUTERNAME%
    echo # User: %USERNAME%
    echo.
    echo OPENCODE_CONFIG_DIR: %OPENCODE_CONFIG_DIR%
    echo OPENCODE_INSTALLED: %OPENCODE_INSTALLED%
    echo OPENCODE_CLI_FOUND: %OPENCODE_CLI_FOUND%
    echo OH-MY-OPENCODE_INSTALLED: %OMO_INSTALLED%
    echo OH-MY-OPENCODE_NPM_PKG: %OMO_PKG_DIR%
    echo BACKUP_FILES_OPENCODE: %FILE_COUNT%
    echo BACKUP_FILES_OMO_PKG: %OMO_FILE_COUNT%
    echo BACKUP_PATH: %BACKUP_PATH%
    echo.
    echo # Contents:
    echo # - opencode_config/ - Full opencode backup (including commands/ and command)
    echo # - oh-my-opencode_pkg/ - oh-my-opencode npm package (if available)
    echo # - backup_info.txt - This file
) > "%STAGING_DIR%\backup_info.txt"

REM ─── Create ZIP archive ─────────────────────────────────────────────────────
call :log "Creating ZIP archive..."
cd /d "%STAGING_DIR%"

REM Try 7z first
where 7z >nul 2>&1
if !ERRORLEVEL!==0 (
    7z a -tzip "%BACKUP_PATH%" . -xr!"*.DS_Store" >nul 2>&1
    set "ZIP_SUCCESS=true"
) else (
    REM Try PowerShell
    powershell -Command "Compress-Archive -Path '*' -DestinationPath '%BACKUP_PATH%' -Force" >nul 2>&1
    if !ERRORLEVEL!==0 (
        set "ZIP_SUCCESS=true"
    ) else (
        call :warn "Neither 7z nor PowerShell Compress-Archive available"
        call :info "Install 7-Zip from https://www.7-zip.org/ or use PowerShell"
        set "ZIP_SUCCESS=false"
    )
)

REM ─── Cleanup staging ────────────────────────────────────────────────────────
cd /d "%SCRIPT_DIR%"
call :log "Cleaning up staging directory..."
if exist "%STAGING_DIR%" rmdir /s /q "%STAGING_DIR%"

REM ─── Final output ───────────────────────────────────────────────────────────
if exist "%BACKUP_PATH%" (
    for %%F in ("%BACKUP_PATH%") do set "SIZE=%%~zF"
    call :ok "Backup created successfully!"
    echo.
    echo =============================================================
    call :color_echo %GREEN% "  Backup: %BACKUP_PATH%"
    call :color_echo %GREEN% "  Size:   !SIZE! bytes"
    call :color_echo %GREEN% "  Files:  OpenCode config (%FILE_COUNT%) + oh-my-opencode (!OMO_FILE_COUNT!)"
    echo =============================================================
    echo.
    call :info "To restore this backup:"
    call :info "  cd %SCRIPT_DIR%"
    call :info "  restore_config.bat %BACKUP_FILENAME%"
    echo.
) else (
    call :err "Backup creation failed!"
    if "!ZIP_SUCCESS!"=="false" (
        call :info "Missing: 7z (7-Zip) or PowerShell Compress-Archive"
    )
    exit /b 1
)

endlocal
