@echo off
REM start_agents.bat - EliaAI Agent Launcher (Windows)
REM Includes voice/whisper detection and installation guidance

setlocal EnableDelayedExpansion

set "AGENT_DIR=%~dp0"
set "TRIGGER_SCRIPT=%~dp0trigger_opencode_interactive.bat"

REM ─── Color variables (empty = plain text, set codes for ANSI-capable terminals) ───
set "CYAN="
set "YELLOW="
set "GREEN="
set "RED="
REM Detect ANSI support via codepage
for /f %%A in ('powershell -Command "[console]::OutputEncoding.CodePage" 2^>nul') do set "CODEPAGE=%%A"
if defined CODEPAGE if !CODEPAGE! geq 65001 (
    set "CYAN=94"
    set "YELLOW=93"
    set "GREEN=92"
    set "RED=91"
)
set "PROMPT_FILE=%AGENT_DIR%PROMPT.md"
set "AGENT_PAYLOADS_DIR=%AGENT_DIR%.agent_payloads"

goto :main

:log
echo [INFO] %~1
goto :eof

:error
echo [ERROR] %~1 >&2
goto :eof

:success
echo [OK] %~1
goto :eof

:warn
echo [WARN] %~1
goto :eof

:cecho
REM Echo helper - prints all arguments (color codes would need ANSI sequences)
REM Usage: call :cecho COLOR_CODE text to print...
REM Since color codes aren't implemented, this just prints the text
echo %*
goto :eof

REM ─── Voice check routine ─────────────────────────────────────────────────
:check_voice
echo.
call :log "Checking voice/whisper system..."

REM Python
set "PY_FOUND=false"
set "PY_CMD="
where python >nul 2>&1
if !ERRORLEVEL!==0 (
    for /f "delims=" %%v in ('python --version 2^>^&1') do set "PY_VERSION=%%v"
    call :success "Python: !PY_VERSION!"
    set "PY_FOUND=true"
    set "PY_CMD=python"
)
if "!PY_FOUND!"=="false" (
    where python3 >nul 2>&1
    if !ERRORLEVEL!==0 (
        for /f "delims=" %%v in ('python3 --version 2^>^&1') do set "PY_VERSION=%%v"
        call :success "Python3: !PY_VERSION!"
        set "PY_FOUND=true"
        set "PY_CMD=python3"
    )
)
if "!PY_FOUND!"=="false" (
    call :warn "Python NOT found - needed for whisper"
)

REM whisper package
set "WHISPER_PKG=false"
if "!PY_FOUND!"=="true" (
    !PY_CMD! -c "import whisper; print('ok')" >nul 2>&1
    if !ERRORLEVEL!==0 (
        call :success "openai-whisper package: installed"
        set "WHISPER_PKG=true"
    ) else (
        call :warn "openai-whisper package: NOT installed"
    )
)

REM whisper models
set "WHISPER_MODEL=false"
if exist "%USERPROFILE%\.cache\whisper\" (
    dir /b "%USERPROFILE%\.cache\whisper\" 2>nul | findstr /i ".pt" >nul
    if !ERRORLEVEL!==0 (
        call :success "Whisper models in cache:"
        for /f %%f in ('dir /b "%USERPROFILE%\.cache\whisper\"') do echo         - %%f
        set "WHISPER_MODEL=true"
    )
)
if "!WHISPER_MODEL!"=="false" (
    call :warn "Whisper models: NOT in cache"
)

REM ffmpeg
set "FFMPEG_FOUND=false"
where ffmpeg >nul 2>&1
if !ERRORLEVEL!==0 (
    for /f "tokens=3" %%v in ('ffmpeg -version 2^>^&1 ^| findstr /i "version"') do set "FF_VER=%%v"
    call :success "ffmpeg: !FF_VER! (for audio recording)"
    set "FFMPEG_FOUND=true"
)

REM sox
set "SOX_FOUND=false"
where sox >nul 2>&1
if !ERRORLEVEL!==0 (
    call :success "sox: installed (alternative audio recorder)"
    set "SOX_FOUND=true"
)
if "!FFMPEG_FOUND!"=="false" if "!SOX_FOUND!"=="false" (
    call :warn "No audio recorder found (need ffmpeg or sox)"
)

REM Overall
set "VOICE_READY=false"
if "!PY_FOUND!"=="true" if "!WHISPER_PKG!"=="true" if "!WHISPER_MODEL!"=="true" (
    if "!FFMPEG_FOUND!"=="true" || "!SOX_FOUND!"=="true" (
        set "VOICE_READY=true"
        call :success "Voice/whisper system: READY"
    )
)
if "!VOICE_READY!"=="false" (
    call :warn "Voice/whisper system: NOT READY"
)
goto :eof

