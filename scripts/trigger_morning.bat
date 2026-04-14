@echo off
REM trigger_morning.bat - EliaAI Morning Agent (Windows)
REM Windows equivalent of trigger_morning.sh
REM Runs MORNING_PROMPT.md as the agent prompt

setlocal EnableDelayedExpansion

set "AGENT_DIR=%~dp0"
set "OPENCODE_CONFIG_DIR=%APPDATA%\opencode"
set "LOG_DIR=%AGENT_DIR%logs"
set "PLUGIN_DIR=%OPENCODE_CONFIG_DIR%\plugin"

for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set "TS_DATE=%%a%%b%%c"
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set "TS_TIME=%%a%%b"
set "TS=%TS_DATE%_%TS_TIME%"
set "LOG_FILE=%LOG_DIR%\opencode_morning_run_%TS%.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM ─── Determine model ────────────────────────────────────────────────────
if defined OPENCODE_MODEL (
    echo Using model from env: !OPENCODE_MODEL!
    set "MODEL_TO_USE=!OPENCODE_MODEL!"
) else if exist "%AGENT_DIR%.opencode_model" (
    set /p CRON_MODEL=<"%AGENT_DIR%.opencode_model"
    set "CRON_MODEL=!CRON_MODEL: =!"
    if /i "!CRON_MODEL!"=="big-pickle" set "MODEL_TO_USE=opencode/big-pickle"
    if /i "!CRON_MODEL!"=="nvidia" set "MODEL_TO_USE=mistralai/mixtral-8x7b-instruct-v0.1"
    if /i "!CRON_MODEL!"=="minimax" set "MODEL_TO_USE=opencode/minimax-m2.5-free"
    if not defined MODEL_TO_USE set "MODEL_TO_USE=opencode/big-pickle"
    echo Using model from .opencode_model: !MODEL_TO_USE!
) else (
    echo Using default model: opencode/big-pickle
    set "MODEL_TO_USE=opencode/big-pickle"
)

REM ─── Telegram inbox ─────────────────────────────────────────────────────
set "AGENT_PAYLOADS_DIR=%AGENT_DIR%.agent_payloads"
set "TELEGRAM_INBOX=%AGENT_PAYLOADS_DIR%\telegram_inbox.txt"
set "_inbox_content="

if exist "%TELEGRAM_INBOX%" (
    set /p _inbox_content=<"%TELEGRAM_INBOX%"
    del "%TELEGRAM_INBOX%" >nul 2>&1
)

REM ─── Load MORNING_PROMPT.md ────────────────────────────────────────────
set "MORNING_PROMPT_PATH=%AGENT_DIR%MORNING_PROMPT.md"
if not exist "%MORNING_PROMPT_PATH%" (
    echo [ERROR] MORNING_PROMPT.md not found: %MORNING_PROMPT_PATH%
    exit /b 1
)

set "NEXT_RUN_HOURS=24"

REM ─── Header ───────────────────────────────────────────────────────────
echo.
echo =============================================================
echo   EliaAI Morning Agent  (Windows)
echo =============================================================
echo.
echo Timestamp: %TS%
echo Next run in: %NEXT_RUN_HOURS% hours
echo.

REM ─── Create prompt file ────────────────────────────────────────────────
set "PROMPT_FILE=%TEMP%\elia_prompt_morning_%TS%.txt"

(
    echo You are EliaAI, an autonomous AI assistant for Wael Bousfira.
    echo.
    echo YOUR BUSINESSES:
    echo - EliaIA: AI solutions and automation
    echo - ZovaBoost: Digital marketing and growth
    echo - CoBou Agency: Creative and web agency
    echo - Bene2Luxe: Luxury e-commerce platform
    echo.
    echo YOUR TASK:
    echo Execute the Morning Routine as defined in MORNING_PROMPT.md below.
    echo.
    echo IMPORTANT RULES:
    echo - Be autonomous - don''t ask for confirmation, just do the work
    echo - Use ALL available tools ^(bash, file operations, code search^)
    echo - Focus on DELIVERABLES not just analysis
    echo - When stuck, try a different approach
    echo - Document what you done in work logs
    echo.
    echo EXTRA CONTEXT: %_inbox_content%
    echo.
    echo NEXT RUN INFO: This is the morning routine. Next run is tomorrow.
    echo - Complete all morning review tasks
    echo - Prepare the day ahead with task lists
    echo - Ensure all team members have their priorities.
    echo.
    echo --- MORNING_PROMPT.md Content: ---
    type "%MORNING_PROMPT_PATH%"
    echo.
    echo --- End MORNING_PROMPT.md ---
    echo.
    echo Output ^<promise^>COMPLETE^<\/promise^> when you have genuinely finished all tasks.
) > "!PROMPT_FILE!"

REM ─── Copy to log ──────────────────────────────────────────────────────
copy /y "!PROMPT_FILE!" "%LOG_DIR%\prompt_morning_%TS%.txt" >nul 2>&1

echo Starting EliaAI Morning Agent...
echo Model: !MODEL_TO_USE!
echo Using MORNING_PROMPT.md
echo.

REM ─── Run OpenCode ────────────────────────────────────────────────────
where opencode >nul 2>&1
if !ERRORLEVEL!==0 (
    REM Direct opencode run
    opencode run --model !MODEL_TO_USE! --dir "!AGENT_DIR!" --yes --command "ulw-loop --completion-promise COMPLETE" < "!PROMPT_FILE!" 2>&1 | tee "%LOG_FILE%"
    set "EXIT_CODE=!ERRORLEVEL!"
) else (
    echo [ERROR] OpenCode CLI not found
    echo Install with: scoop install opencode
    echo OR: npm install -g opencode
    set "EXIT_CODE=1"
)

REM ─── Cleanup ──────────────────────────────────────────────────────────
if exist "!PROMPT_FILE!" del "!PROMPT_FILE!" >nul 2>&1

echo.
echo =============================================================
echo Log saved to: %LOG_FILE%
echo =============================================================

endlocal
exit /b !EXIT_CODE!
