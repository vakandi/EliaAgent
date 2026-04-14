import type { Event } from "@opencode-ai/sdk";
import type { Context } from "grammy";
import type { UserSession } from "../opencode.types.js";
import { escapeHtml, formatAsHtml } from "./utils.js";
import * as fs from 'fs';
import * as path from 'path';

type SessionErrorEvent = Extract<Event, { type: "session.error" }>;

export default async function sessionErrorHandler(
    event: SessionErrorEvent,
    ctx: Context,
    userSession: UserSession
): Promise<string | null> {
    console.log('[session.error handler] Processing error event');
    
    const eventsDir = path.join(process.cwd(), 'events');
    if (!fs.existsSync(eventsDir)) {
        fs.mkdirSync(eventsDir, { recursive: true });
    }
    
    const eventType = event.type.replace(/\./g, '-');
    const filePath = path.join(eventsDir, `${eventType}.last.json`);
    fs.writeFileSync(filePath, JSON.stringify(event, null, 2), 'utf8');
    
    const errorLogPath = path.join(eventsDir, 'session-errors.json');
    let errorLog: any[] = [];
    if (fs.existsSync(errorLogPath)) {
        try {
            errorLog = JSON.parse(fs.readFileSync(errorLogPath, 'utf8'));
        } catch (e) {
            errorLog = [];
        }
    }
    
    const errorEntry = {
        timestamp: Date.now(),
        sessionId: userSession.sessionId,
        error: event.properties?.error || 'Unknown error',
        message: event.properties?.message || 'No message',
        stack: event.properties?.stack || 'No stack'
    };
    
    errorLog.push(errorEntry);
    fs.writeFileSync(errorLogPath, JSON.stringify(errorLog, null, 2), 'utf8');
    
    return null;
}
