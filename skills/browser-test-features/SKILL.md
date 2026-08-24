---
name: browser-test-features
description: >-
  Live-test deployed features using parallel-browser-mcp with JavaScript-first approach
  and network debugging. Use this skill whenever the user says "test live", "test the
  deploy", "check the site", "verify it works", "browse it", "screenshot it", "open
  the URL", "see if it works", "test the feature", "check the frontend", or any
  request to visually verify a deployed website or web app. Also trigger when the
  user just finished building something and wants to see it in a real browser — even
  if they say "let me see" or "show me" referring to a URL.
---

# Browser Test Features

Test deployed web apps live using parallel-browser-mcp. JavaScript-first for speed,
network interception on every action for API debugging, code inspection for solutions.

## Core Principle

**JavaScript is faster than Playwright selectors.** Always prefer `browser_evaluate`
for filling forms, clicking, reading state, and extracting data. Use Playwright
tools only for initial navigation and screenshots.

## Workflow

### 1. Setup + Network Interception

```
start_session(provider: "playwright")
navigate(url)
browser_evaluate: intercept all network requests
```

Inject network monitoring ONCE after navigation — it captures everything:

```js
// Inject network interceptor — runs once per page load
window.__api_log = [];
const origFetch = window.fetch;
window.fetch = async (...args) => {
  const [url, opts] = args;
  const start = Date.now();
  const entry = { url: typeof url === 'string' ? url : url.url, method: opts?.method || 'GET', status: null, duration: null, body: null, response: null };
  try {
    const res = await origFetch(...args);
    entry.status = res.status;
    entry.duration = Date.now() - start;
    const clone = res.clone();
    try { entry.response = await clone.json(); } catch { entry.response = await clone.text().catch(() => ''); }
    window.__api_log.push(entry);
    return res;
  } catch (e) {
    entry.duration = Date.now() - start;
    entry.error = e.message;
    window.__api_log.push(entry);
    throw e;
  }
};
'network interceptor installed';
```

Also intercept XMLHttpRequest:

```js
const origOpen = XMLHttpRequest.prototype.open;
const origSend = XMLHttpRequest.prototype.send;
XMLHttpRequest.prototype.open = function(method, url) {
  this.__log = { method, url, status: null, duration: null };
  return origOpen.apply(this, arguments);
};
XMLHttpRequest.prototype.send = function() {
  const start = Date.now();
  this.addEventListener('load', () => {
    this.__log.status = this.status;
    this.__log.duration = Date.now() - start;
    try { this.__log.response = JSON.parse(this.responseText); } catch { this.__log.response = this.responseText; }
    window.__api_log.push(this.__log);
  });
  return origSend.apply(this, arguments);
};
'xhr interceptor installed';
```

### 2. Test the Feature

Use `browser_evaluate` for all interactions. Examples:

**Fill a form:**
```js
document.querySelector('input[name="email"]').value = 'test@example.com';
document.querySelector('input[name="email"]').dispatchEvent(new Event('input', {bubbles: true}));
document.querySelector('input[name="password"]').value = 'testpass123';
document.querySelector('input[name="password"]').dispatchEvent(new Event('input', {bubbles: true}));
document.querySelector('form').dispatchEvent(new Event('submit', {bubbles: true}));
'form submitted';
```

**React state (controlled inputs):**
```js
const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
const input = document.querySelector('input[name="email"]');
nativeInputValueSetter.call(input, 'test@example.com');
input.dispatchEvent(new Event('input', {bubbles: true}));
'done';
```

**Click a button:**
```js
document.querySelector('button[type="submit"]').click();
'clicked';
```

**Read page state:**
```js
JSON.stringify({
  url: location.href,
  title: document.title,
  bodyText: document.body?.innerText?.substring(0, 500),
  localStorage: Object.fromEntries(Object.keys(localStorage).map(k => [k, localStorage.getItem(k)?.substring(0, 200)]))
});
```

**Check for error elements:**
```js
document.querySelector('.error, .alert-error, [role="alert"], .text-red-500')?.textContent || 'no errors visible';
```

### 3. Debug API Calls After Each Interaction

After every significant action (submit, click, navigation), pull the network log:

```js
JSON.stringify(window.__api_log.filter(e => !e.url.includes('analytics') && !e.url.includes('favicon')), null, 2);
```

Check for:
- **Non-2xx status** — 400, 401, 403, 404, 500 errors
- **CORS errors** — look for "Failed to fetch" or TypeError
- **Missing requests** — expected API call that never fired
- **Wrong payloads** — check request body vs what backend expects
- **Slow responses** — duration > 2000ms worth investigating

If issues found, reset the log and test again:
```js
window.__api_log = [];
'log cleared';
```

### 4. Screenshot at Key Moments

Take screenshots:
- After page load (initial state)
- After form submit (success/error state)
- After navigation (new page loaded)
- After any visual change

### 5. Inspect Code for Solutions

When an issue is found during testing, **read the relevant source code** to propose a fix:

1. Identify the failing endpoint from the network log (e.g., `POST /api/auth/login` returning 400)
2. Use `codegraph_explore` or `grep` to find the backend handler for that route
3. Read the handler code to understand what it expects
4. Compare with what the frontend sent (from `__api_log`)
5. Propose the exact fix in the report

### 6. Final Report

After testing, ALWAYS produce a structured report:

```markdown
## Test Report — [Feature Name] — [URL]

### Summary
- Total actions tested: X
- Issues found: X
- API calls monitored: X

### Issues Found

#### Issue 1: [Short title]
- **What:** What happened vs what was expected
- **API call:** `METHOD /path` → status XXX
- **Request payload:** `{ ... }`
- **Response:** `{ ... }`
- **Screenshot:** [reference]
- **Root cause:** [from code inspection]
- **Proposed fix:** [exact code change, file path, line numbers]

#### Issue 2: ...

### Working Features
- [List of things that work correctly]

### Network Summary
| Endpoint | Method | Status | Duration | Issue |
|----------|--------|--------|----------|-------|
| /api/auth/login | POST | 200 | 340ms | — |
| /api/users/me | GET | 401 | 12ms | Token missing |
```

## Quick Reference

| Task | Tool | Example |
|------|------|---------|
| Navigate | `browser_navigate` | `parallel-browser-mcp_browser_navigate(sessionId, url)` |
| Screenshot | `browser_screenshot` | `parallel-browser-mcp_browser_screenshot(sessionId)` |
| JS eval | `browser_evaluate` | `parallel-browser-mcp_browser_evaluate(sessionId, script)` |
| Fill form | `browser_evaluate` | JS to set values + dispatch events |
| Click | `browser_evaluate` | `document.querySelector('btn').click()` |
| Check DOM | `browser_dom_query` | `parallel-browser-mcp_browser_dom_query(sessionId, selector)` |
| Read layout | `browser_get_page_structure` | `parallel-browser-mcp_browser_get_page_structure(sessionId)` |
| Check network | `browser_evaluate` | Read `window.__api_log` |
| Page structure | `browser_snapshot` | `parallel-browser-mcp_browser_snapshot(sessionId)` |

## Tips

- Always install the network interceptor right after first navigation — don't wait.
- Reset `__api_log = []` before each test phase to keep logs clean.
- For React/Next.js apps, use the native input value setter pattern for controlled inputs.
- For form validation, test both valid AND invalid inputs to check error handling.
- If testing auth, check that tokens are stored (localStorage/cookies) and sent in headers.
- For SPAs, test route transitions — navigate via JS, not full page reloads.
- Always close the session at the end: `parallel-browser-mcp_close_session`.
