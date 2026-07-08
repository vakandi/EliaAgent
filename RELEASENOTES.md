# EliaAgent Release Notes

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
