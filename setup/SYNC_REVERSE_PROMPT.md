# EliaAgent → EliaAI Reverse Sync Prompt

> Use this prompt when you want to sync updates from the public EliaAgent repo to your private EliaAI repo.
> This is for users who want to pull the latest changes from the public repository into their private instance.

---

## Context

You are working with TWO GitHub repos:
- **Public**: `~/user/EliaAgent` (clean repo with latest updates)
- **Private**: `~/user/YOUR_PRIVATE_REPO` (your working repo with personal data)

Your task is to SYNC the public repo to the private repo, **preserving all your personal data** (credentials, configs, logs, etc.) while pulling in the latest features and fixes.

---

## Mission

1. **COMPARE** the two repos to find all differences
2. **IDENTIFY** what needs to be pulled (new files, updated scripts, documentation)
3. **PRESERVE** personal data that should NOT be overwritten:
   - `.env` files with real credentials
   - `logs/` directories
   - `docs/YYYY-MM-DD/` daily log folders
   - `brain/obsidian/` private wiki
   - `memory/*-CREDENTIALS.md` secret files
   - `context/business.md` (your actual business info)
   - `context/TOOLS.md` (your actual tokens/IDs)
   - `PROMPT.md` (your custom prompts)
   - `node_modules/`, `__pycache__/`, `venv/` (rebuild locally)
4. **PULL** clean updates from EliaAgent → YOUR_PRIVATE_REPO
5. **MERGE** carefully - handle conflicts between public templates and your custom configs
6. **REBUILD** dependencies if needed
7. **TEST** to ensure your personal data still works

---

## Step-by-Step Instructions

### Step 1: Read Release Notes

**IMPORTANT**: Before syncing, always read the release notes to understand what's new:
```bash
cat ~/user/EliaAgent/setup/RELEASENOTES.md
```

This will tell you:
- What new features were added
- What bugs were fixed
- What breaking changes (if any) were introduced
- What version you're syncing to

### Step 2: Compare Repos

Run this to find differences:
```bash
diff -rq ~/user/EliaAgent ~/user/YOUR_PRIVATE_REPO --exclude=".git" --exclude="*.log" --exclude="node_modules" --exclude="venv" --exclude="__pycache__" 2>/dev/null | head -100
```

Or use explore agent for deeper analysis.

**Review the diff carefully** to understand:
- Which files will be overwritten
- Which files are new
- Which files you should preserve (your personal data)

### Step 3: Identify What to Pull

**Typically NEW in EliaAgent (pull to YOUR_PRIVATE_REPO):**
- New scripts in `scripts/` (bug fixes, new features)
- Updated `setup/README.md` (new documentation)
- Updated `setup/RELEASENOTES.md` (changelog)
- New tools in `setup/` (e.g., opencode-proxy.sh)
- Updated `ui_electron/` (UI improvements)
- New integrations (if any)

**Typically MODIFIED (check diff):**
- `scripts/*.sh` - Script updates/fixes
- `setup/*.sh` - Setup script updates
- `setup/README.md` - Documentation updates

**NEVER Overwrite (preserve your data):**
- `.env` - Your real credentials
- `logs/` - Your runtime logs
- `docs/YYYY-MM-DD/` - Your daily logs
- `brain/obsidian/` - Your private wiki
- `memory/*-CREDENTIALS.md` - Your secrets
- `context/business.md` - Your actual business info
- `context/TOOLS.md` - Your actual tokens/IDs
- `PROMPT.md` - Your custom prompts (unless you want updates)
- `MORNING_PROMPT.md` - Your custom morning routine
- `node_modules/` - Rebuild locally
- `venv/`, `__pycache__/` - Rebuild locally

### Step 4: Backup Your Personal Data

Before pulling, backup critical files:
```bash
# Create backup directory
BACKUP_DIR="~/user/YOUR_PRIVATE_REPO/.sync_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup critical files
cp ~/user/YOUR_PRIVATE_REPO/.env "$BACKUP_DIR/" 2>/dev/null || true
cp -r ~/user/YOUR_PRIVATE_REPO/context "$BACKUP_DIR/" 2>/dev/null || true
cp ~/user/YOUR_PRIVATE_REPO/PROMPT.md "$BACKUP_DIR/" 2>/dev/null || true
cp ~/user/YOUR_PRIVATE_REPO/MORNING_PROMPT.md "$BACKUP_DIR/" 2>/dev/null || true

echo "✅ Backup created at: $BACKUP_DIR"
```

### Step 5: Pull Updates

```bash
# Pull updated scripts
cp ~/user/EliaAgent/scripts/*.sh ~/user/YOUR_PRIVATE_REPO/scripts/

# Pull setup files (excluding README.md if you have custom changes)
cp ~/user/EliaAgent/setup/*.sh ~/user/YOUR_PRIVATE_REPO/setup/
cp ~/user/EliaAgent/setup/opencode-proxy.sh ~/user/YOUR_PRIVATE_REPO/setup/ 2>/dev/null || true

# Pull README.md (review first, then decide)
# cp ~/user/EliaAgent/setup/README.md ~/user/YOUR_PRIVATE_REPO/setup/README.md

# Pull RELEASENOTES.md
cp ~/user/EliaAgent/setup/RELEASENOTES.md ~/user/YOUR_PRIVATE_REPO/setup/RELEASENOTES.md

# Pull UI updates (if you want them)
# rm -rf ~/user/YOUR_PRIVATE_REPO/ui_electron
# cp -R ~/user/EliaAgent/ui_electron ~/user/YOUR_PRIVATE_REPO/ui_electron
```

### Step 6: Handle Config Conflicts

