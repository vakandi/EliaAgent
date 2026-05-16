/**
 * CLI entry point for TelegramCoder
 * Allows running via npx: npx @tommertom/telegramcoder
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import * as fs from 'fs';
import * as readline from 'readline';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Prompts user for yes/no confirmation
 */
function promptUser(question: string): Promise<boolean> {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    return new Promise((resolve) => {
        rl.question(question, (answer) => {
            rl.close();
            resolve(answer.toLowerCase().trim() === 'y' || answer.toLowerCase().trim() === 'yes');
        });
    });
}

/**
 * Handles Docker setup - copies Dockerfile, docker-compose.yml, and creates .env to current directory
 */
async function handleDockerSetup(): Promise<void> {
    console.log('🐳 Docker Setup Mode\n');

    const currentDir = process.cwd();
    const packageDir = join(__dirname, '..');

    const dockerfilePath = join(currentDir, 'Dockerfile');
    const dockerComposePath = join(currentDir, 'docker-compose.yml');
    const envPath = join(currentDir, '.env');

    const dockerfileSource = join(packageDir, 'Dockerfile');
    const dockerComposeSource = join(packageDir, 'docker-compose.yml');

    // Check if files exist
    const dockerfileExists = fs.existsSync(dockerfilePath);
    const dockerComposeExists = fs.existsSync(dockerComposePath);
    const envExists = fs.existsSync(envPath);

    // Prompt if Dockerfile exists
    if (dockerfileExists) {
        const overwrite = await promptUser('⚠️  Dockerfile already exists. Overwrite? (y/N): ');
        if (!overwrite) {
            console.log('❌ Skipping Dockerfile creation.');
        } else {
            copyDockerfile(dockerfileSource, dockerfilePath);
        }
    } else {
        copyDockerfile(dockerfileSource, dockerfilePath);
    }

    // Prompt if docker-compose.yml exists
    if (dockerComposeExists) {
        const overwrite = await promptUser('⚠️  docker-compose.yml already exists. Overwrite? (y/N): ');
        if (!overwrite) {
            console.log('❌ Skipping docker-compose.yml creation.');
        } else {
            copyDockerCompose(dockerComposeSource, dockerComposePath);
        }
    } else {
        copyDockerCompose(dockerComposeSource, dockerComposePath);
    }

    // Skip .env creation if it already exists (contains sensitive data)
    if (envExists) {
        console.log('ℹ️  .env file already exists. Keeping existing configuration.');
    } else {
        writeEnvFile(envPath);
    }

    console.log('\n✅ Docker setup complete!');
    console.log('\n📝 Next steps:');
    console.log('   1. Edit the .env file with your Telegram bot token and user IDs');
    console.log('   2. Run: docker-compose up -d');
    console.log('   3. View logs: docker-compose logs -f\n');
}

/**
 * Copies Dockerfile from the package to the specified path
 */
function copyDockerfile(sourcePath: string, destinationPath: string): void {
    try {
        if (!fs.existsSync(sourcePath)) {
            console.log(`❌ Dockerfile not found in package at ${sourcePath}`);
            console.log('   This might be a development environment. Checking parent directory...');
            return;
        }
        fs.copyFileSync(sourcePath, destinationPath);
        console.log(`✅ Copied Dockerfile to ${destinationPath}`);
    } catch (error) {
        console.error(`❌ Failed to copy Dockerfile: ${error}`);
    }
}

/**
 * Copies docker-compose.yml from the package to the specified path
 */
function copyDockerCompose(sourcePath: string, destinationPath: string): void {
    try {
        if (!fs.existsSync(sourcePath)) {
            console.log(`❌ docker-compose.yml not found in package at ${sourcePath}`);
            console.log('   This might be a development environment. Checking parent directory...');
            return;
        }
        fs.copyFileSync(sourcePath, destinationPath);
        console.log(`✅ Copied docker-compose.yml to ${destinationPath}`);
    } catch (error) {
        console.error(`❌ Failed to copy docker-compose.yml: ${error}`);
    }
}

/**
 * Writes .env file to the specified path
 */
function writeEnvFile(path: string): void {
    const envContent = `# Environment Variables

# Your Telegram bot tokens from @BotFather, separated by commas
# You can specify one or more tokens to run multiple bot instances
# Example: TELEGRAM_BOT_TOKENS=1234567890:AABBCCDDEEFFGGHHIIJJKKLLMMNNOOPPQQrrss,9876543210:ZZYYXXWWVVUUTTSSRRQQPPOONNMMllkkjjii
TELEGRAM_BOT_TOKENS=

# Comma-separated list of Telegram user IDs allowed to use the bot
# Example: ALLOWED_USER_IDS=123456789,987654321
ALLOWED_USER_IDS=

# Admin user ID who receives notifications about unauthorized access attempts
# This user will be notified when someone not in ALLOWED_USER_IDS tries to use the bot
# Example: ADMIN_USER_ID=123456789
ADMIN_USER_ID=

# Message Configuration
# Message auto-delete timeout in milliseconds (default: 10000 = 10 seconds)
# Time to wait before automatically deleting confirmation messages
# Set to 0 to disable auto-deletion of messages
MESSAGE_DELETE_TIMEOUT=10000
`;

    fs.writeFileSync(path, envContent);
    console.log(`✅ Created .env file at ${path}`);
}

