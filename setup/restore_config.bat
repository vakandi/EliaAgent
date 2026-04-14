@echo off
REM restore_config.bat - Restore OpenCode + oh-my-opencode from backup (Windows)
REM
REM ADAPTATION NOTES:
REM   This is the Windows version of restore_config.sh
REM   Key changes from macOS:
REM   - No shebang needed
REM   - Use %APPDATA% instead of ~/.config
REM   - Use set VAR=value and %VAR%
REM   - Use if exist / if not exist instead of [[ ]]
REM   - Use copy /y or xcopy instead of cp
REM   - Use rmdir /s /q instead of rm -rf
REM   - Use PowerShell or 7z for ZIP extraction
REM
REM PREREQUISITES:
REM   - 7-Zip: https://www.7-zip.org/ (for .zip extraction)
REM   - OR PowerShell 5+ (Windows 10+ has it built-in)
REM   - npm (for oh-my-opencode reinstall via npm link)

setlocal EnableDelayedExpansion

REM ─── Configuration ─────────────────────────────────────────────────────────
set "SCRIPT_DIR=%~dp0"
set "ELIA_ROOT=%SCRIPT_DIR%"
set "OPENCODE_CONFIG_DIR=%APPDATA%\opencode"
set "BACKUP_FILE="
set "RESTORE_DIR="
set "FORCE_RESTORE=false"

goto :main

:color_echo
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

REM ─── Show usage ─────────────────────────────────────────────────────────────
:show_usage
echo Usage: restore_config.bat ^<backup_file^> [--force]
echo.
echo Options:
echo   ^<backup_file^>   Path to .zip backup file
echo   --force          Overwrite existing configs without prompting
echo   -h, --help       Show this help
echo.
echo Examples:
echo   restore_config.bat backups\elia_config_backup_20260319_120000.zip
echo   restore_config.bat C:\temp\my_backup.zip --force
exit /b 0

:main
echo.
echo =============================================================
echo   EliaAI Config Restore  (Windows)
echo =============================================================
echo.

REM ─── Parse arguments ────────────────────────────────────────────────────────
if "%~1"=="-h" goto :show_usage
if "%~1"=="--help" goto :show_usage

if "%~1"=="" (
    call :err "No backup file specified."
    goto :show_usage
    exit /b 1
)

set "BACKUP_FILE=%~f1"
if "%~2"=="--force" set "FORCE_RESTORE=true"

if not exist "%BACKUP_FILE%" (
    call :err "Backup file not found: %BACKUP_FILE%"
    exit /b 1
)

REM Check extension
echo %BACKUP_FILE% | findstr /i "\.zip" >nul
if !ERRORLEVEL!==0 (
    set "EXT=zip"
) else (
    echo %BACKUP_FILE% | findstr /i "\.tar.gz" >nul
    if !ERRORLEVEL!==0 (
        set "EXT=tar.gz"
    ) else (
        call :warn "Unknown backup format (expected .zip or .tar.gz)"
        call :info "Will attempt to extract anyway..."
        set "EXT=zip"
    )
)

call :log "Starting restore from: %BACKUP_FILE%"

REM ─── Check prerequisites ────────────────────────────────────────────────────
call :log "Checking prerequisites..."

where 7z >nul 2>&1
if !ERRORLEVEL!==0 (
    call :ok "7z found - will use for extraction"
    set "HAS_7Z=true"
) else (
    powershell -Command "Get-Command Compress-Archive -ErrorAction SilentlyContinue" >nul 2>&1
    if !ERRORLEVEL!==0 (
        call :ok "PowerShell found - will use Compress-Archive"
        set "HAS_PS=true"
    ) else (
        call :err "Neither 7z nor PowerShell Compress-Archive available"
        call :info "Install 7-Zip from https://www.7-zip.org/"
        exit /b 1
    )
)

REM ─── Create restore staging ────────────────────────────────────────────────
set "RESTORE_DIR=%TEMP%\elia_restore_%RANDOM%"
call :log "Creating staging directory..."
if not exist "%RESTORE_DIR%" mkdir "%RESTORE_DIR%"

REM ─── Extract backup ────────────────────────────────────────────────────────
call :log "Extracting backup..."

if "%HAS_7Z%"=="true" (
    7z x "%BACKUP_FILE%" -o"%RESTORE_DIR%" -y >nul 2>&1
    if not !ERRORLEVEL!==0 (
        call :err "Failed to extract ZIP"
        rmdir /s /q "%RESTORE_DIR%" 2>nul
        exit /b 1
    )
) else (
    powershell -Command "Expand-Archive -Path '%BACKUP_FILE%' -DestinationPath '%RESTORE_DIR%' -Force" >nul 2>&1
    if not !ERRORLEVEL!==0 (
        call :err "Failed to extract backup"
        rmdir /s /q "%RESTORE_DIR%" 2>nul
        exit /b 1
    )
)

REM ─── Check backup info ─────────────────────────────────────────────────────
if exist "%RESTORE_DIR%\backup_info.txt" (
    call :info "Backup info:"
    findstr /v "^#" "%RESTORE_DIR%\backup_info.txt" | findstr /v "^$"
)

REM ─── Check what we have ────────────────────────────────────────────────────
set "HAS_OPENCODE_CONFIG=false"
set "HAS_OMO_PKG=false"

if exist "%RESTORE_DIR%\opencode_config\" (
    dir /b "%RESTORE_DIR%\opencode_config\" 2>nul | findstr . >nul
    if !ERRORLEVEL!==0 set "HAS_OPENCODE_CONFIG=true"
)

if exist "%RESTORE_DIR%\oh-my-opencode_pkg\" (
    dir /b "%RESTORE_DIR%\oh-my-opencode_pkg\" 2>nul | findstr . >nul
    if !ERRORLEVEL!==0 set "HAS_OMO_PKG=true"
)

