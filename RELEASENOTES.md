# EliaAgent Release Notes

## Version: v5.0.1 (July 12, 2026)

### 🛡️ Subworker Premature Completion Fix — 10 Critical Bugfixes

**Subworkers no longer die mid-task.** All 10 root causes of the "All tasks completed" false-positive and silent SSE stream death have been fixed in the oh-my-opencode CLI runner. Subworkers now survive long-running tasks with proper timeout handling, session-scoped event filtering, and continuous progress reporting.

**What changed:**
- **Fix #1** — `EVENT_PROCESSOR_SHUTDOWN_TIMEOUT_MS` raised from 2s → 10s to survive heavy event bursts
- **Fix #2** — Telemetry `capture()` failures caught and logged instead of crashing the runner
- **Fix #3** — Completion diagnostics (verbose mode) wrapped in try/catch — never crashes runner
- **Fix #4** — Unknown completion status no longer treated as idle — requires explicit `completed` or `failed`
- **Fix #5** — Null todo list guard — avoids crash when todo list hasn't been populated yet
- **Fix #6** — `requiredConsecutive` raised from 1 → 3 before declaring idle — prevents false positives during stalls
- **Fix #7** — `eventProcessorDied` flag — detects when the event processor crashes and stops poll loop
- **Fix #8** — Watchdog timer scoped to session — multi-session CLI no longer triggers false idle
- **Fix #9** — Toast notifications filtered by session ID — cross-session toasts no longer corrupt state
- **Fix #10** — `eventProcessorDied` field added to event state — wired through completion detection

**Impact:** Subworkers that previously died after 5-10 minutes of heavy tool use now survive indefinitely. The trigger template, launchd plists, and personality injection are unchanged — only the CLI runner internals were fixed.

**Files modified:** `runner.ts`, `completion.ts`, `poll-for-completion.ts`, `event-stream-processor.ts`, `event-toast-handlers.ts`, `event-state.ts`

**Docs:** See `setup/OH-MY-OPENCODE-CHANGES.md` for the full technical breakdown.

---

## Version: v4.1.0 (July 10, 2026)

### 🚀 Unified Subworker Lifecycle Manager + Security Hardening

**One script to rule all subworkers.** The new `manage_subworkers.sh` replaces the ad-hoc cron-based management with a single command for the full launchd lifecycle on macOS.

**What changed:**
- **Unified Lifecycle Manager** (`scripts/manage_subworkers.sh`) — 6 commands: `default` (status table), `enable`, `disable`, `status`, `install`, `uninstall`. Handles bootstrap for loading agents, bootout for unloading, and plist management across both the project `subworkers/plists/` directory and `~/Library/LaunchAgents/`.
- **`.enabled` File Convention** — Master switch per subworker. Remove a single file = emergency stop without launchctl interaction. The `disable` command additionally marks `Disabled=true` in the plist and unloads from launchd.
- **Color-Coded Status Table** — Default view shows a formatted table with ENABLED/PLIST/LAUNCHD/SCRIPT columns for all subworkers at a glance.

**Security hardening:**
- **Removed 6 files with hardcoded secrets** — `yourapp_run.py` (Discord bot token, Telegram keys), `cloudconvert_md_to_docx.py` (JWT API key), `discord_send.py`, `google_workspace.py`, `captcha_solver.py` (OpenRouter key), `trigger_opencode_interactive.sh` (Jira/Atlassian tokens).
- **Sanitized all public-facing files** — Business names, server IPs, Discord channel IDs, and real paths replaced with placeholders. All 9 security checks from `SYNC_PROMPT.md` pass clean.
- **Created `context/` directory** with sanitized `TOOLS.md` and `business.md` for the public repo.

**New skills synced:**
- `hyperframes` / `hyperframes-cli` / `hyperframes-registry` — Video composition framework
- `gsap` — GSAP animation reference
- `directus-flows-skill` — Directus workflow automation
- `pdf-form-filler` — IRS/government XFA PDF form filling
- `best-heygen-image` — Blog hero image generation
- `vakandi-rapid-api-builder` — RapidAPI marketplace scaffolding
- `website-to-hyperframes` — Website-to-video conversion
- `ui-ux-pro-max-skill` — UI/UX design system
- `yourapp-ga-marketing-review` — GA4 analytics review

### Bug Fixes
- **Subworker plist conflict** — `yourapp-telegram` had both a managed plist and a stale manual plist in `~/Library/LaunchAgents/`. Cleaned up during lifecycle manager integration.
- **Missing tiktok-content plist** — Identified as blocker for enabling the tiktok-content subworker.

### Technical Details
- Script location: `scripts/manage_subworkers.sh` (403 lines, zsh)
- Subworker state tracked across 4 dimensions: `.enabled` file, plist presence, launchctl status, trigger script existence
- 6 subworkers: yourapp-telegram, YourBrand-promoter, youragency-promoter, YourBrand-suppliers, tempack-dev, tiktok-content
- All subworkers currently disabled — enable with `./manage_subworkers.sh enable <name>`

---

## Version: v4.0.0 (July 9, 2026)

