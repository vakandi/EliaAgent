# EliaAI Release Notes

---

## 🚀 Version: v6.0.0 — 🤝 TEAM MODE + PUBLIC RELEASE (August 22, 2026)

### ✨ The Big News: Team Mode — Multi-Agent Collaboration

**🤝 What changed**: Multiple AI agents can now work together **in real-time**, talking to each other via a shared mailbox — not just delegating. Teams are accessible from **any OpenCode session**, work with **custom agents**, and can handle complex tasks that need multiple specialists working simultaneously.

### Team Mode Features

| Feature | What It Does |
|---------|-------------|
| **Real-time collaboration** | Agents send messages to each other, share findings, debate approaches, and coordinate — not just fire-and-forget |
| **Works everywhere** | Accessible on all OpenCode sessions via `team_create`, `team_send_message`, `team_status` |
| **Custom agents** | Your own agents (gilfoyle, setbon, picasso, etc.) can join teams — not limited to built-in agents |
| **Subworker integration** | Complex subworker tasks can be delegated to team members for parallel execution |
| **Open allowlist** | Any registered agent can join a team by default — no need to pre-approve each one |
| **Task tracking** | Built-in task board within teams — create, claim, complete tasks with status updates |
| **Shutdown control** | Members can request shutdown, lead approves/rejects — no rogue agents |

### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                        TEAM MODE                                 │
│                                                                  │
│  user: "Build the landing page"                                  │
│       │                                                          │
│       ▼                                                          │
│  team_create → lead agent + 3 specialists                        │
│       │                                                          │
│       ├──→ @gilfoyle: "Building the API endpoints"               │
│       ├──→ @picasso: "Designing the UI components"               │
│       └──→ @setbon: "Writing the marketing copy"                 │
│                                                                  │
│  Agents talk to each other via shared mailbox:                   │
│       │                                                          │
│       ├──→ @gilfoyle → @picasso: "API returns this shape"        │
│       ├──→ @picasso → @gilfoyle: "What's the auth flow?"         │
│       └──→ @setbon → @picasso: "The hero needs to convert"       │
│                                                                  │
│  Final result: Coordinated deliverable, not 3 isolated outputs   │
└─────────────────────────────────────────────────────────────────┘
```

### Example: Create a Team

```python
# In any OpenCode session
team_create(
    teamName="landing-page-build",
    members=[
        {"name": "gilfoyle", "kind": "subagent_type", "prompt": "Build the FastAPI endpoints"},
        {"name": "picasso", "kind": "subagent_type", "prompt": "Design the React landing page"},
        {"name": "setbon", "kind": "subagent_type", "prompt": "Write conversion-optimized copy"},
    ]
)
```

### Subworker Integration

Complex subworker tasks that need multiple perspectives can now use Team Mode internally:

```python
# A subworker can create a team for complex tasks
team_create(
    members=[
        {"name": "explore", "kind": "subagent_type", "prompt": "Analyze the codebase"},
        {"name": "librarian", "kind": "subagent_type", "prompt": "Research best practices"},
    ]
)
```

### Files Changed

| Component | Change |
|-----------|--------|
| `oh-my-openagent/src/core/types.ts` | Added `TeamMember` type, team-related tool definitions |
| `oh-my-openagent/src/core/member-parser.ts` | Open allowlist — custom agents join by default |
| `oh-my-openagent/src/core/validator.ts` | Team validation with graceful fallback |
| `setup/OH-MY-OPENCODE-CHANGES.md` | Full documentation of Team Mode changes |

### Verification

```bash
# Test team creation
opencode run --agent gilfoyle "Create a test team with 2 members"

# Check team status
team_status(teamRunId="team_xxx")