REM ─── Voice install guide ─────────────────────────────────────────────────
:voice_install_help
echo.
call :cecho %YELLOW% ============================================================
call :cecho %YELLOW%  VOICE/WHISPER INSTALLATION GUIDE (Windows)
call :cecho %YELLOW% ============================================================
echo.
echo Follow these steps to enable voice dictation, then re-run this script.
echo.
call :cecho %CYAN% STEP 1: Install Python (if missing)
echo   Download: https://www.python.org/downloads/
echo   IMPORTANT: Check "Add Python to PATH" during install
echo   Verify: python --version
echo.
call :cecho %CYAN% STEP 2: Install ffmpeg (audio recording)
echo   Option A (Scoop - RECOMMENDED):
echo     scoop install ffmpeg
echo   Option B (Chocolatey):
echo     choco install ffmpeg
echo   Option C (Manual):
echo     https://ffmpeg.org/download.html - extract and add to PATH
echo   Verify: ffmpeg -version
echo.
call :cecho %CYAN% STEP 3: Install openai-whisper
echo   Open CMD as Administrator:
echo     pip install openai-whisper
echo   Verify: python -c "import whisper; print('OK')"
echo.
call :cecho %CYAN% STEP 4: Download whisper model ^(medium recommended^)
echo   Run one of these:
echo     python -m whisper --model medium
echo     python -c "import whisper; whisper.load_model('medium')"
echo.
echo   Model sizes:
echo     tiny   = 39MB   ^(fastest, lowest quality^)
echo     base   = 74MB   ^(fast, good^)
echo     small  = 244MB  ^(balanced^)
echo     medium = 769MB  ^(RECOMMENDED^)
echo     large  = 1550MB ^(best, slowest^)
echo.
call :cecho %CYAN% STEP 5: Re-run this script
echo   cd %AGENT_DIR%
echo   start_agents.bat
echo.
call :cecho %CYAN% After setup, use voice with:
echo   %AGENT_DIR%dictate.bat
echo.
pause
goto :eof

REM ─── Usage ────────────────────────────────────────────────────────────────
:show_usage
echo Usage: start_agents.bat [OPTIONS]
echo.
echo Options:
echo   --extra-prompt="msg"   Add context to agent prompt
echo   --model=MODEL          Choose AI model:
echo                            nvidia     - NVIDIA NIM API ^(requires key^)
echo                            minimax    - MiniMax M2.5 Free
echo                            big-pickle - Big Pickle Free ^(RECOMMENDED^)
echo                            nemotron   - Nemotron 3 Super Free
echo                            mimo       - MiMo V2 Flash Free
echo   --voice-check          Check voice/whisper installation
echo   --voice-install        Show voice installation guide
echo   -h, --help             Show this help
echo.
echo Examples:
echo   start_agents.bat
echo   start_agents.bat --extra-prompt="Check latest messages"
echo   start_agents.bat --model=big-pickle --voice-check
echo   start_agents.bat --voice-install
exit /b 0

REM ─── Parse args ──────────────────────────────────────────────────────────
:parse_loop
if "%~1"=="" goto :parse_done

if /i "%~1"=="-h" goto :show_usage
if /i "%~1"=="--help" goto :show_usage
if /i "%~1"=="--voice-check" goto :voice_check_cmd
if /i "%~1"=="--voice-install" goto :voice_install_help

echo %~1 | findstr /i "--extra-prompt=" >nul
if !ERRORLEVEL!==0 (
    set "EXTRA_PROMPT=%~1"
    set "EXTRA_PROMPT=!EXTRA_PROMPT:*--extra-prompt=!"
    set "EXTRA_PROMPT=!EXTRA_PROMPT:~1!"
    shift
    goto :parse_loop
)

echo %~1 | findstr /i "--model=" >nul
if !ERRORLEVEL!==0 (
    set "MODEL_ARG=%~1"
    set "MODEL_ARG=!MODEL_ARG:*--model=!"
    set "MODEL_ARG=!MODEL_ARG:~1!"
    shift
    goto :parse_loop
)

shift
goto :parse_loop

:parse_done

:main
REM ─── Defaults ─────────────────────────────────────────────────────────────
if not defined MODEL_ARG set "MODEL_ARG=big-pickle"
set "EXTRA_PROMPT="
set "VOICE_READY=false"

echo.
echo =============================================================
call :cecho %CYAN%    EliaAI Agent Launcher  (Windows)
echo =============================================================
echo.

REM ─── Validate model ──────────────────────────────────────────────────────
set "MODEL=%MODEL_ARG%"
set "MODEL_VALID=false"
echo !MODEL! | findstr /i "nvidia minimax big-pickle nemotron mimo" >nul
if !ERRORLEVEL!==0 set "MODEL_VALID=true"

