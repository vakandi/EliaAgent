# EliaAI → EliaAgent Sync Prompt

> Use this prompt when you want to sync your private EliaAI repo to the public EliaAgent repo.

---

## Context

You are working with TWO GitHub repos:
- **Private**: `/path/to/EliaAI` (your working repo with all your changes)
- **Public**: `/path/to/EliaAgent` (cleaned repo for public release)

Your task is to SYNC the private repo to the public repo, cleaning all sensitive data (credentials, logs, personal info) while preserving all functionality.

---

## CRITICAL: Lessons Learned (May 2026)

**⚠️ This sync process has a history of breaking things. Follow these rules strictly.**

### 1. NEVER let shell eat `${}` template literals

Files in EliaAI contain JavaScript/TypeScript template literals like `` `Hello ${name}` `` and bash `${VARIABLE}` references. During `cp -R`, `echo`, or `cat` operations, the shell interprets `${...}` and can silently mangle file contents.

**Check for this before committing:**
```bash
# After copying, verify no template literals were eaten
cd /path/to/EliaAgent
grep -rn '\${[A-Za-z]' --include='*.md' --include='*.sh' --include='*.js' --include='*.ts' --include='*.html' --include='*.json' . 2>/dev/null | grep -v 'node_modules/' | head -30
```

If files have fewer `${...}` patterns than expected, the shell ate them during copy.

**Safe copy techniques:**
- Use `rsync` instead of `cp -R` (avoids shell interpretation)
- Always use single quotes around paths with `${...}` content
- After copy, diff a few files to verify content integrity

### 2. SCRUB sensitive data before ANY commit

GitHub has **automatic secret scanning**. It will BLOCK pushes containing:
- API keys, tokens, secrets
- IP addresses of your servers
- Personal names, business names you want private
- Email addresses, phone numbers
- Server credentials, database URLs

**Pre-push verification checklist:**
```bash
# 1. Check staged changes for sensitive patterns
cd /path/to/EliaAgent
git diff --cached | grep -iE 'api.?key|secret|token|password|credential|\.env|proxy|user|discord|surname|co.?bou|bene.?luxe|157\.180|login|ssh-'

# 2. Check for any private business names
git diff --cached | grep -iE 'surname|yourname|co.?bou|bene.?luxe|yourventures|yourbrand2'

# 3. Check for server IPs
git diff --cached | grep -E '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b'

# 4. Check for real email addresses
git diff --cached | grep -E '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
```

**If ANY of these find matches, DO NOT COMMIT. Fix the files first.**

### 3. NEVER `git rm` without `--cached` on the private repo — breaks credentials on disk

**⚠️ CRITICAL BUG (May 14, 2026)**: Running `git rm` (without `--cached`) on credential files in the PRIVATE repo **deletes them from disk permanently**. The main `.env`, docs/credentials.txt, etc. use `git rm --cached` which keeps files on disk — but integration `.env` files were `git rm`'d and lost.

**Fix if this happens again:**
```bash
# Restore from git history (the file is still in the last commit)
git show HEAD~0:path/to/deleted/file > path/to/deleted/file
```

**Never run `git rm` without `--cached` on the private working repo.**
Only use `git rm --cached` (keeps file on disk) + `.gitignore` (prevents re-tracking).

### 4. If secrets leaked into git history, use `git filter-repo`

If GitHub rejects your push due to secret scanning, OR if you realize secrets are in a past commit:

```bash
# DO NOT use git filter-branch (too slow, unreliable)
# Use git filter-repo instead:

# Step 1: Install git-filter-repo
brew install git-filter-repo

# Step 2: Strip sensitive strings from history
cd /path/to/EliaAgent
git filter-repo --replace-text <(echo "SENSITIVE_STRING==>REPLACEMENT")

# Step 3: Force push the cleaned history
git remote add origin https://github.com/user/EliaAgent.git
git push origin main --force
```

**⚠️ Warning**: `filter-repo` rewrites commit hashes. Anyone with a local clone will need to re-clone.

### 5. Test the push BEFORE committing everything

Make small incremental commits and push after each:
```bash
git add path/to/file
git commit -m "feat: add specific feature"
git push origin main   # Early test - verify push works
git add more/files
git commit -m "feat: add another feature"
git push origin main   # Continuous verification
```

Don't batch 11 commits then push - you'll only discover problems at the end.

### 6. Amending history should be a last resort

If you must fix a commit before pushing:
```bash
# Fix the last commit (only if not pushed yet)
git commit --amend   # Add more changes or fix message
```

### 7. Verify the target repo has the latest content