### 🚀 Subworker Management System — Built for Organic Marketing at Scale

I built a complete subworker orchestration system with an Electron UI dashboard to run and monitor autonomous AI agents. This isn't just a task runner — it's a full marketing operations center.

**What I built:**
- **Subworker Engine** — Each agent gets its own identity (personality file), workspace (isolated directory), PROMPT.md, and per-run logging. The trigger template (`trigger_template.sh`) handles everything: PATH resolution for launchd, .enabled gating, personality injection, proxy support, and task/loop mode switching.
- **Electron UI Dashboard** — Real-time subworker management in a floating window. See every agent's status (● RUNNING / ○ STOPPED), enable/disable with toggle switches, browse per-run log history with time-ago badges, duration badges, and crash detection. The UI uses a unique `EOF_SUBWORKER_EXIT:<code>` marker — impossible for AI output to fake — to reliably detect completion vs crash.
- **Unique Exit Marker Protocol** — Every run log ends with `[timestamp] EOF_SUBWORKER_EXIT:<code>`. The UI parses this with absolute precision: exit 0 → green duration badge, exit non-zero → orange "(crashed)" badge, no marker → gray "???" badge for old logs. No false positives from AI output text.
- **Reliable Crash Recovery** — The shell script uses `set +e` / `set -e` wrapping to capture the exit code even on crashes, always writing the marker before propagating the real exit status. Failed runs show their partial duration instead of being indistinguishable from running agents.

**This powers a full organic marketing system:**
- Multi-platform content creation and scheduling agents
- Automated community engagement
- SEO content generation
- Social media promotion
- All running on cron schedules with the LaunchAgent integration

**Custom MCP Servers** — I built custom MCP servers to make this work seamlessly. The system integrates with the right tools for each platform. If you need specialized MCPs for your own automation stack, contact me — I build custom MCP servers tailored to your use case.

**Contact for custom MCP development**: Reach out to discuss your automation needs. I build production-ready MCP servers for any platform or workflow.

### New Features
- **Subworker Management UI** (`subworker-popup.html`) — Electron-based floating dashboard with per-agent status badges, enable/disable toggles, per-run log dropdown with time-ago + duration badges, crash detection via unique EOF marker.
- **Unique Exit Marker Protocol** — `EOF_SUBWORKER_EXIT:<code>` written at end of every run. Zero ambiguity between success, crash, and still-running. Backward compatible with old logs (shows gray "???" badge).
- **Robust Shell Exit Handling** — `set +e` wrapping around `oh-my-opencode run` captures exit code even on crash. The marker is always written before propagating the real exit status.
- **Status-Based Badge System** — Three-state rendering: green (success), orange (crashed with duration), gray (unknown — old log or unparseable), yellow (● RUNNING — agent still executing).
- **Fallback Duration Parsing** — Even without the unique marker, the UI scans for the last `[timestamp]` line to show partial duration for old or pre-marker logs.

### Bug Fixes
- **False "RUNNING" for old logs** — Previously, any log without a completion marker showed "RUNNING." Now shows gray "???" with partial duration if available.
- **Fuzzy "completed" regex parsing** — Removed unreliable `.*completed` matching that could false-trigger on AI output text. Replaced with exact unique marker match.
- **set -e crash masking** — `set -euo pipefail` was killing the trigger script before it could write the completion line on non-zero exits. Fixed with `set +e` wrapper.

### Technical Details
- Marker format: `[YYYY-MM-DD HH:MM:SS] EOF_SUBWORKER_EXIT:<exit_code>`
- Log parsing: reads first 300 bytes (head) for start timestamp, last 300 bytes (tail) for marker
- UI renders up to 100 most recent runs per subworker, newest first
- All trigger scripts share the template via `source trigger_template.sh` — one change propagates everywhere
- Node.js `--check` verified, no runtime dependencies added

---

## Version: v3.3.0 (July 8, 2026)

### New Features
- **Symlink integrity check in trigger_template.sh** — Automatically detects when `oh-my-opencode` bun global package is a symlink to a local source checkout (causes EPERM on macOS). Fails early with a clear fix message instead of a cryptic Node.js stack trace.

### Bug Fixes
- **Subworker EPERM crash resolved** — `oh-my-opencode` global package was a symlink to a clone in `nayo-app-fastapi` project. Reinstalled properly via `bun install -g oh-my-opencode`. All subworker triggers now work without macOS permission errors.

### Documentation
- **SUBWORKERS_SYSTEM.md** — Rewritten with Table of Contents, workspace isolation architecture, per-agent permissions, agent registration guide (opencode.json + oh-my-openagent.json + personality file + categories), and expanded troubleshooting section including the bun global symlink pitfall.
- **trigger_template.sh** — Added binary integrity check, updated example paths, cleaner structure.

### Technical Details
- `oh-my-opencode` upgraded from 3.17.2 → 4.16.0 (major version jump).
- Version 4.16.0 uses JS-based platform binaries instead of Mach-O executables.
- Trigger template now checks `~/.bun/install/global/node_modules/oh-my-opencode` for symlink status before running.
