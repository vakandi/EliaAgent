import { createOpencodeClient } from "@opencode-ai/sdk";
import type { Event } from "@opencode-ai/sdk";
import type { Context } from "grammy";
import type { UserSession } from "./opencode.types.js";
import { processEvent } from "./opencode.event-handlers.js";

export class OpenCodeService {
    private userSessions: Map<number, UserSession> = new Map();
    private baseUrl: string;
    private eventAbortControllers: Map<number, AbortController> = new Map();

    constructor(baseUrl?: string) {
        this.baseUrl = baseUrl || process.env.OPENCODE_SERVER_URL || "http://localhost:4096";
    }

    async createSession(userId: number, title?: string): Promise<UserSession> {
        const client = createOpencodeClient({ baseUrl: this.baseUrl });

        try {
            const result = await client.session.create({
                body: { title: title || `Telegram Session ${new Date().toISOString()}` },
            });

            if (!result.data) {
                throw new Error("Failed to create session");
            }

            const userSession: UserSession = {
                userId,
                sessionId: result.data.id,
                session: result.data,
                createdAt: new Date(),
                currentAgent: "build",
            };

            this.userSessions.set(userId, userSession);
            return userSession;
        } catch (error) {
            // Provide more helpful error message for connection failures
            if (error instanceof Error && (error.message.includes('fetch failed') || error.message.includes('ECONNREFUSED'))) {
                throw new Error(`Cannot connect to OpenCode server at ${this.baseUrl}. Please ensure:\n1. OpenCode server is running\n2. OPENCODE_SERVER_URL is configured correctly in .env file`);
            }
            throw error;
        }
    }

    getUserSession(userId: number): UserSession | undefined {
        return this.userSessions.get(userId);
    }

    updateSessionContext(userId: number, chatId: number, messageId: number): void {
        const session = this.userSessions.get(userId);
        if (session) {
            session.chatId = chatId;
            session.lastMessageId = messageId;
        }
    }

    async startEventStream(userId: number, ctx: Context): Promise<void> {
        const userSession = this.getUserSession(userId);
        if (!userSession || !userSession.chatId) {
            return;
        }

        // Stop any existing event stream for this user
        this.stopEventStream(userId);

        const abortController = new AbortController();
        this.eventAbortControllers.set(userId, abortController);

        const client = createOpencodeClient({ baseUrl: this.baseUrl });

        try {
            const events = await client.event.subscribe();

            for await (const event of events.stream) {
                if (abortController.signal.aborted) {
                    break;
                }

                // Process event through handler
                await processEvent(event, ctx, userSession);
            }
        } catch (error) {
            console.error("Event stream error:", error);
        } finally {
            this.eventAbortControllers.delete(userId);
        }
    }

    stopEventStream(userId: number): void {
        const controller = this.eventAbortControllers.get(userId);
        if (controller) {
            controller.abort();
            this.eventAbortControllers.delete(userId);
        }
    }

    async sendPrompt(userId: number, text: string, fileContext?: string): Promise<string> {
        const userSession = this.getUserSession(userId);

        if (!userSession) {
            throw new Error("No active session. Please use /opencode to start a session first.");
        }

        const client = createOpencodeClient({ baseUrl: this.baseUrl });

        try {
            // Prepend file context if provided
            const fullPrompt = fileContext ? `${fileContext}\n\n${text}` : text;
            
            const result = await client.session.prompt({
                path: { id: userSession.sessionId },
                body: {
                    parts: [{ type: "text", text: fullPrompt }],
                    agent: userSession.currentAgent,
                },
            });

            if (!result.data) {
                throw new Error("Failed to send prompt");
            }

            // Extract text from response parts
            const textParts = result.data.parts
                ?.filter((part) => part.type === "text")
                .map((part) => part.text)
                .join("\n");

            return textParts || "No response received";
        } catch (error) {
            // Provide more helpful error message for connection failures
            if (error instanceof Error && (error.message.includes('fetch failed') || error.message.includes('ECONNREFUSED'))) {
                throw new Error(`Cannot connect to OpenCode server at ${this.baseUrl}. Please ensure the OpenCode server is running.`);
            }
            throw error;
        }
    }

