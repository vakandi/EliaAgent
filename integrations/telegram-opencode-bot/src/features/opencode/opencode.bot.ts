import { Bot, Context, InputFile, Keyboard } from "grammy";
import { OpenCodeService } from "./opencode.service.js";
import { ConfigService } from "../../services/config.service.js";
import { OpenCodeServerService } from "../../services/opencode-server.service.js";
import { AccessControlMiddleware } from "../../middleware/access-control.middleware.js";
import { MessageUtils } from "../../utils/message.utils.js";
import { ErrorUtils } from "../../utils/error.utils.js";
import { formatAsHtml, escapeHtml } from "./event-handlers/utils.js";
import { FileMentionService, FileMentionUI } from "../file-mentions/index.js";
import { getAgentDir, getEliaAIRuns, handleResumeIfSet } from "../elia-extraprompt/extraprompt.handler.js";
import * as fs from "fs";
import * as path from "path";
import { spawn, ChildProcess } from "child_process";

function timeAgo(timestamp: number): string {
    const now = Date.now();
    const diff = now - timestamp;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    const weeks = Math.floor(days / 7);

    if (seconds < 10) return "Few seconds ago";
    if (seconds < 60) return `${seconds} seconds ago`;
    if (minutes < 60) return minutes === 1 ? "1 minute ago" : `${minutes} minutes ago`;
    if (hours < 24) return hours === 1 ? "1 hour ago" : `${hours} hours ago`;
    if (days < 7) return days === 1 ? "1 day ago" : `${days} days ago`;
    return weeks === 1 ? "1 week ago" : `${weeks} weeks ago`;
}

// Whisper transcription helper
async function transcribeWithWhisper(audioPath: string): Promise<string> {
    return new Promise((resolve, reject) => {
        const whisperBin = '/opt/homebrew/bin/whisper';
        const args = [
            audioPath,
            '--model', 'large-v3',
            '--language', 'fr',
            '--task', 'transcribe',
            '--output_format', 'txt'
        ];
        
        console.log(`[Whisper] Starting transcription: ${audioPath}`);
        
        // Verify file exists and has content
        try {
            const stats = fs.statSync(audioPath);
            console.log(`[Whisper] File size: ${stats.size} bytes`);
            if (stats.size === 0) {
                reject(new Error("Audio file is empty"));
                return;
            }
        } catch (e) {
            reject(new Error(`Cannot access audio file: ${e}`));
            return;
        }
        
        const whisper = spawn(whisperBin, args);
        let output = '';
        let errorOutput = '';
        
        whisper.stdout.on('data', (data: Buffer) => {
            output += data.toString();
        });
        
        whisper.stderr.on('data', (data: Buffer) => {
            errorOutput += data.toString();
        });
        
        whisper.on('close', (code: number) => {
            if (code === 0) {
                console.log(`[Whisper] Transcription complete`);
                resolve(output.trim());
            } else {
                console.error(`[Whisper] Error: ${errorOutput}`);
                reject(new Error(`Whisper failed: ${errorOutput}`));
            }
        });
        
        whisper.on('error', (err: Error) => {
            console.error(`[Whisper] Spawn error: ${err.message}`);
            reject(err);
        });
    });
}

export class OpenCodeBot {
    private opencodeService: OpenCodeService;
    private configService: ConfigService;
    private serverService: OpenCodeServerService;
    private fileMentionService: FileMentionService;
    private fileMentionUI: FileMentionUI;

    constructor(
        opencodeService: OpenCodeService,
        configService: ConfigService
    ) {
        this.opencodeService = opencodeService;
        this.configService = configService;
        this.serverService = new OpenCodeServerService();
        this.fileMentionService = new FileMentionService();
        this.fileMentionUI = new FileMentionUI();
    }

    private createControlKeyboard(): Keyboard {
        return new Keyboard()
            .text("⏹️ ESC")
            .text("⇥ TAB")
            .resized()
            .persistent();
    }

