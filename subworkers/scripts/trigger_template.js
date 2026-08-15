#!/usr/bin/env node
import { execSync, spawn } from "node:child_process";
import { appendFileSync, existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync } from "node:fs";
import { homedir, tmpdir } from "node:os";
import { join } from "node:path";
import { createConnection } from "node:net";

const AGENT_DIR = join(homedir(), "EliaAI");
const SESSION_REUSE_COOLDOWN_MS = 20_000;
const SESSION_REUSE_MAX_COOLDOWN_MS = 60_000;
const RETRY_BACKOFF_MIN_MS = 20_000;
const RETRY_BACKOFF_MAX_MS = 40_000;
const RECOVERY_RESEND_MAX_ATTEMPTS = 6;

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = { force: false, retry: 2, timeout: 30, agent: "CHANGE_ME", prompt: null, model: null };
  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case "--force": opts.force = true; break;
      case "--retry": opts.retry = parseInt(args[++i], 10) || 2; break;
      case "--timeout": opts.timeout = parseInt(args[++i], 10) || 30; break;
      case "--agent": opts.agent = args[++i] || "CHANGE_ME"; break;
      case "--prompt": opts.prompt = args[++i] || null; break;
      case "--model": opts.model = args[++i] || null; break;
    }
  }
  return opts;
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function which(name) {
  try {
    return execSync(`which ${name}`, { encoding: "utf-8" }).trim();
  } catch {
    const dirs = [
      join(homedir(), ".bun/bin"),
      join(homedir(), ".opencode/bin"),
      "/opt/homebrew/bin",
      "/usr/local/bin",
    ];
    if (name === "opencode") {
      const nvmBase = join(homedir(), ".nvm/versions/node");
      if (existsSync(nvmBase)) {
        readdirSync(nvmBase)
          .filter((v) => v.startsWith("v"))
          .reverse()
          .forEach((v) => dirs.unshift(join(nvmBase, v, "bin")));
      }
    }
    for (const d of dirs) {
      const p = join(d, name);
      if (existsSync(p)) {
        process.env.PATH = `${d}:${process.env.PATH}`;
        return p;
      }
    }
    return null;
  }
}

function checkPort(port) {
  return new Promise((resolve) => {
    const sock = createConnection(port, "127.0.0.1");
    const done = (val) => { try { sock.destroy(); } catch {} resolve(val); };
    sock.on("connect", () => done(true));
    sock.on("error", () => done(false));
    sock.setTimeout(500, () => done(false));
  });
}

class Trigger {
  constructor(opts) {
    this.force = opts.force;
    this.maxRetries = opts.retry;
    this.watchdogMin = opts.timeout;
    this.agentName = opts.agent;
    this.promptOverride = opts.prompt;
    this.modelOverride = opts.model;
    this.agentId = this.agentName.replace(/_/g, "-");

    this.subworkerDir = join(AGENT_DIR, "subworkers", this.agentId);
    this.workspaceDir = join(this.subworkerDir, "workspace");
    this.logDir = join(AGENT_DIR, "subworkers", "logs");
    this.aggregateLog = join(this.logDir, `${this.agentName}.log`);
    this.runsDir = join(this.logDir, "runs", this.agentName);
    const now = new Date();
    this.ts = `${now.getFullYear()}${String(now.getMonth()+1).padStart(2,"0")}${String(now.getDate()).padStart(2,"0")}_${String(now.getHours()).padStart(2,"0")}${String(now.getMinutes()).padStart(2,"0")}${String(now.getSeconds()).padStart(2,"0")}`;
    this.runLog = join(this.runsDir, `${this.ts}.log`);
    this.activeRunLog = this.runLog;
    this.spawnedServerPid = null;
    this.opencodeSandboxRoot = mkdtempSync(join(tmpdir(), `subworkers-opencode-${this.agentName}-`));
    this.opencodeDataHome = join(this.opencodeSandboxRoot, "data");
    this.opencodeCacheHome = join(this.opencodeSandboxRoot, "cache");
    this.opencodeStateHome = join(this.opencodeSandboxRoot, "state");
    this.proxyEnv = {};
    mkdirSync(this.opencodeDataHome, { recursive: true });
    mkdirSync(this.opencodeCacheHome, { recursive: true });
    mkdirSync(this.opencodeStateHome, { recursive: true });

    mkdirSync(this.runsDir, { recursive: true });
    mkdirSync(this.workspaceDir, { recursive: true });
    mkdirSync(join(this.workspaceDir, "docs", new Date().toISOString().slice(0, 10)), { recursive: true });
    this.log(`[SANDBOX] OpenCode sandbox root: ${this.opencodeSandboxRoot}`);
  }