    async deleteSession(userId: number): Promise<boolean> {
        const userSession = this.getUserSession(userId);

        if (!userSession) {
            return false;
        }

        // Stop event stream first
        this.stopEventStream(userId);

        const client = createOpencodeClient({ baseUrl: this.baseUrl });

        try {
            await client.session.delete({
                path: { id: userSession.sessionId },
            });
            this.userSessions.delete(userId);
            return true;
        } catch (error) {
            console.error(`Failed to delete session for user ${userId}:`, error);
            return false;
        }
    }

    hasActiveSession(userId: number): boolean {
        return this.userSessions.has(userId);
    }

    attachToSession(userId: number, sessionId: string, title?: string): void {
        const userSession: UserSession = {
            userId,
            sessionId,
            session: { id: sessionId, title: title || "Resumed Session" },
            createdAt: new Date(),
            currentAgent: "build",
            chatId: 0,
        };
        this.userSessions.set(userId, userSession);
    }

    async abortSession(userId: number): Promise<boolean> {
        const userSession = this.getUserSession(userId);

        if (!userSession) {
            return false;
        }

        const client = createOpencodeClient({ baseUrl: this.baseUrl });

        try {
            await client.session.abort({
                path: { id: userSession.sessionId },
            });
            return true;
        } catch (error) {
            console.error(`Failed to abort session for user ${userId}:`, error);
            return false;
        }
    }

    async getAvailableAgents(): Promise<Array<{ name: string; mode?: string; description?: string }>> {
        const client = createOpencodeClient({ baseUrl: this.baseUrl });

        try {
            const result = await client.app.agents();
            
            if (!result.data) {
                return [];
            }

            // Filter for user-selectable agents:
            // - mode must be "primary" (not "subagent")
            // - hidden must NOT be true
            // - exclude internal utility agents by name as well
            const internalAgents = ['compaction', 'title', 'summary'];

            const filtered = result.data
                .filter((agent: any) => {
                    // Exclude hidden agents
                    if (agent.hidden === true) {
                        console.log(`Filtering out hidden agent: ${agent.name}`);
                        return false;
                    }
                    
                    // Exclude subagents (only meant to be called by other agents)
                    if (agent.mode === "subagent") {
                        console.log(`Filtering out subagent: ${agent.name}`);
                        return false;
                    }
                    
                    // Exclude internal utility agents by name
                    if (internalAgents.includes(agent.name)) {
                        console.log(`Filtering out internal agent: ${agent.name}`);
                        return false;
                    }
                    
                    // Only include primary agents
                    return agent.mode === "primary" || agent.mode === "all";
                })
                .map((agent: any) => ({
                    name: agent.name || "unknown",
                    mode: agent.mode,
                    description: agent.description
                }));

            console.log("Filtered agents:", filtered.map((a: any) => a.name));
            return filtered;
        } catch (error) {
            console.error("Failed to get available agents:", error);
            return [];
        }
    }

    async cycleToNextAgent(userId: number): Promise<{ success: boolean; currentAgent?: string }> {
        const userSession = this.getUserSession(userId);

        if (!userSession) {
            return { success: false };
        }

        const client = createOpencodeClient({ baseUrl: this.baseUrl });

        try {
            // Get available primary agents (not hidden, not subagents)
            const agents = await this.getAvailableAgents();
            
            if (agents.length === 0) {
                console.error("No available agents to cycle through");
                return { success: false };
            }

            // Get current agent or default to first one
            const currentAgent = userSession.currentAgent || agents[0].name;
            
            // Find current agent index
            const currentIndex = agents.findIndex(a => a.name === currentAgent);
            
            // Cycle to next agent (wrap around to start if at end)
            const nextIndex = (currentIndex + 1) % agents.length;
            const nextAgent = agents[nextIndex].name;
            
            // Update user session with new agent
            userSession.currentAgent = nextAgent;
            
            console.log(`✓ Cycled agent for user ${userId}: ${currentAgent} → ${nextAgent}`);
            console.log(`  Available agents: ${agents.map(a => a.name).join(", ")}`);
            
            return { success: true, currentAgent: nextAgent };
        } catch (error) {
            console.error(`Failed to cycle agent for user ${userId}:`, error);
            return { success: false };
        }
    }