# Send message to team
team_send_message(teamRunId="team_xxx", to="*", body="Status update")
```

---

### 🧹 Public Release Cleanup

This release includes a comprehensive scrub of all sensitive data for the public EliaAgent repository:

| Category | Action |
|----------|--------|
| **Business names** | mirorpay → your-saas, bene2luxe → your-brand, cobou → your-agency, teleorbit → your-telecom |
| **Agent names** | setbon/gilfoyle/picasso → your-agent (in docs/templates) |
| **Paths** | `/Users/vakandi` → `~` (markdown), `$HOME` (shell), `os.path.expanduser()` (Python) |
| **Credentials** | All proxy creds, API keys, tokens, server IPs scrubbed |
| **Personal data** | Wael → the owner/the developer, real domains → your-brand.com |
| **Browser snapshots** | `.playwright-mcp/` removed (contained personal browsing data) |
| **Private prompts** | `setup/prompts/` removed (private prompt templates) |
| **Sync docs** | `setup/SYNC_PROMPT.md` removed from public (sync procedure stays private) |
| **Skills** | 12 business-specific skills removed (higgsfield, mirorpay-specific, etc.) |
| **Subworkers** | All subworker directories removed (private agent implementations) |

### What's New in the Public Release

- **Team Mode** — Multi-agent collaboration (see above)
- **Open allowlist** — Custom agents join teams by default
- **Rebuild script** — `scripts/rebuild-oh-my-openagent.sh` for oh-my-openagent rebuilds
- **Clean templates** — All business references replaced with generic placeholders
- **4 generic subworker examples** — refund-hunter, social-media, code-review, data-pipeline

### Companion Repos

| Repo | Purpose |
|------|---------|
| [EliaTopBar](https://github.com/vakandi/Elia-Topbar) | Menu bar app for subworker control |
| [Elia-OC](https://github.com/vakandi/Elia-OC) | UI sessions management |
| [EliaAgent](https://github.com/vakandi/EliaAgent) | This repo — public release |

---

## 🚀 Version: v2.0.0 — 🧠 AGENT DIFFERENTIATION: PER-AGENT MEMORY (May 16, 2026)

### ✨ The Big News: Each Agent Now Has Its Own Memory

**🧠 What changed**: Every OpenCode agent (Sisyphus, Gilfoyle, Setbon, Picasso, YourBrand, etc.) now sees **only its own memories** in the codemem feed and `mem-recent`/`mem-status` tools. No more cross-contamination between agent contexts.

**🔬 Technical breakdown:**

| Before | After |
|--------|-------|
| All agents shared one feed with everyone's memories | Each agent has a **scoped feed** filtered by `project/agentId` |
| `mem-recent` returned global results | `mem-recent --project <project/agent>` returns agent-specific results |
| No way to tell which agent created a memory | Every memory item tagged with `actor_id` via observer pipeline |
| UI feed showed everything mixed together | Feed tab has **agent chips** to filter per-agent views |

### 🏗️ Architecture: How It Works

The differentiation is built on **3 layers** working together:

#### 1️⃣ Plugin Layer (`packages/opencode-plugin/`)
- The OpenCode plugin resolves `--project` as `baseProject/agentId` (e.g. `EliaAI/elia`)
- `mem-recent`, `mem-status` now pass this scoped project to `codemem recent --project …`
- `mem-stats` remains a **global** database summary (intentionally unscoped)

#### 2️⃣ Observer Pipeline (`packages/core/src/`)
- `observer-client.ts` — Major refactor: now tags every memory with `actor_id` from session metadata
- `ingest-pipeline.ts` — Smarter session-to-agent mapping
- `observer-config.ts` — Updated observer config to support per-agent project resolution
- `raw-event-sweeper.ts` — Ignores events from unrelated agent sessions
- `schema-bootstrap.ts` — Auto-creates agent-specific tables/indexes on first access

#### 3️⃣ UI Layer (`packages/ui/src/`)
- **`FeedTabView.tsx`** — Agent chip filter added to memory feed
- **`filter.ts`** — New project/agent filter logic
- **`meta.ts`** — Metadata tracking for agent scoping
- **`state.ts`** — Global state now holds agent context
- **`feed.ts`** — Feed tab redesigned for scoped views

#### 4️⃣ Viewer Server & MCP Server
- Viewer API routes support agent-scoped query parameters
- MCP memory tools (`mcp-codemem`) filter by agent on the server side

### 📦 Files Changed (39 files, +1096 / -124 lines)

```
packages/opencode-plugin/     → Plugin: agent-aware --project resolution
packages/core/src/            → Observer: actor_id tagging, scoped sweeps
packages/ui/src/tabs/feed/    → UI: agent chips, scoped filter, redesigned feed
packages/ui/src/lib/          → State: agent context support
packages/cli/src/             → CLI: --project flag in search/stats/recent
packages/viewer-server/       → API: scoped query parameters
packages/mcp-server/          → MCP: agent-filtered memory tools
```

### 🛠️ How to Verify

```bash
# Agent Gilfoyle's memories only
codemem recent --project "EliaAI/gilfoyle" --limit 10