  readSessionIdFromLog(runLogPath) {
    if (!existsSync(runLogPath)) return null;
    try {
      const text = readFileSync(runLogPath, "utf-8");
      const matches = text.matchAll(/\bSession(?: ID)?:\s*(ses_[A-Za-z0-9_-]+)/gi);
      let latest = null;
      for (const match of matches) {
        latest = match[1] || latest;
      }
      return latest;
    } catch {
      return null;
    }
  }

  collectRecoveryCandidates(attempt) {
    const candidates = [];
    for (let i = attempt - 1; i >= 1; i--) {
      candidates.push(join(this.runsDir, `${this.ts}${i === 1 ? "" : `_retry${i - 1}`}.log`));
    }
    return candidates;
  }

  describeExitCode(exitCode) {
    if (exitCode === 0) return "success";
    if (exitCode === 124) return "watchdog timeout / killed";
    if (exitCode === 137) return "SIGKILL / external kill";
    return `exit ${exitCode}`;
  }

  async waitWithLog(ms, reason) {
    const seconds = Math.round(ms / 1000);
    this.log(`${reason} — waiting ${seconds}s`);
    await sleep(ms);
    this.log(`${reason} — wait finished`);
  }

  async waitWithHeartbeat(ms, reason) {
    const stepMs = 10_000;
    let remainingMs = ms;
    while (remainingMs > 0) {
      const chunkMs = Math.min(stepMs, remainingMs);
      await sleep(chunkMs);
      remainingMs -= chunkMs;
      if (remainingMs > 0) {
        this.log(`${reason} — ${Math.round(remainingMs / 1000)}s remaining`);
      }
    }
  }

  getRecoveryRetryDelayMs(recoveryAttempt) {
    const retryIndex = Math.max(1, recoveryAttempt - 1);
    return Math.min(
      SESSION_REUSE_COOLDOWN_MS + ((retryIndex - 1) * 10_000),
      SESSION_REUSE_MAX_COOLDOWN_MS,
    );
  }

  getRetryBackoffMs() {
    const min = RETRY_BACKOFF_MIN_MS;
    const max = RETRY_BACKOFF_MAX_MS;
    return Math.floor(min + (Math.random() * (max - min)));
  }

  async resumeExistingSession(runLog, sessionId, sourceLog) {
    let exitCode = 1;
    let validated = false;
    let resumeBlockedByActiveSession = false;

    for (let recoveryAttempt = 1; recoveryAttempt <= RECOVERY_RESEND_MAX_ATTEMPTS; recoveryAttempt++) {
      if (recoveryAttempt > 1) {
        const retryDelayMs = this.getRecoveryRetryDelayMs(recoveryAttempt);
        await this.waitWithLog(
          retryDelayMs,
          `[RECOVERY] Reattempting same session ${sessionId} (attempt ${recoveryAttempt}/${RECOVERY_RESEND_MAX_ATTEMPTS}, delay=${Math.round(retryDelayMs / 1000)}s)`
        );
      }

      this.log(`[RECOVERY] Reusing session ${sessionId} with continuation prompt`);
      this.log(`[RECOVERY] Dispatching continuation prompt to session ${sessionId}: "continue the work"`);
      exitCode = this.mode === "loop"
        ? await this.runLoopMode(runLog, sessionId)
        : await this.runTaskMode("continue the work", runLog, sessionId);
      this.log(`[RECOVERY] Continuation dispatch returned exit_code=${exitCode} (${this.describeExitCode(exitCode)}) for session ${sessionId}`);

      resumeBlockedByActiveSession = this.isResumeBlockedByActiveSession(runLog);
      validated = exitCode === 0 && this.validateRun(runLog);
      this.log(`[RECOVERY] Reuse result: blockedByActive=${resumeBlockedByActiveSession}, validated=${validated}`);

      if (validated) {
        this.log(`[RECOVERY] Continuation prompt accepted for session ${sessionId}`);
        return { exitCode, validated, resumeBlockedByActiveSession, sessionId, sourceLog };
      }

      if (resumeBlockedByActiveSession) {
        this.log(
          `[RECOVERY] Session ${sessionId} is still active; keeping the same session and retrying after cooldown`
        );
      } else {
        this.log(`[RECOVERY] Resume attempt did not validate — keeping the same session for another retry (reason=${this.describeExitCode(exitCode)})`);
      }
    }

    this.log(
      `[RECOVERY] Exhausted same-session retries for ${sessionId} without validation; leaving fallback decision to the outer retry loop`
    );
    return { exitCode, validated, resumeBlockedByActiveSession, sessionId, sourceLog };
  }