call :log "Backup contents:"
if "%HAS_OPENCODE_CONFIG%"=="true" (
    call :ok "  - opencode_config\"
) else (
    call :warn "  - opencode_config\ (empty/not found)"
)
if "%HAS_OMO_PKG%"=="true" (
    call :ok "  - oh-my-opencode_pkg\"
) else (
    call :warn "  - oh-my-opencode_pkg\ (empty/not found)"
)

REM ─── Confirm restore ───────────────────────────────────────────────────────
if "%FORCE_RESTORE%"=="false" (
    echo.
    call :info "This will restore configs to:"
    call :info "  - %OPENCODE_CONFIG_DIR%\"
    if "%HAS_OMO_PKG%"=="true" (
        call :info "  - npm global node_modules\ (oh-my-opencode)"
    )
    echo.
    set /p REPLY="Continue with restore? [y/N] "
    if /i not "!REPLY!"=="y" (
        call :log "Restore cancelled."
        rmdir /s /q "%RESTORE_DIR%" 2>nul
        exit /b 0
    )
)

REM ─── Restore opencode config ───────────────────────────────────────────────
if "%HAS_OPENCODE_CONFIG%"=="true" (
    call :log "Restoring %%APPDATA%%\opencode\..."

    if exist "%OPENCODE_CONFIG_DIR%" (
        if "%FORCE_RESTORE%"=="true" (
            call :log "Backing up existing config first..."
            call :warn "Pre-restore backup not implemented in Windows - manual backup recommended"
        )
        call :info "Merging into existing directory..."
        xcopy /s /e /y "%RESTORE_DIR%\opencode_config\*" "%OPENCODE_CONFIG_DIR%\" >nul 2>&1
    ) else (
        call :log "Creating new config directory..."
        mkdir "%OPENCODE_CONFIG_DIR%" 2>nul
        xcopy /s /e /y "%RESTORE_DIR%\opencode_config\*" "%OPENCODE_CONFIG_DIR%\" >nul 2>&1
    )

    for /f %%c in ('dir /s /b "%OPENCODE_CONFIG_DIR%\*.json" "%OPENCODE_CONFIG_DIR%\*.md" 2^>nul ^| find /c /v ""') do set "TOTAL_FILES=%%c"
    call :ok "Restored to %%APPDATA%%\opencode\"
) else (
    call :warn "No opencode_config\ found in backup - skipping"
)

REM ─── Restore oh-my-opencode npm package ────────────────────────────────────
if "%HAS_OMO_PKG%"=="true" (
    call :log "Restoring oh-my-opencode npm package..."

    if exist "%RESTORE_DIR%\oh-my-opencode_pkg\package.json" (
        for /f "tokens=2 delims=: " %%v in ('findstr "version" "%RESTORE_DIR%\oh-my-opencode_pkg\package.json" ^| findstr /r "[0-9]"') do set "OMO_VERSION=%%v"
        call :info "Package version: !OMO_VERSION!"
    )

    where npm >nul 2>&1
    if !ERRORLEVEL!==0 (
        for /f "delims=" %%p in ('npm root -g 2^>nul') do set "NPM_PREFIX=%%p"
        set "OMO_TARGET_DIR=!NPM_PREFIX!\oh-my-opencode"

        if exist "!NPM_PREFIX!" (
            call :log "Installing to global npm: !NPM_PREFIX!"
            if not exist "!OMO_TARGET_DIR!" mkdir "!OMO_TARGET_DIR!"
            xcopy /s /e /y "%RESTORE_DIR%\oh-my-opencode_pkg\*" "!OMO_TARGET_DIR!\" >nul 2>&1
            call :ok "Restored oh-my-opencode to !OMO_TARGET_DIR!"

            call :log "Linking oh-my-opencode binary..."
            npm link -g oh-my-opencode >nul 2>&1
            if !ERRORLEVEL!==0 (
                call :ok "Binary linked successfully"
            ) else (
                call :warn "Could not npm link -g oh-my-opencode"
            )
        ) else (
            call :warn "Global npm directory not found: !NPM_PREFIX!"
            call :info "To install manually:"
            call :info "  npm install -g oh-my-opencode"
        )
    ) else (
        call :warn "npm not found - cannot reinstall oh-my-opencode"
        call :info "To install manually:"
        call :info "  npm install -g oh-my-opencode"
    )
) else (
    call :warn "No oh-my-opencode_pkg\ found in backup"
    call :info "To install oh-my-opencode:"
    call :info "  npm install -g oh-my-opencode"
    call :info "  OR: bunx oh-my-opencode install"
)

REM ─── Fix permissions ────────────────────────────────────────────────────────
call :log "Fixing file permissions (Windows - attrib)..."
attrib +r "%OPENCODE_CONFIG_DIR%\*.json" 2>nul
attrib +r "%OPENCODE_CONFIG_DIR%\*.md" 2>nul
attrib -r +h "%OPENCODE_CONFIG_DIR%\*.json" 2>nul
call :ok "Permissions set"

REM ─── Cleanup ────────────────────────────────────────────────────────────────
call :log "Cleaning up staging..."
if exist "%RESTORE_DIR%" rmdir /s /q "%RESTORE_DIR%" 2>nul

echo.
echo =============================================================
call :ok "Restore complete!"
echo =============================================================
echo.
call :info "Next steps:"
call :info "  1. Verify: opencode --version"
call :info "  2. Verify: oh-my-opencode --version"
call :info "  3. Run: cd %ELIA_ROOT% && opencode"
call :info "  4. If issues: installer.bat"
echo.

endlocal
