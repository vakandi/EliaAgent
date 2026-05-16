import type { Context } from "grammy";

let toolMessageId: number | null = null;
let toolDeleteTimeout: NodeJS.Timeout | null = null;

export async function handleToolPart(ctx: Context, part: any): Promise<void> {
    try {
        // Clear existing tool delete timeout
        if (toolDeleteTimeout) {
            clearTimeout(toolDeleteTimeout);
            toolDeleteTimeout = null;
        }

        if (!toolMessageId && part.tool) {
            // Send tool name message
            const sentMessage = await ctx.reply(`🔧 ${part.tool}`);
            toolMessageId = sentMessage.message_id;
        }

        // Set timeout to delete message after 2.5 seconds (half of 5 seconds)
        toolDeleteTimeout = setTimeout(async () => {
            try {
                if (toolMessageId) {
                    await ctx.api.deleteMessage(ctx.chat!.id, toolMessageId);
                    toolMessageId = null;
                }
            } catch (error) {
                console.log("Error deleting tool message:", error);
            }
        }, 2500);

    } catch (error) {
        console.log("Error in tool part handler:", error);
    }
}