  log(msg, target) {
    const line = `[${new Date().toISOString().replace("T", " ").slice(0, 19)}] ${msg}`;
    console.log(line);
    appendFileSync(this.aggregateLog, line + "\n");
    appendFileSync(target || this.activeRunLog || this.runLog, line + "\n");
  }

  buildEnv() {
    return {
      ...process.env,
      XDG_DATA_HOME: this.opencodeDataHome,
      XDG_CACHE_HOME: this.opencodeCacheHome,
      XDG_STATE_HOME: this.opencodeStateHome,
      ...this.proxyEnv,
      OPENCODE_DISABLE_AUTOUPDATE: "1",
      OPENCODE_DISABLE_MODELS_FETCH: "1",
    };
  }

  refreshProxy() {
    if (!this.useProxy) return;

    const switchProxyScript = join(AGENT_DIR, "setup", "switch-proxy.sh");
    if (!existsSync(switchProxyScript)) {
      this.log(`[PROXY] switch-proxy.sh not found at ${switchProxyScript}`);
      return;
    }

    this.log(`[PROXY] Refreshing proxy via ${switchProxyScript}`);
    const output = execSync(`/bin/bash "${switchProxyScript}"`, {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"],
      cwd: AGENT_DIR,
    });
    if (output.trim()) {
      for (const line of output.trim().split("\n")) {
        this.log(`[PROXY] ${line}`);
      }
    }

    const proxyConf = join(homedir(), ".proxychains.conf");
    let proxyLine = null;
    try {
      const content = readFileSync(proxyConf, "utf8");
      proxyLine = content.split("\n").find((line) => {
        const trimmed = line.trim();
        return trimmed && !trimmed.startsWith("#") && trimmed.startsWith("http ");
      }) ?? null;
    } catch (error) {
      this.log(`[PROXY] Failed to read ${proxyConf}: ${error instanceof Error ? error.message : String(error)}`);
    }

    if (!proxyLine) {
      this.log("[PROXY] No proxy line found after refresh; continuing without proxy env overrides");
      return;
    }

    const parts = proxyLine.trim().split(/\s+/);
    if (parts.length < 5) {
      this.log(`[PROXY] Unexpected proxy line format: ${proxyLine}`);
      return;
    }

    const [, ip, port, user, pass] = parts;
    const proxyUrl = `http://${user}:${pass}@${ip}:${port}`;
    this.proxyEnv = {
      HTTP_PROXY: proxyUrl,
      HTTPS_PROXY: proxyUrl,
      http_proxy: proxyUrl,
      https_proxy: proxyUrl,
      NO_PROXY: "127.0.0.1,localhost,::1",
      no_proxy: "127.0.0.1,localhost,::1",
    };
    this.log(`[PROXY] Proxy refreshed for run: ${ip}:${port}`);
  }

  resolveBinaries() {
    const localOmoBin = join(AGENT_DIR, "setup", "oh-my-openagent", "bin", "oh-my-opencode.js");
    if (existsSync(localOmoBin)) {
      this.omoBin = localOmoBin;
      this.log(`[BIN] Using repo-local oh-my-opencode at ${this.omoBin}`);
    } else {
      this.omoBin = which("oh-my-opencode");
    }
    if (!this.omoBin) { this.log("FATAL: oh-my-opencode not found"); process.exit(1); }
    this.log(`[BIN] Using oh-my-opencode=${this.omoBin}`);
    this.opencodeBin = which("opencode");
    if (!this.opencodeBin) { this.log("FATAL: opencode not found"); process.exit(1); }
    this.log(`[BIN] Using opencode=${this.opencodeBin}`);
  }

  checkEnabled() {
    const flag = join(this.subworkerDir, ".enabled");
    if (this.force) {
      this.log("[FORCE] Bypassing .enabled check");
    } else if (!existsSync(flag)) {
      this.log(`${this.agentId} skipped (.enabled not found). Use --force to bypass.`);
      process.exit(0);
    }
  }

  loadPrompt() {
    if (this.promptOverride) return this.promptOverride;
    const file = join(this.subworkerDir, "PROMPT.md");
    if (!existsSync(file)) { this.log(`ERROR: PROMPT.md not found at ${file}`); process.exit(1); }
    return readFileSync(file, "utf-8");
  }

  detectMode() {
    this.mode = existsSync(join(this.subworkerDir, ".loop_mode")) ? "loop" : "task";
    this.log(`Mode: ${this.mode}`);
  }

