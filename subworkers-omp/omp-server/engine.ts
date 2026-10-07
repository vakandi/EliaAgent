/** Engine bridge — the sole omp dependency.
 * createAgentSession from ./packages/coding-agent/src/sdk.ts with per-run cwd,
 * agentDir, isolated EventBus. Session events normalized to text|reasoning|tool
 * frames (TopBar contract fixed; SDK names remapped here if they differ).
 */
import { existsSync, readFileSync, writeFileSync, mkdirSync, unlinkSync } from "node:fs";
import { join } from "node:path";
import type { EventBus as EventBusType } from "./packages/coding-agent/src/utils/event-bus.ts";
import type {
  CreateAgentSessionOptions,
  CreateAgentSessionResult,
} from "./packages/coding-agent/src/sdk.ts";

/** SDK handles resolved at runtime (values, not types). */
export interface SdkHandles {
  createAgentSession: (opts: CreateAgentSessionOptions) => Promise<CreateAgentSessionResult>;
  EventBus: new () => EventBusType;
}

// Host checkout holds `packages/...` beside this file; the image likewise
// holds `packages/...` beside it (WORKDIR tree).
// Try the sibling layout first, parent second — whichever module graph resolves wins.
const SDK_BASES = ["./packages/coding-agent/src", "../packages/coding-agent/src"];
const PRELUDES = ["tools/browser/prelude-definition.ts", "tools/computer/prelude-definition.ts"];

let sdkPromise: Promise<SdkHandles> | null = null;

/** Load the omp SDK from the first layout that resolves. Result cached. */
export function loadSdk(): Promise<SdkHandles> {
  if (!sdkPromise) {
    sdkPromise = (async () => {
      const errors: string[] = [];
      for (const base of SDK_BASES) {
        try {
          const sdkMod = await import(`${base}/sdk.ts`);
          const busMod = await import(`${base}/utils/event-bus.ts`);
          // Registry pre-warm (engine runs fail under Bun <=1.3.x without this):
          // browser.ts:158 and computer.ts:121 load these via synchronous
          // require(), which drops `with { type: "text" }` attributes. A static
          // ESM import honors them, so require() hits the warmed registry.
          await Promise.allSettled(PRELUDES.map((p) => import(`${base}/${p}`)));
          if (typeof sdkMod.createAgentSession !== "function" || typeof busMod.EventBus !== "function") {
            throw new Error("SDK shape mismatch");
          }
          return { createAgentSession: sdkMod.createAgentSession, EventBus: busMod.EventBus } as SdkHandles;
        } catch (err) {
          errors.push(`${base}: ${String(err).split("\n")[0]}`);
        }
      }
      throw new Error(`SDK unloadable in any known layout: ${errors.join(" | ")}`);
    })();
  }
  return sdkPromise;
}
import { appendFrame, upsertRun, getRun, nowIso } from "./store.ts";
import { emitRunLog, emitRunBanner, emitSubworkerCompleted } from "./ws.ts";
import { notify } from "./notifier.ts";
import { effectiveWorkspace, type SubworkerEntry } from "./auth.ts";
import { setRunKiller } from "./watchdog.ts";

const AGENT_DIR = `${process.env.HOME ?? process.env.USERPROFILE ?? ""}/.config/omp/agents`;

/** Live worker children by session — kill registry for watchdog/STOP. */
const liveChildren = new Map<string, { proc: ReturnType<typeof Bun.spawn> | null }>();

/** SIGKILL a live worker child + best-effort prompt cleanup. */
export function killRun(sessionId: string): boolean {
  const tracked = liveChildren.get(sessionId);
  if (!tracked || !tracked.proc) {
    if (tracked) liveChildren.delete(sessionId);
    return false;
  }
  try {
    tracked.proc.kill();
  } catch {
    // exited/dead guard
  }
  cleanupPromptFile(sessionId);
  liveChildren.delete(sessionId);
  return true;
}

setRunKiller(killRun);

function workspacePrompt(workspace: string, override?: string | null): string {
  if (override?.trim()) return override.trim();
  // workspace/ holds run outputs; PROMPT.md lives in the agent home (parent).
  for (const dir of [workspace, join(workspace, "..")]) {
    try {
      const promptPath = join(dir, "PROMPT.md");
      if (existsSync(promptPath)) return readFileSync(promptPath, "utf8");
    } catch {
      // try next
    }
  }
  return "Continue the tasks defined for this subworker.";
}

