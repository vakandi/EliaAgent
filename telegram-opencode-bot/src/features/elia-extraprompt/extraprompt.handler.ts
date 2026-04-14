/**
 * EliaAI /extraprompt: run trigger_opencode_interactive.sh and stream output to Telegram.
 * Only registered when ELIA_HELPER_DIR is set.
 */

import { Bot, Context } from "grammy";
import * as fs from "fs";
import * as path from "path";
import { spawn } from "child_process";
import { fileURLToPath } from "url";
import { AccessControlMiddleware } from "../../middleware/access-control.middleware.js";

const TELEGRAM_MAX_MESSAGE = 4000;
const runningSessions = new Set<string>();

/** EliaAI repo root: from env, or inferred as parent of telegram-opencode-bot when running from this package. */
export function getAgentDir(): string | null {
    const fromEnv = process.env.ELIA_HELPER_DIR;
    if (fromEnv && fs.existsSync(fromEnv)) return path.resolve(fromEnv);
    try {
        const thisDir = path.dirname(fileURLToPath(import.meta.url));
        for (const rel of ["../..", "../../../..", "../../../../.."]) {
            const candidate = path.resolve(thisDir, rel);
            if (fs.existsSync(path.join(candidate, "logs"))) return candidate;
        }
    } catch {
        // ignore
    }
    return null;
}

function getOpenCodeModelEnv(agentDir: string): string {
    const modelFile = path.join(agentDir, ".opencode_model");
    if (!fs.existsSync(modelFile)) return "opencode/big-pickle";
    const id = fs.readFileSync(modelFile, "utf8").trim() || "big-pickle";
    switch (id) {
        case "nvidia": return "mistralai/mixtral-8x7b-instruct-v0.1";
        case "minimax": return "opencode/minimax-m2.5-free";
        case "big-pickle": return "opencode/big-pickle";
        case "nemotron": return "opencode/nemotron-3-super-free";
        case "mimo": return "opencode/mimo-v2-flash-free";
        default: return "opencode/big-pickle";
    }
}