    registerHandlers(bot: Bot): void {
        bot.command("start", AccessControlMiddleware.requireAccess, this.handleStart.bind(this));
        bot.command("help", AccessControlMiddleware.requireAccess, this.handleStart.bind(this));
        bot.command("opencode", AccessControlMiddleware.requireAccess, this.handleOpenCode.bind(this));
        bot.command("esc", AccessControlMiddleware.requireAccess, this.handleEsc.bind(this));
        bot.command("endsession", AccessControlMiddleware.requireAccess, this.handleEndSession.bind(this));
        bot.command("rename", AccessControlMiddleware.requireAccess, this.handleRename.bind(this));
        bot.command("projects", AccessControlMiddleware.requireAccess, this.handleProjects.bind(this));
        bot.command("sessions", AccessControlMiddleware.requireAccess, this.handleSessions.bind(this));
        bot.command("undo", AccessControlMiddleware.requireAccess, this.handleUndo.bind(this));
        bot.command("redo", AccessControlMiddleware.requireAccess, this.handleRedo.bind(this));
        
        // Handle keyboard button presses
        bot.hears("⏹️ ESC", AccessControlMiddleware.requireAccess, this.handleEsc.bind(this));
        bot.hears("⇥ TAB", AccessControlMiddleware.requireAccess, this.handleTab.bind(this));
        
        // Handle inline button callbacks
        bot.callbackQuery("esc", AccessControlMiddleware.requireAccess, this.handleEscButton.bind(this));
        bot.callbackQuery("tab", AccessControlMiddleware.requireAccess, this.handleTabButton.bind(this));
        
        // Handle OpenCode session selection (from /sessions command)
        bot.callbackQuery(/^oc_session:/, AccessControlMiddleware.requireAccess, this.handleSessionSelect.bind(this));
        
        // Handle file uploads (documents, photos, videos, audio, etc.)
        bot.on("message:document", AccessControlMiddleware.requireAccess, this.handleFileUpload.bind(this));
        bot.on("message:photo", AccessControlMiddleware.requireAccess, this.handleFileUpload.bind(this));
        bot.on("message:video", AccessControlMiddleware.requireAccess, this.handleFileUpload.bind(this));
        bot.on("message:audio", AccessControlMiddleware.requireAccess, this.handleFileUpload.bind(this));
        bot.on("message:voice", AccessControlMiddleware.requireAccess, this.handleFileUpload.bind(this));
        bot.on("message:video_note", AccessControlMiddleware.requireAccess, this.handleFileUpload.bind(this));
        
        // Handle regular messages (non-commands) as prompts
        bot.on("message:text", AccessControlMiddleware.requireAccess, async (ctx, next) => {
            // Skip if it's a command
            if (ctx.message?.text?.startsWith("/")) {
                return next();
            }
            // Skip if it's a keyboard button
            if (ctx.message?.text === "⏹️ ESC" || ctx.message?.text === "⇥ TAB") {
                return next();
            }
            // Treat as prompt
            await this.handleMessageAsPrompt(ctx);
        });
    }

    private async handleStart(ctx: Context): Promise<void> {
        try {
            const helpMessage = [
                '👋 <b>Welcome to TelegramCoder!</b>',
                '',
                '🎯 <b>Session Commands:</b>',
                '/opencode [title] - Start a new OpenCode AI session',
                '   Example: /opencode Fix login bug',
                '/rename &lt;title&gt; - Rename your current session',
                '   Example: /rename Updated task name',
                '/endsession - End and close your current session',
                '/sessions - View your recent sessions (last 5)',
                '/projects - List available projects',
                '',
                '⚡️ <b>Control Commands:</b>',
                '/esc - Abort the current AI operation',
                '/undo - Revert the last message/change',
                '/redo - Restore a previously undone change',
                '⇥ TAB button - Cycle between agents (build ↔ plan)',
                '⏹️ ESC button - Same as /esc command',
                '',
                '📋 <b>Information Commands:</b>',
                '/start - Show this help message',
                '/help - Show this help message',
                '/sessions - View recent sessions with IDs',
                '/projects - List available projects',
                '',
                '💬 <b>How to Use:</b>',
                '1. Start: /opencode My Project',
                '2. Chat: Just send messages directly (no /prompt needed)',
                '3. Upload: Send any file - it saves to /tmp/telegramCoder',
                '4. Control: Use ESC/TAB buttons on session message',
                '5. Rename: /rename New Name (anytime during session)',
                '6. Undo/Redo: /undo or /redo to manage changes',
                '7. End: /endsession when done',
                '',
                '🤖 <b>Agents Available:</b>',
                '• <b>build</b> - Implements code and makes changes',
                '• <b>plan</b> - Plans and analyzes without editing',
                '• Use TAB button to switch between agents',
                '',
                '💡 <b>Tips:</b>',
                '• This help message stays - reference it anytime!',
                '• Send files - they\'re saved to /tmp/telegramCoder',
                '• Tap the file path to copy it to clipboard',
                '• Session messages auto-delete after 10 seconds',
                '• Tab between build/plan agents as needed',
                '• Use descriptive titles for better organization',
                '• All messages go directly to the AI',
                '• Use /undo if AI makes unwanted changes',
                '• Streaming responses limited to last 50 lines',
                '',
                '🔧 <b>EliaAI (if configured):</b>',
                '/extraprompt &lt;message&gt; - Run EliaAI agent with extra context (streams output here)',
                '/runs - List agent runs (cron + /extraprompt) from EliaAI logs',
                '',
                '🚀 <b>Get started:</b> /opencode'
            ].join('\n');

            await ctx.reply(helpMessage, { parse_mode: "HTML" });
            
            // Help message should not auto-delete - users may want to reference it
        } catch (error) {
            await ctx.reply(ErrorUtils.createErrorMessage('show help message', error));
        }
    }

