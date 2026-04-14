@echo off
REM dictate.bat - Windows Voice Dictation with Whisper Transcription
REM Windows equivalent of dictate.command
REM
REM ADAPTATION NOTES:
REM   This script records audio and transcribes it using Whisper.
REM   It then launches the AI agent with your voice as the prompt.
REM
REM PREREQUISITES (install before first use):
REM   1. Python: https://www.python.org/downloads/
REM   2. ffmpeg: scoop install ffmpeg
REM   3. openai-whisper: pip install openai-whisper
REM   4. Whisper model: python -m whisper --model medium
REM
REM USAGE:
REM   Run this script to:
REM   1. Record audio (press Enter to stop)
REM   2. Transcribe using Whisper (French language)
REM   3. Copy transcript to clipboard
REM   4. Launch AI agent with transcript as context
REM
REM MODEL SELECTION:
REM   - tiny   (39MB)  - Fastest, lowest quality
REM   - base   (74MB)  - Fast, good quality
REM   - small  (244MB) - Good balance
REM   - medium (769MB) - RECOMMENDED
REM   - large  (1550MB)- Best quality, slowest
REM
REM SHORTcuts:
REM   Run without launching agent: dictate.bat --no-launch

setlocal EnableDelayedExpansion

REM ─── Configuration ─────────────────────────────────────────────────────────
set "AGENT_DIR=%~dp0"
set "TRANSCRIPT_FILE=%TEMP%\transcript.txt"
set "AUDIO_FILE=%TEMP%\dictation.wav"
set "WHISPER_MODEL=medium"
set "REC_PID_FILE=%TEMP%\dictate_rec_pid.txt"

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

REM ─── Check for :cecho helper (used in header) ──────────────────────────────
REM Note: :cecho not defined in this script - define a simple echo wrapper
goto :main

:cecho
REM Simple echo that just prints text (no ANSI color support in this script)
echo %~1
goto :eof

:log
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

REM ─── Check dependencies ─────────────────────────────────────────────────
:check_deps
set "PYTHON_FOUND=false"
set "PY_CMD="
set "WHISPER_FOUND=false"
set "FFMPEG_FOUND=false"
set "VOICE_READY=false"

call :log "Checking voice system dependencies..."

REM Python
where python >nul 2>&1
if !ERRORLEVEL!==0 (
    for /f "delims=" %%v in ('python --version 2^>^&1') do call :ok "Python: %%v"
    set "PYTHON_FOUND=true"
    set "PY_CMD=python"
)
if "!PYTHON_FOUND!"=="false" (
    where python3 >nul 2>&1
    if !ERRORLEVEL!==0 (
        for /f "delims=" %%v in ('python3 --version 2^>^&1') do call :ok "Python3: %%v"
        set "PYTHON_FOUND=true"
        set "PY_CMD=python3"
    )
)
if "!PYTHON_FOUND!"=="false" (
    call :error "Python NOT found - install from https://www.python.org/downloads/"
    goto :deps_fail
)

REM ffmpeg
where ffmpeg >nul 2>&1
if !ERRORLEVEL!==0 (
    call :ok "ffmpeg: installed (audio recording)"
    set "FFMPEG_FOUND=true"
) else (
    call :error "ffmpeg NOT found - install with: scoop install ffmpeg"
    goto :deps_fail
)

REM whisper package
!PY_CMD! -c "import whisper; print('ok')" >nul 2>&1
if !ERRORLEVEL!==0 (
    call :ok "openai-whisper package: installed"
    set "WHISPER_FOUND=true"
) else (
    call :error "openai-whisper NOT installed"
    call :info "Install with: pip install openai-whisper"
    goto :deps_fail
)

REM whisper model
if exist "%USERPROFILE%\.cache\whisper\" (
    dir /b "%USERPROFILE%\.cache\whisper\" 2>nul | findstr /i "!WHISPER_MODEL!.pt" >nul
    if !ERRORLEVEL!==0 (
        call :ok "Whisper model '!WHISPER_MODEL!' found in cache"
    ) else (
        call :warn "Whisper model '!WHISPER_MODEL!' NOT in cache"
        call :info "Download with: !PY_CMD! -m whisper --model !WHISPER_MODEL!"
        goto :deps_fail
    )
) else (
    call :error "Whisper cache not found at %USERPROFILE%\.cache\whisper\"
    call :info "Download model with: !PY_CMD! -m whisper --model !WHISPER_MODEL!"
    goto :deps_fail
)

set "VOICE_READY=true"
exit /b 0

:deps_fail
echo.
call :error "Voice system NOT ready - please install missing dependencies"
echo.
call :info "Quick install commands:"
echo   pip install openai-whisper
echo   !PY_CMD! -m whisper --model !WHISPER_MODEL!
echo   scoop install ffmpeg
echo.
call :info "Or run: start_agents.bat --voice-install"
echo.
pause
exit /b 1

