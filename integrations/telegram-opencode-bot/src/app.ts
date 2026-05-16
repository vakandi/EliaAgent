import { Bot } from "grammy";
import { ConfigService } from './services/config.service.js';
import { OpenCodeService } from './features/opencode/opencode.service.js';
import { OpenCodeBot } from './features/opencode/opencode.bot.js';
import { AnalyzeBottleneckBot } from './features/opencode/analyze-bottleneck.bot.js';
import { registerExtrapromptHandlers } from './features/elia-extraprompt/extraprompt.handler.js';
import { AccessControlMiddleware } from './middleware/access-control.middleware.js';
import dotenv from 'dotenv';
import * as fs from 'fs';
import * as path from 'path';

console.log('[TelegramCoder] Starting bot...');

dotenv.config();

// Initialize config service
const configService = new ConfigService();

try {
    configService.validate();
    console.log('[TelegramCoder] Configuration loaded successfully');
    console.log(configService.getDebugInfo());
} catch (error) {
    console.error('[TelegramCoder] Configuration error:', error);
    process.exit(1);
}

// Get the first bot token
const tokens = configService.getTelegramBotTokens();
if (tokens.length === 0) {
    console.error('[TelegramCoder] No bot tokens found in configuration');
    process.exit(1);
}

const botToken = tokens[0];
console.log(`[TelegramCoder] Initializing with token: ${botToken.substring(0, 10)}...`);

// Create bot instance
const bot = new Bot(botToken);

// Initialize services
const opencodeService = new OpenCodeService();

// Set global error handler to prevent crashes
bot.catch((err) => {
    const ctx = err.ctx;
    console.error(`[TelegramCoder] Error while handling update ${ctx.update.update_id}:`, err.error);
});

// Set config service for access control
AccessControlMiddleware.setConfigService(configService);

// Set bot instance for access control (needed for admin notifications)
AccessControlMiddleware.setBot(bot);

// Initialize the OpenCode bot
const opencodeBot = new OpenCodeBot(opencodeService, configService);
const analyzeBottleneckBot = new AnalyzeBottleneckBot(opencodeService, configService);

// Register handlers
opencodeBot.registerHandlers(bot);
analyzeBottleneckBot.registerHandlers(bot);
registerExtrapromptHandlers(bot);

async function startBot() {
    try {
        console.log('[TelegramCoder] Starting initialization...');

        // Clean up media directory if configured
        if (configService.shouldCleanUpMediaDir()) {
            const botMediaPath = path.join(configService.getMediaTmpLocation(), 'bot-1');
            if (fs.existsSync(botMediaPath)) {
                console.log(`[TelegramCoder] Cleaning up media directory: ${botMediaPath}`);
                fs.rmSync(botMediaPath, { recursive: true, force: true });
                console.log('[TelegramCoder] ✅ Media directory cleaned');
            }
        }

        // Get bot info
        try {
            const me = await bot.api.getMe();
            const fullName = [me.first_name, me.last_name].filter(Boolean).join(" ");
            console.log(`[TelegramCoder] Bot info: ${fullName} (@${me.username})`);
        } catch (error) {
            console.error('[TelegramCoder] Failed to get bot info:', error);
        }

        // Set bot commands for Telegram UI
        try {
            await bot.api.setMyCommands([
                { command: 'start', description: 'Show help message' },
                { command: 'help', description: 'Show help message' },
                { command: 'opencode', description: 'Start an OpenCode session' },
                { command: 'rename', description: 'Rename current session' },
                { command: 'endsession', description: 'End your OpenCode session' },
                { command: 'esc', description: 'Abort current AI operation' },
                { command: 'sessions', description: 'List sessions' },
                { command: 'extraprompt', description: 'Run EliaAI agent with extra context' },
                { command: 'runs', description: 'List EliaAI agent runs (cron + extraprompt)' },
                { command: 'analyse_your_bottleneck', description: 'Analyze AI bottlenecks and issues' }
            ]);
            console.log('[TelegramCoder] ✅ Bot commands registered');
        } catch (error) {
            console.error('[TelegramCoder] Failed to set bot commands:', error);
        }

        // Start the bot using webhook instead of long polling (more reliable)
        console.log('[TelegramCoder] About to start bot with webhook...');
        
        // Set webhook (required for webhook mode)
        const webhookUrl = process.env.TELEGRAM_WEBHOOK_URL;
        
        if (webhookUrl) {
            console.log('[TelegramCoder] Using webhook mode:', webhookUrl);
            await bot.api.setWebhook(webhookUrl);
            console.log('[TelegramCoder] ✅ Webhook set successfully');
        } else {
            console.log('[TelegramCoder] No webhook URL, using long polling...');
            await bot.start({
                polling: {
                    timeout: 30,
                }
            });
        }
        console.log('[TelegramCoder] ✅ Bot started successfully');
    } catch (error) {
        console.error('[TelegramCoder] Failed to start:', error);
        process.exit(1);
    }
}

let shuttingDown = false;

/**
 * Graceful shutdown handler for cleanup on process termination
 */
async function gracefulShutdown(signal: string): Promise<void> {
    if (shuttingDown) {
        console.log('[TelegramCoder] Shutdown already in progress...');
        return;
    }

    shuttingDown = true;
    console.log(`[TelegramCoder] Received ${signal}, shutting down gracefully...`);

    try {
        // Stop bot
        await bot.stop();

        console.log('[TelegramCoder] ✅ Shutdown complete');
        process.exit(0);
    } catch (error) {
        console.error('[TelegramCoder] Error during shutdown:', error);
        process.exit(1);
    }
}

// Handle graceful shutdown for both SIGINT and SIGTERM
process.on('SIGINT', () => gracefulShutdown('SIGINT'));
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
    console.error('[TelegramCoder] Unhandled Rejection at:', promise, 'reason:', reason);
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
    console.error('[TelegramCoder] Uncaught Exception:', error);
    gracefulShutdown('UNCAUGHT_EXCEPTION');
});

// Start the bot
startBot().catch((error) => {
    console.error('[TelegramCoder] Fatal error:', error);
    process.exit(1);
});
