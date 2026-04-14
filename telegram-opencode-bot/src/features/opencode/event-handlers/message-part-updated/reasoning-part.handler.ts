import type { Context } from "grammy";

let reasoningMessageId: number | null = null;
let reasoningDeleteTimeout: NodeJS.Timeout | null = null;

export async function handleReasoningPart(ctx: Context): Promise<void> {
    try {
        // Clear existing reasoning delete timeout
        if (reasoningDeleteTimeout) {
            clearTimeout(reasoningDeleteTimeout);
            reasoningDeleteTimeout = null;
        }

        if (!reasoningMessageId) {
            // Send reasoning message
            const sentMessage = await ctx.reply("Reasoning");
            reasoningMessageId = sentMessage.message_id;
        }

        // Set timeout to delete message after 2.5 seconds (half of 5 seconds)
        reasoningDeleteTimeout = setTimeout(async () => {
            try {
                if (reasoningMessageId) {
                    await ctx.api.deleteMessage(ctx.chat!.id, reasoningMessageId);
                    reasoningMessageId = null;
                }
            } catch (error) {
                console.log("Error deleting reasoning message:", error);
            }
        }, 2500);

    } catch (error) {
        console.log("Error in reasoning part handler:", error);
    }
}