REM ─── Record audio ─────────────────────────────────────────────────────────
:record_audio
echo.
call :ok "Starting audio recording..."
echo.
echo Press ENTER to stop recording.
echo.

REM Delete old audio
if exist "!AUDIO_FILE!" del "!AUDIO_FILE!" >nul 2>&1

REM Record with ffmpeg using PowerShell background job (more reliable than start /b)
REM Start ffmpeg in background, save PID to file
powershell -Command "Start-Process -FilePath 'ffmpeg' -ArgumentList '-f dshow -i audio=\"Microphone\" -ar 16000 -ac 1 -c:a pcm_s16le -y \"%AUDIO_FILE%\"' -WindowStyle Hidden -PassThru | Select-Object -ExpandProperty Id" > "!REC_PID_FILE!" 2>nul

REM Wait for user to press Enter
set /p STOP_RECORDING=""

REM Stop ffmpeg using the recorded PID
if exist "!REC_PID_FILE!" (
    set /p REC_PID=<"!REC_PID_FILE!"
    if defined REC_PID (
        taskkill /f /pid !REC_PID! >nul 2>&1
    )
    del "!REC_PID_FILE!" >nul 2>&1
)

REM Also kill any remaining ffmpeg instances started by this script
taskkill /f /im ffmpeg.exe >nul 2>&1

exit /b 0

REM ─── Transcribe ──────────────────────────────────────────────────────────
:transcribe
echo.
call :log "Transcribing audio with Whisper ^(model: !WHISPER_MODEL!^)..."
echo.

REM Run whisper transcription
!PY_CMD! -c "
import whisper
print('Loading model...')
model = whisper.load_model('!WHISPER_MODEL!')
print('Transcribing...')
result = model.transcribe('!AUDIO_FILE!', language='fr', task='transcribe')
print('DONE')
print(result['text'].strip())
" > "!TRANSCRIPT_FILE!" 2>&1

REM Check if transcription succeeded
findstr /i "DONE" "!TRANSCRIPT_FILE!" >nul 2>&1
if !ERRORLEVEL!==0 (
    REM Extract just the transcript (remove DONE marker)
    findstr /v /i "Loading Transcribing DONE" "!TRANSCRIPT_FILE!" > "!TRANSCRIPT_FILE!.tmp"
    move /y "!TRANSCRIPT_FILE!.tmp" "!TRANSCRIPT_FILE!" >nul 2>&1
    exit /b 0
) else (
    REM Show error
    type "!TRANSCRIPT_FILE!"
    exit /b 1
)

REM ─── Copy to clipboard ──────────────────────────────────────────────────
:clipboard
REM Windows clipboard via PowerShell
powershell -Command "Get-Content '!TRANSCRIPT_FILE!' | Set-Clipboard" 2>nul
if !ERRORLEVEL!==0 (
    call :ok "Transcript copied to clipboard"
) else (
    call :warn "Could not copy to clipboard"
)
goto :eof

REM ─── Count words ─────────────────────────────────────────────────────────
:count_words
set "WORD_COUNT=0"
for /f %%c in ('findstr /r "[a-zA-Z]" ^< "!TRANSCRIPT_FILE!" ^| find /c /v ""') do set "WORD_COUNT=%%c"
exit /b 0

REM ─── Usage ────────────────────────────────────────────────────────────────
:show_usage
echo Usage: dictate.bat [OPTIONS]
echo.
echo Options:
echo   --model=MODEL    Whisper model: tiny, base, small, medium, large
echo                    Default: medium ^(recommended^)
echo   --no-launch      Record and transcribe only, don't launch agent
echo   --help, -h       Show this help
echo.
echo Prerequisites:
echo   1. Python: https://www.python.org/downloads/
echo   2. ffmpeg: scoop install ffmpeg
echo   3. Whisper: pip install openai-whisper
echo   4. Model: python -m whisper --model medium
echo.
echo Examples:
echo   dictate.bat
echo   dictate.bat --model=small
echo   dictate.bat --no-launch
exit /b 0

:main
REM ─── Parse args ──────────────────────────────────────────────────────────
set "NO_LAUNCH=false"
set "CUSTOM_MODEL="

:parse_loop
if "%~1"=="" goto :parse_done

if /i "%~1"=="-h" goto :show_usage
if /i "%~1"=="--help" goto :show_usage
if /i "%~1"=="--no-launch" (
    set "NO_LAUNCH=true"
    shift
    goto :parse_loop
)