  detectProxy() {
    this.useProxy = process.env.USE_PROXY_ENV === "1" || existsSync(join(AGENT_DIR, ".proxy_enabled"));
    if (this.useProxy) this.log("[PROXY] Proxy mode enabled");
  }

  runCommand(cmd, args, runLogPath) {
    return new Promise((resolve) => {
      const watchdogMs = this.watchdogMin * 60_000;
      let killed = false;

      const proc = spawn(cmd, args, {
        cwd: AGENT_DIR,
        stdio: ["ignore", "pipe", "pipe"],
        detached: true,
        env: this.buildEnv(),
      });

      proc.stdout.on("data", (chunk) => {
        appendFileSync(runLogPath, chunk);
        appendFileSync(this.aggregateLog, chunk);
      });
      proc.stderr.on("data", (chunk) => {
        appendFileSync(runLogPath, chunk);
        appendFileSync(this.aggregateLog, chunk);
      });

      const timer = setTimeout(() => {
        killed = true;
        this.log(`[WATCHDOG] Exceeded ${this.watchdogMin}m — killing PID ${proc.pid}`);
        try { process.kill(-proc.pid, "SIGKILL"); } catch {}
      }, watchdogMs);

      proc.on("close", (code) => {
        clearTimeout(timer);
        resolve(killed ? 124 : (code ?? 1));
      });

      proc.on("error", (err) => {
        clearTimeout(timer);
        this.log(`SPAWN ERROR: ${err.message}`);
        resolve(1);
      });
    });
  }

  async runTaskMode(prompt, runLog, sessionId = null) {
    const args = ["run", "-d", this.workspaceDir, "-a", this.agentId];
    if (sessionId) args.push("--session-id", sessionId);
    if (this.modelOverride) args.push("--model", this.modelOverride);
    args.push(prompt);
    return this.runCommand(this.omoBin, args, runLog);
  }

  async runLoopMode(runLog, sessionId = null) {
    const port = 4096;
    if (!(await checkPort(port))) {
      this.log(`[SERVER] Starting server on port ${port}`);
      const serverCmd = this.useProxy
        ? ["proxychains4", "-f", `${homedir()}/.proxychains.conf`, "opencode", "serve", "--port", String(port)]
        : ["opencode", "serve", "--port", String(port)];
      const serverProc = spawn(serverCmd[0], serverCmd.slice(1), { detached: true, stdio: "ignore", env: { ...process.env, XDG_DATA_HOME: this.opencodeDataHome, XDG_CACHE_HOME: this.opencodeCacheHome, XDG_STATE_HOME: this.opencodeStateHome, OPENCODE_DISABLE_AUTOUPDATE: "1", OPENCODE_DISABLE_MODELS_FETCH: "1" } });
      this.spawnedServerPid = serverProc.pid ?? null;
      serverProc.unref();
      await sleep(3000);
    } else {
      this.log(`[SERVER] Running on port ${port} — attaching`);
    }
    const loopCmd = existsSync(join(AGENT_DIR, ".ralph_mode")) ? "/ralph-loop" : "/ulw-loop";
    this.log(`Loop: ${loopCmd}`);
    const args = ["run", "--attach", `http://127.0.0.1:${port}`, "-d", this.workspaceDir, "-a", this.agentId];
    if (sessionId) args.push("--session-id", sessionId);
    if (this.modelOverride) args.push("--model", this.modelOverride);
    args.push(loopCmd);
    return this.runCommand(this.omoBin, args, runLog);
  }

  validateRun(runLog) {
    if (!existsSync(runLog)) return false;
    const text = readFileSync(runLog, "utf-8");
    if (!text.includes("All tasks completed")) {
      this.log("[VALIDATE] No completion marker — incomplete");
      return false;
    }
    const markers = ["→ Bash", "→ mcp-cli", "→ zernio", "→ Write", "→ Edit", "→ Web", "→ agent-browser", "→ glob", "→ grep"];
    const toolCalls = markers.reduce((s, m) => s + (text.split(m).length - 1), 0);
    if (toolCalls > 0) { this.log(`[VALIDATE] ${toolCalls} tool calls — valid`); return true; }
    if (text.split("\n").length > 100) { this.log("[VALIDATE] 100+ lines — likely valid"); return true; }
    this.log("[VALIDATE] No tool calls — false completion");
    return false;
  }

  isResumeBlockedByActiveSession(runLog) {
    if (!existsSync(runLog)) return false;
    try {
      const text = readFileSync(runLog, "utf-8");
      return text.includes("promptAsync skipped by gate: active") ||
        text.includes("Session is not idle");
    } catch {
      return false;
    }
  }

