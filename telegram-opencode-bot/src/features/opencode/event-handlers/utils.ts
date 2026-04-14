export function escapeHtml(text: string): string {
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

export function formatAsHtml(text: string): string {
    // Convert markdown-style formatting to HTML
    // Note: Telegram HTML doesn't support <br> tags well, so we keep newlines
    return escapeHtml(text)
        // Convert code blocks ``` to <pre><code>
        .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
        // Convert inline code ` to <code>
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        // Convert **bold** to <b>
        .replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>')
        // Convert *italic* to <i>
        .replace(/\*([^*]+)\*/g, '<i>$1</i>')
        // Convert __underline__ to <u>
        .replace(/__([^_]+)__/g, '<u>$1</u>')
        // Convert ~~strikethrough~~ to <s>
        .replace(/~~([^~]+)~~/g, '<s>$1</s>')
        // Convert headers # ## ### to <b> (simple approach)
        .replace(/^###\s+(.*)$/gm, '<b>$1</b>')
        .replace(/^##\s+(.*)$/gm, '<b>$1</b>')
        .replace(/^#\s+(.*)$/gm, '<b>$1</b>');
    // Keep newlines as-is - Telegram HTML supports them natively
}

export async function sendAndAutoDelete(
    ctx: any,
    message: string,
    deleteAfterMs: number = 2500
): Promise<void> {
    try {
        const sentMessage = await ctx.reply(message);
        setTimeout(async () => {
            try {
                await ctx.api.deleteMessage(ctx.chat!.id, sentMessage.message_id);
            } catch (error) {
                console.log("Error deleting auto-delete message:", error);
            }
        }, deleteAfterMs);
    } catch (error) {
        console.log("Error sending auto-delete message:", error);
    }
}