function touchRun(sessionId: string): void {
  const run = getRun(sessionId);
  if (run) upsertRun({ ...run, last_frame_at: nowIso() });
}

/** Read a string field off an unknown object with runtime narrowing. */
function strField(obj: object, key: string): string | null {
  if (key in obj) {
    const value: unknown = obj[key as keyof typeof obj];
    if (typeof value === "string") return value;
  }
  return null;
}

/** One TopBar-consumable frame. Field contract fixed; SDK names remapped here. */
export interface EngineFrame {
  field: "text" | "reasoning" | "tool";
  text: string;
}

export interface EngineStartOptions {
  entry: SubworkerEntry;
  sessionId: string;
  promptOverride?: string | null;
  modelOverride?: string | null;
  variantOverride?: string | null;
}

/** Non-empty trimmed string or null. */
function nonEmpty(value: unknown): string | null {
  return typeof value === "string" && value.length > 0 ? value : null;
}

/** Map one SDK session event to zero or more TopBar frames. TOTAL: every path returns an array. */
function eventToFrames(event: unknown): EngineFrame[] {
  if (!event || typeof event !== "object") return [];
  const type = strField(event, "type") ?? "";
  // Streaming deltas: the incremental payload lives in assistantMessageEvent
  // (message.content is cumulative — emitting it here would duplicate every
  // previous delta into the frame log). Map each sub-event kind to its field.
  if (type === "message_update") {
    if ("assistantMessageEvent" in event && event.assistantMessageEvent && typeof event.assistantMessageEvent === "object") {
      const sub = event.assistantMessageEvent;
      const subtype = strField(sub, "type") ?? "";
      if (subtype === "text_delta") {
        const d = "delta" in sub ? nonEmpty(sub.delta) : null;
        return d ? [{ field: "text", text: d }] : [];
      }
      if (subtype === "text_end") {
        const d = "content" in sub ? nonEmpty(sub.content) : null;
        return d ? [{ field: "text", text: d }] : [];
      }
      if (subtype === "thinking_delta") {
        const d = "delta" in sub ? nonEmpty(sub.delta) : null;
        return d ? [{ field: "reasoning", text: d }] : [];
      }
      if (subtype === "thinking_end") {
        const d = "content" in sub ? nonEmpty(sub.content) : null;
        return d ? [{ field: "reasoning", text: d }] : [];
      }
      if (subtype === "toolcall_end") {
        if ("toolCall" in sub && sub.toolCall && typeof sub.toolCall === "object") {
          const name = strField(sub.toolCall, "name");
          if (name) return [{ field: "tool", text: `▸ ${name}` }];
        }
        return [];
      }
      // start | text_start | thinking_start | toolcall_start | toolcall_delta |
      // image_end | done | error carry no incremental display text.
      return [];
    }
    return [];
  }
  if (type === "message" || type === "message_start" || type === "message_delta" || type === "message_end") {
    const holder: unknown =
      "message" in event && event.message && typeof event.message === "object"
        ? event.message
        : "delta" in event && event.delta && typeof event.delta === "object"
          ? event.delta
          : event;
    if (holder && typeof holder === "object" && "content" in holder) {
      const content: unknown = holder.content;
      if (typeof content === "string" && content.length > 0) {
        // skip system prelude chatter on start; stream real deltas
        if (type === "message_start" && holder && typeof holder === "object" && "customType" in holder) return [];
        return [{ field: "text", text: content }];
      }
      if (Array.isArray(content)) {
        const texts: string[] = [];
        const reasoning: string[] = [];
        const tools: string[] = [];
        for (const block of content) {
          if (!block || typeof block !== "object" || !("type" in block)) continue;
          if (block.type === "text" && "text" in block && typeof block.text === "string" && block.text.length > 0) {
            texts.push(block.text);
          } else if (block.type === "thinking" && "thinking" in block && typeof block.thinking === "string" && block.thinking.length > 0) {
            reasoning.push(block.thinking);
          } else if (block.type === "toolCall" && "name" in block && typeof block.name === "string" && block.name.length > 0) {
            tools.push(`▸ ${block.name}`);
          }
        }
        const out: EngineFrame[] = [];
        if (texts.length > 0) out.push({ field: "text", text: texts.join("") });
        if (reasoning.length > 0) out.push({ field: "reasoning", text: reasoning.join("") });
        for (const t of tools) out.push({ field: "tool", text: t });
        if (out.length > 0) return out;
      }
    }
    return [];
  }
  // Tool lifecycle carries the tool name + status line, never the full payload.
  if (type === "tool_execution_start") {
    const name = strField(event, "toolName");
    return name ? [{ field: "tool", text: `▶ ${name}` }] : [];
  }
  if (type === "tool_execution_end") {
    const name = strField(event, "toolName");
    if (!name) return [];
    const failed = "isError" in event && event.isError === true;
    return [{ field: "tool", text: `${failed ? "✘" : "✔"} ${name}` }];
  }
  // agent_start/end, turn_start/end, tool_execution_update, tool_stream_update,
  // notices, compaction/retry/todo/advisor/IRC session events: no frame text.
  // Completion is handled by the subscriber's agent_end branch, not here.
  return [];
}