# Agent Setbon's memories only
codemem recent --project "EliaAI/setbon" --limit 10

# Global summary (all agents)
codemem stats

# SQLite check
sqlite3 $CODEMEM_DB "SELECT s.project, m.actor_id, COUNT(*) AS n
FROM memory_items m JOIN sessions s ON s.id=m.session_id
WHERE m.active=1 GROUP BY 1,2 ORDER BY n DESC LIMIT 20;"
```

### 🐛 Bug Fixes in This Release

| Fix | File |
|-----|------|
| Auto-bootstrap fresh DB on first access | `core/src/schema-bootstrap.ts` |
| Observer shutdown race condition fix | `core/src/observer-client.ts` |
| Memory store validation edge case | `core/src/db.ts` |
| Ingest pipeline null session guard | `core/src/ingest-pipeline.ts` |
| Raw event sweeper scoping fix | `core/src/raw-event-sweeper.ts` |
| UI lifecycle double-render fix | `ui/src/tabs/health/lifecycle.ts` |
| CLI search stats display alignment | `cli/src/commands/search.ts` |
| MCP server tool arg validation | `mcp-server/` |

### ⚙️ Script Improvements

- `scripts/opencode-serve.sh` — Added `is_already_opencode_server()` to detect existing healthy servers and avoid unnecessary restarts
- `scripts/manage_cron.sh` — Better launchd plist management, scheduler disable/enable respects agent kill
- `scripts/start_agents.sh` — Respects `.scheduler_disabled` flag, exits cleanly when scheduler is off
- `com.elia.elia-agent.plist` — Expanded schedule: now runs every hour from 08:00–21:00

### 🧼 Data Scrubbing for Public Release

- **Memory/MEMORY.md**: All real server IPs replaced with `[your-server-ip]` placeholders
- **setup/README.md**: All proxy credentials replaced with `[your-proxy-ip:port:user:pass]` placeholders
- **context/TOOLS.md**: Personal info (phone numbers, real names, IDs) scrubbed for public template

---

## 🚀 Version: v2.1.0 — 🔧 SCRIPT HARDENING + SUBWORKER MANAGER (Jul 8, 2026)

### 🔒 Tmux Safety Guards

**Problem**: Running `elia-ui.sh`, `kill_elia.sh`, `run-tmux.sh` from inside an existing tmux session (e.g., OpenCode's terminal pane) would kill the parent session or replace the calling shell — destroying the agent's workspace.

**Fix**: Added tmux-inside-tmux detection to all entry-point scripts:

| Script | Guard Added |
|--------|-------------|
| `elia-ui.sh` | Early exit if `$TMUX` is set |
| `elia-ui-4win.sh` | Deprecation warning + exit |
| `kill_elia.sh` | Client-aware kill (only kills if no active tmux clients) |
| `run-tmux.sh` | Early exit if `$TMUX` is set |

### 🛡️ Scheduler Disable Improvements

- `trigger_opencode_interactive.sh` / `start_agents.sh` — Added `.scheduler_disabled` guard: immediate exit if scheduler is disabled
- `start_agents.bat` — Same guard for Windows
- `manage_cron.sh` — Better interval logging (shows `:00, :20, :40` for 20min, `:00, :30` for 30min)
- `manage_cron.sh` — Added `pkill` cleanup for `oh-my-opencode run` and `ralph-loop` processes on disable
- `manage_cron.sh` — Kill Elia agent sessions started outside the scheduler

### 🧩 Script Improvements

- **`manage_subworkers.sh`** (NEW — public release) — Script to enable/disable/install/uninstall subworkers via launchd plists. Template with example format for users to customize.
- `elia-ui.sh` — Added `is_already_opencode_server()` to detect existing healthy servers and avoid unnecessary restarts

### 📚 Documentation

- **`subworkers/SUBWORKERS_SYSTEM.md`** — New comprehensive section on trigger bash scripts: why bash, architecture diagram, production-grade pattern (`.enabled` flag, per-run logs, personality injection), integration examples (launchd, cron, systemd, Docker, CI/CD, HTTP webhooks), and forensic debugging with per-run log history.

### 📋 Changelog Summary

| Version | Date | Changes |
|---------|------|---------|
| **v2.1.0** | **Jul 8, 2026** | **🔧 Script hardening + subworker manager** |
| **v2.0.0** | **May 16, 2026** | **🧠 Agent differentiation — per-agent memory system** |
| v1.2.0 | May 14, 2026 | Scheduler fix: real enable/disable system |
| v1.1.0 | May 13, 2026 | codemem integration |
| v1.0.3 | May 22, 2026 | Proxy fix: curl health check + NO_PROXY + validation |
| v1.0.2 | May 3, 2026 | Proxy system update (HTTP_PROXY) |
| v1.0.1 | April 27, 2026 | Desktop shortcuts, Discord bot, subworkers |
| Public | April 2026 | Initial public release |

### Scheduler Fix: Real Enable/Disable System

**Problem**: The launchd scheduler had `RunAtLoad=true` causing Elia to run immediately on every `install`/`enable`, even when "disabled" in the UI. The `.scheduler_state` file was display-only — it had no effect on whether launchd actually started the agent.

**Solution**: Complete rewrite of the scheduler control system:

#### New Commands in `manage_cron.sh`
- `disable` — Unloads launchd plists, creates `.scheduler_disabled` flag, preserves all settings
- `enable` — Removes disabled flag, reloads plists from saved settings
- Settings (interval, hours) persist between disable/enable cycles

#### Fixes
- **`RunAtLoad=false`** — Plist template changed from `<true/>` to `<false/>`. No more immediate execution on install or login.
- **`cron_wrapper.sh` guard** — Exits immediately if `.scheduler_disabled` exists (belt-and-suspenders)
- **`install_scheduler`** — Respects disabled flag: writes plist to disk but doesn't load it
- **`show` command** — Displays yellow `⏹ SCHEDULER DISABLED` banner when disabled

#### Files Changed
- `scripts/manage_cron.sh` — Added disable/enable commands, RunAtLoad=false, disabled flag check
- `scripts/cron_wrapper.sh` — Added `.scheduler_disabled` early-exit guard

---

## Version: v1.1.0 (May 13, 2026)

### New Integration: codemem (OpenCode Persistent Memory)

**Added full codemem integration** at `integrations/codemem/` — persistent memory for OpenCode and Claude Code that captures work across sessions, retrieves relevant context using hybrid search, and injects context automatically.

#### Features

- **Local-first** — everything lives in SQLite on your machine
- **Hybrid retrieval** — FTS5 BM25 lexical search + sqlite-vec semantic search, merged and re-ranked
- **Automatic injection** — the OpenCode plugin injects context into every prompt, no manual steps
- **Claude Code plugin support** — install from the codemem marketplace source
- **Built-in viewer** — browse memories, sessions, and observer output in a local web UI
- **Peer-to-peer sync** — replicate memories across machines without a central service
- **Memory export/import** — share project knowledge with teammates
- **CLI commands** — `codemem stats`, `codemem search`, `codemem recent`, `codemem serve`, etc.

#### Local fixes applied

- Observer pipeline fixes (ingest pipeline, observer client/config)
- UI improvements (feed tab, filter state, health lifecycle, API layer)
- Viewer server enhancements (config routes, plugin-observer support)
- CLI fixes (pack, recent, search, serve commands)
- Core fixes (memory store, raw event sweeper)

#### Quick start

```bash
cd integrations/codemem
pnpm install
pnpm build
pnpm run codemem --help
```

Or via npx (no install):
```bash
npx -y codemem stats
```

#### Setup

```bash
# OpenCode plugin and MCP config
npx -y codemem setup --opencode-only

