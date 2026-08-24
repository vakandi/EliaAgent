---
name: codegraph-index
description: Trigger a full codegraph index of the current folder. Use this whenever the user asks to index, reindex, or set up codegraph for a project. Also trigger when codegraph tools return "project isn't indexed" or "no .codegraph/" errors, when the user says "index this project", "set up codegraph", "reindex", "run codegraph", or when starting work on a new codebase where codegraph hasn't been initialized yet.
---

# Codegraph Indexing

Run a full codegraph index on the current project folder.

## Steps

1. Run `codegraph init` in the current working directory:
   ```bash
   codegraph init
   ```
   This scans the project and builds the `.codegraph/` knowledge graph.

2. Verify the index was created by checking for `.codegraph/` directory:
   ```bash
   ls -la .codegraph/
   ```

3. Report results to user:
   - Number of files indexed
   - Index size
   - Confirmation that codegraph tools (`codegraph_explore`, `codegraph_node`, etc.) are now available

## Notes

- Indexing typically takes 10-30 seconds depending on project size
- The index lags file writes by ~1 second (file watcher)
- If `codegraph` command is not found, check if it's installed: `which codegraph` or `npm list -g codegraph`
