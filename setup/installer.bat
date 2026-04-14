@echo off
REM installer.bat - Full Windows installer for EliaAI + OpenCode + oh-my-opencode
REM
REM ============================================================
REM WINDOWS ADAPTATION NOTES
REM ============================================================
REM This file is the Windows-equivalent of installer.sh.
REM Key differences from macOS/Linux:
REM
REM  PATH VARIABLES:
REM   macOS: ~  = %USERPROFILE%
REM   macOS: $HOME = %USERPROFILE%
REM   macOS: ${HOME}/.config/opencode = %APPDATA%\opencode
REM
REM  SHELL COMMANDS vs WINDOWS:
REM   macOS: curl -fsSL | bash   = Invoke-WebRequest + cmd /c (PowerShell)
REM   macOS: chmod +x script.sh  = Not needed on Windows
REM   macOS: mkdir -p dir        = mkdir dir 2>nul & if not exist dir mkdir dir
REM   macOS: export VAR=value    = set VAR=value (in cmd) / $env:VAR = "value" (in PowerShell)
REM   macOS: ${VAR}/path         = %VAR%\path
REM   macOS: $(command)           = $(command) in PowerShell or FOR /f
REM   macOS: # comments          = REM or :: comments
REM   macOS: echo -e "\033..."   = echo [TEXT] (no ANSI colors in cmd, use PowerShell or ANSI.SYS)
REM   macOS: zsh/bash shebang     = No shebang on Windows (.bat / .cmd auto-detected)
REM
REM  OPENCODE/OH-MY-OPENCODE:
REM   On Windows, opencode may be installed via:
REM   - Scoop:   scoop install opencode
REM   - Manual:  Download from https://opencode.ai/
REM   - npm:     npm install -g opencode
REM
REM   oh-my-opencode on Windows:
REM   - Requires WSL (Windows Subsystem for Linux) for best compatibility
REM   - OR: npm install -g oh-my-opencode
REM   - OR: bunx oh-my-opencode install (if bun installed via WSL)
REM
REM  ELIAAI SCRIPTS ADAPTATION:
REM   EliaAI shell scripts (.sh) need to be converted to batch files (.bat) for Windows:
REM   - start_agents.sh    -> start_agents.bat  (convert shebang, export, zsh-isms)
REM   - trigger_opencode.sh -> trigger_opencode.bat
REM   - backup_config.sh   -> backup_config.bat
REM   - restore_config.sh  -> restore_config.bat
REM   - installer.sh       -> installer.bat (this file)
REM
REM  TIPS FOR CONVERTING .sh TO .bat:
REM   1. Remove #!/bin/zsh or #!/bin/bash shebang
REM   2. Replace export VAR=value with set VAR=value
REM   3. Replace ${VAR} with %VAR%
REM   4. Replace $(command) with FOR /f or call :function
REM   5. Replace echo -e "\033..." with echo [message]
REM   6. Replace mkdir -p with: if not exist "dir" mkdir "dir"
REM   7. Replace || true with (goto :eof) or if errorlevel
REM   8. Replace set -euo pipefail with if not defined see docs
REM   9. Replace [[ condition ]] with if condition
REM   10. Replace ${0:a:h} with %~dp0
REM   11. Replace command &> /dev/null with >nul 2>&1
REM   12. Replace ${SCRIPT_DIR:-$DEFAULT} with %SCRIPT_DIR% or %DEFAULT%
REM   13. Replace $(date +%Y%m%d) with %date:~-4%%date:~4,2%%date:~7,2%
REM   14. Replace :? patterns with goto labels or if defined checks
REM   15. Replace tr/d/ commands with string manipulation or for loops
REM
REM ============================================================
REM BEFORE RUNNING THIS SCRIPT ON WINDOWS:
REM ============================================================
REM 1. Install Git for Windows (provides bash, curl, git):
REM    https://git-scm.com/download/win
REM
REM 2. Install WSL (recommended for full oh-my-opencode support):
REM    Open PowerShell as Admin: wsl --install
REM    Then use the WSL terminal for oh-my-opencode installation
REM
REM 3. OR Install Scoop (Windows package manager):
REM    In PowerShell: iwr -useb get.scoop.sh | iex
REM    Then: scoop install opencode bun node
REM
REM 4. OR Install npm/node manually:
REM    https://nodejs.org/
REM    Then: npm install -g opencode
REM
REM 5. Clone/copy EliaAI to a Windows path:
REM    Example: C:\Users\YourName\EliaAI\
REM
REM 6. Update paths in this script:
REM    - %ELIA_ROOT% should point to your EliaAI folder
REM    - %OPENCODE_CONFIG_DIR% should be %APPDATA%\opencode
REM    - %SCRIPT_DIR% is auto-detected (%~dp0)
REM
REM ============================================================

