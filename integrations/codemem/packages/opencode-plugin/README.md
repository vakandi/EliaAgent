# @codemem/opencode-plugin

Persistent memory plugin for [OpenCode](https://opencode.ai).

## Install

Recommended:

```text
npx -y codemem setup --opencode-only
```

Manual config also works. Add the package name to your OpenCode config:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["@codemem/opencode-plugin"]
}
```

OpenCode installs npm plugins automatically with Bun at startup.

### Development / symlink install

When you symlink the bundled plugin file into `~/.config/opencode/plugins/`, reference the **file** (`codemem.js`), not a directory named `codemem`. Listing `./plugins/codemem` loads a folder without a function export and produces `Plugin export is not a function`.

On some OpenCode versions, **symlinking straight to the large plugin file** fails with `Plugin export is not a function` because the loader does not expose the async default correctly for that resolve path. If you see that error, symlink `~/.config/opencode/plugins/codemem.js` to the thin re-export shim in `~/.opencode/plugins/codemem.js` (three lines that `export … from "<absolute-path-to-repo>/codemem.js"`).

Keep a **single** codemem entry in the merged OpenCode config (`config.json`, `opencode.json`, and project `.opencode/*`). Duplicates can load the same logic twice.

Example:

```json
{
  "plugin": [
    "./plugins/codemem.js"
  ]
}
```

### Agent-scoped memory (`mem-*` tools)

The plugin resolves a `--project` string aligned with the viewer feed: `baseProject` from the repo cwd and, when the session agent is known, **`baseProject/agentId`** (e.g. `EliaAI/elia`). **`mem-recent`** and the recent section of **`mem-status`** pass that value to `codemem recent --project …`. **`mem-stats`** remains a **global** database summary; see `mem-status` labels for which section is scoped.

### Verifying sessions and agents in SQLite

With `CODEMEM_DB` pointing at your DB (or `codemem stats` / viewer settings for the path):

```sql
SELECT project, COUNT(*) AS sessions
FROM raw_event_sessions
GROUP BY project
ORDER BY sessions DESC
LIMIT 20;

SELECT s.project, m.actor_id, COUNT(*) AS n
FROM memory_items m
JOIN sessions s ON s.id = m.session_id
WHERE m.active = 1
GROUP BY 1, 2
ORDER BY n DESC
LIMIT 30;
```

Rows for a given OpenCode agent should use a `sessions.project` suffix such as `/elia` matching the feed agent chip, and `actor_id` / display names that still pass client-side filtering when mixed.

## Documentation

- Repository: https://github.com/kunickiaj/codemem
- Full README: https://github.com/kunickiaj/codemem#readme
- User guide: https://github.com/kunickiaj/codemem/blob/main/docs/user-guide.md
- Architecture: https://github.com/kunickiaj/codemem/blob/main/docs/architecture.md
