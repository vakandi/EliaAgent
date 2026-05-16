import { Context } from 'grammy';
import { ConfigService } from '../services/config.service.js';

/**
 * Utility class for message-related operations
 */
export class MessageUtils {
    /**
     * Schedules a message for automatic deletion after a timeout
     * @param ctx - The context object containing bot API
     * @param messageId - The ID of the message to delete
     * @param timeoutMs - Timeout in milliseconds (default: 10000 = 10 seconds)
     */
    static async scheduleMessageDeletion(
        ctx: Context,
        messageId: number,
        timeoutMs: number = 10000
    ): Promise<void> {
        if (timeoutMs <= 0) {
            return;
        }

        setTimeout(async () => {
            try {
                await ctx.api.deleteMessage(ctx.chat!.id, messageId);
            } catch (error) {
                console.error('Failed to delete message:', error);
            }
        }, timeoutMs);
    }

    /**
     * Escapes special characters for Telegram's Markdown format
     * @param text - The text to escape
     * @returns The escaped text safe for use in Markdown messages
     */
    static escapeMarkdown(text: string): string {
        // Escape special characters for Telegram's Markdown
        return text.replace(/[_*[\]()~`>#+\-=|{}.!\\]/g, '\\$&');
    }
}
