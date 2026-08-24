@echo off
REM trigger_opencode_interactive.bat - EliaAI Agent with ULW/Ralph Loop (Windows)
REM Includes voice/whisper detection and installation guidance

setlocal EnableDelayedExpansion

set "AGENT_DIR=%~dp0"
set "OPENCODE_CONFIG_DIR=%APPDATA%\opencode"
set "LOG_DIR=%AGENT_DIR%logs"
set "PLUGIN_DIR=%OPENCODE_CONFIG_DIR%\plugin"

for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set "TS_DATE=%%a%%b%%c"
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set "TS_TIME=%%a%%b"
set "TS=%TS_DATE%_%TS_TIME%"
set "LOG_FILE=%LOG_DIR%\opencode_interactive_%TS%.log"

set "OMO_DISABLED_FILE=%AGENT_DIR%.omo_disabled"
set "RALPH_MODE_FILE=%AGENT_DIR%.ralph_mode"
set "OMO_ENABLED=true"
set "RALPH_MODE=false"

REM ─── Color variables (empty = no ANSI codes, set to actual codes on supported terminals) ───
set "CYAN="
set "YELLOW="
set "GREEN="
set "RED="

REM Check if terminal supports ANSI colors
for /f %%A in ('powershell -Command "[console]::OutputEncoding.CodePage" 2^>nul') do set "CODEPAGE=%%A"
if defined CODEPAGE if !CODEPAGE! geq 65001 (
    set "CYAN=94"
    set "YELLOW=93"
    set "GREEN=92"
    set "RED=91"
)

if exist "%OMO_DISABLED_FILE%" (
    set "OMO_ENABLED=false"
    echo OMO is DISABLED
) else (
    echo OMO is ENABLED
)

if exist "%RALPH_MODE_FILE%" (
    set "RALPH_MODE=true"
    echo RALPH loop mode active
) else (
    echo ULW-LOOP mode is ENABLED by DEFAULT
)

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

if exist "%AGENT_DIR%ralph-loop.local.md" del "%AGENT_DIR%ralph-loop.local.md" >nul 2>&1
if exist "%AGENT_DIR%.ralph-state.json" del "%AGENT_DIR%.ralph-state.json" >nul 2>&1

if defined OPENCODE_MODEL (
    echo Using model from env: !OPENCODE_MODEL!
    set "MODEL_TO_USE=!OPENCODE_MODEL!"
) else (
    echo No OPENCODE_MODEL set, using: opencode/big-pickle
    set "MODEL_TO_USE=opencode/big-pickle"
)

set "AGENT_PAYLOADS_DIR=%AGENT_DIR%.agent_payloads"
set "TELEGRAM_INBOX=%AGENT_PAYLOADS_DIR%\telegram_inbox.txt"
set "_inbox_content="

if exist "%TELEGRAM_INBOX%" (
    set /p _inbox_content=<"%TELEGRAM_INBOX%"
    del "%TELEGRAM_INBOX%" >nul 2>&1
)

set "EXTRA_CONTEXT=%~1"

if defined _inbox_content (
    REM Write combined context to a temp file to avoid batch multiline issues
    (
        echo [Telegram session messages]
        type "%TELEGRAM_INBOX%"
    ) > "%AGENT_PAYLOADS_DIR%\.ctx_tmp.txt"
    set /p EXTRA_CONTEXT=<"%AGENT_PAYLOADS_DIR%\.ctx_tmp.txt"
    del "%AGENT_PAYLOADS_DIR%\.ctx_tmp.txt" >nul 2>&1
    set "EXTRA_CONTEXT=!EXTRA_CONTEXT! none"
)

if not defined EXTRA_CONTEXT set "EXTRA_CONTEXT=none"

REM ─── Calculate NEXT_RUN_HOURS ──────────────────────────────────────────
for /f "tokens=1 delims=: " %%h in ('echo !TIME!') do set "CURRENT_HOUR=%%h"
set /a CURRENT_HOUR=1!CURRENT_HOUR! - 100 2>nul

if !CURRENT_HOUR! geq 11 if !CURRENT_HOUR! lss 21 (
    set /a NEXT_RUN_HOURS=1
) else (
    if !CURRENT_HOUR! lss 10 (
        set /a NEXT_RUN_HOURS=10 - !CURRENT_HOUR!
    ) else (
        set /a NEXT_RUN_HOURS=24 - !CURRENT_HOUR! + 10
    )
)