setlocal EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
set "ELIA_ROOT=%SCRIPT_DIR%"
set "OPENCODE_CONFIG_DIR=%APPDATA%\opencode"

set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "CYAN=[96m"
set "NC=[0m"

goto :main

:color_echo
REM Usage: call :color_echo %RED% "message"
REM Note: Windows cmd.exe has limited ANSI color support.
REM      Use PowerShell or enable Virtual Terminal on Windows 10+.
setlocal & endlocal & (
    echo %~1%~2%NC%
)
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

:main
echo.
echo =============================================================
echo   EliaAI + OpenCode Installer  (Windows)
echo =============================================================
echo.

call :log "Phase 1: Checking prerequisites..."

REM Check for git (provides bash/curl)
where git >nul 2>&1
if %ERRORLEVEL%==0 (
    call :ok "git found: "
    git --version
) else (
    call :warn "git not found - install from https://git-scm.com/download/win"
)

REM Check for node
where node >nul 2>&1
if %ERRORLEVEL%==0 (
    call :ok "node found: "
    node --version
) else (
    call :warn "node not found - install from https://nodejs.org/"
)

REM Check for npm
where npm >nul 2>&1
if %ERRORLEVEL%==0 (
    call :ok "npm found: "
    npm --version
) else (
    call :warn "npm not found - install Node.js from https://nodejs.org/"
)

REM Check for bun
where bun >nul 2>&1
if %ERRORLEVEL%==0 (
    call :ok "bun found: "
    bun --version
) else (
    call :info "bun not found - optional. Install via: scoop install bun"
    call :info "         OR: curl -fsSL https://bun.sh/install.bat | cmd /d/s/c"
)

echo.
call :log "Phase 2: Installing OpenCode CLI..."

where opencode >nul 2>&1
if %ERRORLEVEL%==0 (
    call :ok "OpenCode already installed: "
    opencode --version 2>nul
) else (
    call :info "OpenCode CLI not found. Installation options:"
    call :info "  Option 1: scoop install opencode   (if Scoop installed)"
    call :info "  Option 2: npm install -g opencode  (if npm installed)"
    call :info "  Option 3: Download from https://opencode.ai/"
    call :info ""
    call :info "After installing OpenCode, re-run this script."
    set /p CONTINUE="Press Enter to continue with config setup anyway, or Ctrl+C to exit..."
)

echo.
call :log "Phase 3: Installing oh-my-opencode..."

where oh-my-opencode >nul 2>&1
if %ERRORLEVEL%==0 (
    call :ok "oh-my-opencode already installed: "
    oh-my-opencode --version 2>nul
) else (
    call :info "oh-my-opencode not found. Installation options:"
    call :info "  Option 1 (WSL recommended):"
    call :info "    wsl --install"
    call :info "    wsl -e curl -fsSL https://bun.sh/install | bash"
    call :info "    wsl -e bunx oh-my-opencode install"
    call :info "  Option 2 (npm): npm install -g oh-my-opencode"
    call :info "  Option 3 (bun on Windows): bunx oh-my-opencode install"
    call :info ""
    call :info "oh-my-opencode works best on WSL for full compatibility."
)

echo.
call :log "Phase 4: Setting up OpenCode configuration..."

