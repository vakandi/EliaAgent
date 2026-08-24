---
name: website-cloner
description: Clone any website into a runnable Next.js (or Vite React) project using the ditto.site MCP server, OR extract its design DNA with Hallmark and rebuild it with a unique non-AI look. ALWAYS asks one question first — "Clone with ditto or redesign with Hallmark?" — before proceeding. Use this skill whenever the user says "clone this site", "copy this website", "scrape this page into code", "turn this URL into a project", "make a copy of [site]", "replicate this page", or provides a URL and wants a downloadable/copyable version of it. Also trigger when the user says "clone", "mirror", "reproduce", "redesign this site", "make this look unique", "not AI-generated", referring to a website. TRIGGER PROACTIVELY on any URL + intent to have the source code of a page or to redesign an existing site's look.
---

# Website Cloner — Clone or Hallmark

**ALWAYS ask ONE question before doing anything. Never skip this step. Never infer. Never assume.**

The user gave you a URL. Your first message MUST be:

> *"I have the URL. Do you want to (1) **clone** it as-is with ditto (exact copy → runnable Next.js project), or (2) **redesign it with Hallmark** (extract the content, rebuild it with a unique non-AI look using Hallmark's design skill)?"*

Wait for the user's answer. Do NOT proceed until they choose. If they say something ambiguous, re-ask with the same two options.

Then branch:

---

## Branch A — Clone with ditto.site

Clone any public website into a self-contained Next.js project using the ditto.site MCP. The pipeline is: start a clone job → poll until done → download the bundle → extract and optionally serve.

### Prerequisites

- `ditto-site` MCP server configured in `~/.config/mcp/mcp_servers.json` (HTTP type, Bearer auth)
- `mcp-cli` available in PATH

**All `mcp-cli` commands are shell commands — always execute them via the `bash` tool, not as native MCP tool calls.** Syntax:
```bash
mcp-cli call <server-name> <tool-name> '<json-arguments>'
```
To list servers, run bare `mcp-cli` (no arguments). For full reference on mcp-cli usage and all available servers, load `skill(name="mcp-cli")`.

If the MCP isn't configured, tell the user and offer to install it. The config entry looks like:

```json
"ditto-site": {
  "type": "http",
  "url": "https://api.ditto.site/mcp",
  "headers": {
    "Authorization": "Bearer <DITTO_API_KEY>"
  }
}
```

### Workflow

#### Step 1: Start the clone job

Extract the URL from the user's request. If they gave just a domain (e.g. `cursor.com`), add `https://` prefix. The user may also specify options (framework, styling, mode) — use sensible defaults if not.

```bash
mcp-cli call ditto-site clone_website '{"url":"<URL>","options":{"mode":"single","styling":"tailwind","framework":"next"}}'
```

This returns `{ "jobId": "...", "status": "queued" }`.

**Options:**

| Option | Values | Default | Notes |
|--------|--------|---------|-------|
| `mode` | `single`, `multi` | `single` | `single` = homepage only, `multi` = crawl linked pages |
| `styling` | `tailwind`, `css` | `tailwind` | Tailwind = utility classes, CSS = plain stylesheet |
| `framework` | `next`, `vite` | `next` | Next.js App Router or Vite React |

#### Step 2: Poll for completion

The clone takes 30s–5min depending on site complexity. Poll every 15–30s:

```bash
mcp-cli call ditto-site get_clone_status '{"jobId":"<JOB_ID>"}'
```

Status progression: `queued` → `running` → `succeeded`

On success, the response includes `timings` (captureMs, generateMs) and `capture` stats (nodeCount, pollution).

If it fails or hangs for 5+ minutes, cancel and retry with a simpler URL.

#### Step 3: Download the bundle

Once succeeded, download the full project as a `.tgz` archive:

```bash
curl -L -H "Authorization: Bearer <API_KEY>" \
  "https://api.ditto.site/v1/clones/<JOB_ID>/bundle?format=tgz" \
  -o /tmp/ditto-clone-<domain>.tgz
```

Or use `get_clone_result` to inspect the file map first, and `read_clone_files` to selectively grab specific files.

#### Step 4: Extract and serve

```bash
mkdir -p <OUTPUT_DIR> && cd <OUTPUT_DIR>
tar -xzf /tmp/ditto-clone-<domain>.tgz
npm install
npx next dev --port 3456
```

Output directory: use `~/mcps_server/ditto-output/<domain>` or whatever the user requests.

#### Step 5: Report to user

Tell the user:
- How many files were generated (from `list_clone_files`)
- The output directory path
- The dev server URL (if started)
- Key files they might want to edit (usually `src/app/content.ts`, `src/app/sections/*.tsx`, `src/app/components/*.tsx`)

### Useful MCP Tools

| Tool | Purpose |
|------|---------|
| `clone_website` | Start a clone job |
| `get_clone_status` | Poll job progress |
| `list_clone_files` | List all generated files with sizes |
| `read_clone_files` | Read specific text files from the result |
| `get_clone_bundle` | Get download URL for the full archive |
| `list_clones` | List all past clone jobs |
| `cancel_clone` | Cancel a running job |

### Common Pitfalls

- **Auth tokens**: The API key must be in the `Authorization: Bearer` header for both MCP and REST calls. The MCP server handles auth automatically; raw `curl` calls need the header.
- **Large sites**: Multi-page clones can take 5+ minutes and produce 500+ files. Start with `single` mode unless the user wants the full site.
- **Dynamic content**: Sites that require login, have heavy JS state, or serve content via client-side routing may not clone well. The capture uses a real browser but can't interact with auth walls.
- **Binary assets**: Fonts, images, and videos are bundled in `public/assets/cloned/`. The total bundle size can be 5-20MB.

### Output Structure

A cloned project contains:
```
├── package.json          # Next.js 15 + React 19 + Tailwind 4
├── next.config.mjs
├── tsconfig.json
├── preview.html          # Static preview of the captured page
├── AGENTS.md             # AI-friendly docs for the generated code
├── ARCHITECTURE.md       # Project structure overview
├── src/app/
│   ├── page.tsx          # Main page
│   ├── ditto.css         # Global styles
│   ├── content.ts        # Editable content data
│   ├── components/       # Reusable UI components
│   ├── sections/         # Page sections (hero, footer, etc.)
│   └── svgs/             # SVG icons as React components
└── public/assets/cloned/
    ├── fonts/            # Captured font files
    ├── images/           # Captured images
    ├── svg/              # Captured SVGs
    └── videos/           # Captured video files
```

Edit `src/app/content.ts` and `src/app/sections/*.tsx` to customize the clone.

---

## Branch B — Redesign with Hallmark

Load the **hallmark** skill (installed at `~/.config/opencode/skills/hallmark/SKILL.md`).

Use `hallmark study <URL>` first to extract the site's design DNA (macrostructure, type-pairing, colour anchor). Present the diagnosis to the user. Then ask:

>*"I've extracted the DNA. Do you want to (1) **build with this DNA** (rebuild the page with Hallmark's non-AI look while keeping the extracted structure), (2) **use a different theme** (keep the structure but pick a different Hallmark theme), or (3) **just keep the diagnosis**?"*

Based on their answer, follow the Hallmark skill's workflow (default build, redesign, or study-only). The output is a self-contained HTML/CSS page with Hallmark's anti-slop gates applied — no Next.js project, just pure hand-crafted front-end code.
