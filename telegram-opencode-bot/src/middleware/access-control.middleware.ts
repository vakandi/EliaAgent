import { Context, NextFunction, Bot } from 'grammy';
import { ConfigService } from '../services/config.service.js';
import { MessageUtils } from '../utils/message.utils.js';

export class AccessControlMiddleware {
    private static allowedUserIds: Set<number> | null = null;
    private static adminUserId: number | null = null;
    private static notifiedUsers: Set<number> = new Set();
    private static configService: ConfigService | null = null;
    private static bot: Bot | null = null;

    static setConfigService(config: ConfigService): void {
        AccessControlMiddleware.configService = config;
    }

    static setBot(bot: Bot): void {
        AccessControlMiddleware.bot = bot;
    }

    private static initializeAllowedUsers(): Set<number> {
        if (AccessControlMiddleware.allowedUserIds === null) {
            if (!AccessControlMiddleware.configService) {
                throw new Error('ConfigService not set in AccessControlMiddleware');
            }

            const allowedIds = AccessControlMiddleware.configService.getAllowedUserIds();
            AccessControlMiddleware.allowedUserIds = new Set(allowedIds);

            // Get admin user ID from config, or fall back to first allowed user
            const configAdminId = AccessControlMiddleware.configService.getAdminUserId();
            if (configAdminId) {
                AccessControlMiddleware.adminUserId = configAdminId;
            } else {
                const firstUser = Array.from(AccessControlMiddleware.allowedUserIds)[0];
                if (firstUser) {
                    AccessControlMiddleware.adminUserId = firstUser;
                }
            }

            console.log(`Access Control: ${AccessControlMiddleware.allowedUserIds.size} user(s) allowed`);
            if (AccessControlMiddleware.adminUserId) {
                console.log(`Access Control: Admin user ID: ${AccessControlMiddleware.adminUserId}`);
            }
        }
        return AccessControlMiddleware.allowedUserIds;
    }

    static async requireAccess(ctx: Context, next: NextFunction): Promise<void> {
        if (!ctx.from) {
            await ctx.reply("Unable to identify user. Please try again.");
            return;
        }

        const userId = ctx.from.id;
        const allowedUsers = AccessControlMiddleware.initializeAllowedUsers();

        if (!allowedUsers.has(userId)) {
            console.log(`Unauthorized access attempt from user ${userId}`);

            // Send notification to admin about unauthorized access attempt
            await AccessControlMiddleware.notifyAdminOfUnauthorizedAccess(ctx);

            // Check if auto-kill is enabled
            if (AccessControlMiddleware.isAutoKillEnabled()) {
                // Send immediate response to unauthorized user
                await ctx.reply(
                    "🚫 Unauthorized access detected.\n\n" +
                    `The Telegram User ID is: ${userId}\n\n` +
                    "The bot worker is now shutting down for security reasons."
                );

                console.log(`AUTO_KILL: Unauthorized access from ${userId}. Shutting down worker...`);

                // Kill this worker process
                setTimeout(() => {
                    process.exit(1);
                }, 1000);
                return;
            }

            // Standard denial (no auto-kill)
            await ctx.reply(
                "🚫 You don't have access to this bot.\n\n" +
                `Your Telegram User ID is: ${userId}\n\n` +
                "Please contact the bot administrator to get access."
            );
            return;
        }

        await next();
    }

    static isAllowed(userId: number): boolean {
        const allowedUsers = AccessControlMiddleware.initializeAllowedUsers();
        return allowedUsers.has(userId);
    }

    static getAllowedUserIds(): number[] {
        const allowedUsers = this.initializeAllowedUsers();
        return Array.from(allowedUsers);
    }

    static isAdmin(userId: number): boolean {
        this.initializeAllowedUsers();
        return AccessControlMiddleware.adminUserId === userId;
    }