/** Start the engine for a run WITHOUT awaiting completion (admission already persisted). */
export function startEngine(opts: EngineStartOptions): void {
  void runEngine(opts).catch((err) => {
    console.error(`[engine] failed session=${opts.sessionId} error=`, err);
    const reason = `engine error: ${String(err).slice(0, 500)}`;
    const run = getRun(opts.sessionId);
    if (run && (run.status === "running" || run.status === "continued")) {
      upsertRun({ ...run, status: "failed", error: reason, last_frame_at: nowIso() });
      emitRunBanner(opts.entry.name, { kind: "error", error: reason });
      emitSubworkerCompleted(opts.entry.name, "failed", opts.sessionId);
      void notify(opts.entry.name, "error", `${reason} (session ${opts.sessionId})`);
    }
  });
}

// The SDK replaces a process-wide Main-agent singleton during session init;
// concurrent createAgentSession calls abort each other
// ("Agent Main was replaced during session initialization"). Serialize creation
// only — prompts and turn waits stay fully parallel after the session exists.
let creationGate: Promise<void> = Promise.resolve();

function claimCreationSlot(): Promise<() => void> {
  const { promise, resolve } = Promise.withResolvers<void>();
  const previous = creationGate;
  creationGate = promise;
  return previous.then(() => resolve);
}
// Cold starts (Bun runtime + full SDK graph compile) spike CPU/RAM when N
// workers boot the same second. Space spawns ≥5 s apart; runs stay parallel.
let spawnSlot: Promise<void> = Promise.resolve();

function claimSpawnSlot(): Promise<() => void> {
  const { promise, resolve } = Promise.withResolvers<void>();
  const previous = spawnSlot;
  spawnSlot = promise;
  return previous.then(() => () => {
    setTimeout(resolve, 5000);
  });
}

const PROMPTS_DIR = new URL("./data/prompts/", import.meta.url).pathname;
const REPO_ROOT = new URL("..", import.meta.url).pathname;

function promptPathFor(sessionId: string): string {
  mkdirSync(PROMPTS_DIR, { recursive: true });
  return join(PROMPTS_DIR, `${sessionId}.txt`);
}

/** Best-effort prompt-file cleanup after finalize. */
function cleanupPromptFile(sessionId: string): void {
  try {
    unlinkSync(join(PROMPTS_DIR, `${sessionId}.txt`));
  } catch {
    // best-effort
  }
}

interface WorkerRunArgs {
  entry: SubworkerEntry;
  sessionId: string;
  promptText: string;
  model?: string | undefined;
}

/** Spawn omp-server/worker.ts as an isolated process and stream its protocol
 * lines (frames + terminal done) into the run record. Egress proxying is the
 * vendored proxy-local extension's job (in-worker forward on 127.0.0.1:18898,
 * native rotation, monitored log) — the parent sets no proxy env. */
/** Pool file for per-worker upstream seeding (same pool the plugin reads). */
const POOL_PATH = new URL("./config/proxies.txt", import.meta.url).pathname;
const CONF_DIR = new URL("./data/proxy-conf/", import.meta.url).pathname;

