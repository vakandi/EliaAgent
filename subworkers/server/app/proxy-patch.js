/**
 * proxy-patch.js — Preloaded before `opencode serve` to intercept provider `fetch`.
 *
 * Production version (elia-subworker-srv). Proves per-session proxy works WITHOUT
 * the plugin system. It does NOT use `shell.env` (useless for LLM) — it patches
 * `globalThis.fetch` with Bun's per-request `init.proxy` and learns `sessionID`
 * from the proxy map written by the runner:
 *
 *   1. File map written by the runner: /data/proxy-map.json { sessionID: proxyUrl }
 *   2. Fallback round-robin per fetch (proves proxy itself works even without session)
 *
 * No plugin hooks. No forward proxy. The runner writes /data/proxy-map.json before
 * each send_message; this patch reads it per fetch and routes the session's LLM
 * egress through its assigned proxy.
 *
 * Loaded via: `bun --preload /app/proxy-patch.js /tmp/opencode-src/packages/opencode/src/index.ts serve`
 */

// --- Load proxy pool ---
import { readFileSync, existsSync } from "node:fs";

let pool = [];
let rrIdx = 0;

function loadPool() {
  try {
    const txt = readFileSync("/data/proxies.txt", "utf-8");
    pool = txt
      .split("\n")
      .map((l) => l.split("|")[0].trim())
      .filter(Boolean)
      .map((line) => {
        // IP:PORT:USER:PASS → http://USER:PASS@IP:PORT
        const [ip, port, user, pass] = line.split(":");
        if (!ip || !port || !user || !pass) return null;
        return `http://${user}:${pass}@${ip}:${port}`;
      })
      .filter(Boolean);
    console.log(`[proxy-patch] loaded pool size=${pool.length}`);
  } catch (e) {
    console.log(`[proxy-patch] pool load failed: ${e.message}`);
  }
}
loadPool();

function nextProxy() {
  if (!pool.length) return undefined;
  const p = pool[rrIdx % pool.length];
  rrIdx++;
  return p;
}

// Map sessionID → proxy (written by the runner before each send_message)
function getProxyForSession(sessionID) {
  if (!sessionID) return undefined;
  try {
    if (!existsSync("/data/proxy-map.json")) return undefined;
    const map = JSON.parse(readFileSync("/data/proxy-map.json", "utf-8"));
    return map[sessionID];
  } catch {
    return undefined;
  }
}

// Try to extract sessionID from the current async context if available
function currentSessionID() {
  // 1) explicit global set by the runner before fetch
  if (globalThis.__currentSessionID) return globalThis.__currentSessionID;
  // 2) AsyncLocalStorage if available (opencode may not preserve it, but we try)
  try {
    return globalThis.__als?.getStore?.()?.sessionID;
  } catch {}
  return undefined;
}

// --- Patch fetch ---
const origFetch = globalThis.fetch;
let patchedCalls = 0;

globalThis.fetch = async function patchedFetch(input, init = {}) {
  const urlStr =
    typeof input === "string" ? input : input instanceof URL ? input.href : input?.url ?? "";
  // Never proxy local TUI↔server
  if (urlStr) {
    try {
      const u = new URL(urlStr);
      if (u.hostname === "localhost" || u.hostname === "127.0.0.1" || u.hostname === "::1") {
        return origFetch(input, init);
      }
    } catch {}
  }

  // Don't override if caller already set proxy
  if (!init.proxy) {
    const sid = currentSessionID();
    const perSession = sid ? getProxyForSession(sid) : undefined;
    const chosen = perSession ?? nextProxy();
    if (chosen) {
      init.proxy = chosen;
      patchedCalls++;
      // Log for verification (first 20 only to avoid spam)
      if (patchedCalls <= 20) {
        console.log(
          `[proxy-patch] fetch #${patchedCalls} url=${urlStr.slice(0, 80)} sid=${sid ?? "none"} proxy=${chosen.slice(0, 35)}...`
        );
      }
    }
  }

  return origFetch(input, init);
};

console.log("[proxy-patch] installed, origFetch preserved, pool size", pool.length);

// Also patch WebSocket for completeness (wss:// Responses API)
const OrigWS = globalThis.WebSocket;
if (OrigWS) {
  globalThis.WebSocket = class extends OrigWS {
    constructor(url, opts) {
      const sid = currentSessionID();
      const perSession = sid ? getProxyForSession(sid) : undefined;
      const chosen = perSession ?? (pool.length ? pool[0] : undefined);
      if (chosen && typeof url === "string" && url.startsWith("ws")) {
        opts = { ...(opts ?? {}), proxy: chosen };
        console.log(`[proxy-patch] WS sid=${sid ?? "none"} proxy=${String(chosen).slice(0, 35)}`);
      }
      super(url, opts);
    }
  };
  console.log("[proxy-patch] WebSocket patched");
}

// Expose helpers for the runner / debugging
globalThis.__proxyPatch = {
  nextProxy,
  getProxyForSession,
  currentSessionID,
  poolSize: () => pool.length,
  calls: () => patchedCalls,
};
export function Plugin() {
  console.log("[proxy-patch] Plugin() called");
}
