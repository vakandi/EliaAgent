# Fix OpenCode TUI Not Opening - Agent Prompt

## Context

You are a debugging specialist tasked with fixing OpenCode TUI that stopped working after modifications to the codemem memory system.

## Problem

OpenCode TUI (Terminal UI) stopped opening after the user modified the codemem memory system at `/path/to/EliaAI/integrations/codemem`. 

**Symptoms:**
- TUI tries to open but doesn't display
- No logs are visible
- The command hangs indefinitely
- Basic command `opencode run --agent elia "say hi" --attach` does not complete

## What Was Changed

1. User modified files in `/path/to/EliaAI/integrations/codemem` (memory system)
2. After modifications, OpenCode stopped working

## Current State

**Plugin Configuration (`~/.config/opencode/config.json`):**
```json
{
  "plugin": [
    "file:///path/to/config/opencode/plugins/open-island.js",
    "file:///path/to/config/opencode/plugins/codemem.js"
  ]
}
```

**Codemem Plugin:**
- Symlink: `~/.config/opencode/plugins/codemem.js` → `/path/to/EliaAI/integrations/codemem/packages/opencode-plugin/.opencode/plugins/codemem.js`
- File exists and is valid
- Last modified: May 5, 23:26

**OpenCode Version:** 1.14.39

**Files to Check:**
- `~/.config/opencode/config.json`
- `~/.config/opencode/opencode.json`
- `~/.config/opencode/settings.json`
- `~/.config/opencode/plugins/codemem.js`
- `/path/to/EliaAI/integrations/codemem/packages/opencode-plugin/.opencode/plugins/codemem.js`

## Your Mission

1. **Diagnose the issue** - Check all relevant config files and logs
2. **Identify the root cause** - Find what's preventing OpenCode from starting
3. **Fix the issue** - Make the necessary changes to restore functionality
4. **Verify the fix** - Ensure `opencode run --agent elia "say hi" --attach` works in under 30 seconds

## Important Notes

- **DO NOT run long-running commands** without timeout
- **DO NOT run opencode directly** - it will hang indefinitely
- Use read-only commands to diagnose: `cat`, `ls`, `grep`, `jq`
- Check for syntax errors in JSON files
- Check for broken symlinks
- Check for plugin loading errors
- The codemem plugin may have compatibility issues

## Success Criteria

- OpenCode TUI opens successfully
- Basic command `opencode run --agent elia "say hi" --attach` completes in under 30 seconds
- No errors in logs
- All plugins load correctly

## Files to Review

1. `~/.config/opencode/config.json` - Main config
2. `~/.config/opencode/opencode.json` - Agent config
3. `~/.config/opencode/settings.json` - Settings
4. `~/.config/opencode/plugins/codemem.js` - Codemem plugin
5. Any log files in `~/.config/opencode/` or subdirectories

## Approach

1. First, check all JSON files for syntax errors
2. Verify symlink is valid
3. Check if codemem plugin has errors
4. Try disabling codemem plugin temporarily to isolate the issue
5. If codemem is the problem, either fix it or disable it
6. Test with minimal config

## Start Here

Begin by checking the JSON files for syntax errors using `jq` or similar tools.