function readPool(): Array<{ host: string; port: number; user: string; pass: string }> {
  const out: Array<{ host: string; port: number; user: string; pass: string }> = [];
  try {
    for (const line of readFileSync(POOL_PATH, "utf8").split("\n")) {
      const parts = (line.trim().split(/\s+/)[0] ?? "").split(":");
      const port = Number.parseInt(parts[1] ?? "", 10);
      if (parts[0] && Number.isFinite(port) && parts[2] && parts[3]) {
        out.push({ host: parts[0], port, user: parts[2], pass: parts[3] });
      }
    }
  } catch {
    // no pool → worker falls back to shared conf
  }
  return out;
}

/** Live sessions' current upstream labels (`host:port`), for distinct picks. */
const workerUpstreams = new Map<string, string>();

/** Seed a per-worker upstream conf with the least-recently-seeded entry. */
function seedWorkerConf(sessionId: string): string | null {
  const pool = readPool();
  if (pool.length === 0) return null;
  const used = new Set(workerUpstreams.values());
  const idxPath = join(CONF_DIR, ".idx");
  let idx = 0;
  try {
    idx = Number.parseInt(readFileSync(idxPath, "utf8").trim(), 10) || 0;
  } catch {
    idx = 0;
  }
  for (let i = 0; i < pool.length; i++) {
    const cand = pool[(idx + i) % pool.length];
    const label = `${cand.host}:${cand.port}`;
    if (used.has(label)) continue;
    try {
      mkdirSync(CONF_DIR, { recursive: true });
      writeFileSync(idxPath, String((idx + i + 1) % pool.length));
      const confPath = join(CONF_DIR, `${sessionId}.conf`);
      writeFileSync(confPath, `http ${cand.host} ${cand.port} ${cand.user} ${cand.pass}\n`);
      workerUpstreams.set(sessionId, label);
      return confPath;
    } catch {
      return null;
    }
  }
  return null;
}

function releaseWorkerConf(sessionId: string): void {
  workerUpstreams.delete(sessionId);
  try {
    unlinkSync(join(CONF_DIR, `${sessionId}.conf`));
  } catch {
    // best-effort
  }
}