if not exist "%OPENCODE_CONFIG_DIR%" (
    call :log "Creating OpenCode config directory: %OPENCODE_CONFIG_DIR%"
    mkdir "%OPENCODE_CONFIG_DIR%" 2>nul
)

REM Create subdirectories
if not exist "%OPENCODE_CONFIG_DIR%\agents" mkdir "%OPENCODE_CONFIG_DIR%\agents"
if not exist "%OPENCODE_CONFIG_DIR%\skills" mkdir "%OPENCODE_CONFIG_DIR%\skills"
if not exist "%OPENCODE_CONFIG_DIR%\themes" mkdir "%OPENCODE_CONFIG_DIR%\themes"
if not exist "%OPENCODE_CONFIG_DIR%\docs" mkdir "%OPENCODE_CONFIG_DIR%\docs"
if not exist "%OPENCODE_CONFIG_DIR%\plugin" mkdir "%OPENCODE_CONFIG_DIR%\plugin"

call :ok "Config directories created"

echo.
call :log "Phase 5: Applying recommended configuration..."

REM Create config.json
set "CONFIG_JSON=%OPENCODE_CONFIG_DIR%\config.json"
if not exist "%CONFIG_JSON%" (
    call :log "Creating config.json..."
    (
        echo {
        echo   "$schema": "https://opencode.ai/config.json",
        echo   "permission": {
        echo     "read": "allow",
        echo     "edit": "allow",
        echo     "glob": "allow",
        echo     "grep": "allow",
        echo     "list": "allow",
        echo     "bash": "allow",
        echo     "task": "allow",
        echo     "external_directory": "allow",
        echo     "todowrite": "allow",
        echo     "todoread": "allow",
        echo     "question": "allow",
        echo     "webfetch": "allow",
        echo     "websearch": "allow",
        echo     "codesearch": "allow",
        echo     "lsp": "allow",
        echo     "doom_loop": "allow",
        echo     "skill": "allow"
        echo   },
        echo   "theme": "dracula"
        echo }
    ) > "%CONFIG_JSON%"
    call :ok "config.json created (dracula theme, big-pickle only)"
) else (
    call :info "config.json already exists - skipping"
)

REM Create oh-my-opencode.json
set "OMO_JSON=%OPENCODE_CONFIG_DIR%\oh-my-opencode.json"
if not exist "%OMO_JSON%" (
    call :log "Creating oh-my-opencode.json..."
    (
        echo {
        echo   "$schema": "https://raw.githubusercontent.com/code-yeongyu/oh-my-openagent/dev/assets/oh-my-opencode.schema.json",
        echo   "model_fallback": false,
        echo   "default_run_agent": "sisyphus",
        echo   "agents": {
        echo     "sisyphus": { "model": "opencode/big-pickle", "fallback_models": [] },
        echo     "sisyphus-junior": { "model": "opencode/big-pickle", "fallback_models": [] },
        echo     "hephaestus": { "model": "opencode/big-pickle", "fallback_models": [] },
        echo     "prometheus": { "model": "opencode/big-pickle", "fallback_models": [] },
        echo     "metis": { "model": "opencode/big-pickle", "fallback_models": [] },
        echo     "atlas": { "model": "opencode/big-pickle", "fallback_models": [] },
        echo     "oracle": { "model": "opencode/big-pickle", "fallback_models": [] },
        echo     "librarian": { "model": "opencode/big-pickle", "fallback_models": [] },
        echo     "explore": { "model": "opencode/big-pickle", "fallback_models": [] },
        echo     "momus": { "model": "opencode/big-pickle", "fallback_models": [] }
        echo   },
        echo   "agent_display_names": {
        echo     "sisyphus": "Elia"
        echo   }
        echo }
    ) > "%OMO_JSON%"
    call :ok "oh-my-opencode.json created (big-pickle only, no fallbacks)"
) else (
    call :info "oh-my-opencode.json already exists - skipping"
)