set "EXTRA_CONTEXT=!EXTRA_CONTEXT!"

REM ─── NEXT_RUN_HOURS context (written to temp file to avoid batch multiline issues) ───
if not exist "%AGENT_PAYLOADS_DIR%" mkdir "%AGENT_PAYLOADS_DIR%" >nul 2>&1
(
    echo.
    echo NEXT RUN INFO: This agent will run again in approximately !NEXT_RUN_HOURS! hour(s). Use this to:
    echo - Pre-prepare documents and research for tasks you anticipate
    echo - Identify decisions needed from team members ^(Thomas, Rida, Ali, etc.^)
    echo - Prepare options/recommendations for upcoming conversations
    echo - Do preparatory work now to save time on next run
) >> "%AGENT_PAYLOADS_DIR%\.ctx_tmp.txt" 2>nul

REM ─── Logging helpers ────────────────────────────────────────────────────
goto :main

:log
echo [%TIME%] %~1
goto :eof

:info
echo [INFO] %~1
goto :eof

:warn
echo [WARN] %~1
goto :eof

:error
echo [ERROR] %~1 >&2
goto :eof

:ok
echo [OK] %~1
goto :eof

:cecho
REM Echo helper - prints all text (color codes not implemented in this script)
echo %*
goto :eof

REM ─── Voice/whisper check ─────────────────────────────────────────────────
:check_voice
echo.
call :log "Checking voice/whisper system..."