# Restart OpenCode
```

#### What was synced

- Full source tree (7.9MB, excluding node_modules/.git)
- All 22 locally-modified files + 2 new files with fixes
- Proper .gitignore for sensitive patterns (no credentials, DBs, or build artifacts leaked)

---

## Version: v1.0.2 (May 3, 2026)

### Critical Proxy System Update

**Issue (May 2, 2026)**: `proxychains4` stopped intercepting OpenCode network requests properly due to macOS SIP (System Integrity Protection) limitations where signed binaries cannot have libraries injected.

**Solution**: Migrated from `proxychains4` library injection to **HTTP_PROXY environment variables** applied locally to each command using `env`.

### New Features

- **HTTP_PROXY Wrapper** (`setup/opencode-proxy.sh`) - Robust proxy wrapper that applies HTTP_PROXY locally without polluting the terminal
- **Updated All Scripts** - All opencode-related scripts now use HTTP_PROXY instead of proxychains4:
  - `scripts/trigger_opencode_interactive.sh`
  - `scripts/trigger_morning.sh`
  - `scripts/opencode-serve.sh`
  - `scripts/opencode-serve-fixed.sh`
  - `scripts/opencode-server-launchd.sh`
  - `scripts/opencode-server-simple.sh`
  - `scripts/run-tmux.sh`
  - `scripts/start_elias_discord.sh`

### Benefits

- ✅ **Works reliably** - No SIP limitations
- ✅ **Doesn't pollute the terminal** - Proxy vars are applied only to the specific command using `env`
- ✅ **Compatible with all scripts** - Works with opencode, oh-my-opencode, Discord bot, etc.
- ✅ **Easy to debug** - Can verify proxy by checking the command's environment

### Usage

```bash
# Enable proxy
touch ~/EliaAI/.proxy_enabled

