---
name: macos-disk-usage
description: "Full macOS disk usage analysis — find what apps, projects, GitHub repos, background services, and built-in apps eat your disk space. Identifies the biggest space consumers, categorizes everything by type, and proposes safe cleanup actions. CRITICAL: This skill NEVER deletes, moves, or modifies any files. It only reads and reports. Use this skill whenever the user asks about disk space, what's using storage, why their disk is full, cleanup recommendations, or wants to free up space. TRIGGER on: 'disk usage', 'storage full', 'what's using my disk', 'free up space', 'disk cleanup', 'why is my disk full', 'storage analysis', 'what's taking space', 'biggest files', 'disk space report', 'clean my mac', 'storage check', 'disk health', even casual requests like 'my disk is almost full' or 'I need more space'."
compatibility: macOS only (uses native commands: du, df, find, mdls, mdfind, diskutil, system_profiler, brew, npm, pip)
---

# macOS Disk Usage Analysis

Deep investigation of disk space consumption on macOS. Finds every app, project, cache, background service, and built-in component that uses space — then proposes safe cleanup actions.

## SAFETY RULE — READ ONLY, NEVER DELETE

**This skill NEVER deletes, moves, modifies, or trashes any files.**

Every script is read-only. The analysis produces a report with cleanup *recommendations* — the user decides what to delete manually. The model using this skill must not run `rm`, `trash`, `xattr`, `diskutil erase`, or any destructive command. If the user asks to delete something, remind them this skill only recommends — they do the cleanup themselves.

This is by design: automated deletion on macOS can break system services, corrupt app state, or remove data the user didn't realize was important. Read-only analysis is always safe. Deletion is the user's choice.

## When to use

This skill runs when the user wants to understand what's consuming disk space on their Mac. It works on any Mac running macOS — no extra tools needed. Use it when:

- The user reports "disk full" or "storage almost full"
- They want to know what's eating space before cleaning up
- They want a categorized breakdown of disk usage by type
- They're considering cleanup but want to know what's safe to remove
- They want to find large GitHub repos, node_modules, Docker images, or caches

## Investigation workflow

Run the diagnostic scripts in order. Each script outputs structured data you interpret.

### Phase 1: Disk overview (always start here)

```bash
bash scripts/01-disk-overview.sh
```

Shows: total disk size, used vs free, APFS volume layout, biggest mount points. This gives you the big picture — how much space is left and where the pressure is.

### Phase 2: Applications and installed software

```bash
bash scripts/02-apps-installed.sh
```

Shows: all apps in /Applications and ~/Applications sorted by size, App Store apps, Homebrew packages, npm global packages, pip packages, Ruby gems, Go binaries. Each entry shows size so you can spot bloated apps.

### Phase 3: Projects and repositories

```bash
bash scripts/03-projects-repos.sh
```

Shows: GitHub repos (~/Projects, ~/Developer, ~/code, ~/repos), node_modules directories, .git folder sizes, Python venvs, Cargo targets, build artifacts. This is where developer disk usage hides — node_modules alone can consume 10-50GB.

### Phase 4: Caches, logs, and temporary files

```bash
bash scripts/04-caches-logs.sh
```

Shows: ~/Library/Caches breakdown by app, ~/Library/Logs, /tmp, system logs, crash reports, Browser caches (Chrome, Safari, Firefox), Xcode derived data and archives. Caches are often the biggest safe-to-delete category.

### Phase 5: System data and hidden consumers

```bash
05-system-data.sh
```

Shows: Docker images and containers, Time Machine local snapshots, Spotlight index size, APFS snapshots, iCloud sync data, Photos library size, Mail attachments, Messages database. "System Data" in macOS storage is often these hidden consumers.

### Phase 6: Cleanup advisor

```bash
bash scripts/06-cleanup-advisor.sh
```

Shows: prioritized list of cleanup recommendations organized by safety level. Categorizes each item as SAFE (caches, logs, temp), MODERATE (old repos, unused apps), or RISKY (system data, snapshots). Includes exact commands the user can run to free space — but never runs them automatically.

## Interpretation guide

After collecting data, synthesize findings into this structure:

### Disk pressure summary
- Total disk / Used / Free / Percentage used
- Which volume is under pressure (Macintosh HD, Data, external)

### Top space consumers by category
- **Applications** — installed apps sorted by size (show top 10)
- **Developer projects** — repos, node_modules, build artifacts, venvs
- **Caches and logs** — per-app cache sizes, total cache footprint
- **System data** — Docker, snapshots, Spotlight, iCloud, Photos
- **Downloads** — the classic junk drawer

### Cleanup recommendations (NEVER auto-execute)

Organize by safety tier:

#### SAFE to delete (user can do these with zero risk)
- Browser caches (Chrome, Safari, Firefox) — they rebuild automatically
- ~/Library/Caches for apps that don't matter
- Old log files (>30 days)
- /tmp contents
- Xcode derived data (if not actively building)
- Downloaded files the user no longer needs

#### MODERATE risk (delete if you're sure)
- Old GitHub repos you'll never work on again
- Unused Homebrew/npm/pip packages
- Docker images for projects you've abandoned
- Time Machine local snapshots (can be recreated)
- Large files in ~/Downloads

#### RISKY (think twice)
- Photos library optimization (use macOS built-in tool)
- Mail attachment cleanup
- Messages database (back up first)
- System snapshots (Time Machine will recreate)

### Why space matters
- macOS needs ~10-15% free for swap, caching, and system operations
- Below 10% free: apps may crash, performance degrades
- Below 5% free: system instability, potential data loss
- Target: keep at least 20% free for healthy operation

## Output format

Present results as a disk audit report with:
1. **Disk overview** — total, used, free, percentage, volume layout
2. **Top 10 space consumers** — table with name, type, size, path
3. **Category breakdown** — apps, projects, caches, system data, other
4. **Cleanup recommendations** — organized by safety tier with exact paths
5. **Estimated reclaimable space** — how much could be freed from each tier
6. **Action items** — specific commands the user can copy-paste to clean up

## Tips

- Start with Phase 1-2 for a quick overview. Full analysis is Phases 1-6.
- If the user just wants to know "what's big", Phase 1 + Phase 3 catches 80% of usage.
- Developer machines are often 50%+ node_modules and .git — emphasize this in reports.
- Docker is a common silent space hog — Docker.qcow2 can grow to 60GB+.
- Never suggest deleting anything in /System or /usr — those are protected by SIP.
- If the user says "just clean it up", remind them: this skill recommends, they execute.