    static async notifyAdminOfDownload(ctx: Context, url: string): Promise<void> {
        if (!AccessControlMiddleware.bot || !AccessControlMiddleware.adminUserId || !ctx.from) {
            return;
        }

        const userId = ctx.from.id;
        
        if (AccessControlMiddleware.isAdmin(userId)) {
            return;
        }

        try {
            const username = ctx.from.username ? `@${ctx.from.username}` : 'No username';
            const firstName = ctx.from.first_name || 'Unknown';
            const lastName = ctx.from.last_name || '';
            const fullName = `${firstName} ${lastName}`.trim();

            const notificationMessage = [
                '📥 <b>Download Request</b>',
                '',
                '<b>User Information:</b>',
                `• Name: ${fullName}`,
                `• Username: ${username}`,
                `• User ID: <code>${userId}</code>`,
                '',
                '<b>Requested Link:</b>',
                `<code>${url}</code>`,
                '',
                `<i>Time: ${new Date().toLocaleString()}</i>`
            ].join('\n');

            const sentMessage = await AccessControlMiddleware.bot.api.sendMessage(
                AccessControlMiddleware.adminUserId,
                notificationMessage,
                { parse_mode: 'HTML' }
            );

            // Schedule message deletion using the configured timeout
            if (AccessControlMiddleware.configService && sentMessage) {
                const deleteTimeout = AccessControlMiddleware.configService.getMessageDeleteTimeout();
                if (deleteTimeout > 0) {
                    setTimeout(async () => {
                        try {
                            await AccessControlMiddleware.bot!.api.deleteMessage(
                                AccessControlMiddleware.adminUserId!,
                                sentMessage.message_id
                            );
                        } catch (error) {
                            console.error('Failed to delete admin notification message:', error);
                        }
                    }, deleteTimeout);
                }
            }

            console.log(`Notified admin ${AccessControlMiddleware.adminUserId} about download request from ${userId}`);
        } catch (error) {
            console.error('Failed to notify admin of download request:', error);
        }
    }

    private static isAutoKillEnabled(): boolean {
        if (!AccessControlMiddleware.configService) {
            return false;
        }
        return AccessControlMiddleware.configService.isAutoKillEnabled();
    }

    private static async notifyAdminOfUnauthorizedAccess(ctx: Context): Promise<void> {
        // Only notify if we have a bot instance and admin user ID
        if (!AccessControlMiddleware.bot || !AccessControlMiddleware.adminUserId || !ctx.from) {
            return;
        }

        try {
            const userId = ctx.from.id;
            const username = ctx.from.username ? `@${ctx.from.username}` : 'No username';
            const firstName = ctx.from.first_name || 'Unknown';
            const lastName = ctx.from.last_name || '';
            const fullName = `${firstName} ${lastName}`.trim();

            const message = ctx.message?.text || ctx.callbackQuery?.data || 'Unknown action';

            const notificationMessage = [
                '🚨 <b>Unauthorized Access Attempt</b>',
                '',
                '<b>User Information:</b>',
                `• Name: ${fullName}`,
                `• Username: ${username}`,
                `• User ID: <code>${userId}</code>`,
                '',
                '<b>Attempted Action:</b>',
                `<code>${message}</code>`,
                '',
                `<i>Time: ${new Date().toLocaleString()}</i>`
            ].join('\n');

            const sentMessage = await AccessControlMiddleware.bot.api.sendMessage(
                AccessControlMiddleware.adminUserId,
                notificationMessage,
                { parse_mode: 'HTML' }
            );

            // Schedule message deletion using the configured timeout
            if (AccessControlMiddleware.configService && sentMessage) {
                const deleteTimeout = AccessControlMiddleware.configService.getMessageDeleteTimeout();
                if (deleteTimeout > 0) {
                    setTimeout(async () => {
                        try {
                            await AccessControlMiddleware.bot!.api.deleteMessage(
                                AccessControlMiddleware.adminUserId!,
                                sentMessage.message_id
                            );
                        } catch (error) {
                            console.error('Failed to delete admin notification message:', error);
                        }
                    }, deleteTimeout);
                }
            }

            console.log(`Notified admin ${AccessControlMiddleware.adminUserId} about unauthorized access from ${userId}`);
        } catch (error) {
            console.error('Failed to notify admin of unauthorized access:', error);
        }
    }
}
