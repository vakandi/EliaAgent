import type { Event } from "@opencode-ai/sdk";
import type { Context } from "grammy";
import type { UserSession } from "../opencode.types.js";
import { sendAndAutoDelete } from "./utils.js";

type TodoUpdatedEvent = Extract<Event, { type: "todo.updated" }>;

export default async function todoUpdatedHandler(
    event: TodoUpdatedEvent,
    ctx: Context,
    userSession: UserSession
): Promise<string | null> {
    try {
        const { todos } = event.properties;
        
        if (todos && Array.isArray(todos)) {
            const todoCount = todos.length;
            await sendAndAutoDelete(ctx, `📋 ${todoCount} todo${todoCount !== 1 ? 's' : ''}`, 2500);
        }
    } catch (error) {
        console.log("Error in todo.updated handler:", error);
    }
    
    return null;
}
