# EliaAI → EliaAgent Sync Prompt

> Use this prompt when you want to sync your private EliaAI repo to the public EliaAgent repo.

---

## Context

You are working with TWO GitHub repos:
- **Private**: `/Users/vakandi/EliaAI` (your working repo with all your changes)
- **Public**: `/Users/vakandi/EliaAgent` (cleaned repo for public release)

Your task is to SYNC the private repo to the public repo, cleaning all sensitive data (credentials, logs, personal info) while preserving all functionality.

---

## Mission

1. **COMPARE** the two repos to find all differences
2. **IDENTIFY** what needs to be copied (new files) or updated (modified files)
3. **FILTER** out sensitive data that should NOT be copied:
   - `.env` files with real credentials
   - `logs/` directories
   - `docs/YYYY-MM-DD/` daily log folders
   - `brain/obsidian/` private wiki
   - `memory/*-CREDENTIALS.md` secret files
   - `node_modules/` (will be rebuilt)
   - `__pycache__/`, `venv/` Python caches
   - `.sisyphus/` runtime state
   - `store/` Electron user data
4. **COPY** clean files from EliaAI → EliaAgent
5. **UPDATE** documentation:
   - `setup/README.md` with any new features
   - `RELEASENOTES.md` with changelog
6. **COMMIT** with clear message
7. **PUSH** to GitHub
8. **UPDATE** the GitHub release

---

## Step-by-Step Instructions

### Step 1: Compare Repos

Run this to find differences:
```bash
diff -rq /Users/vakandi/EliaAI /Users/vakandi/EliaAgent --exclude=".git" --exclude="*.log" 2>/dev/null | head -100
```

Or use explore agent for deeper analysis.

### Step 2: Identify What to Copy

**Typically NEW in EliaAI (copy to EliaAgent):**
- `setup/desktop_shortcuts/` - Desktop shortcuts
- `integrations/elia-discord-bot/` - Discord bot
- `subworkers/` - Subworker agents
- New scripts in `scripts/`
- Updated `ui_electron/` (without node_modules)

**Typically MODIFIED (check diff):**
- `setup/README.md` - Setup docs
- `PROMPT.md` - Main prompt
- `context/TOOLS.md` - Tools reference
- `context/business.md` - Business info

**NEVER Copy:**
- `.env` - Real credentials
- `logs/` - Runtime logs
- `docs/YYYY-MM-DD/` - Daily logs
- `brain/obsidian/` - Private wiki
- `memory/*-CREDENTIALS.md` - Secrets
- `node_modules/` - NPM packages
- `venv/`, `__pycache__/` - Python caches

### Step 3: Clean Sensitive Data

Before copying, clean the source:
```bash
# Clean EliaAI integrations before copy
rm -rf /Users/vakandi/EliaAI/integrations/elia-discord-bot/.env
rm -rf /Users/vakandi/EliaAI/integrations/elia-discord-bot/__pycache__
rm -rf /Users/vakandi/EliaAI/integrations/elia-discord-bot/venv
rm -rf /Users/vakandi/EliaAI/integrations/elia-discord-bot/logs
rm -rf /Users/vakandi/EliaAI/integrations/elia-discord-bot/sessions.json
rm -rf /Users/vakandi/EliaAI/ui_electron/node_modules
rm -rf /Users/vakandi/EliaAI/ui_electron/.sisyphus
rm -rf /Users/vakandi/EliaAI/ui_electron/store
rm -rf /Users/vakandi/EliaAI/ui_electron/.jarvis-position.json
```

### Step 4: Copy Files

```bash
# Copy desktop shortcuts
cp -R /Users/vakandi/EliaAI/setup/desktop_shortcuts/* /Users/vakandi/EliaAgent/setup/desktop_shortcuts/

# Copy discord bot (clean)
cp -R /Users/vakandi/EliaAI/integrations/elia-discord-bot /Users/vakandi/EliaAgent/integrations/

# Copy ui_electron (without node_modules)
rm -rf /Users/vakandi/EliaAgent/ui_electron
cp -R /Users/vakandi/EliaAI/ui_electron /Users/vakandi/EliaAgent/ui_electron

# Clean any remaining private data in target
rm -rf /Users/vakandi/EliaAgent/ui_electron/.jarvis-position.json
rm -rf /Users/vakandi/EliaAgent/ui_electron/.sisyphus
rm -rf /Users/vakandi/EliaAgent/ui_electron/store
```

### Step 5: Update Documentation

