# dev-browser

Use `parallel-browser-mcp` for all browser automation. Use agent-browser CLI as fallback only if parallel-browser-mcp sessions fail (very unlikely). Triggers on any browser task, web verification, screenshot capture, form filling, or web scraping request.

## Core Rules

1. **Prioritize parallel-browser-mcp** — always. It's the primary tool. agent-browser is legacy fallback only.
2. **Session isolation is mandatory** — always assume other agents share the MCP server. Every agent must use distinct session names with the pattern `{agent}_{task}`.
3. **Never use session IDs from other agents** — create fresh ones.
4. **For launchd/cron/subworker/headless runs** — parallel-browser-mcp is strictly required over agent-browser.

## parallel-browser-mcp

### Session Lifecycle

```python
# Step 1: Start a named session (use your agent + task name)
start_session(sessionName="gilfoyle-login-check")
# Returns: { sessionId: 1, ... }

# Step 2: Navigate and interact
browser_navigate(sessionId=1, url="https://example.com")
browser_snapshot(sessionId=1)          # DOM tree summary
browser_screenshot(sessionId=1)        # PNG screenshot
browser_click(sessionId=1, selector="button#submit")
browser_fill(sessionId=1, selector="input#email", value="test@example.com")
browser_fill_form(sessionId=1, fields=[
  {"selector": "input#email", "value": "test@example.com"},
  {"selector": "input#pass",  "value": "secret"}
])

# Step 3: Close when done
close_session(sessionId=1)
```

### Naming Convention

```
{agent_name}_{short_task}
```

Examples:
- `gilfoyle_login-check`
- `elina_analytics-screenshot`
- `subworker_markov-deploy-verify`

### Tools (26 total)

| Category | Tools |
|----------|-------|
| Lifecycle | `start_session`, `close_session`, `close_all_sessions`, `get_sessions` |
| Navigation | `browser_navigate`, `browser_go_back` |
| Interaction | `browser_click`, `browser_fill`, `browser_fill_form`, `browser_select_option`, `browser_upload_file`, `browser_hover`, `browser_drag` |
| Keyboard | `browser_keyboard_press`, `browser_keyboard_type` |
| Mouse | `browser_mouse_click_xy`, `browser_mouse_move`, `browser_mouse_drag` |
| Query | `browser_snapshot`, `browser_screenshot`, `browser_get_page_structure`, `browser_dom_query`, `browser_generate_locator` |
| Wait | `browser_wait_for_selector`, `browser_wait_for_timeout` |
| Evaluate | `browser_evaluate` (run JS in page context) |

### Common Workflows

**Verify a page loads correctly:**
```python
start_session(sessionName="{agent}_verify")
browser_navigate(sessionId=1, url="https://target.com")
snapshot = browser_snapshot(sessionId=1)
close_session(sessionId=1)
```

**Fill and submit a form:**
```python
start_session(sessionName="{agent}_form-fill")
browser_navigate(sessionId=1, url="https://target.com/form")
browser_fill_form(sessionId=1, fields=[
  {"selector": "#name",  "value": "John Doe"},
  {"selector": "#email", "value": "john@example.com"},
  {"selector": "#msg",   "value": "Hello from dev-browser"}
])
browser_click(sessionId=1, selector="button[type='submit']")
browser_wait_for_timeout(sessionId=1, milliseconds=2000)
snapshot = browser_snapshot(sessionId=1)
close_session(sessionId=1)
```

**Take a screenshot for documentation:**
```python
start_session(sessionName="{agent}_screenshot")
browser_navigate(sessionId=1, url="https://target.com")
browser_screenshot(sessionId=1, fullPage=True)
close_session(sessionId=1)
```

**Run JS to extract data:**
```python
start_session(sessionName="{agent}_extract")
browser_navigate(sessionId=1, url="https://target.com")
result = browser_evaluate(sessionId=1, script="document.querySelectorAll('h2').length")
close_session(sessionId=1)
```

### Troubleshooting

| Problem | Fix |
|---------|-----|
| Session ID collision / wrong session data | You used another agent's session ID. Call `get_sessions` to see active sessions. Create a new one with `start_session`. |
| `selector` not found | Use `browser_generate_locator` to get suggestions, or `browser_get_page_structure` to see the DOM. |
| Page not fully loaded | Add `browser_wait_for_selector` or `browser_wait_for_timeout` before interacting. |
| Need to handle JS popups | Use `browser_evaluate` to inspect or dismiss them. |
| Auth flow (OAuth, CAPTCHA) | Parallel-browser-mcp doesn't have `--headed` mode. For auth flows requiring human login, fall back to agent-browser with `--headed`. |

## Fallback: agent-browser CLI

Use **only** when:
- Parallel-browser-mcp fails to start (very unlikely)
- You need `--headed` mode for human-visible auth flows (OAuth, CAPTCHA)
- You specifically need persistent `~/.agent-browser-profile` cookies

**Always pass `--profile`** — without it, sessions are empty and useless.

```bash
agent-browser --profile ~/.agent-browser-profile navigate "https://target.com"
agent-browser --profile ~/.agent-browser-profile snapshot
agent-browser --profile ~/.agent-browser-profile close
```

If agent-browser also fails, report the error to the user. Do not retry indefinitely.