    private async handleOpenCode(ctx: Context): Promise<void> {
        try {
            const userId = ctx.from?.id;
            if (!userId) {
                await ctx.reply("❌ Unable to identify user");
                return;
            }

            // Check if user already has an active session
            if (this.opencodeService.hasActiveSession(userId)) {
                const message = await ctx.reply("✅ Session already started", {
                    reply_markup: {
                        inline_keyboard: [
                            [
                                { text: "⏹️ ESC", callback_data: "esc" },
                                { text: "⇥ TAB", callback_data: "tab" }
                            ]
                        ]
                    }
                });
                
                // Schedule auto-deletion
                await MessageUtils.scheduleMessageDeletion(
                    ctx,
                    message.message_id,
                    this.configService.getMessageDeleteTimeout()
                );
                return;
            }

            // Extract title from command text (everything after /opencode)
            const text = ctx.message?.text || "";
            const title = text.replace("/opencode", "").trim() || undefined;

            // Create a new session
            const statusMessage = await ctx.reply("🔄 Starting OpenCode session...");

            try {
                // Try to create session with optional title
                let userSession;
                try {
                    userSession = await this.opencodeService.createSession(userId, title);
                } catch (error) {
                    // Check if it's a connection error
                    if (error instanceof Error && (error.message.includes('Cannot connect to OpenCode server'))) {
                        // Try to start the server automatically
                        await ctx.api.editMessageText(
                            ctx.chat!.id,
                            statusMessage.message_id,
                            "🔄 OpenCode server not running. Starting server...\n\nThis may take up to 30 seconds."
                        );

                        const startResult = await this.serverService.startServer();

                        if (!startResult.success) {
                            await ctx.api.editMessageText(
                                ctx.chat!.id,
                                statusMessage.message_id,
                                `❌ Failed to start OpenCode server.\n\n${startResult.message}\n\nPlease start the server manually using:\n<code>opencode serve</code>`,
                                { parse_mode: "HTML" }
                            );
                            return;
                        }

                        // Update status
                        await ctx.api.editMessageText(
                            ctx.chat!.id,
                            statusMessage.message_id,
                            "✅ OpenCode server started!\n\n🔄 Creating session..."
                        );

                        // Retry session creation with title
                        userSession = await this.opencodeService.createSession(userId, title);
                    } else {
                        throw error;
                    }
                }

                const successMessage = await ctx.api.editMessageText(
                    ctx.chat!.id,
                    statusMessage.message_id,
                    "✅ Session started",
                    {
                        reply_markup: {
                            inline_keyboard: [
                                [
                                    { text: "⏹️ ESC", callback_data: "esc" },
                                    { text: "⇥ TAB", callback_data: "tab" }
                                ]
                            ]
                        }
                    }
                );

                // Schedule auto-deletion of the session started message
                const messageId = (typeof successMessage === "object" && successMessage && "message_id" in successMessage) ? (successMessage as any).message_id : statusMessage.message_id;
                await MessageUtils.scheduleMessageDeletion(
                    ctx,
                    messageId,
                    this.configService.getMessageDeleteTimeout()
                );

                // Store chat context and start event streaming
                this.opencodeService.updateSessionContext(userId, ctx.chat!.id, messageId);

                // Start event streaming in background
                this.opencodeService.startEventStream(userId, ctx).catch(error => {
                    console.error("Event stream error:", error);
                });
            } catch (error) {
                await ctx.api.editMessageText(
                    ctx.chat!.id,
                    statusMessage.message_id,
                    ErrorUtils.createErrorMessage("start OpenCode session", error)
                );
            }
        } catch (error) {
            await ctx.reply(ErrorUtils.createErrorMessage("start OpenCode session", error));
        }
    }