    async updateSessionTitle(userId: number, title: string): Promise<{ success: boolean; message?: string }> {
        const userSession = this.getUserSession(userId);

        if (!userSession) {
            return { success: false, message: "No active session found" };
        }

        const client = createOpencodeClient({ baseUrl: this.baseUrl });

        try {
            await client.session.update({
                path: { id: userSession.sessionId },
                body: { title }
            });

            console.log(`✓ Updated session title for user ${userId}: "${title}"`);
            return { success: true };
        } catch (error) {
            console.error(`Failed to update session title for user ${userId}:`, error);
            return { success: false, message: "Failed to update session title" };
        }
    }

    async getProjects(): Promise<Array<{ id: string; worktree: string }>> {
        const client = createOpencodeClient({ baseUrl: this.baseUrl });

        try {
            const result = await client.project.list();
            
            if (!result.data) {
                return [];
            }

            return result.data.map((project: any) => ({
                id: project.id,
                worktree: project.worktree
            }));
        } catch (error) {
            console.error("Failed to get projects:", error);
            return [];
        }
    }

    async getSessions(limit: number = 5): Promise<Array<{ id: string; title: string; created: number; updated: number }>> {
        const client = createOpencodeClient({ baseUrl: this.baseUrl });

        try {
            const result = await client.session.list();
            
            if (!result.data) {
                return [];
            }

            // Sort by updated time (most recent first) and limit to specified number
            return result.data
                .sort((a: any, b: any) => b.time.updated - a.time.updated)
                .slice(0, limit)
                .map((session: any) => ({
                    id: session.id,
                    title: session.title,
                    created: session.time.created,
                    updated: session.time.updated
                }));
        } catch (error) {
            console.error("Failed to get sessions:", error);
            return [];
        }
    }

    async undoLastMessage(userId: number): Promise<{ success: boolean; message?: string }> {
        const userSession = this.getUserSession(userId);

        if (!userSession) {
            return { success: false, message: "No active session found" };
        }

        const client = createOpencodeClient({ baseUrl: this.baseUrl });

        try {
            // Check if revert method exists on the client
            if (typeof client.session.revert !== 'function') {
                return { success: false, message: "Undo is not available in this SDK version" };
            }

            await client.session.revert({
                path: { id: userSession.sessionId }
            });

            console.log(`✓ Undid last message for user ${userId}`);
            return { success: true };
        } catch (error) {
            console.error(`Failed to undo message for user ${userId}:`, error);
            return { success: false, message: "Failed to undo last message" };
        }
    }

    async redoLastMessage(userId: number): Promise<{ success: boolean; message?: string }> {
        const userSession = this.getUserSession(userId);

        if (!userSession) {
            return { success: false, message: "No active session found" };
        }

        const client = createOpencodeClient({ baseUrl: this.baseUrl });

        try {
            // Check if unrevert method exists on the client
            if (typeof client.session.unrevert !== 'function') {
                return { success: false, message: "Redo is not available in this SDK version" };
            }

            await client.session.unrevert({
                path: { id: userSession.sessionId }
            });

            console.log(`✓ Redid last message for user ${userId}`);
            return { success: true };
        } catch (error) {
            console.error(`Failed to redo message for user ${userId}:`, error);
            return { success: false, message: "Failed to redo last message" };
        }
    }
}