After push, check the GitHub web UI to verify:
```bash
gh repo view user/EliaAgent --json description,url
# Or open in browser:
open https://github.com/user/EliaAgent
```

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
   - `setup/proxies.txt` - Real proxy credentials (contains IP:PORT:USER:PASS)
   - `integrations/elia-discord-bot/.env` - Discord bot token
   - `integrations/elia-discord-bot/sessions.json` - Session data
4. **COPY** clean files from EliaAI → EliaAgent
5. **UPDATE** documentation:
   - `setup/README.md` with any new features
   - `RELEASENOTES.md` with changelog
6. **VERIFY** no sensitive data leaked (see checklist above)
7. **COMMIT** with clear message
8. **PUSH** to GitHub

---

## Step-by-Step Instructions

### Step 1: Compare Repos

Run this to find differences:
```bash
diff -rq /path/to/EliaAI /path/to/EliaAgent --exclude=".git" --exclude="*.log" --exclude="node_modules" 2>/dev/null | head -100
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
- `setup/proxies.txt` - Proxy list with real IP:PORT:USER:PASS
- `integrations/elia-discord-bot/.env` - Discord bot token
- `integrations/elia-discord-bot/logs/` - Bot runtime logs
- `integrations/elia-discord-bot/sessions.json` - Active sessions
- `.scheduler_state` - Scheduler state files

### Step 3: Clean Sensitive Data (NEVER modify source)

**⚠️ CRITICAL**: NEVER `rm -rf` or `git rm` files in the SOURCE repo (`EliaAI`). This deletes credentials from disk and breaks the system.

Instead, use `rsync --exclude` to skip sensitive files during copy to TARGET (`EliaAgent`). The source stays intact.

```bash
# Safe: use --exclude patterns in rsync (source is never modified)
# See Step 4 below for the full rsync commands
```

**IMPORTANT**: Before copying, check for sensitive strings in files you plan to copy. Replace them in the TARGET copy only:
- Real business names → Generic placeholders (e.g., "Your Company")
- Real server IPs → `127.0.0.1` or `[server-ip]`
- Real API keys → `[your-api-key]`
- Real email addresses → `[your-email]`
- Real Discord/Telegram IDs → `[channel-id]`

### Step 4: Copy Files (SAFELY - avoid shell interpolation)

Use `rsync` for safe copying (handles special characters better than `cp`):

```bash
# Copy desktop shortcuts
rsync -a /path/to/EliaAI/setup/desktop_shortcuts/ /path/to/EliaAgent/setup/desktop_shortcuts/

# Copy discord bot (clean)
rsync -a /path/to/EliaAI/integrations/elia-discord-bot/ /path/to/EliaAgent/integrations/elia-discord-bot/ \
  --exclude='.env' --exclude='__pycache__' --exclude='venv' --exclude='logs' --exclude='sessions.json'

# Copy ui_electron (without node_modules)
rm -rf /path/to/EliaAgent/ui_electron
rsync -a /path/to/EliaAI/ui_electron/ /path/to/EliaAgent/ui_electron/ \
  --exclude='node_modules' --exclude='.sisyphus' --exclude='store' --exclude='.jarvis-position.json'

# Copy scripts (excluding logs)
rsync -a /path/to/EliaAI/scripts/ /path/to/EliaAgent/scripts/ \
  --exclude='logs'

# Copy subworkers
rsync -a /path/to/EliaAI/subworkers/ /path/to/EliaAgent/subworkers/
```

### Step 5: VERIFY No Sensitive Data Leaked (CRITICAL)

Run these checks BEFORE staging files:

```bash
cd /path/to/EliaAgent

echo "=== Checking for business names ==="
grep -rni 'surname\|user\|co.bou\|bene.luxe\|yourventures\|yourbrand2\|yourtool\|yourproject\|yourco' \
  --include='*.md' --include='*.sh' --include='*.js' --include='*.ts' --include='*.json' --include='*.html' \
  . 2>/dev/null | grep -v '.git/' | grep -v 'SYNC_PROMPT.md' | grep -v 'SYNC_REVERSE'

echo "=== Checking for server IPs ==="
grep -rnE '([0-9]{1,3}\.){3}[0-9]{1,3}' \
  --include='*.md' --include='*.sh' --include='*.js' --include='*.ts' --include='*.json' --include='*.html' \
  . 2>/dev/null | grep -v '.git/' | grep -v 'node_modules/' | grep -v '127.0.0.1\|0.0.0.0\|255\|8.8.8.8\|1.1.1.1'