    private async handleMessageAsPrompt(ctx: Context): Promise<void> {
        try {
            const userId = ctx.from?.id;
            if (!userId) {
                await ctx.reply("❌ Unable to identify user");
                return;
            }

            // If user selected "Resume" on a EliaAI run, treat this message as /extraprompt continuation
            const resumed = await handleResumeIfSet(ctx);
            if (resumed) return;

            // Check if user has an active session
            if (!this.opencodeService.hasActiveSession(userId)) {
                await ctx.reply("❌ No active OpenCode session. Use /opencode to start a session first.");
                return;
            }

            const promptText = ctx.message?.text?.trim() || "";

            if (!promptText) {
                return;
            }

            // Check for file mentions
            const mentions = this.fileMentionService.parseMentions(promptText);
            
            if (mentions.length > 0 && this.fileMentionService.isEnabled()) {
                await this.handlePromptWithMentions(ctx, userId, promptText, mentions);
            } else {
                await this.sendPromptToOpenCode(ctx, userId, promptText);
            }
        } catch (error) {
            await ctx.reply(ErrorUtils.createErrorMessage("send prompt to OpenCode", error));
        }
    }

    private async handlePromptWithMentions(
        ctx: Context,
        userId: number,
        promptText: string,
        mentions: any[]
    ): Promise<void> {
        try {
            // Show searching indicator
            const searchMessage = await this.fileMentionUI.showSearching(ctx, mentions.length);
            
            // Search for files
            const matches = await this.fileMentionService.searchMentions(mentions);
            
            // Delete searching message
            await ctx.api.deleteMessage(searchMessage.chat.id, searchMessage.message_id).catch(() => {});
            
            // Get user confirmation for file selections
            const selectedFiles = await this.fileMentionUI.confirmAllMatches(ctx, matches);
            
            if (!selectedFiles) {
                await ctx.reply("❌ File selection cancelled");
                return;
            }
            
            // Resolve files and get content
            const resolved = await this.fileMentionService.resolveMentions(
                mentions,
                selectedFiles,
                true
            );
            
            // Format file context
            const fileContext = this.fileMentionService.formatForPrompt(resolved);
            
            // Send prompt with file context
            await this.sendPromptToOpenCode(ctx, userId, promptText, fileContext);
            
        } catch (error) {
            await ctx.reply(ErrorUtils.createErrorMessage("process file mentions", error));
        }
    }

    private async sendPromptToOpenCode(ctx: Context, userId: number, promptText: string, fileContext?: string): Promise<void> {
        try {
            const response = await this.opencodeService.sendPrompt(userId, promptText, fileContext);

            // Check if response is markdown (contains markdown formatting)
            const isMarkdown = this.isMarkdownContent(response);
            
            // Check if response has more than 20 lines
            const hasManyLines = response.split('\n').length > 20;
            
            if (isMarkdown || hasManyLines) {
                // Send as markdown file
                const buffer = Buffer.from(response, 'utf-8');
                await ctx.replyWithDocument(new InputFile(buffer, "response.md"));
                return;
            }

            // Split response if it's too long (Telegram has a 4096 character limit)
            const maxLength = 4000;
            if (response.length <= maxLength) {
                await ctx.reply(formatAsHtml(response), { parse_mode: "HTML" });
            } else {
                const chunks = this.splitIntoChunks(response, maxLength);
                for (const chunk of chunks) {
                    await ctx.reply(formatAsHtml(chunk), { parse_mode: "HTML" });
                }
            }

        } catch (error) {
            await ctx.reply(ErrorUtils.createErrorMessage("send prompt to OpenCode", error));
        }
    }

    private isMarkdownContent(text: string): boolean {
        // If first character is a hash, it's markdown
        return text.trimStart().startsWith('#');
    }



    private splitIntoChunks(text: string, maxLength: number): string[] {
        const chunks: string[] = [];
        let currentChunk = "";

        const lines = text.split("\n");
        for (const line of lines) {
            if (currentChunk.length + line.length + 1 > maxLength) {
                if (currentChunk) {
                    chunks.push(currentChunk);
                }
                currentChunk = line;
            } else {
                if (currentChunk) {
                    currentChunk += "\n" + line;
                } else {
                    currentChunk = line;
                }
            }
        }

        if (currentChunk) {
            chunks.push(currentChunk);
        }

        return chunks;
    }