async function spawnWorkerAndWait({ entry, sessionId, promptText, model }: WorkerRunArgs): Promise<void> {
  const workspace = effectiveWorkspace(entry);
  const promptFile = promptPathFor(sessionId);
  writeFileSync(promptFile, promptText);
  const proxyConf = seedWorkerConf(sessionId);
  const releaseSpawn = await claimSpawnSlot();
  let child: ReturnType<typeof Bun.spawn>;
  try {
    child = Bun.spawn(["bun", "--smol", "omp-server/worker.ts", sessionId, workspace, promptFile, model ?? "", entry.name], {
      cwd: REPO_ROOT,
      env: {
        ...process.env,
        ...(proxyConf ? { ELIA_PROXY_CONF: proxyConf } : {}),
      },
      stdout: "pipe",
      stdin: "pipe",
      stderr: "inherit",
    });
    releaseSpawn();
  } catch (err) {
    releaseSpawn();
    cleanupPromptFile(sessionId);
    releaseWorkerConf(sessionId);
    liveChildren.delete(sessionId);
    throw new Error(`worker spawn failed: ${String(err).slice(0, 300)}`);
  }
  liveChildren.set(sessionId, { proc: child });
  console.log(`[engine] worker session=${sessionId} pid=${child.pid} conf=${proxyConf ?? "shared"}`);

  let done = false;
  let exited = false;
  const finish = (status: "completed" | "failed", error?: string): void => {
    liveChildren.delete(sessionId);
    releaseWorkerConf(sessionId);
    cleanupPromptFile(sessionId);
    const run = getRun(sessionId);
    if (run && (run.status === "running" || run.status === "continued")) {
      if (status === "completed") {
        upsertRun({ ...run, status: "completed", last_frame_at: nowIso() });
        emitSubworkerCompleted(entry.name, "completed", sessionId);
        void notify(entry.name, "completed", `run finished (session ${sessionId})`);
      } else {
        const reason = error ?? `worker exited without done (session ${sessionId})`;
        upsertRun({ ...run, status: "failed", error: reason, last_frame_at: nowIso() });
        emitRunBanner(entry.name, { kind: "error", error: reason });
        emitSubworkerCompleted(entry.name, "failed", sessionId);
        void notify(entry.name, "error", `${reason} (session ${sessionId})`);
      }
    }
  };
  try {
    const reader = child.stdout.getReader();
    const decoder = new TextDecoder();
    let buf = "";
    const handleLine = (line: string): void => {
      const trimmed = line.trim();
      if (!trimmed) return;
      let msg: unknown;
      try {
        msg = JSON.parse(trimmed);
      } catch {
        return;
      }
      if (!msg || typeof msg !== "object") return;
      if ("event" in msg && msg.event === "done") {
        done = true;
        const status = "status" in msg ? msg.status : undefined;
        const errText = "error" in msg && typeof msg.error === "string" ? msg.error : undefined;
        if (status === "failed") finish("failed", errText ?? "worker reported failure");
        else finish("completed");
        return;
      }
      if (
        "field" in msg &&
        "text" in msg &&
        (msg.field === "text" || msg.field === "reasoning" || msg.field === "tool") &&
        typeof msg.text === "string"
      ) {
        const field = msg.field as "text" | "reasoning" | "tool";
        const extra: { tool?: string; input?: unknown; output?: string } = {};
        if ("tool" in msg && typeof msg.tool === "string") extra.tool = msg.tool;
        if ("input" in msg && msg.input !== undefined) extra.input = msg.input;
        if ("output" in msg && typeof msg.output === "string") extra.output = msg.output;
        // TopBar parses tool deltas as JSON {tool,input,output} for live
        // subagent/todo detection; plain text otherwise (unchanged display).
        const delta = field === "tool" && extra.tool
          ? JSON.stringify({ tool: extra.tool, ...(extra.input !== undefined ? { input: extra.input } : {}), ...(extra.output !== undefined ? { output: extra.output } : {}) })
          : msg.text;
        try {
          appendFrame(sessionId, field, msg.text, extra);
          emitRunLog(entry.name, field, delta);
          touchRun(sessionId);
        } catch (err) {
          console.error(`[engine] worker frame failed session=${sessionId}: ${String(err)}`);
        }
      }
    };
    for (;;) {
      const { done: eof, value } = await reader.read();
      if (value) {
        buf += decoder.decode(value, { stream: true });
        let idx: number;
        while ((idx = buf.indexOf("\n")) >= 0) {
          handleLine(buf.slice(0, idx));
          buf = buf.slice(idx + 1);
        }
      }
      if (eof) break;
    }
    if (buf.trim()) handleLine(buf);
  } catch (err) {
    console.error(`[engine] worker stdout failed session=${sessionId}: ${String(err)}`);
  }

  let exitCode = 0;
  try {
    exitCode = await child.exited;
  } catch (err) {
    console.error(`[engine] worker wait failed session=${sessionId}: ${String(err)}`);
    exitCode = 1;
  }
  exited = true;
  try {
    const sink = child.stdin as unknown as { end?: unknown; close?: unknown };
    if (typeof sink.end === "function") (sink as { end: () => void }).end();
    else if (typeof sink.close === "function") (sink as { close: () => void }).close();
  } catch {
    // best-effort
  }
  if (!done) {
    finish("failed", `worker exited code=${exitCode} without done (session ${sessionId})`.slice(0, 500));
  }
}

async function runEngine({ entry, sessionId, promptOverride, modelOverride, variantOverride }: EngineStartOptions): Promise<void> {
  void variantOverride;
  const workspace = effectiveWorkspace(entry);
  const prompt = workspacePrompt(workspace, promptOverride);
  const model = modelOverride ?? entry.model ?? undefined;
  await spawnWorkerAndWait({ entry, sessionId, promptText: prompt, model });
}

/** Re-inject a message into a run (continue path uses the identical worker mechanism). */
export async function continueEngineSession(
  entry: SubworkerEntry,
  sessionId: string,
  message: string,
): Promise<void> {
  await spawnWorkerAndWait({ entry, sessionId, promptText: message, model: entry.model ?? undefined });
}

export { AGENT_DIR };