  async cleanupServers() {
    if (!this.spawnedServerPid) {
      this.log("[CLEANUP] Skipping cleanup; no owned loop server was spawned by this trigger");
      return;
    }

    try {
      this.log(`[CLEANUP] Killing owned loop server PID ${this.spawnedServerPid}`);
      try {
        process.kill(-this.spawnedServerPid, "SIGKILL");
      } catch {
        process.kill(this.spawnedServerPid, "SIGKILL");
      }
      await sleep(1000);
    } catch (error) {
      this.log(`[CLEANUP] Owned loop server cleanup failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  async execute() {
    this.resolveBinaries();
    this.log(`Starting ${this.agentId} trigger... (max_retries=${this.maxRetries}, watchdog=${this.watchdogMin}m)`);
    this.checkEnabled();
    const prompt = this.loadPrompt();
    this.detectMode();
    this.detectProxy();
    if (this.useProxy) this.refreshProxy();

    let exitCode = 0;
    for (let attempt = 1; attempt <= this.maxRetries + 1; attempt++) {
      const runLog = attempt === 1 ? this.runLog : join(this.runsDir, `${this.ts}_retry${attempt - 1}.log`);
      this.activeRunLog = runLog;
      if (attempt > 1) this.log(`Retry ${attempt - 1}/${this.maxRetries} — attempt ${attempt}`);

      const runStart = Date.now();
      const previousRunLog = attempt > 1 ? (attempt === 2 ? this.runLog : join(this.runsDir, `${this.ts}_retry${attempt - 2}.log`)) : null;
      let recoveredSessionId = null;
      let recoveredSessionSource = null;
      let validated = false;
      let resumeBlockedByActiveSession = false;

      if (attempt > 1) {
        const candidates = this.collectRecoveryCandidates(attempt);
        this.log(`[RECOVERY] Previous run log: ${previousRunLog || "n/a"}`);
        this.log(`[RECOVERY] Recovery candidates: ${candidates.join(" -> ")}`);
        for (const candidate of candidates) {
          const sessionId = this.readSessionIdFromLog(candidate);
          if (sessionId) {
            recoveredSessionId = sessionId;
            recoveredSessionSource = candidate;
            break;
          }
        }
        this.log(`[RECOVERY] Session lookup result: ${recoveredSessionId || "none found"}`);
        if (recoveredSessionSource) {
          this.log(`[RECOVERY] Session source: ${recoveredSessionSource}`);
        }
      }

      if (attempt > 1 && recoveredSessionId) {
        await this.waitWithLog(
          SESSION_REUSE_COOLDOWN_MS,
          `[RECOVERY] Cooling down before reusing session ${recoveredSessionId}`
        );
        const recoveryResult = await this.resumeExistingSession(runLog, recoveredSessionId, recoveredSessionSource || previousRunLog || runLog);
        exitCode = recoveryResult.exitCode;
        validated = recoveryResult.validated;
        resumeBlockedByActiveSession = recoveryResult.resumeBlockedByActiveSession;
        if (!validated && !resumeBlockedByActiveSession) {
          this.log(`[RECOVERY] Resume attempts exhausted for session ${recoveredSessionId}; falling back to a fresh session`);
        }
      } else if (attempt > 1) {
        this.log("[RECOVERY] No reusable session id found in any prior log; skipping continuation path");
      }

      if (!(attempt > 1 && recoveredSessionId && (validated || resumeBlockedByActiveSession))) {
        if (attempt > 1 && recoveredSessionId) {
          this.log("[RECOVERY] Starting fresh session after reuse path");
        }
        exitCode = this.mode === "loop"
          ? await this.runLoopMode(runLog)
          : await this.runTaskMode(prompt, runLog);
        validated = exitCode === 0 && this.validateRun(runLog);
      }

      const duration = Math.round((Date.now() - runStart) / 1000);
      this.log(`Run completed: exit_code=${exitCode} duration=${duration}s attempt=${attempt}`, runLog);

      if (validated) {
        this.log("Run validated successfully", runLog);
        break;
      }
      if (attempt <= this.maxRetries) {
        const retryBackoffMs = this.getRetryBackoffMs();
        this.log(`Will retry in ${Math.round(retryBackoffMs / 1000)}s...`);
        await this.waitWithHeartbeat(retryBackoffMs, "[RETRY]");
        if (this.mode === "loop" && !resumeBlockedByActiveSession) await this.cleanupServers();
      }
    }

    if (this.mode === "loop") await this.cleanupServers();
    this.log(`EOF_SUBWORKER_EXIT:${exitCode}`);
    return exitCode;
  }
}

const trigger = new Trigger(parseArgs());
const code = await trigger.execute();
process.exit(code);
