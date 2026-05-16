import type { Event } from "@opencode-ai/sdk";
import { createOpencodeClient } from "@opencode-ai/sdk";
import type { Context } from "grammy";
import type { UserSession } from "../opencode.types.js";
import { sendAndAutoDelete } from "./utils.js";

type MessageUpdatedEvent = Extract<Event, { type: "message.updated" }>;

export default async function messageUpdatedHandler(
    event: MessageUpdatedEvent,
    ctx: Context,
    userSession: UserSession
): Promise<string | null> {
    try {
        const { info } = event.properties;
        
        // Check if title exists in info.summary
        if (info?.summary?.title) {
            const title = info.summary.title;
            
            // Update the session title using OpenCode SDK
            const client = createOpencodeClient({ 
                baseUrl: process.env.OPENCODE_BASE_URL || "http://localhost:4000" 
            });
            
            await client.session.update({
                path: { id: userSession.sessionId },
                body: { title }
            });
            
            console.log(`✓ Updated session title: "${title}"`);
            
            // Send the new title to the user and auto-delete
            await sendAndAutoDelete(ctx, `📝 New title: ${title}`, 2500);
        }
    } catch (error) {
        console.log("Error in message.updated handler:", error);
    }
    
    return null;
}