    private async handleEndSession(ctx: Context): Promise<void> {
        try {
            const userId = ctx.from?.id;
            if (!userId) {
                await ctx.reply("❌ Unable to identify user");
                return;
            }

            if (!this.opencodeService.hasActiveSession(userId)) {
                await ctx.reply("ℹ️ You don't have an active OpenCode session. Use /opencode to start one.");
                return;
            }

            const success = await this.opencodeService.deleteSession(userId);

            if (success) {
                const sentMessage = await ctx.reply("✅ OpenCode session ended successfully.");
                const deleteTimeout = this.configService.getMessageDeleteTimeout();
                if (deleteTimeout > 0 && sentMessage) {
                    await MessageUtils.scheduleMessageDeletion(
                        ctx,
                        sentMessage.message_id,
                        deleteTimeout
                    );
                }
            } else {
                await ctx.reply("⚠️ Failed to end session. It may have already been closed.");
            }
        } catch (error) {
            await ctx.reply(ErrorUtils.createErrorMessage("end OpenCode session", error));
        }
    }

    private async handleEsc(ctx: Context): Promise<void> {
        try {
            const userId = ctx.from?.id;
            if (!userId) {
                await ctx.reply("❌ Unable to identify user");
                return;
            }

            if (!this.opencodeService.hasActiveSession(userId)) {
                await ctx.reply("ℹ️ You don't have an active OpenCode session. Use /opencode to start one.");
                return;
            }

            const success = await this.opencodeService.abortSession(userId);

            if (success) {
                await ctx.reply("⏹️ Current operation aborted successfully.");
            } else {
                await ctx.reply("⚠️ Failed to abort operation. Please try again.");
            }
        } catch (error) {
            await ctx.reply(ErrorUtils.createErrorMessage("abort OpenCode operation", error));
        }
    }

    private async handleTab(ctx: Context): Promise<void> {
        try {
            const userId = ctx.from?.id;
            if (!userId) {
                await ctx.reply("❌ Unable to identify user");
                return;
            }

            if (!this.opencodeService.hasActiveSession(userId)) {
                await ctx.reply("ℹ️ You don't have an active OpenCode session. Use /opencode to start one.");
                return;
            }

            try {
                // Cycle to next agent
                const result = await this.opencodeService.cycleToNextAgent(userId);

                if (result.success && result.currentAgent) {
                    // Show simple agent name message
                    const message = await ctx.reply(`⇥ <b>${result.currentAgent}</b>`, { parse_mode: "HTML" });
                    
                    // Schedule auto-deletion
                    await MessageUtils.scheduleMessageDeletion(
                        ctx,
                        message.message_id,
                        this.configService.getMessageDeleteTimeout()
                    );
                } else {
                    const errorMsg = await ctx.reply("⚠️ Failed to cycle agent. Please try again.");
                    await MessageUtils.scheduleMessageDeletion(
                        ctx,
                        errorMsg.message_id,
                        this.configService.getMessageDeleteTimeout()
                    );
                }
            } catch (error) {
                const errorMsg = await ctx.reply(ErrorUtils.createErrorMessage("cycle agent", error));
                await MessageUtils.scheduleMessageDeletion(
                    ctx,
                    errorMsg.message_id,
                    this.configService.getMessageDeleteTimeout()
                );
            }
        } catch (error) {
            await ctx.reply(ErrorUtils.createErrorMessage("handle TAB", error));
        }
    }

    private async handleEscButton(ctx: Context): Promise<void> {
        try {
            // Answer the callback query to remove loading state
            await ctx.answerCallbackQuery();
            
            // Call the same handler as the ESC command/keyboard
            await this.handleEsc(ctx);
        } catch (error) {
            await ctx.answerCallbackQuery("Error handling ESC");
            console.error("Error in handleEscButton:", error);
        }
    }

    private async handleTabButton(ctx: Context): Promise<void> {
        try {
            // Answer the callback query to remove loading state
            await ctx.answerCallbackQuery();
            
            // Call the same handler as the TAB keyboard
            await this.handleTab(ctx);
        } catch (error) {
            await ctx.answerCallbackQuery("Error handling TAB");
            console.error("Error in handleTabButton:", error);
        }
    }

