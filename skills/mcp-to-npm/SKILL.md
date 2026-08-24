---
name: mcp-to-npm
description: Transform any MCP server (Python, Node.js, or any language) into a plug-and-play npm package that works with `npx`. Creates the full npm wrapper: Node.js launcher, auto-dependency installation, postinstall script, and publishes to npm. Use this skill whenever someone says "make this MCP installable via npx", "package this MCP for npm", "wrap this MCP as an npm package", "turn this MCP into a global install", or any request to make an MCP server easy to install and run via npx. Also trigger on: "publish MCP to npm", "MCP npm package", "npx MCP server", "make MCP plug and play".
---

# MCP → npm Package Wrapper

Transform any MCP server into an npm package that works with `npx <package-name>` — zero manual setup required from the user.

## What this skill does

1. Creates a Node.js bin launcher that auto-installs dependencies and starts the MCP server
2. Creates a postinstall script for instant setup on `npm install`
3. Configures package.json for npm publish
4. Creates .npmignore for clean packages
5. Updates README with npx usage instructions
6. Publishes to npm (with user's auth)

## Prerequisites

The user must have:
- Node.js 18+ installed
- npm account (for publishing)
- The MCP server source code in a directory

## Workflow

### Step 1: Analyze the MCP server

Read the MCP server entry point to determine:
- **Language**: Python (FastMCP, etc.), Node.js, or other
- **Dependencies**: What needs to be installed (pip packages, npm packages, etc.)
- **Binary requirements**: Swift compilation, C extensions, etc.
- **Platform constraints**: macOS-only, cross-platform, etc.

```bash
# Find the entry point
grep -r "FastMCP\|FastAPI\|app = \|mcp.run\|server.run" --include="*.py" --include="*.js" -l | head -5
```

### Step 2: Create the Node.js bin launcher

Create `bin/<package-name>` as a Node.js script (NOT bash). This is the key to npx compatibility — npx expects a Node.js entry point.

```javascript
#!/usr/bin/env node
"use strict";

const { execSync, spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

const ROOT = path.resolve(__dirname, "..");
const PYTHON_SCRIPT = path.join(ROOT, "<entry_point>.py");

function log(msg) {
  process.stderr.write(`\x1b[36m[<package-name>]\x1b[0m ${msg}\n`);
}

function warn(msg) {
  process.stderr.write(`\x1b[33m[<package-name>]\x1b[0m ${msg}\n`);
}

// Find python3 (>= 3.10)
function findPython() {
  for (const cmd of ["python3", "python"]) {
    try {
      const ver = execSync(`${cmd} -c "import sys; print(sys.version_info[:2])"`, {
        encoding: "utf-8", timeout: 5000, stdio: ["pipe", "pipe", "pipe"],
      }).trim();
      const [major, minor] = ver.replace(/[()]/g, "").split(",").map(Number);
      if (major >= 3 && minor >= 10) return cmd;
    } catch { continue; }
  }
  return null;
}

// Compile Swift helper (macOS only, skip if not applicable)
function compileSwift() {
  if (process.platform !== "darwin") return;
  const src = path.join(ROOT, "helper.swift");
  const bin = path.join(ROOT, "helper");
  if (!fs.existsSync(src)) return;
  if (fs.existsSync(bin) && fs.statSync(bin).mtimeMs >= fs.statSync(src).mtimeMs) return;
  try { execSync("which swiftc", { stdio: "ignore", timeout: 3000 }); } catch { return; }
  log("Compiling Swift helper (one-time)...");
  try {
    execSync(`swiftc "${src}" -o "${bin}" -O -framework ImagePlayground`, { stdio: "pipe", timeout: 60_000 });
    log("Compiled ✓");
  } catch { warn("Swift compilation skipped"); }
}

// Install Python deps
function ensurePythonDeps(python) {
  try { execSync(`${python} -c "import mcp; import PIL"`, { stdio: "ignore", timeout: 5000 }); return true; } catch {}
  log("Installing Python dependencies...");
  try {
    execSync(`${python} -m pip install --quiet --no-warn-script-location "mcp[cli]" pillow`, { stdio: "pipe", timeout: 120_000 });
    log("Dependencies installed ✓");
    return true;
  } catch { warn("pip install failed — run manually"); return false; }
}

// Main
function main() {
  const python = findPython();
  if (!python) { process.stderr.write("Python 3.10+ required\n"); process.exit(1); }
  compileSwift();
  if (!ensurePythonDeps(python)) process.exit(1);
  if (!fs.existsSync(PYTHON_SCRIPT)) { process.stderr.write(`Entry point not found: ${PYTHON_SCRIPT}\n`); process.exit(1); }
  const child = spawn(python, [PYTHON_SCRIPT, ...process.argv.slice(2)], {
    stdio: "inherit", cwd: ROOT, env: process.env,
  });
  child.on("error", (err) => { process.stderr.write(`Failed: ${err.message}\n`); process.exit(1); });
  child.on("exit", (code) => process.exit(code ?? 1));
}

main();
```

**Customize per MCP:**
- Replace `<package-name>` with the actual npm package name
- Replace `<entry_point>.py` with the actual Python file
- Add/remove dependency checks (e.g., remove PIL check if not using Pillow)
- Add/remove Swift compilation if not applicable
- For Node.js MCP servers, skip Python entirely and just spawn the Node process

### Step 3: Create postinstall.js

```javascript
#!/usr/bin/env node
const { execSync } = require("child_process");
const path = require("path");
const fs = require("fs");

const ROOT = __dirname;
function log(msg) { console.log(`\x1b[36m[<package-name>]\x1b[0m ${msg}`); }
function warn(msg) { console.warn(`\x1b[33m[<package-name>]\x1b[0m ${msg}`); }

// Swift compilation (macOS only)
if (process.platform === "darwin") {
  const src = path.join(ROOT, "helper.swift");
  const bin = path.join(ROOT, "helper");
  if (fs.existsSync(src) && (!fs.existsSync(bin) || fs.statSync(src).mtimeMs > fs.statSync(bin).mtimeMs)) {
    try {
      execSync(`swiftc "${src}" -o "${bin}" -O`, { stdio: "inherit", timeout: 60_000 });
      log("Swift helper compiled ✓");
    } catch { warn("Swift compilation skipped"); }
  }
}

// Python deps
try {
  execSync('python3 -c "import mcp; import PIL"', { stdio: "ignore", timeout: 5000 });
  log("Python deps OK ✓");
} catch {
  try {
    execSync('python3 -m pip install --quiet --no-warn-script-location "mcp[cli]" pillow', { stdio: "inherit", timeout: 120_000 });
    log("Python deps installed ✓");
  } catch { warn("pip install failed"); }
}

log("Setup complete! Run: npx <package-name>");
```

### Step 4: Configure package.json

```json
{
  "name": "<package-name>",
  "version": "1.0.0",
  "description": "<description with MCP, npx, Claude Desktop, Cursor keywords>",
  "keywords": ["mcp", "model-context-protocol", "npx", "claude-desktop", "cursor", "<domain-keywords>"],
  "author": "<author>",
  "license": "MIT",
  "repository": { "type": "git", "url": "https://github.com/<user>/<repo>.git" },
  "engines": { "node": ">=18" },
  "publishConfig": { "access": "public" },
  "bin": { "<package-name>": "bin/<package-name>" },
  "files": ["bin/", "postinstall.js", "<python-package>/", "<entry_point>.py", "README.md", "LICENSE"],
  "scripts": { "postinstall": "node postinstall.js" }
}
```

**Key rules:**
- `"publishConfig": { "access": "public" }` — required for scoped packages
- `"bin"` must point to the Node.js script (not Python)
- `"files"` must include everything needed at runtime, exclude `__pycache__/`, `.git/`, etc.
- Do NOT include `"os"` or `"cpu"` restrictions unless the MCP is truly platform-locked

### Step 5: Create .npmignore

```
.git/
.github/
__pycache__/
*.pyc
*.pyo
.env
.env.*
venv/
.venv/
node_modules/
*.tgz
.codegraph/
omo/
```

### Step 6: Update README.md

Add these sections to the README:

**Quick Start section:**
```markdown
## Quick Start

### npx (recommended)
\`\`\`bash
npx <package-name>
\`\`\`

### npm install
\`\`\`bash
npm install -g <package-name>
<package-name>
\`\`\`

### From source
\`\`\`bash
pip install "mcp[cli]" pillow
python3 <entry_point>.py
\`\`\`
```

**IDE Integration section:**
```markdown
## IDE Integration

### Cursor / Windsurf / VS Code
\`\`\`json
{
  "mcpServers": {
    "server_name": {
      "command": "npx",
      "args": ["<package-name>"]
    }
  }
}
\`\`\`

### Claude Desktop
\`\`\`json
{
  "mcpServers": {
    "server_name": {
      "command": "npx",
      "args": ["<package-name>"]
    }
  }
}
\`\`\`

### OpenCode / Claude Code
\`\`\`bash
claude mcp add server_name --scope user -- npx <package-name>
\`\`\`
```

### Step 7: Publish

```bash
npm publish --access public
```

If 2FA is required, the user needs a granular access token with "Allow publishing without 2FA" enabled at npmjs.com/settings/tokens.

## Node.js MCP servers

If the MCP server is already Node.js (not Python), the wrapper is simpler:
- No Python/dependency checks needed
- Just spawn the Node.js entry point directly
- postinstall.js can skip pip installs
- Consider using `node_modules/.bin/` if it has npm deps

## Common issues and fixes

| Issue | Fix |
|-------|-----|
| Cursor can't find npx | Use full path: `"/Users/<user>/.nvm/versions/node/v20.x.x/bin/npx"` |
| 403 on npm publish | Create granular token with "Allow publishing without 2FA" |
| __pycache__ in package | Add `!python-package/__pycache__/` to `files` in package.json |
| Swift compilation fails | Warn and continue — Pollinations/cloud engine still works |
| Python not found | Error with clear message to install Python 3.10+ |

## Testing the package locally

Before publishing, test the full npx flow:

```bash
cd <package-dir>
npm pack                    # creates .tgz
npm install -g ./<name>-<version>.tgz
<package-name>              # should start the MCP server
npm unlink -g <package-name>
```
