# EliaAI – Windows Setup Guide

**NOTE:** This is the Windows adaptation of the macOS-based EliaAI system. For the main documentation, see [README.md](./README.md).

---

## Overview

EliaAI has been ported to Windows with full equivalents for all macOS shell scripts (.sh → .bat/.ps1). This includes:
- ✅ Agent launcher (`start_agents.bat`)
- ✅ Interactive trigger (`trigger_opencode_interactive.bat`)
- ✅ Morning trigger (`trigger_morning.bat`)
- ✅ Cron manager (`manage_cron.bat` + `cron_monitor.ps1`)
- ✅ Voice dictation (`dictate.bat`)
- ✅ Config backup/restore (`backup_config.bat`, `restore_config.bat`)
- ✅ Full installer (`installer.bat`)

---

## Prerequisites

### Required Software

| Tool | Purpose | Install |
|------|---------|---------|
| **OpenCode CLI** | AI agent runtime | `scoop install opencode` or [opencode.ai](https://opencode.ai/) |
| **Node.js / npm** | Package management | [nodejs.org](https://nodejs.org/) |
| **Git for Windows** | Bash tools, SSH | [git-scm.com](https://git-scm.com/download/win) |
| **PowerShell 5+** | Scripts & scheduler | Built-in on Windows 10+ |

### Recommended

| Tool | Purpose | Install |
|------|---------|---------|
| **Scoop** | Package manager | `iwr -useb get.scoop.sh \| iex` |
| **WSL** | Full Unix compatibility | `wsl --install` (Admin PowerShell) |
| **7-Zip** | ZIP file handling | [7-zip.org](https://www.7-zip.org/) |

### Voice Dictation (Optional)

| Tool | Purpose | Install |
|------|---------|---------|
| **Python** | Whisper runtime | [python.org/downloads](https://www.python.org/downloads/) |
| **ffmpeg** | Audio recording | `scoop install ffmpeg` |
| **openai-whisper** | Transcription | `pip install openai-whisper` |
| **Whisper model** | AI model (~769MB) | `python -m whisper --model medium` |

---

## Installation

### Step 1: Clone/Copy EliaAI to Windows

```batch
# Example path: C:\Users\YourName\EliaAI\
```

### Step 2: Run the Installer

```batch
cd C:\Users\YourName\EliaAI\setup
installer.bat
```

The installer will:
1. Check for git, node, npm, bun, opencode, oh-my-opencode
2. Create `%APPDATA%\opencode\` config directories
3. Apply big-pickle-only configuration (free models only)
4. Install Dracula theme
5. Set up rate-limit-fallback plugin

### Step 3: Install oh-my-opencode (Recommended: use WSL)

```batch
# Option A: WSL (RECOMMENDED - full compatibility)
wsl --install
wsl -e curl -fsSL https://bun.sh/install | bash
wsl -e bunx oh-my-opencode install

# Option B: npm
npm install -g oh-my-opencode

# Option C: Direct download from https://opencode.ai/
```

---

## Usage

### Manual Agent Run

```batch
cd C:\Users\YourName\EliaAI

# Basic run (big-pickle model)
start_agents.bat

# With extra context
start_agents.bat --extra-prompt="Check latest messages"

# With specific model
start_agents.bat --model=big-pickle
```

### Interactive Run (ULW Loop)

```batch
trigger_opencode_interactive.bat
```

### Voice Dictation

```batch
dictate.bat
```

**First time setup:**
```batch
start_agents.bat --voice-install
```

### Cron Scheduling (Windows = PowerShell Monitor)

```batch
cd C:\Users\YourName\EliaAI

# Install standard scheduler (every hour, 11:00-21:00)
manage_cron.bat install

# Install morning scheduler (10:00 daily)
manage_cron.bat install-morning --morning-hour 10

# Check status
manage_cron.bat show

# Uninstall all
manage_cron.bat uninstall
```

**Scheduling Options:**
```batch
manage_cron.bat install --interval 2h --start 10 --end 22
manage_cron.bat install --interval 30min --start 9 --end 23
```

### Config Backup & Restore

```batch
# Backup
setup\backup_config.bat

# Restore
setup\restore_config.bat elia_config_backup_*.zip
```

---

## Voice Dictation Setup

### Step 1: Find Your Microphone Name

```batch
ffmpeg -list_devices true -f dshow -i dummy
```

Note the exact name (e.g., `Microphone (USB Audio Device)`).

### Step 2: Install Dependencies

```batch
# Python (download from python.org - CHECK "Add to PATH")

# ffmpeg
scoop install ffmpeg

# Whisper
pip install openai-whisper

# Download model (medium recommended - ~769MB)
python -m whisper --model medium
```

### Step 3: Verify Installation

```batch
start_agents.bat --voice-check
```

---

## Windows-Specific Differences

### Path Differences

| macOS | Windows |
|-------|---------|
| `~/.config/opencode/` | `%APPDATA%\opencode\` |
| `~/EliaAI/` | `%USERPROFILE%\EliaAI\` |
| `/Users/name/` | `%USERPROFILE%\` |
| Forward slashes `/` | Backslashes `\` |

### Command Differences

| macOS | Windows |
|-------|---------|
| `./script.sh` | `script.bat` or `call script.bat` |
| `export VAR=value` | `set VAR=value` |
| `mkdir -p dir` | `if not exist dir mkdir dir` |
| `tee` | PowerShell `Tee-Object` |
| `cron` | PowerShell background monitor |
| `launchctl` | Task Scheduler |

### Script File Map

| macOS (.sh) | Windows (.bat/.ps1) |
|-------------|---------------------|
| `start_agents.sh` | `start_agents.bat` |
| `trigger_opencode.sh` | REMOVED (use interactive) |
| `trigger_opencode_interactive.sh` | `trigger_opencode_interactive.bat` |
| `trigger_morning.sh` | `trigger_morning.bat` |
| `manage_cron.sh` | `manage_cron.bat` + `cron_monitor.ps1` |
| `dictate.command` | `dictate.bat` |
| `backup_config.sh` | `setup\backup_config.bat` |
| `restore_config.sh` | `setup\restore_config.bat` |
| `installer.sh` | `setup\installer.bat` |

---

## Known Limitations on Windows

### 1. oh-my-opencode Best on WSL
The oh-my-opencode subagent system works best with WSL. On native Windows, it falls back to direct `opencode run` commands, which bypasses the subagent architecture.

### 2. PowerShell Cron Monitor
Windows has no native cron. The scripts use a PowerShell background process that runs continuously. This can be terminated by Windows Update or system sleep. For production use, consider:
- Using a Windows Scheduled Task that runs `trigger_opencode_interactive.bat` at intervals
- Or always keeping a terminal open with the cron monitor running

### 3. ANSI Colors
cmd.exe has limited ANSI color support. Color output may not display correctly on older Windows versions. Consider using Windows Terminal for better compatibility.

### 4. Microphone Name
Voice dictation requires the exact name of your microphone device. See "Find Your Microphone Name" above.

---

## Troubleshooting

### "tee" command not found
This means you're running a command that uses `tee`. On native Windows, use PowerShell instead:
```batch
# Instead of:
command | tee log.txt

# Use:
powershell -Command "command | Tee-Object log.txt"
```

### OpenCode CLI not found
```batch
# Install via Scoop
scoop install opencode

# Or via npm
npm install -g opencode

# Or download from https://opencode.ai/
```

### Voice dictation fails
1. Check microphone name: `ffmpeg -list_devices true -f dshow -i dummy`
2. Verify whisper installed: `python -c "import whisper; print('OK')"`
3. Check model downloaded: `dir "%USERPROFILE%\.cache\whisper\"`
4. Test ffmpeg recording: `ffmpeg -f dshow -i audio="Microphone" -t 3 test.wav`

### Cron monitor not running
```batch
# Check status
manage_cron.bat show

# Reinstall
manage_cron.bat uninstall
manage_cron.bat install

# Or start manually
start_cron_monitor.bat
```

### Colors not showing
The scripts use ANSI escape codes which work on Windows 10+ with Virtual Terminal enabled (default). If colors don't show:
1. Use Windows Terminal instead of cmd.exe
2. Or enable Virtual Terminal: `reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f`

### Scripts hang or freeze
- Press `Ctrl+C` to interrupt
- Use `taskkill /f /im powershell.exe` to kill stuck processes
- Use `taskkill /f /im cmd.exe` to kill stuck cmd processes

---

## Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| `config.json` | `%APPDATA%\opencode\` | OpenCode main config |
| `oh-my-opencode.json` | `%APPDATA%\opencode\` | Agent/subagent config |
| `rate-limit-fallback.json` | `%APPDATA%\opencode\` | Rate limit fallback |
| `dracula.json` | `%APPDATA%\opencode\themes\` | Terminal theme |
| `.opencode_model` | `EliaAI\` | Selected AI model |
| `.cron_config.json` | `EliaAI\` | Scheduler config |
| `.cron_morning_config.json` | `EliaAI\` | Morning scheduler config |

---

## Model Configuration

All scripts are pre-configured for **free OpenCode models only** (big-pickle recommended). To change the model:

### Via Environment Variable
```batch
set OPENCODE_MODEL=opencode/big-pickle
start_agents.bat
```

### Via .opencode_model File
Create `EliaAI\.opencode_model` with one line:
```
big-pickle
```

**Available free models:**
- `big-pickle` — **Recommended** (default)
- `minimax` — MiniMax M2.5 Free
- `nvidia` — NVIDIA NIM (may require API key)

---

## Architecture

```
EliaAI\
├── start_agents.bat                    # Main launcher
├── trigger_opencode_interactive.bat     # Interactive agent runner
├── trigger_opencode.bat                 # REMOVED: use trigger_opencode_interactive.bat
├── trigger_morning.bat                  # Morning trigger
├── dictate.bat                          # Voice dictation
├── manage_cron.bat                      # Cron manager
├── cron_monitor.ps1                     # PowerShell scheduler
├── start_cron_monitor.bat               # Monitor launcher
├── setup\
│   ├── installer.bat                   # Full installer
│   ├── backup_config.bat               # Config backup
│   └── restore_config.bat              # Config restore
├── context\                             # Business context files
├── PROMPT.md                           # Agent prompt
├── MORNING_PROMPT.md                   # Morning routine
└── logs\                               # Run logs
```

---

## Security Notes

- All AI calls use **only free OpenCode models** (no paid APIs)
- Config files stored in `%APPDATA%\opencode\` (user-level)
- Voice recordings stored in `%TEMP%` (temporary, auto-cleaned)
- Whisper models cached in `%USERPROFILE%\.cache\whisper\`
- No admin privileges required for normal operation

---

*For the full EliaAI documentation, see [README.md](./README.md).*