if "!MODEL_VALID!"=="false" (
    call :warn "Unknown model: !MODEL! - using: big-pickle"
    set "MODEL=big-pickle"
)

REM ─── Check trigger script ─────────────────────────────────────────────────
if not exist "%TRIGGER_SCRIPT%" (
    call :error "trigger_opencode_interactive.bat not found"
    exit /b 1
)

REM ─── Create payload dir ───────────────────────────────────────────────────
if not exist "%AGENT_PAYLOADS_DIR%" mkdir "%AGENT_PAYLOADS_DIR%"

REM ─── Temp prompt file ────────────────────────────────────────────────────
set "EXTRA_PROMPT_FILE="
if not "!EXTRA_PROMPT!"=="" (
    call :log "Creating temporary prompt file..."

    for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set "TS=%%a%%b%%c"
    for /f "tokens=1-2 delims=: " %%a in ('time /t') do set "TS=!TS:_=%%a%%b!"

    set "TIMESTAMPED_PROMPT=%AGENT_PAYLOADS_DIR%\prompt_!TS!.txt"

    REM Write prompt to temp file using PowerShell to handle multiline content safely
    powershell -Command "Set-Content -Path '%AGENT_PAYLOADS_DIR%\.prompt_hdr.txt' -Value '# URGENT CONTEXT - !TS!', '', '!EXTRA_PROMPT!', ''"

    if exist "!TIMESTAMPED_PROMPT!" del "!TIMESTAMPED_PROMPT!" >nul 2>&1
    if exist "%AGENT_PAYLOADS_DIR%\.prompt_hdr.txt" (
        copy "%AGENT_PAYLOADS_DIR%\.prompt_hdr.txt" "!TIMESTAMPED_PROMPT!" >nul 2>&1
        del "%AGENT_PAYLOADS_DIR%\.prompt_hdr.txt" >nul 2>&1
    )
    if exist "%PROMPT_FILE%" (
        type "%PROMPT_FILE%" >> "!TIMESTAMPED_PROMPT!"
    )

    call :success "Prompt file created"
    set "EXTRA_PROMPT_FILE=!TIMESTAMPED_PROMPT!"
)

REM ─── Check dependencies ─────────────────────────────────────────────────
call :log "Checking dependencies..."

where opencode >nul 2>&1
if !ERRORLEVEL!==0 (
    for /f "delims=" %%v in ('opencode --version 2^>^&1 ^| findstr /r "[0-9]"') do call :success "OpenCode: %%v"
) else (
    call :error "OpenCode CLI NOT FOUND"
    call :info "Install: scoop install opencode"
    call :info "OR: npm install -g opencode"
    call :info "OR: Download from https://opencode.ai/"
    exit /b 1
)

where oh-my-opencode >nul 2>&1
if !ERRORLEVEL!==0 (
    for /f "delims=" %%v in ('oh-my-opencode --version 2^>^&1 ^| findstr /r "[0-9]"') do call :success "oh-my-opencode: %%v"
) else (
    call :warn "oh-my-opencode not found - using direct opencode"
)

REM ─── Voice check ─────────────────────────────────────────────────────────
call :check_voice

REM ─── ULW/Ralph toggle ────────────────────────────────────────────────────
set "RALPH_MODE_FILE=%AGENT_DIR%.ralph_mode"
if exist "%RALPH_MODE_FILE%" (
    call :log "Loop mode: RALPH"
) else (
    call :log "Loop mode: ULW"
)

REM ─── Execute ────────────────────────────────────────────────────────────
echo.
call :log "Starting EliaAI Agent..."
call :log "Model: !MODEL!"
if "!VOICE_READY!"=="true" (
    call :success "Voice: READY"
) else (
    call :warn "Voice: NOT READY (run --voice-install for setup)"
)
echo.

if "!EXTRA_PROMPT_FILE!"=="" (
    call "%TRIGGER_SCRIPT%"
) else (
    call "%TRIGGER_SCRIPT%" "!EXTRA_PROMPT_FILE!"
)

set "EXIT_CODE=!ERRORLEVEL!"

echo.
echo =============================================================
if !EXIT_CODE!==0 (
    call :success "Agent completed"
) else (
    call :warn "Agent exited with code: !EXIT_CODE!"
)
echo =============================================================

REM ─── Cleanup ────────────────────────────────────────────────────────────
if not "!EXTRA_PROMPT_FILE!"=="" (
    if exist "!EXTRA_PROMPT_FILE!" del "!EXTRA_PROMPT_FILE!" >nul 2>&1
)

if "!VOICE_READY!"=="false" (
    echo.
    call :info "Run: start_agents.bat --voice-install"
)

endlocal
exit /b !EXIT_CODE!
