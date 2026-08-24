#!/usr/bin/env node
import { execSync, spawn } from "node:child_process";
import { appendFileSync, existsSync, mkdirSync, readFileSync, readdirSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { createConnection } from "node:net";

const AGENT_DIR = join(homedir(), "EliaAI");

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
    this.mainAgentName = this.readMainAgentName();
    this.isMainAgent = this.agentId === this.mainAgentName;
    this.workspaceDir = this.isMainAgent ? AGENT_DIR : join(this.subworkerDir, "workspace");
    this.logDir = join(AGENT_DIR, "subworkers", "logs");
    this.aggregateLog = join(this.logDir, `${this.agentName}.log`);
    this.runsDir = join(this.logDir, "runs", this.agentName);
    const now = new Date();
    this.ts = `${now.getFullYear()}${String(now.getMonth()+1).padStart(2,"0")}${String(now.getDate()).padStart(2,"0")}_${String(now.getHours()).padStart(2,"0")}${String(now.getMinutes()).padStart(2,"0")}${String(now.getSeconds()).padStart(2,"0")}`;
    this.runLog = join(this.runsDir, `${this.ts}.log`);

    mkdirSync(this.runsDir, { recursive: true });
    mkdirSync(this.workspaceDir, { recursive: true });
    if (!this.isMainAgent) {
      mkdirSync(join(this.workspaceDir, "docs", new Date().toISOString().slice(0, 10)), { recursive: true });
    }
  }

  readMainAgentName() {
    try {
      const p = join(AGENT_DIR, "subworkers", "main-agent.json");
      if (!existsSync(p)) return "elia";
      const d = JSON.parse(readFileSync(p, "utf-8"));
      if (d && typeof d.name === "string" && d.name) return d.name;
    } catch {}
    return "elia";
  }

  log(msg, target) {
    const line = `[${new Date().toISOString().replace("T", " ").slice(0, 19)}] ${msg}`;
    console.log(line);
    appendFileSync(this.aggregateLog, line + "\n");
    appendFileSync(target || this.runLog, line + "\n");
  }

  resolveBinaries() {
    this.omoBin = which("oh-my-opencode");
    if (!this.omoBin) { this.log("FATAL: oh-my-opencode not found"); process.exit(1); }
    this.opencodeBin = which("opencode");
    if (!this.opencodeBin) { this.log("FATAL: opencode not found"); process.exit(1); }
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

  loadModelSelection() {
    if (this.modelOverride) return;
    try {
      const p = join(AGENT_DIR, "ui_electron", "model-selections.json");
      if (!existsSync(p)) return;
      const sel = JSON.parse(readFileSync(p, "utf-8"));
      if (sel && typeof sel === "object" && typeof sel[this.agentName] === "string" && sel[this.agentName]) {
        this.modelOverride = sel[this.agentName];
        this.log(`[MODEL] Using ${this.modelOverride} from model-selections.json`);
      }
    } catch (e) {
      this.log(`[MODEL] load error: ${e.message}`);
    }
  }

  runCommand(cmd, args, runLogPath) {
    return new Promise((resolve) => {
      const watchdogMs = this.watchdogMin * 60_000;
      let killed = false;

      const proc = spawn(cmd, args, {
        cwd: AGENT_DIR,
        stdio: ["ignore", "pipe", "pipe"],
        detached: true,
        env: { ...process.env },
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

  async runTaskMode(prompt, runLog) {
    const args = ["run", "-d", this.workspaceDir, "-a", this.agentId];
    if (this.modelOverride) args.push("--model", this.modelOverride);
    args.push(prompt);
    return this.runCommand(this.omoBin, args, runLog);
  }

  async runLoopMode(runLog) {
    const port = 4096;
    if (!(await checkPort(port))) {
      this.log(`[SERVER] Starting server on port ${port}`);
      const serverCmd = this.useProxy
        ? ["proxychains4", "-f", `${homedir()}/.proxychains.conf`, "opencode", "serve", "--port", String(port)]
        : ["opencode", "serve", "--port", String(port)];
      spawn(serverCmd[0], serverCmd.slice(1), { detached: true, stdio: "ignore", env: { ...process.env } }).unref();
      await sleep(3000);
    } else {
      this.log(`[SERVER] Running on port ${port} — attaching`);
    }
    const loopCmd = existsSync(join(AGENT_DIR, ".ralph_mode")) ? "/ralph-loop" : "/ulw-loop";
    this.log(`Loop: ${loopCmd}`);
    const args = ["run", "--attach", `http://127.0.0.1:${port}`, "-d", this.workspaceDir, "-a", this.agentId];
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

  async cleanupServers() {
    for (const port of [4096, 4097, 4098, 4099, 4100]) {
      try {
        const pids = execSync(`lsof -ti:${port}`, { encoding: "utf-8" }).trim();
        if (pids) {
          this.log(`[CLEANUP] Killing orphaned server(s) on port ${port}: ${pids}`);
          for (const pid of pids.split(/\s+/)) { try { process.kill(parseInt(pid), 9); } catch {} }
          await sleep(1000);
        }
      } catch {}
    }
  }

  async execute() {
    this.resolveBinaries();
    this.log(`Starting ${this.agentId} trigger... (max_retries=${this.maxRetries}, watchdog=${this.watchdogMin}m)`);
    this.checkEnabled();
    const prompt = this.loadPrompt();
    this.detectMode();
    this.detectProxy();
    this.loadModelSelection();

    let exitCode = 0;
    for (let attempt = 1; attempt <= this.maxRetries + 1; attempt++) {
      const runLog = attempt === 1 ? this.runLog : join(this.runsDir, `${this.ts}_retry${attempt - 1}.log`);
      if (attempt > 1) this.log(`Retry ${attempt - 1}/${this.maxRetries} — attempt ${attempt}`);

      const runStart = Date.now();
      exitCode = this.mode === "loop"
        ? await this.runLoopMode(runLog)
        : await this.runTaskMode(prompt, runLog);

      const duration = Math.round((Date.now() - runStart) / 1000);
      this.log(`Run completed: exit_code=${exitCode} duration=${duration}s attempt=${attempt}`, runLog);

      if (exitCode === 0 && this.validateRun(runLog)) {
        this.log("Run validated successfully", runLog);
        break;
      }
      if (attempt <= this.maxRetries) {
        this.log("Will retry in 5s...");
        await sleep(5000);
        if (this.mode === "task") await this.cleanupServers();
      }
    }

    if (this.mode === "task") await this.cleanupServers();
    this.log(`EOF_SUBWORKER_EXIT:${exitCode}`);
    return exitCode;
  }
}

const trigger = new Trigger(parseArgs());
const code = await trigger.execute();
process.exit(code);