    private async handleSessionSelect(ctx: Context): Promise<void> {
        console.log("[handleSessionSelect] Called!");
        
        try {
            const data = ctx.callbackQuery.data;
            const sessionId = data?.replace(/^oc_session:/, "");
            console.log("[handleSessionSelect] Session ID:", sessionId);
            
            if (!sessionId) {
                await ctx.answerCallbackQuery("Invalid session");
                return;
            }

            const userId = ctx.from?.id;
            if (!userId) {
                await ctx.answerCallbackQuery("Cannot identify user");
                return;
            }

            // Get session details
            const sessions = await this.opencodeService.getSessions(20);
            const session = sessions.find(s => s.id === sessionId);
            
            if (!session) {
                await ctx.answerCallbackQuery("Session not found");
                return;
            }

            await ctx.answerCallbackQuery();

            const shortId = session.id.substring(0, 12);
            const title = session.title || "Untitled";
            const created = new Date(session.created * 1000).toLocaleString();
            const updated = new Date(session.updated * 1000).toLocaleString();

            // Attach to session using the proper method
            this.opencodeService.attachToSession(userId, session.id, session.title);
            
            await ctx.reply(
                `📋 <b>Session Attached:</b>\n\n` +
                `<b>Title:</b> ${title}\n` +
                `<b>ID:</b> <code>${shortId}</code>...\n` +
                `<b>Created:</b> ${created}\n` +
                `<b>Updated:</b> ${updated}\n\n` +
                `✅ You are now attached to this session!\n` +
                `Send any message to continue the conversation.`,
                {
                    parse_mode: "HTML",
                    reply_markup: {
                        inline_keyboard: [
                            [
                                { text: "⏹️ ESC", callback_data: "esc" },
                                { text: "⇥ TAB", callback_data: "tab" }
                            ]
                        ]
                    }
                }
            );
        } catch (error) {
            console.error("[handleSessionSelect] Error:", error);
            await ctx.answerCallbackQuery("Error: " + String(error));
        }
    }

    private async handleRename(ctx: Context): Promise<void> {
        try {
            const userId = ctx.from?.id;
            if (!userId) {
                await ctx.reply("❌ Unable to identify user");
                return;
            }

            // Check if user has an active session
            if (!this.opencodeService.hasActiveSession(userId)) {
                await ctx.reply("❌ No active session. Use /opencode to start one first.");
                return;
            }

            // Extract new title from command text
            const text = ctx.message?.text || "";
            const newTitle = text.replace("/rename", "").trim();

            if (!newTitle) {
                await ctx.reply("❌ Please provide a new title.\n\nUsage: /rename <new title>");
                return;
            }

            // Update the session title
            const result = await this.opencodeService.updateSessionTitle(userId, newTitle);

            if (result.success) {
                const message = await ctx.reply(`✅ Session renamed to: <b>${newTitle}</b>`, { parse_mode: "HTML" });
                
                // Schedule auto-deletion
                await MessageUtils.scheduleMessageDeletion(
                    ctx,
                    message.message_id,
                    this.configService.getMessageDeleteTimeout()
                );
            } else {
                await ctx.reply(`❌ ${result.message || "Failed to rename session"}`);
            }
        } catch (error) {
            await ctx.reply(ErrorUtils.createErrorMessage("rename session", error));
        }
    }

    private async handleProjects(ctx: Context): Promise<void> {
        try {
            const projects = await this.opencodeService.getProjects();

            if (projects.length === 0) {
                const message = await ctx.reply("📂 No projects found");
                await MessageUtils.scheduleMessageDeletion(
                    ctx,
                    message.message_id,
                    this.configService.getMessageDeleteTimeout()
                );
                return;
            }

            // Format as numbered list
            const projectList = projects
                .map((project, index) => `${index + 1}. ${project.worktree}`)
                .join("\n");

            const message = await ctx.reply(`📂 <b>Available Projects:</b>\n\n${projectList}`, {
                parse_mode: "HTML"
            });

            // Schedule auto-deletion
            await MessageUtils.scheduleMessageDeletion(
                ctx,
                message.message_id,
                this.configService.getMessageDeleteTimeout()
            );
        } catch (error) {
            await ctx.reply(ErrorUtils.createErrorMessage("list projects", error));
        }
    }