// Parse command-line arguments
const args = process.argv.slice(2);
const dockerFlag = args.includes('--docker');

console.log('🤖 TelegramCoder - AI-Powered Telegram Bot');
console.log('================================================\n');

// Handle --docker flag
if (dockerFlag) {
    (async () => {
        await handleDockerSetup();
        process.exit(0);
    })();
} else {
    // Continue with normal startup
    startBot();
}

function startBot() {
    // Windows compatibility warning
    if (process.platform === 'win32') {
        console.log('⚠️  Windows is not supported for direct installation.');
        console.log('   TelegramCoder uses node-pty which requires native compilation.');
        console.log('\n   📦 Please use Docker instead:');
        console.log('   See https://github.com/Tommertom/telegramCoder/blob/main/DOCKER_GUIDE.md\n');
    }

    // Check if .env file exists in current directory
    const envPath = join(process.cwd(), '.env');
    const templatePath = join(__dirname, '..', 'dot-env.template');

    if (!fs.existsSync(envPath)) {
        console.log('⚠️  No .env file found in current directory!');
        console.log('\n📝 Creating .env template...\n');

        if (fs.existsSync(templatePath)) {
            fs.copyFileSync(templatePath, envPath);
            console.log('✅ Created .env file from template');
            console.log('\n🔧 Please edit .env and configure:');
            console.log('   - TELEGRAM_BOT_TOKENS (required)');
            console.log('   - ALLOWED_USER_IDS (required)');
            console.log('\nThen run the command again.\n');
            process.exit(0);
        } else {
            console.log('❌ Template file not found. Please create .env manually.');
            console.log('\nRequired variables:');
            console.log('   TELEGRAM_BOT_TOKENS=your_bot_token_here');
            console.log('   ALLOWED_USER_IDS=your_user_id_here\n');
            process.exit(1);
        }
    }

    // Check if .env has the required variables
    const envContent = fs.readFileSync(envPath, 'utf-8');
    const hasToken = /TELEGRAM_BOT_TOKENS\s*=\s*.+/.test(envContent);
    const hasUsers = /ALLOWED_USER_IDS\s*=\s*.+/.test(envContent);

    if (!hasToken || !hasUsers) {
        console.log('⚠️  .env file is incomplete!\n');
        if (!hasToken) console.log('   ❌ Missing TELEGRAM_BOT_TOKENS');
        if (!hasUsers) console.log('   ❌ Missing ALLOWED_USER_IDS');
        console.log('\n🔧 Please edit .env and configure the required variables.\n');
        process.exit(1);
    }

    console.log('🚀 Starting TelegramCoder...\n');

    // Start the main application
    const appPath = join(__dirname, 'app.js');

    // Windows-compatible process spawning
    const isWindows = process.platform === 'win32';
    const child = spawn('node', [appPath], {
        stdio: 'inherit',
        env: { ...process.env, NODE_ENV: 'production' },
        // On Windows, we need shell: false for proper signal handling
        shell: false,
        windowsHide: true
    });

    child.on('exit', (code) => {
        if (code !== 0) {
            console.error(`\n❌ TelegramCoder exited with code ${code}`);
            process.exit(code || 1);
        }
    });

    child.on('error', (err) => {
        console.error(`\n❌ Failed to start TelegramCoder: ${err.message}`);
        process.exit(1);
    });

    // Cross-platform signal handling
    if (isWindows) {
        // On Windows, use readline to handle Ctrl+C
        if (process.stdin.isTTY) {
            const readline = require('readline');
            readline.createInterface({
                input: process.stdin,
                output: process.stdout
            });
        }

        // Windows doesn't support POSIX signals properly, just kill the child
        process.on('SIGINT', () => {
            child.kill();
            process.exit(0);
        });
        process.on('SIGTERM', () => {
            child.kill();
            process.exit(0);
        });
        process.on('SIGBREAK', () => {
            child.kill();
            process.exit(0);
        });
    } else {
        // Unix-like systems support proper signal forwarding
        process.on('SIGINT', () => child.kill('SIGINT'));
        process.on('SIGTERM', () => child.kill('SIGTERM'));
    }
}