**For context files:**
- Compare `context/business.md` - Public has placeholders, yours has real data
- Compare `context/TOOLS.md` - Public has placeholders, yours has real toikens
- **Keep your versions** unless you want to adopt new structure

**For prompt files:**
- Compare `PROMPT.md` - Public may have new features
- Compare `MORNING_PROMPT.md` - Public may have updates
- **Manual merge** - Add new sections to your custom prompts

**For setup/README.md:**
- Public may have new documentation sections
- **Manual merge** - Add new sections to your local copy if needed

### Step 7: Rebuild Dependencies

```bash
cd ~/user/YOUR_PRIVATE_REPO

# Rebuild UI if you pulled ui_electron
cd ui_electron
rm -rf node_modules
npm install
cd ..

# Rebuild Discord bot if needed
cd integrations/elia-discord-bot
rm -rf venv __pycache__
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ../..
```

### Step 8: Test Your Setup

```bash
# Test proxy wrapper
~/YOUR_PRIVATE_REPO/setup/opencode-proxy.sh --version

# Test scripts
~/YOUR_PRIVATE_REPO/scripts/trigger_opencode_interactive.sh --help

# Verify your .env still works
# (Test your integrations, MCP servers, etc.)
```

### Step 9: Commit Your Updates

```bash
cd ~/user/YOUR_PRIVATE_REPO
git add -A
git status  # Verify only intended files
git commit -m "chore: sync updates from EliaAgent v1.0.2"
git push origin main
```

---

## Quick Copy-Paste Prompts

### For Explore Agent:
```
Compare ~/user/EliaAgent vs ~/user/YOUR_PRIVATE_REPO

List ALL differences:
- New files in EliaAgent (need pull)
- Modified files (need update)
- Files that should NOT be overwritten (personal data)

Focus on: scripts/, setup/, ui_electron/
```

### For Execution:
```
Sync EliaAgent to YOUR_PRIVATE_REPO:
1. Backup personal data
2. Pull new/updated files
3. Handle config conflicts manually
4. Rebuild dependencies
5. Test your setup
6. Commit updates

Use ~/user/EliaAgent as source, ~/user/YOUR_PRIVATE_REPO as target.
```

---

## Common Files to Handle

| Path | Action | Notes |
|------|--------|-------|
| `scripts/*.sh` | PULL | Script updates/fixes |
| `setup/*.sh` | PULL | Setup script updates |
| `setup/opencode-proxy.sh` | PULL | New proxy wrapper |
| `setup/README.md` | MERGE | Review new docs, merge manually |
| `setup/RELEASENOTES.md` | PULL | Changelog |
| `ui_electron/*` | OPTIONAL | UI updates (rebuild node_modules) |
| `context/business.md` | KEEP | Your actual business info |
| `context/TOOLS.md` | KEEP | Your actual tokens/IDs |
| `PROMPT.md` | MERGE | Add new features to your custom prompt |
| `MORNING_PROMPT.md` | MERGE | Add new features to your routine |
| `.env` | KEEP | Your real credentials |
| `logs/*` | KEEP | Your runtime logs |
| `docs/YYYY-MM-DD/*` | KEEP | Your daily logs |
| `brain/obsidian/*` | KEEP | Your private wiki |
| `memory/*-CREDENTIALS.md` | KEEP | Your secrets |

---

## Automated Script (Optional)

Create a sync script:
```bash
#!/bin/bash
# EliaAgent → YOUR_PRIVATE_REPO Sync Script

SOURCE="~/user/EliaAgent"
TARGET="~/user/YOUR_PRIVATE_REPO"

echo "🔄 Syncing EliaAgent → YOUR_PRIVATE_REPO"

# Create backup
BACKUP_DIR="$TARGET/.sync_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "📦 Creating backup at: $BACKUP_DIR"

# Backup critical files
cp "$TARGET/.env" "$BACKUP_DIR/" 2>/dev/null || true
cp -r "$TARGET/context" "$BACKUP_DIR/" 2>/dev/null || true
cp "$TARGET/PROMPT.md" "$BACKUP_DIR/" 2>/dev/null || true
cp "$TARGET/MORNING_PROMPT.md" "$BACKUP_DIR/" 2>/dev/null || true

# Pull updated scripts
echo "📦 Pulling updated scripts..."
cp "$SOURCE/scripts"/*.sh "$TARGET/scripts/"

# Pull setup files
echo "📦 Pulling setup files..."
cp "$SOURCE/setup"/*.sh "$TARGET/setup/"
cp "$SOURCE/setup/opencode-proxy.sh" "$TARGET/setup/" 2>/dev/null || true
cp "$SOURCE/setup/RELEASENOTES.md" "$TARGET/setup/"

echo "✅ Sync complete!"
echo "📝 Backup at: $BACKUP_DIR"
echo "⚠️  Review and merge context files manually"
echo "⚠️  Rebuild dependencies if needed"
echo "Run: cd $TARGET && git status"
```

---

## Important Notes

- **Always backup** before pulling updates
- **Review context files** - Public has placeholders, yours has real data
- **Manual merge prompts** - Add new features to your custom prompts
- **Test after sync** - Verify your integrations still work
- **Commit your changes** - Track what you pulled from public
- **Check RELEASENOTES.md** - See what's new in the public version

---

## When to Use This

Use this reverse sync when:
- A new version is released on EliaAgent (check RELEASENOTES.md)
- Bug fixes are published that you need
- New features are added that you want
- Documentation is updated with new information

**Do NOT use this if:**
- You have made significant custom changes that conflict
- You want to keep your private repo completely separate
- The public version has breaking changes you're not ready for

---

**Last updated**: May 3, 2026