    private async handleSessions(ctx: Context): Promise<void> {
        try {
            console.log("[handleSessions] Called! userId:", ctx.from?.id);
            
            // First, show OpenCode server sessions with buttons (for resuming)
            const sessions = await this.opencodeService.getSessions(10);
            
            console.log("[handleSessions] Got sessions:", sessions.length);
            
            if (sessions.length === 0) {
                await ctx.reply("💬 No OpenCode server sessions found. Use /opencode to start a new session.");
                return;
            }

            // Format sessions with buttons
            const lines = ["📋 <b>OpenCode Sessions</b> (tap to resume):", ""];
            sessions.forEach((s, i) => {
                const shortId = s.id.substring(0, 8);
                const title = s.title || "Untitled";
                const createdAgo = timeAgo(s.created);
                const updatedAgo = timeAgo(s.updated);
                lines.push(`${i + 1}. <b>${title}</b>\n   🆔 ${shortId}...\n   📅 Created: ${createdAgo}\n   💬 Last chat: ${updatedAgo}`);
            });

            // Create buttons with time info
            const keyboard = sessions.map((s, i) => {
                const createdAgo = timeAgo(s.created);
                const updatedAgo = timeAgo(s.updated);
                const label = `${i + 1}. ${updatedAgo}`;
                return [{ text: label, callback_data: `oc_session:${s.id}` }];
            });

            await ctx.reply(lines.join("\n"), {
                parse_mode: "HTML",
                reply_markup: { inline_keyboard: keyboard },
            });
        } catch (error) {
            console.error("[handleSessions] Error:", error);
            await ctx.reply("Error: " + String(error));
        }
    }

    private async handleUndo(ctx: Context): Promise<void> {
        const userId = ctx.from?.id;
        if (!userId) return;

        try {
            const result = await this.opencodeService.undoLastMessage(userId);

            if (result.success) {
                const message = await ctx.reply("↩️ <b>Undone</b> - Last message reverted", { parse_mode: "HTML" });
                await MessageUtils.scheduleMessageDeletion(
                    ctx,
                    message.message_id,
                    this.configService.getMessageDeleteTimeout()
                );
            } else {
                const errorMsg = result.message || "Failed to undo last message";
                const message = await ctx.reply(`❌ ${errorMsg}`);
                await MessageUtils.scheduleMessageDeletion(
                    ctx,
                    message.message_id,
                    this.configService.getMessageDeleteTimeout()
                );
            }
        } catch (error) {
            await ctx.reply(ErrorUtils.createErrorMessage("undo", error));
        }
    }

    private async handleRedo(ctx: Context): Promise<void> {
        const userId = ctx.from?.id;
        if (!userId) return;

        try {
            const result = await this.opencodeService.redoLastMessage(userId);

            if (result.success) {
                const message = await ctx.reply("↪️ <b>Redone</b> - Change restored", { parse_mode: "HTML" });
                await MessageUtils.scheduleMessageDeletion(
                    ctx,
                    message.message_id,
                    this.configService.getMessageDeleteTimeout()
                );
            } else {
                const errorMsg = result.message || "Failed to redo last message";
                const message = await ctx.reply(`❌ ${errorMsg}`);
                await MessageUtils.scheduleMessageDeletion(
                    ctx,
                    message.message_id,
                    this.configService.getMessageDeleteTimeout()
                );
            }
        } catch (error) {
            await ctx.reply(ErrorUtils.createErrorMessage("redo", error));
        }
    }