REM Create rate-limit-fallback.json
set "RLF_JSON=%OPENCODE_CONFIG_DIR%\rate-limit-fallback.json"
if not exist "%RLF_JSON%" (
    call :log "Creating rate-limit-fallback.json..."
    (
        echo {
        echo   "enabled": true,
        echo   "fallbackModel": "opencode/big-pickle",
        echo   "cooldownMs": 60000,
        echo   "patterns": [
        echo     "rate limit", "usage limit", "too many requests",
        echo     "quota exceeded", "overloaded", "capacity exhausted",
        echo     "limit exceeded", "rate_limit_exceeded",
        echo     "RESOURCE_EXHAUSTED", "No capacity available"
        echo   ],
        echo   "logging": true
        echo }
    ) > "%RLF_JSON%"
    call :ok "rate-limit-fallback.json created"
)

REM Install Dracula theme
set "DRACULA_JSON=%OPENCODE_CONFIG_DIR%\themes\dracula.json"
if not exist "%DRACULA_JSON%" (
    call :log "Installing Dracula theme..."
    (
        echo {
        echo   "black": "#000000",
        echo   "red": "#ff5555",
        echo   "green": "#50fa7b",
        echo   "yellow": "#f1fa8c",
        echo   "blue": "#6272a4",
        echo   "magenta": "#ff79c6",
        echo   "cyan": "#8be9fd",
        echo   "white": "#f8f8f2",
        echo   "brightBlack": "#555555",
        echo   "brightRed": "#ff6e67",
        echo   "brightGreen": "#69ff94",
        echo   "brightYellow": "#ffffa5",
        echo   "brightBlue": "#d6acff",
        echo   "brightMagenta": "#ff92df",
        echo   "brightCyan": "#a4ffff",
        echo   "brightWhite": "#ffffff",
        echo   "background": "#282a36",
        echo   "foreground": "#f8f8f2",
        echo   "selectionBackground": "#44475a",
        echo   "cursorColor": "#f8f8f2"
        echo }
    ) > "%DRACULA_JSON%"
    call :ok "Dracula theme installed"
)

echo.
call :log "Phase 6: Installing rate-limit-fallback plugin..."

set "RLF_PLUGIN=%OPENCODE_CONFIG_DIR%\plugin\rate-limit-fallback"
if not exist "%RLF_PLUGIN%" (
    call :log "Creating rate-limit-fallback plugin..."
    mkdir "%RLF_PLUGIN%\src" 2>nul
    (
        echo {
        echo   "name": "rate-limit-fallback",
        echo   "version": "1.0.0",
        echo   "type": "module"
        echo }
    ) > "%RLF_PLUGIN%\package.json"
    call :ok "rate-limit-fallback plugin created"
) else (
    call :info "rate-limit-fallback plugin already exists - skipping"
)

echo.
call :log "Phase 7: Finalizing..."

REM Fix permissions (Windows equivalent - attrib)
attrib +r "%CONFIG_JSON%" 2>nul
attrib +r "%OMO_JSON%" 2>nul
attrib +r "%RLF_JSON%" 2>nul
attrib +r "%DRACULA_JSON%" 2>nul

echo.
echo =============================================================
call :ok "Installation complete!"
echo =============================================================
echo.
call :info "Installed:"
call :info "  - Config directories in %OPENCODE_CONFIG_DIR%"
call :info "  - Dracula theme"
call :info "  - rate-limit-fallback plugin"
echo.
call :info "Config location: %OPENCODE_CONFIG_DIR%"
call :info "Backup scripts: %ELIA_ROOT%setup\backup_config.bat"
call :info "Restore script:  %ELIA_ROOT%setup\restore_config.bat"
echo.
call :info "To start EliaAI:"
call :info "  cd %ELIA_ROOT%"
call :info "  opencode"
echo.
call :info "IMPORTANT - Windows-specific:"
call :info "  - For full oh-my-opencode support, use WSL (Windows Subsystem for Linux)"
call :info "  - EliaAI shell scripts need .bat equivalents on Windows"
call :info "  - See comments at the top of this file for .sh to .bat conversion guide"
echo.
pause

endlocal