echo "=== Checking for template literal integrity ==="
# Compare a known file with template literals between source and target
diff <(grep -c '\${' /path/to/EliaAI/setup/README.md) <(grep -c '\${' /path/to/EliaAgent/setup/README.md) || echo "⚠️  Template literal count mismatch!"
```

**If ANY sensitive data is found, DO NOT PROCEED.** Fix files before staging.

### Step 6: Update Documentation

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

### Step 7: Commit (Small, Incremental)

```bash
cd /path/to/EliaAgent

# Commit individually - push after each to verify
git add setup/desktop_shortcuts/
git commit -m "feat: add desktop shortcuts"
git push origin main

git add integrations/elia-discord-bot/
git commit -m "feat: add Discord bot integration"
git push origin main

# ... continue for each module
```

### Step 8: Final Push & Verify

```bash
# Push any remaining changes
git push origin main

# Verify on GitHub
gh repo view user/EliaAgent --web
```

### Step 9: Update GitHub Release (Optional)

```bash
gh release edit v1.0.0 --notes-file RELEASENOTES.md
# Or create new release:
gh release create "vX.X.X" --title "EliaAI vX.X.X" --notes-file RELEASENOTES.md --target main
```

---

## Quick Copy-Paste Prompts

### For Explore Agent:
```
Compare /path/to/EliaAI vs /path/to/EliaAgent

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
2. Check for business names, server IPs, and template literal integrity
3. Copy new/modified files using rsync (NOT cp -R)
4. Verify no sensitive data in staged files
5. Update RELEASENOTES.md
6. Commit and push incrementally
7. Update GitHub release

Use /path/to/EliaAI as source, /path/to/EliaAgent as target.
```

---

## Common Files to Check

| Path | Copy? | Notes |
|------|--------|-------|
| `setup/desktop_shortcuts/*` | YES | Desktop shortcuts |
| `integrations/elia-discord-bot/` | YES | Discord bot (clean .env, logs, sessions.json first) |
| `ui_electron/*` | YES | UI (exclude node_modules, .sisyphus, store) |
| `subworkers/*` | YES | Subworker agents |
| `context/TOOLS.md` | YES (cleaned) | Remove real tokens, IPs, business names |
| `context/business.md` | YES (cleaned) | Replace with placeholders |
| `PROMPT.md` | YES | Main prompt (scrub personal names) |
| `setup/README.md` | YES | Update with new features (scrub personal info) |
| `setup/proxies.txt` | NO | Contains real IP:PORT:USER:PASS - NEVER copy |
| `RELEASENOTES.md` | YES | Add changelog |
| `.env` | NO | Never copy |
| `logs/*` | NO | Never copy |
| `docs/YYYY-MM-DD/*` | NO | Never copy |
| `brain/obsidian/*` | NO | Never copy |
| `memory/*-CREDENTIALS.md` | NO | Never copy |
| `.scheduler_state` | NO | State files |

---

## Troubleshooting Sync Issues

### Problem: "remote rejected due to secret scanning"

If GitHub blocks your push:
```bash
# 1. Find what secret triggered it
# Check the email from GitHub or:
gh api repos/user/EliaAgent/secret-scanning/alerts 2>/dev/null | head -20

# 2. Remove the secret from the file
# Edit the file to remove/replace the sensitive string

# 3. If secret is in git history (not just latest commit):
brew install git-filter-repo
cd /path/to/EliaAgent
git filter-repo --replace-text <(echo "THE_SENSITIVE_STRING==>REPLACEMENT")
git remote add origin https://github.com/user/EliaAgent.git
git push origin main --force
```

### Problem: Files have mangled template literals after copy

If `${...}` patterns were eaten by shell:
```bash
# Re-copy the affected files using rsync
rsync -a /path/to/EliaAI/path/to/file /path/to/EliaAgent/path/to/file

# Verify integrity
diff /path/to/EliaAI/path/to/file /path/to/EliaAgent/path/to/file
```

### Problem: Wrong content pushed to public repo

If you accidentally pushed private data:
1. **Immediately** use `git filter-repo` to remove from history
2. Force push the cleaned history
3. Consider the data compromised - rotate any exposed credentials

---

## Safety Checklist (Run Before Each Commit)

```
[ ] Sensitive files excluded (.env, logs, proxies.txt, etc.)
[ ] No business names in clean files
[ ] No server IP addresses in clean files
[ ] No API keys or tokens in clean files
[ ] No personal names in clean files
[ ] Template literals (${...}) are intact after copy
[ ] `git diff --cached` reviewed for sensitive data
[ ] NEVER `git rm` on source repo — only `--cached` (keeps files on disk)
[ ] Integration `.env` files restored to disk after cleanup
[ ] Incremental push working (not batching all commits)
[ ] GitHub web UI shows correct content
```

---

**Last updated**: May 14, 2026