const ANSI_RE = /\x1b\[[0-9;]*[a-zA-Z]?/g;
function stripAnsi(s: string): string {
    return s.replace(ANSI_RE, "").trim();
}

function summarizeLine(line: string): string | null {
    const t = stripAnsi(line);
    if (!t) return null;
    if (t.startsWith("→ ")) return "🔧 " + t.slice(2).replace(/\s+/g, " ").slice(0, 120);
    if (t.startsWith("✱ ")) return "🔧 " + t.slice(2).replace(/\s+/g, " ").slice(0, 120);
    if (t.startsWith("✗ ")) return "❌ " + t.slice(2).replace(/\s+/g, " ").slice(0, 200);
    if (t.startsWith("$ ")) return "⌘ " + t.slice(2).replace(/\n/g, " ").slice(0, 100);
    if (t.includes("Wrote file successfully") || t.includes("Write ") || /←\s*Write\s+/.test(t)) {
        const m = t.match(/Write\s+([^\s]+)/) || t.match(/Wrote\s+([^\s]+)/);
        return "📝 Wrote: " + (m ? m[1] : "file");
    }
    return null;
}

function chunkSend(text: string): string[] {
    const out: string[] = [];
    let rest = text;
    while (rest.length > TELEGRAM_MAX_MESSAGE) {
        let split = rest.slice(0, TELEGRAM_MAX_MESSAGE);
        const lastNewline = split.lastIndexOf("\n");
        if (lastNewline > TELEGRAM_MAX_MESSAGE / 2) split = rest.slice(0, lastNewline + 1);
        out.push(split);
        rest = rest.slice(split.length);
    }
    if (rest) out.push(rest);
    return out;
}

async function runExtrapromptWithStream(
    chatId: number,
    extraPrompt: string,
    send: (text: string) => Promise<unknown>
): Promise<void> {
    const agentDir = getAgentDir();
    if (!agentDir) {
        await send("EliaAI not configured (set ELIA_HELPER_DIR).");
        return;
    }
    const triggerScript = path.join(agentDir, "trigger_opencode_interactive.sh");
    if (!fs.existsSync(triggerScript)) {
        await send("Trigger script not found: trigger_opencode_interactive.sh");
        return;
    }

    const key = String(chatId);
    if (runningSessions.has(key)) {
        await send("A session is already running. Wait for it to finish.");
        return;
    }
    runningSessions.add(key);
    const sessionId = Date.now();
    await send(`🔄 New session started (id: ${sessionId})\n\nStreaming agent output…`);

    // Create temp prompt file like start_agents.sh does
    // This matches how start_agents.sh creates and passes prompt files
    const agentPayloadsDir = path.join(agentDir, ".agent_payloads");
    if (!fs.existsSync(agentPayloadsDir)) {
        fs.mkdirSync(agentPayloadsDir, { recursive: true });
    }
    const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
    const promptFile = path.join(agentPayloadsDir, `prompt_${timestamp}.txt`);

    // Write the prompt to temp file (matches start_agents.sh format)
    const promptContent = `# 🚨 URGENT CONTEXT - ${new Date().toLocaleString()}

${extraPrompt}
`;
    fs.writeFileSync(promptFile, promptContent, "utf8");

    let buffer = "";
    let lastSend = 0;
    const SEND_INTERVAL_MS = 2000;
    const BUF_MAX = 3500;

    const flush = async (force = false) => {
        const now = Date.now();
        if (buffer.length === 0) return;
        if (!force && buffer.length < BUF_MAX && now - lastSend < SEND_INTERVAL_MS) return;
        const chunks = chunkSend(buffer);
        buffer = "";
        lastSend = now;
        for (const c of chunks) {
            if (c.trim()) await send(c).catch(() => {});
        }
    };

    return new Promise((resolve) => {
        // Read the prompt file content and pass it as argument to the trigger script
        // This is IDENTICAL to how start_agents.sh passes prompts via temp files
        const promptContent = fs.readFileSync(promptFile, "utf8");

        const child = spawn("/bin/zsh", [triggerScript, promptContent], {
            cwd: agentDir,
            env: {
                ...process.env,
                ELIA_HELPER_DIR: agentDir,
                OPENCODE_MODEL: getOpenCodeModelEnv(agentDir),
            },
            stdio: ["ignore", "pipe", "pipe"],
        });

        const onData = async (raw: Buffer) => {
            const s = raw.toString("utf8");
            const lines = s.split(/\r?\n/);
            for (const line of lines) {
                const summarized = summarizeLine(line);
                if (summarized !== null) {
                    buffer += summarized + "\n";
                } else {
                    const clean = stripAnsi(line);
                    if (clean) buffer += (clean.length > 400 ? clean.slice(0, 400) + "…" : clean) + "\n";
                }
            }
            await flush();
        };

        child.stdout?.on("data", onData);
        child.stderr?.on("data", onData);

        child.on("exit", async (code, signal) => {
            // Clean up temp prompt file
            try {
                if (fs.existsSync(promptFile)) fs.unlinkSync(promptFile);
            } catch {}

            runningSessions.delete(key);
            await flush(true);
            const status = code === 0 ? "✅" : "⚠️";
            await send(`${status} Session finished (exit: ${code ?? "—"}${signal ? `, signal: ${signal}` : ""})`).catch(() => {});
            resolve();
        });

        child.on("error", async (err) => {
            // Clean up temp prompt file
            try {
                if (fs.existsSync(promptFile)) fs.unlinkSync(promptFile);
            } catch {}

            runningSessions.delete(key);
            await send("❌ Failed to start agent: " + err.message).catch(() => {});
            resolve();
        });
    });
}

/** EliaAI agent runs from logs (cron + /extraprompt); uses modified OpenCode CLI, not the OpenCode server. */
export function getEliaAIRuns(agentDir: string, limit: number = 20): Array<{ name: string; mtime: number; type: "interactive" | "cron" }> {
    const logDir = path.join(agentDir, "logs");
    if (!fs.existsSync(logDir)) return [];
    const entries: Array<{ name: string; mtime: number; type: "interactive" | "cron" }> = [];
    const files = fs.readdirSync(logDir);
    for (const name of files) {
        if (name.startsWith("opencode_interactive_") && name.endsWith(".log")) {
            const stat = fs.statSync(path.join(logDir, name));
            entries.push({ name, mtime: stat.mtimeMs, type: "interactive" });
        } else if (name.startsWith("opencode_run_") && name.endsWith(".log")) {
            const stat = fs.statSync(path.join(logDir, name));
            entries.push({ name, mtime: stat.mtimeMs, type: "cron" });
        }
    }
    entries.sort((a, b) => b.mtime - a.mtime);
    return entries.slice(0, limit);
}

/** Per-user state: when they clicked "Resume", next text message continues this run. */
const resumingRun = new Map<number, string>();

/** Read first and last lines of a run log for context preview (no full file). */
function getRunContext(agentDir: string, logFileName: string, headLines = 15, tailLines = 15): string {
    const logPath = path.join(agentDir, "logs", logFileName);
    if (!fs.existsSync(logPath)) return "(log file not found)";
    const raw = fs.readFileSync(logPath, "utf8");
    const lines = raw.split(/\r?\n/).filter((l) => stripAnsi(l).trim());
    if (lines.length === 0) return "(empty log)";
    const head = lines.slice(0, headLines).map(stripAnsi).join("\n");
    const tail = lines.length > headLines ? lines.slice(-tailLines).map(stripAnsi).join("\n") : "";
    if (!tail) return head.slice(0, 2500);
    return `--- First ${headLines} lines ---\n${head.slice(0, 1200)}\n\n--- Last ${tailLines} lines ---\n${tail.slice(-1200)}`;
}

/**
 * If this user has a "resume run" set, run extraprompt with "Continuing from run X: <message>" and clear state.
 * Call this at the start of text message handling. Returns true if it handled the message.
 */
export async function handleResumeIfSet(ctx: Context): Promise<boolean> {
    const userId = ctx.from?.id;
    const text = ctx.message?.text?.trim();
    if (userId === undefined || !text) return false;
    const logFileName = resumingRun.get(userId);
    if (!logFileName) return false;
    resumingRun.delete(userId);
    const agentDir = getAgentDir();
    if (!agentDir) {
        await ctx.reply("EliaAI not configured.");
        return true;
    }
    const prompt = `[Resuming run: ${logFileName}]\n\n${text}`;
    const chatId = ctx.chat!.id;
    const send = (t: string) => ctx.api.sendMessage(chatId, t, { parse_mode: undefined });
    await runExtrapromptWithStream(chatId, prompt, send);
    return true;
}

export function registerExtrapromptHandlers(bot: Bot): void {
    const agentDir = getAgentDir();
    if (!agentDir) {
        console.log("[Elia] ELIA_HELPER_DIR not set, /extraprompt and /extra-prompt disabled");
        return;
    }

    const handler = async (ctx: Context) => {
        const msg = ctx.message?.text?.replace(/^\/extraprompt\s*/i, "").replace(/^\/extra-prompt\s*/i, "").trim();
        if (!msg) {
            await ctx.reply("Usage: /extraprompt <your message>");
            return;
        }
        const chatId = ctx.chat?.id;
        if (chatId === undefined) return;
        const send = (text: string) => bot.api.sendMessage(chatId, text, { parse_mode: undefined });
        await runExtrapromptWithStream(chatId, msg, send);
    };

    const runsHandler = async (ctx: Context) => {
        const runs = getEliaAIRuns(agentDir, 20);
        if (runs.length === 0) {
            await ctx.reply("No EliaAI agent runs found in logs/ (opencode_interactive_*.log, opencode_run_*.log).");
            return;
        }
        const lines = ["📋 EliaAI runs (select to see context & resume):", ""];
        runs.forEach((r, i) => {
            const date = new Date(r.mtime);
            const label = r.type === "cron" ? "cron" : "interactive";
            lines.push(`${i + 1}. ${date.toLocaleString()} [${label}] ${r.name}`);
        });
        const keyboard = runs.map((r, i) => [
            { text: `Select #${i + 1}`, callback_data: `wh_run:${r.name}` as string }
        ]);
        await ctx.reply(lines.join("\n"), {
            reply_markup: { inline_keyboard: keyboard },
        });
    };

    bot.command("extraprompt", AccessControlMiddleware.requireAccess, handler);
    bot.command("extra-prompt", AccessControlMiddleware.requireAccess, handler);
    bot.command("runs", AccessControlMiddleware.requireAccess, runsHandler);

    bot.callbackQuery(/^wh_run:/, AccessControlMiddleware.requireAccess, async (ctx) => {
        await ctx.answerCallbackQuery();
        const data = ctx.callbackQuery.data;
        const logFileName = data?.replace(/^wh_run:/, "") ?? "";
        if (!logFileName) return;
        const context = getRunContext(agentDir, logFileName);
        const preview = context.length > 3500 ? context.slice(0, 3500) + "\n…" : context;
        await ctx.reply(`📄 Run: ${logFileName}\n\n${preview}`, {
            reply_markup: {
                inline_keyboard: [[{ text: "▶ Resume this run", callback_data: `wh_resume:${logFileName}` as string }]],
            },
        });
    });

    bot.callbackQuery(/^wh_resume:/, AccessControlMiddleware.requireAccess, async (ctx) => {
        await ctx.answerCallbackQuery();
        const data = ctx.callbackQuery.data;
        const logFileName = data?.replace(/^wh_resume:/, "") ?? "";
        if (!logFileName) return;
        const userId = ctx.from?.id;
        if (userId === undefined) return;
        resumingRun.set(userId, logFileName);
        await ctx.reply(`✅ Resuming run: ${logFileName}\n\nSend your next message to continue this session.`);
    });
}
