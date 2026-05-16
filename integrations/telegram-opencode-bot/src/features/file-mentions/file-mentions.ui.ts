/**
 * Telegram UI helpers for file mention selection
 */

import type { Context } from "grammy";
import type { FileMention, FileMatch } from "./file-mentions.types.js";

export class FileMentionUI {
    /**
     * Show file picker for a single mention with multiple matches
     */
    async showFilePicker(
        ctx: Context,
        mention: FileMention,
        matches: FileMatch[]
    ): Promise<number | null> {
        if (matches.length === 0) {
            await ctx.reply(`❌ No files found matching: ${mention.raw}`);
            return null;
        }
        
        if (matches.length === 1) {
            // Auto-select if only one match
            return 0;
        }
        
        // Build inline keyboard with file options
        const keyboard = matches.slice(0, 10).map((match, index) => [
            {
                text: `${index + 1}. ${this.shortenPath(match.path)}`,
                callback_data: `file:select:${index}`
            }
        ]);
        
        keyboard.push([
            { text: "❌ Cancel", callback_data: "file:cancel" }
        ]);
        
        const message = await ctx.reply(
            `🔍 Found ${matches.length} match${matches.length > 1 ? 'es' : ''} for <code>${this.escapeHtml(mention.raw)}</code>:\n\n` +
            `Please select the correct file:`,
            {
                parse_mode: "HTML",
                reply_markup: { inline_keyboard: keyboard }
            }
        );
        
        // Wait for user selection
        return new Promise((resolve) => {
            const listener = async (callbackCtx: Context) => {
                const data = callbackCtx.callbackQuery?.data;
                if (!data) return;
                
                if (data === "file:cancel") {
                    await callbackCtx.answerCallbackQuery("Cancelled");
                    await ctx.api.editMessageText(
                        message.chat.id,
                        message.message_id,
                        "❌ File selection cancelled"
                    );
                    resolve(null);
                } else if (data.startsWith("file:select:")) {
                    const index = parseInt(data.split(":")[2]);
                    await callbackCtx.answerCallbackQuery();
                    await ctx.api.editMessageText(
                        message.chat.id,
                        message.message_id,
                        `✅ Selected: <code>${this.escapeHtml(matches[index].path)}</code>`,
                        { parse_mode: "HTML" }
                    );
                    resolve(index);
                }
            };
            
            // Note: In production, you'd register this callback handler properly
            // For now, this is a simplified version
            ctx.api.on("callback_query", listener as any);
        });
    }
    
    /**
     * Show summary of all file matches and get confirmations
     */
    async confirmAllMatches(
        ctx: Context,
        matches: Map<FileMention, FileMatch[]>
    ): Promise<Map<FileMention, FileMatch> | null> {
        const resolved = new Map<FileMention, FileMatch>();
        
        for (const [mention, fileMatches] of matches.entries()) {
            if (fileMatches.length === 0) {
                await ctx.reply(`❌ No files found matching: ${mention.raw}`);
                return null;
            }
            
            if (fileMatches.length === 1) {
                // Auto-select exact match
                resolved.set(mention, fileMatches[0]);
                await ctx.reply(
                    `✅ <code>${this.escapeHtml(mention.raw)}</code> → <code>${this.escapeHtml(fileMatches[0].path)}</code>`,
                    { parse_mode: "HTML" }
                );
            } else {
                // Need user selection
                const selectedIndex = await this.showFilePicker(ctx, mention, fileMatches);
                if (selectedIndex === null) {
                    return null; // User cancelled
                }
                resolved.set(mention, fileMatches[selectedIndex]);
            }
        }
        
        return resolved;
    }
    
    /**
     * Show error message for file mention
     */
    async showError(ctx: Context, mention: FileMention, error: string): Promise<void> {
        await ctx.reply(
            `❌ Error with <code>${this.escapeHtml(mention.raw)}</code>:\n${error}`,
            { parse_mode: "HTML" }
        );
    }
    
    /**
     * Show loading indicator
     */
    async showSearching(ctx: Context, mentionCount: number): Promise<any> {
        return await ctx.reply(
            `🔍 Searching for ${mentionCount} file${mentionCount > 1 ? 's' : ''}...`
        );
    }
    
    /**
     * Shorten long file paths for display
     */
    private shortenPath(path: string, maxLength: number = 50): string {
        if (path.length <= maxLength) return path;
        
        const parts = path.split('/');
        if (parts.length <= 2) return path;
        
        // Show first and last parts
        const filename = parts[parts.length - 1];
        const remaining = maxLength - filename.length - 3; // -3 for "..."
        
        if (remaining <= 0) return `.../${filename}`;
        
        let prefix = "";
        for (let i = 0; i < parts.length - 1; i++) {
            if ((prefix + parts[i]).length < remaining) {
                prefix += parts[i] + "/";
            } else {
                break;
            }
        }
        
        return `${prefix}.../${filename}`;
    }
    
    /**
     * Escape HTML special characters
     */
    private escapeHtml(text: string): string {
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }
}