# Use wrapper
~/EliaAI/setup/opencode-proxy.sh -s <session_id>
~/EliaAI/setup/opencode-proxy.sh run --agent elia "task"

# Or via elia alias
alias elia='~/EliaAI/setup/opencode-proxy.sh'
```

### Documentation Updated

- `setup/README.md` - Proxy Switcher section completely rewritten with new HTTP_PROXY approach

---

## Version: v1.0.3 (May 22, 2026)

### Proxy Fixes & Hardening

**Issue (May 22, 2026)**: `switch-proxy.sh` used `wget` for proxy health checks, which is not installed on macOS by default. Users without Homebrew `wget` got "❌ All proxies dead" even with valid proxies. Additionally, `opencode-proxy.sh` had no validation for missing/broken config and was missing localhost exclusions.

### Fixes

| Fix | File |
|-----|------|
| **wget → curl** — `curl` is available on ALL macOS by default | `setup/switch-proxy.sh` |
| **time_ago() cascading echo bug** — was printing multiple time strings instead of one | `setup/switch-proxy.sh` |
| **NO_PROXY env vars** — prevents proxying localhost/127.0.0.1 traffic | `setup/opencode-proxy.sh` |
| **Config validation** — graceful error if `~/.proxychains.conf` is missing or malformed | `setup/opencode-proxy.sh` |

### Migration

```bash
# Re-sync from EliaAgent or manually copy:
cp path/to/EliaAgent/setup/switch-proxy.sh ~/EliaAI/setup/
cp path/to/EliaAgent/setup/opencode-proxy.sh ~/EliaAI/setup/
```

---

## Version: Public Release v1.0.1 (April 27, 2026)

### What's New in This Release

---

## 1. Desktop Shortcuts (NEW!)

### EliaUI.app (Platypus Native App)
- Native macOS application created with Platypus
- Double-click to launch EliaUI in clean app window
- No Terminal window required

### EliaUI.command (tmux-based)
- Terminal with tmux session for cleaner log display
- All logs in one organized window
- Easy desktop shortcut

### Other Shortcuts
- `Elia.command` - Main Elia agent
- `Elia-OC` - OpenCode CLI  
- `EliaDiscord.command` - Discord bot

---

## 2. Discord Integration (NEW!)

Full Discord bot integration at `integrations/elia-discord-bot/`:
- Chat with Elia in any Discord channel
- Slash commands: `/elia`, `/elia-reset`, `/elia-new`
- Typing indicator during processing
- Session persistence across messages

### Setup
```bash
cd integrations/elia-discord-bot
cp .env.example .env
# Add your DISCORD_BOT_TOKEN
pip install -r requirements.txt
python bot.py
```

---

## 3. Updated UI (ui_electron/)

- New GIF assets (`elia.gif`, `elia5.gif`, `elia6.gif`)
- New HTML popups (cron, morning, proxy-error)
- Updated src files

---

## 4. Subworkers System (Continued)

From v1.0.0 - Autonomous promotion agents now included:

| Component | Purpose |
|-----------|---------|
| `yourbrand-promoter/` | Autonomous agent for YourBrand |
| `yourco-promoter/` | Autonomous agent for Your Company |
| `plists/` | macOS LaunchAgent configurations |

### Overview
Subworkers are autonomous AI promotion agents that run on a schedule to promote your businesses automatically.

### Components Added
| Component | Purpose |
|-----------|---------|
| `yourbrand-promoter/` | Autonomous agent for YourBrand (luxury fashion resale) promotion |
| `yourco-promoter/` | Autonomous agent for Your Company (B2B) promotion |
| `plists/` | macOS LaunchAgent configurations |
| `scripts/trigger_*.sh` | Trigger scripts for promoters |

### How Subworkers Work

**YourCo Promoter** (B2B - every 30 min, 09:00-21:00):
- LinkedIn engagement
- X (Twitter) interactions  
- Reddit community participation
- Lead generation for web development services

**YourBrand Promoter** (B2C - every 20 min, 10:00-22:00):
- Instagram engagement
- TikTok interactions (via browser)
- Facebook Marketplace browsing
- Luxury fashion resale promotion

### Setup
```bash
# Install LaunchAgents
cd plists
launchctl load com.elia.yourco-promoter.plist
launchctl load com.elia.yourbrand-promoter.plist