REM Python
set "PY_FOUND=false"
where python >nul 2>&1
if !ERRORLEVEL!==0 (
    for /f "delims=" %%v in ('python --version 2^>^&1') do set "PY_VERSION=%%v"
    call :ok "Python: !PY_VERSION!"
    set "PY_FOUND=true"
    set "PY_CMD=python"
)
if "!PY_FOUND!"=="false" (
    where python3 >nul 2>&1
    if !ERRORLEVEL!==0 (
        for /f "delims=" %%v in ('python3 --version 2^>^&1') do set "PY_VERSION=%%v"
        call :ok "Python3: !PY_VERSION!"
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
        call :ok "openai-whisper package: installed"
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
        call :ok "Whisper models in cache:"
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
    call :ok "ffmpeg: installed (audio recording)"
    set "FFMPEG_FOUND=true"
) else (
    call :warn "ffmpeg NOT found - need for audio recording"
)

REM sox
where sox >nul 2>&1
if !ERRORLEVEL!==0 (
    call :ok "sox: installed (alternative audio recorder)"
) else (
    call :warn "sox NOT found"
)

REM Overall
set "VOICE_READY=false"
if "!PY_FOUND!"=="true" if "!WHISPER_PKG!"=="true" if "!WHISPER_MODEL!"=="true" (
    if "!FFMPEG_FOUND!"=="true" (
        set "VOICE_READY=true"
        call :ok "Voice/whisper system: READY"
    )
)
if "!VOICE_READY!"=="false" (
    call :warn "Voice/whisper system: NOT READY"
)
goto :eof

REM ─── Voice install guide ─────────────────────────────────────────────────
:voice_install_help
echo.
echo =============================================================
echo   VOICE/WHISPER INSTALLATION GUIDE (Windows)
echo =============================================================
echo.
echo STEP 1: Install Python
echo   https://www.python.org/downloads/
echo   IMPORTANT: Add Python to PATH during install
echo.
echo STEP 2: Install ffmpeg
echo   scoop install ffmpeg
echo   OR: choco install ffmpeg
echo   OR: https://ffmpeg.org/download.html
echo.
echo STEP 3: Install openai-whisper
echo   pip install openai-whisper
echo   Verify: python -c "import whisper; print('OK')"
echo.
echo STEP 4: Download whisper model
echo   python -m whisper --model medium
echo   ^(Downloads ~769MB model to %USERPROFILE%\.cache\whisper\^)
echo.
echo STEP 5: Re-run this script
echo   cd %AGENT_DIR%
echo   start_agents.bat
echo.
echo Then use voice with: %AGENT_DIR%dictate.bat
echo.
pause
goto :eof

:main
echo.
echo =============================================================
echo    EliaAI Agent  (Windows)
echo =============================================================
echo.

REM Check opencode
where opencode >nul 2>&1
if !ERRORLEVEL!==0 (
    for /f "delims=" %%v in ('opencode --version 2^>^&1 ^| findstr /r "[0-9]"') do call :ok "OpenCode: %%v"
) else (
    call :error "OpenCode CLI NOT FOUND"
    call :info "Run: start_agents.bat --voice-install"
    exit /b 1
)

REM Voice check
call :check_voice

REM Build loop prompt
if "!RALPH_MODE!"=="true" (
    set "LOOP_MODE_DISPLAY=Ralph (50 iters)"
    set "LOOP_COMMAND=ralph-loop"
    set "LOOP_ARGS=--completion-promise COMPLETE --max-iterations 50"
    echo Using Ralph loop ^(max 50 iterations^)
) else (
    set "LOOP_MODE_DISPLAY=ULW ^(unlimited^)"
    set "LOOP_COMMAND=ulw-loop"
    set "LOOP_ARGS=--completion-promise DONE --max-iterations 0"
    echo Using ULW-LOOP ^(unlimited iterations^)
)

echo Loop mode: !LOOP_MODE_DISPLAY!
echo Timestamp: !TS!
echo Next run in: !NEXT_RUN_HOURS! hour(s)
echo Model: !MODEL_TO_USE!
echo.

REM oh-my-opencode check
set "OMO_RUN_CMD="
where oh-my-opencode >nul 2>&1
if !ERRORLEVEL!==0 (
    if "!OMO_ENABLED!"=="true" (
        for /f "delims=" %%v in ('oh-my-opencode --version 2^>^&1 ^| findstr /r "[0-9]"') do set "OMOV=%%v"
        echo oh-my-opencode enabled: !OMOV!
        set "OMO_RUN_CMD=oh-my-opencode run"
    ) else (
        echo OMO disabled - using direct opencode
        set "OMO_RUN_CMD=opencode run"
    )
) else (
    echo oh-my-opencode not found - using direct opencode
    set "OMO_RUN_CMD=opencode run"
)

REM WSL check
where wsl >nul 2>&1
set "IS_WSL=false"
if !ERRORLEVEL!==0 set "IS_WSL=true"

REM Build prompt
set "LOOP_PROMPT=You are EliaAI, an autonomous AI assistant for Wael Bousfira.

YOUR BUSINESSES:
- EliaIA: AI solutions and automation
- ZovaBoost: Digital marketing and growth
- CoBou Agency: Creative and web agency
- Bene2Luxe: Luxury e-commerce platform

YOUR TASK:
1. Read context from %AGENT_DIR%context\ ^(business.md, opportunities.md, jira-projects.md, TOOLS.md^)
2. Check docs\ for recent work logs and TODOs
3. Identify bugs, incomplete tasks, or issues
4. DO ACTUAL WORK - write code, fix bugs, complete tasks
5. VERIFY your work - check that code compiles/runs
6. Report progress via curl to ntfy.sh/AITeamHelper

IMPORTANT RULES:
- Be autonomous - don''t ask for confirmation, just do the work
- Use ALL available tools ^(bash, file operations, code search^)
- Focus on DELIVERABLES not just analysis
- When stuck, try a different approach
- Document what you did in work logs

EXTRA CONTEXT: !EXTRA_CONTEXT!

Output ^<promise^>DONE^<\/promise^> when you have genuinely finished all tasks and verified your work.

!LOOP_COMMAND! !LOOP_ARGS!"

REM ─── Execute ────────────────────────────────────────────────────────────
echo Starting OpenCode agent...
echo.

REM Build and execute the opencode command
REM Note: WSL redirect to .sh removed - always runs native Windows
set "RUN_CMD=opencode run --model !MODEL_TO_USE! --dir "!AGENT_DIR!" --yes --command "!LOOP_COMMAND! !LOOP_ARGS!""

REM Execute, capture exit code, and tee output to log file
REM Windows has no native tee - use: run > logfile, then type logfile to show output
!RUN_CMD! > "%LOG_FILE%" 2>&1
set "EXEC_EXIT_CODE=!ERRORLEVEL!"

REM Show output to console
type "%LOG_FILE%"

if !EXEC_EXIT_CODE! neq 0 (
    echo.
    echo Agent exited with code !EXEC_EXIT_CODE!
)

echo.
echo =============================================================
call :ok "Log saved to: %LOG_FILE%"
echo =============================================================

endlocal
exit /b !EXEC_EXIT_CODE!
