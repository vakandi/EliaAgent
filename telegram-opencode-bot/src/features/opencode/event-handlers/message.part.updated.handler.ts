import type { Event } from "@opencode-ai/sdk";
import type { Context } from "grammy";
import type { UserSession } from "../opencode.types.js";
import { handleTextPart } from "./message-part-updated/text-part.handler.js";
import { handleReasoningPart } from "./message-part-updated/reasoning-part.handler.js";
import { handleToolPart } from "./message-part-updated/tool-part.handler.js";

type MessagePartUpdatedEvent = Extract<Event, { type: "message.part.updated" }>;

export default async function messagePartUpdatedHandler(
    event: MessagePartUpdatedEvent,
    ctx: Context,
    userSession: UserSession
): Promise<string | null> {
    try {
        const { part } = event.properties;
        
        // Handle reasoning parts separately
        if (part.type === "reasoning") {
            await handleReasoningPart(ctx);
            return null;
        }
        
        // Handle tool calls separately
        if (part.type === "tool") {
            await handleToolPart(ctx, part);
            return null;
        }
        
        // Only process text parts
        if (part.type !== "text") {
            return null;
        }

        await handleTextPart(ctx, part.text);

    } catch (error) {
        console.log("Error in message.part.updated handler:", error);
    }

    return null;
}