echo %~1 | findstr /i "--model=" >nul
if !ERRORLEVEL!==0 (
    set "CUSTOM_MODEL=%~1"
    set "CUSTOM_MODEL=!CUSTOM_MODEL:*--model=!"
    set "CUSTOM_MODEL=!CUSTOM_MODEL:~1!"
    shift
    goto :parse_loop
)

shift
goto :parse_loop

:parse_done

if not "!CUSTOM_MODEL!"=="" set "WHISPER_MODEL=!CUSTOM_MODEL!"

REM ─── Header ─────────────────────────────────────────────────────────────
echo.
echo =============================================================
echo    Windows Voice Dictation - EliaAI
echo =============================================================
echo.

REM ─── Check JARVIS_MODEL env ────────────────────────────────────────────
if defined JARVIS_MODEL (
    set "AGENT_MODEL=!JARVIS_MODEL!"
) else (
    set "AGENT_MODEL=big-pickle"
)
call :log "Agent model: !AGENT_MODEL!"

REM ─── Check dependencies ─────────────────────────────────────────────────
call :check_deps
if "!VOICE_READY!"=="false" exit /b 1

REM ─── Record audio ────────────────────────────────────────────────────────
echo.
echo =============================================================
echo   Recording audio... Speak now!
echo   Press ENTER to stop recording
echo =============================================================
echo.

if exist "!AUDIO_FILE!" del "!AUDIO_FILE!" >nul 2>&1

REM Start recording in background using PowerShell (more reliable than start /b on Windows)
powershell -Command "Start-Process -FilePath 'ffmpeg' -ArgumentList '-f dshow -i audio=\"Microphone\" -ar 16000 -ac 1 -c:a pcm_s16le -y \"%AUDIO_FILE%\"' -WindowStyle Hidden -PassThru | Select-Object -ExpandProperty Id" > "!REC_PID_FILE!" 2>nul

REM Wait for user to press Enter
set /p STOP_RECORDING=""

REM Stop ffmpeg using the recorded PID
if exist "!REC_PID_FILE!" (
    set /p REC_PID=<"!REC_PID_FILE!"
    if defined REC_PID (
        taskkill /f /pid !REC_PID! >nul 2>&1
    )
    del "!REC_PID_FILE!" >nul 2>&1
)
REM Also kill any remaining ffmpeg started by this script
taskkill /f /im ffmpeg.exe >nul 2>&1

echo.
call :log "Recording stopped"
echo.

REM Check if audio was recorded
if not exist "!AUDIO_FILE!" (
    call :error "No audio recorded - is your microphone working?"
    call :info "Try: ffmpeg -list_devices true -f dshow -i dummy"
    pause
    exit /b 1
)

REM ─── Transcribe ──────────────────────────────────────────────────────────
call :log "Transcribing with Whisper..."

!PY_CMD! -c "
import whisper, sys
print('Loading whisper model: !WHISPER_MODEL!...', file=sys.stderr)
model = whisper.load_model('!WHISPER_MODEL!')
print('Transcribing audio...', file=sys.stderr)
result = model.transcribe('!AUDIO_FILE!', language='fr', task='transcribe')
print(result['text'].strip())
" 2>nul > "!TRANSCRIPT_FILE!"

REM Read transcript
set /p TRANSCRIPT=<"!TRANSCRIPT_FILE!"
if not defined TRANSCRIPT (
    call :error "Transcription failed"
    pause
    exit /b 1
)

REM ─── Display transcript ─────────────────────────────────────────────────
echo.
call :ok "Transcript:"
echo --------------------------------------------------------
type "!TRANSCRIPT_FILE!"
echo --------------------------------------------------------
echo.

REM ─── Copy to clipboard ───────────────────────────────────────────────────
powershell -Command "Get-Content '!TRANSCRIPT_FILE!' | Set-Clipboard" 2>nul
call :ok "Copied to clipboard"

REM ─── Launch agent if transcript has content ──────────────────────────────
if "!NO_LAUNCH!"=="true" (
    call :log "Skipping agent launch (--no-launch flag)"
    pause
    exit /b 0
)

REM Count words
set WORD_COUNT=0
for /f %%c in ('findstr /r "[a-zA-Z]" ^< "!TRANSCRIPT_FILE!" ^| find /c /v ""') do set WORD_COUNT=%%c

if !WORD_COUNT! gtr 3 (
    echo.
    call :ok "Transcript has !WORD_COUNT! words - launching AI agent..."
    echo.
    call :log "Starting EliaAI with voice prompt..."
    echo.

    cd /d "!AGENT_DIR!"
    call start_agents.bat --model=!AGENT_MODEL! --extra-prompt="!TRANSCRIPT!"
) else (
    echo.
    call :warn "Transcript too short (!WORD_COUNT! words) - skipping agent launch"
)

echo.
pause
endlocal
exit /b 0