    private async handleFileUpload(ctx: Context): Promise<void> {
        try {
            const message = ctx.message;
            if (!message) return;

            let fileId: string | undefined;
            let fileName: string | undefined;
            let fileType: string = "file";

            // Extract file info based on message type
            if (message.document) {
                fileId = message.document.file_id;
                fileName = message.document.file_name || `document_${Date.now()}`;
                fileType = "document";
            } else if (message.photo && message.photo.length > 0) {
                // Get the largest photo
                const photo = message.photo[message.photo.length - 1];
                fileId = photo.file_id;
                fileName = `photo_${Date.now()}.jpg`;
                fileType = "photo";
            } else if (message.video) {
                fileId = message.video.file_id;
                fileName = message.video.file_name || `video_${Date.now()}.mp4`;
                fileType = "video";
            } else if (message.audio) {
                fileId = message.audio.file_id;
                fileName = message.audio.file_name || `audio_${Date.now()}.mp3`;
                fileType = "audio";
            } else if (message.voice) {
                fileId = message.voice.file_id;
                fileName = `voice_${Date.now()}.ogg`;
                fileType = "voice";
            } else if (message.video_note) {
                fileId = message.video_note.file_id;
                fileName = `video_note_${Date.now()}.mp4`;
                fileType = "video_note";
            }

            if (!fileId || !fileName) {
                await ctx.reply("❌ Unable to process this file type");
                return;
            }

            // Get file from Telegram
            const file = await ctx.api.getFile(fileId);
            if (!file.file_path) {
                await ctx.reply("❌ Unable to get file path from Telegram");
                return;
            }

            // Download file
            const fileUrl = `https://api.telegram.org/file/bot${ctx.api.token}/${file.file_path}`;
            const response = await fetch(fileUrl);
            
            if (!response.ok) {
                await ctx.reply("❌ Failed to download file from Telegram");
                return;
            }

            // Ensure directory exists (create if needed)
            const saveDir = "/tmp/telegramCoder";
            if (!fs.existsSync(saveDir)) {
                console.log(`Creating directory: ${saveDir}`);
                fs.mkdirSync(saveDir, { recursive: true });
                console.log(`✓ Directory created: ${saveDir}`);
            }

            // Save file
            const savePath = path.join(saveDir, fileName);
            const buffer = Buffer.from(await response.arrayBuffer());
            fs.writeFileSync(savePath, buffer);

            // Handle voice/audio transcription with Whisper
            if (fileType === "voice" || fileType === "audio") {
                const userId = ctx.from?.id;
                
                await ctx.reply("🎙️ Transcription en cours avec Whisper... (large-v3, français)");
                
                try {
                    const transcription = await transcribeWithWhisper(savePath);
                    
                    if (!transcription || transcription.trim() === "") {
                        await ctx.reply("⚠️ Aucun texte détecté dans l'audio.");
                        return;
                    }
                    
                    console.log(`[Whisper] Transcription: ${transcription.substring(0, 100)}...`);
                    
                    // Check if user has an active OpenCode session
                    if (userId && this.opencodeService.hasActiveSession(userId)) {
                        // Send transcription to OpenCode
                        await ctx.reply("📤 Envoi de la transcription à OpenCode...");
                        
                        const response = await this.opencodeService.sendPrompt(
                            userId,
                            `[Transcription vocale]: ${transcription}`
                        );
                        
                        // Send the response back to user
                        await ctx.reply(response || "✅ Transcription envoyée à OpenCode!");
                    } else {
                        // No active session - automatically start one and send transcription
                        await ctx.reply("🎙️ Démarrage d'une session OpenCode...");
                        
                        try {
                            const sessionTitle = `Voice: ${transcription.substring(0, 30)}...`;
                            const newSession = await this.opencodeService.createSession(userId, sessionTitle);
                            
                            // Update chat context
                            this.opencodeService.updateSessionContext(userId, ctx.chat?.id || 0, ctx.message?.message_id || 0);
                            
                            await ctx.reply("✅ Session démarrée! Envoi de la transcription...");
                            
                            // Send transcription to new session
                            const response = await this.opencodeService.sendPrompt(
                                userId,
                                `[Transcription vocale]: ${transcription}`
                            );
                            
                            // Send response to user
                            await ctx.reply(response || "✅ Transcription envoyée à la nouvelle session!");
                        } catch (sessionError) {
                            console.error("[Voice] Session error:", sessionError);
                            // Fallback: just show transcription
                            await ctx.reply(
                                `🎙️ <b>Transcription:</b>\n\n${transcription}\n\n` +
                                `❌ Impossible de démarrer une session: ${sessionError instanceof Error ? sessionError.message : String(sessionError)}\n\n` +
                                `Utilise /opencode pour démarrer une session manuellement.`,
                                { parse_mode: "HTML" }
                            );
                        }
                    }
                    
                    // Optionally delete the audio file after transcription
                    fs.unlinkSync(savePath);
                    return;
                    
                } catch (whisperError) {
                    console.error("[Whisper] Error:", whisperError);
                    await ctx.reply(`❌ Erreur de transcription: ${whisperError instanceof Error ? whisperError.message : String(whisperError)}`);
                }
            }

            // Send confirmation with clickable filename
            const confirmMessage = await ctx.reply(
                `✅ <b>File saved!</b>\n\nPath: <code>${savePath}</code>\n\nTap the path to copy it.`,
                { parse_mode: "HTML" }
            );

            // Auto-delete after configured timeout
            await MessageUtils.scheduleMessageDeletion(
                ctx,
                confirmMessage.message_id,
                this.configService.getMessageDeleteTimeout()
            );

            console.log(`✓ File saved: ${savePath} (${fileType}, ${buffer.length} bytes)`);

        } catch (error) {
            console.error("Error handling file upload:", error);
            await ctx.reply(ErrorUtils.createErrorMessage("save file", error));
        }
    }
}