# Manual test
cd scripts
./trigger_yourco_promoter.sh
./trigger_yourbrand_promoter.sh
```

---

## 2. New Triggers System

### Command-based Triggers (in PROMPT.md)

The main trigger system now uses command keywords to spawn specialized agents:

| Command Trigger | Agent Spawned |
|----------------|--------------|
| `/ulw-loop` | UltraWork Loop (unlimited iterations) |
| `/ralph-loop` | Ralph Loop (50 iter max) |
| `appel Gilfoyle` | Backend dev agent |
| `appel Setbon` | Marketing agent |
| `appel Picasso` | Visual/design agent |

### Subagent Categories
- `gilfoyle` - Backend dev, SSH, accounts
- `yourbrand` - Luxury e-commerce
- `yourco-agency` - B2B digital
- `yourtool` - SMMPanel
- `setbon` - Marketing & conversion
- `tiktok-youtube-auto` - Content automation

---

## 3. Pre-Report Checklist (NEW in PROMPT.md)

Before sending ANY Discord report, agents MUST complete:

```markdown
PRE-REPORT CHECKLIST:
For each business area, decide: DOES THIS APPLY THIS RUN?

☐ Server Health / MCP Status → #health-checks
☐ YourBrand Orders / Sales → #orders
☐ YourBrand Products → #products
☐ YourBrand Clients → #clients
☐ YourTool Panel → #panel
☐ TikTok/YouTube Content → #content
☐ TikTok/YouTube Analytics → #analytics
```

**VALIDATION**: Reports without this checklist are INVALID.

---

## 4. File Sending Enhancement

### Discord File Upload (NEW)
```bash
# Send file directly to Discord
mcp-cli call discord-server-mcp discord_send_file '{
  "channel_id": "CHANNEL_ID",
  "file_path": "[AGENT_DIR]/docs/YYYY-MM-DD/report.md",
  "content": "📋 Rapport détaillé"
}'
```

**IMPORTANT**: Never send file paths as text - always upload the file directly.

---

## 5. Context Files Updated

### Tools Reference (context/TOOLS.md)
- MCP-CLI commands with proper JSON syntax
- WhatsApp business groups
- Discord channel IDs
- Telegram commands
- Image generation (Higgsfield.ai)

### Business Context (context/business.md)
- Cleaned for public release
- Placeholders forYOUR information
- Team structure templates

---

## 6. Documentation Added

### SETUP_TOOLS.md
Quick reference for setting up the agent system.

### SUBWORKERS_SYSTEM.md (NEW - 1700+ lines)
Complete implementation guide including:
- Subworker architecture
- OpenCode agent configuration
- System prompts for promoters
- LaunchAgent setup
- MCP server integration
- Workflows & reporting
- Step-by-step implementation

---

## 7. Updates to Core Files

### PROMPT.md (Major Update)
- Increased from ~600 to ~830 lines
- New triggers section with `/ulw-loop` and `/ralph-loop`
- Pre-report checklist requirement
- File sending enhancement
- Updated startup sequence

### MORNING_PROMPT.md
- Updated business references
- Team communication channels
- Reporting templates

---

## 8. Files Cleaned for Public Release

### Removed/Redacted
| File | Action |
|------|--------|
| `.env` | NOT included (private credentials) |
| `docs/YYYY-MM-DD/*` | NOT included (daily logs) |
| `brain/obsidian/*` | NOT included (private wiki) |
| `memory/*-CREDENTIALS.md` | NOT included (secrets) |
| `logs/*.log` | NOT included (runtime logs) |

### Kept for Public
| File | Purpose |
|------|--------|
| `PROMPT.md` | Main system prompt template |
| `MORNING_PROMPT.md` | Morning routine template |
| `README.md` | Setup guide |
| `context/TOOLS.md` | Tools reference (template) |
| `context/business.md` | Business info (template) |
| `skills/INDEX.md` | Available skills list |
| `setup/README.md` | Full setup guide |
| `SUBWORKERS_SYSTEM.md` | Subworker implementation |

---

## 9. Setup Instructions for Your Own Instance

### Quick Setup

1. **Clone the repo**:
```bash
git clone https://github.com/user/EliaAgent.git
cd EliaAgent
```

2. **Update context files**:
```bash
# Edit these files with YOUR information:
vim context/business.md
vim context/TOOLS.md
vim context/jira-projects.md
vim PROMPT.md    # Update owner name
```

3. **Configure OpenCode**:
```bash
# Copy OpenCode config
mkdir -p ~/.config/opencode
cp -r setup/opencode-config/* ~/.config/opencode/

# Restart OpenCode
```

4. **Set up cron** (optional):
```bash
# Every 30 minutes
./scripts/manage_cron.sh install --interval 30m
```

### Full Setup Guide
See `setup/README.md` for complete instructions.

---

## 10. What's Different from Private Version

| Feature | Public | Private (EliaAI) |
|---------|--------|------------------|
| Business credentials | Template/Holders | Real data |
| Daily docs logs | NOT included | Full history |
| Obsidian brain | NOT included | Full wiki |
| Memory files | Generic | Personal |
| .env | NOT included | Contains secrets |

---

## 11. Architecture Summary

```
EliaAgent/
├── PROMPT.md              # Main system prompt
├── MORNING_PROMPT.md       # Morning routine
├── README.md              # → setup/README.md
├── setup/                # Setup scripts & docs
│   ├── README.md         # Full setup guide
│   ├── README_WINDOWS.md
│   └── switch-proxy.sh
├── context/              # 📝 UPDATE THESE
│   ├── TOOLS.md         # MCP commands
│   ├── business.md      # Business info
│   └── jira-projects.md
├── skills/               # Available skills
├── ui_electron/         # Desktop UI app
├── scripts/             # Automation scripts
│   ├── manage_cron.sh
│   ├── trigger_opencode_interactive.sh
│   └── ...
├── yourbrand-promoter/  # Subworker
├── yourco-promoter/     # Subworker
└── plists/           # macOS LaunchAgents
```

---

## 12. Model Configuration

**REQUIRED**: Use ONLY free OpenCode models:

| Model | Badge | Use |
|-------|-------|-----|
| `opencode/big-pickle` | 🔴 Red | Default - 200K context |
| `opencode/minimax-m2.5-free` | 🟡 Yellow | Fallback |

**DO NOT USE**: Claude Opus, GPT-4, or any paid models.

---

## 13. Troubleshooting

### MCP Tools Not Working
```bash
# Restart MCP servers
mcp-cli list  # Check servers
pkill -f mcp && mcp-cli &  # Restart
```

### Cron Not Running (macOS)
```bash
# Use root crontab
./scripts/manage_cron.sh install --interval 30m --sudo
```

### Subworkers Not Starting
```bash
# Check LaunchAgents
launchctl list | grep -i promoter
launchctl load plists/com.elia.yourco-promoter.plist
```

---

## 14. Credits & License

**Creator**: YourName YourSurname  
**Repository**: https://github.com/user/EliaAgent  
**License**: MIT

---

## 15. Quick Start

See `setup/README.md` for full setup instructions.