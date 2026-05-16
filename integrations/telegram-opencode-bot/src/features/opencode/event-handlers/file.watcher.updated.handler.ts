import type { Event } from "@opencode-ai/sdk";
import type { Context } from "grammy";
import type { UserSession } from "../opencode.types.js";
import * as fs from 'fs';
import * as path from 'path';

type FileWatcherUpdatedEvent = Extract<Event, { type: "file.watcher.updated" }>;

export default async function fileWatcherUpdatedHandler(
    event: FileWatcherUpdatedEvent,
    ctx: Context,
    userSession: UserSession
): Promise<string | null> {
    console.log(event.type);
    
    const eventsDir = path.join(process.cwd(), 'events');
    if (!fs.existsSync(eventsDir)) {
        fs.mkdirSync(eventsDir, { recursive: true });
    }

    const eventType = event.type.replace(/\./g, '-');
    const filePath = path.join(eventsDir, `${eventType}.last.json`);
    fs.writeFileSync(filePath, JSON.stringify(event, null, 2), 'utf8');
    
    return null;
}