Add new features to `RELEASENOTES.md`:
```markdown
## Version: vX.X.X (DATE)

### New Features
- [Feature 1] - Description
- [Feature 2] - Description

### Bug Fixes
- [Fix 1] - Description
```

Update `setup/README.md` if needed with new sections.

### Step 6: Commit

```bash
cd /Users/vakandi/EliaAgent
git add -A
git status  # Verify only intended files
git commit -m "feat: add [feature 1], [feature 2], [feature 3]"
```

### Step 7: Push

```bash
git push origin main
```

### Step 8: Update Release

```bash
gh release edit v1.0.0 --notes-file RELEASENOTES.md
# Or create new release:
gh release create "vX.X.X" --title "EliaAI vX.X.X" --notes-file RELEASENOTES.md --target main
```

---

## Quick Copy-Paste Prompts

### For Explore Agent:
```
Compare /Users/vakandi/EliaAI vs /Users/vakandi/EliaAgent

List ALL differences:
- New files in EliaAI (need copy)
- Modified files (need update)
- Files that should NOT be copied (sensitive)

Focus on: setup/, ui_electron/, integrations/, subworkers/
```

### For Execution:
```
Sync EliaAI to EliaAgent:
1. Clean sensitive data from source
2. Copy new/modified files
3. Update RELEASENOTES.md
4. Commit and push
5. Update GitHub release

Use /Users/vakandi/EliaAI as source, /Users/vakandi/EliaAgent as target.
```

---

## Common Files to Check

| Path | Copy? | Notes |
|------|--------|-------|
| `setup/desktop_shortcuts/*` | YES | Desktop shortcuts |
| `integrations/elia-discord-bot/` | YES | Discord bot (clean .env first) |
| `ui_electron/*` | YES | UI (exclude node_modules) |
| `subworkers/*` | YES | Subworker agents |
| `context/TOOLS.md` | YES (cleaned) | Remove real tokens |
| `context/business.md` | YES (cleaned) | Replace with placeholders |
| `PROMPT.md` | YES | Main prompt |
| `setup/README.md` | YES | Update with new features |
| `RELEASENOTES.md` | YES | Add changelog |
| `.env` | NO | Never copy |
| `logs/*` | NO | Never copy |
| `docs/YYYY-MM-DD/*` | NO | Never copy |
| `brain/obsidian/*` | NO | Never copy |
| `memory/*-CREDENTIALS.md` | NO | Never copy |

---

## Automated Script (Optional)

Create a sync script:
```bash
#!/bin/bash
# EliaAI → EliaAgent Sync Script

SOURCE="/Users/vakandi/EliaAI"
TARGET="/Users/vakandi/EliaAgent"

echo "🔄 Syncing EliaAI → EliaAgent"

# Clean sensitive data from source
echo "🧹 Cleaning sensitive data..."
rm -rf "$SOURCE/integrations/elia-discord-bot/.env"
rm -rf "$SOURCE/integrations/elia-discord-bot/__pycache__"
rm -rf "$SOURCE/integrations/elia-discord-bot/venv"
rm -rf "$SOURCE/integrations/elia-discord-bot/logs"
rm -rf "$SOURCE/integrations/elia-discord-bot/sessions.json"
rm -rf "$SOURCE/ui_electron/node_modules"
rm -rf "$SOURCE/ui_electron/.sisyphus"
rm -rf "$SOURCE/ui_electron/store"
rm -rf "$SOURCE/ui_electron/.jarvis-position.json"

# Copy directories
echo "📦 Copying files..."
cp -R "$SOURCE/setup/desktop_shortcuts" "$TARGET/setup/"
cp -R "$SOURCE/integrations/elia-discord-bot" "$TARGET/integrations/"

# Copy ui_electron (replace)
rm -rf "$TARGET/ui_electron"
cp -R "$SOURCE/ui_electron" "$TARGET/ui_electron"

# Clean target
rm -rf "$TARGET/ui_electron/.sisyphus"
rm -rf "$TARGET/ui_electron/store"
rm -rf "$TARGET/ui_electron/.jarvis-position.json"

echo "✅ Sync complete!"
echo "Run: cd $TARGET && git status"
```

---

## Notes

- Always verify `.gitignore` covers sensitive files
- Check for Discord bot tokens in TOOLS.md before commit
- Use `gh release edit` to update existing release or `gh release create` for new
- Run `git status` before commit to verify only intended files

---

**Last updated**: April 2026
