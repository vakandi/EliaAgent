#!/usr/bin/env node
var __require = /* @__PURE__ */ ((x) => typeof require !== "undefined" ? require : typeof Proxy !== "undefined" ? new Proxy(x, {
  get: (a, b) => (typeof require !== "undefined" ? require : a)[b]
}) : x)(function(x) {
  if (typeof require !== "undefined") return require.apply(this, arguments);
  throw Error('Dynamic require of "' + x + '" is not supported');
});

// src/cli.ts
import { spawn } from "child_process";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import * as fs from "fs";
import * as readline from "readline";
var __filename = fileURLToPath(import.meta.url);
var __dirname = dirname(__filename);
function promptUser(question) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.toLowerCase().trim() === "y" || answer.toLowerCase().trim() === "yes");
    });
  });
}
async function handleDockerSetup() {
  console.log("\u{1F433} Docker Setup Mode\n");
  const currentDir = process.cwd();
  const packageDir = join(__dirname, "..");
  const dockerfilePath = join(currentDir, "Dockerfile");
  const dockerComposePath = join(currentDir, "docker-compose.yml");
  const envPath = join(currentDir, ".env");
  const dockerfileSource = join(packageDir, "Dockerfile");
  const dockerComposeSource = join(packageDir, "docker-compose.yml");
  const dockerfileExists = fs.existsSync(dockerfilePath);
  const dockerComposeExists = fs.existsSync(dockerComposePath);
  const envExists = fs.existsSync(envPath);
  if (dockerfileExists) {
    const overwrite = await promptUser("\u26A0\uFE0F  Dockerfile already exists. Overwrite? (y/N): ");
    if (!overwrite) {
      console.log("\u274C Skipping Dockerfile creation.");
    } else {
      copyDockerfile(dockerfileSource, dockerfilePath);
    }
  } else {
    copyDockerfile(dockerfileSource, dockerfilePath);
  }
  if (dockerComposeExists) {
    const overwrite = await promptUser("\u26A0\uFE0F  docker-compose.yml already exists. Overwrite? (y/N): ");
    if (!overwrite) {
      console.log("\u274C Skipping docker-compose.yml creation.");
    } else {
      copyDockerCompose(dockerComposeSource, dockerComposePath);
    }
  } else {
    copyDockerCompose(dockerComposeSource, dockerComposePath);
  }
  if (envExists) {
    console.log("\u2139\uFE0F  .env file already exists. Keeping existing configuration.");
  } else {
    writeEnvFile(envPath);
  }
  console.log("\n\u2705 Docker setup complete!");
  console.log("\n\u{1F4DD} Next steps:");
  console.log("   1. Edit the .env file with your Telegram bot token and user IDs");
  console.log("   2. Run: docker-compose up -d");
  console.log("   3. View logs: docker-compose logs -f\n");
}
function copyDockerfile(sourcePath, destinationPath) {
  try {
    if (!fs.existsSync(sourcePath)) {
      console.log(`\u274C Dockerfile not found in package at ${sourcePath}`);
      console.log("   This might be a development environment. Checking parent directory...");
      return;
    }
    fs.copyFileSync(sourcePath, destinationPath);
    console.log(`\u2705 Copied Dockerfile to ${destinationPath}`);
  } catch (error) {
    console.error(`\u274C Failed to copy Dockerfile: ${error}`);
  }
}
function copyDockerCompose(sourcePath, destinationPath) {
  try {
    if (!fs.existsSync(sourcePath)) {
      console.log(`\u274C docker-compose.yml not found in package at ${sourcePath}`);
      console.log("   This might be a development environment. Checking parent directory...");
      return;
    }
    fs.copyFileSync(sourcePath, destinationPath);
    console.log(`\u2705 Copied docker-compose.yml to ${destinationPath}`);
  } catch (error) {
    console.error(`\u274C Failed to copy docker-compose.yml: ${error}`);
  }
}
function writeEnvFile(path) {
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
  console.log(`\u2705 Created .env file at ${path}`);
}
var args = process.argv.slice(2);
var dockerFlag = args.includes("--docker");
console.log("\u{1F916} TelegramCoder - AI-Powered Telegram Bot");
console.log("================================================\n");
if (dockerFlag) {
  (async () => {
    await handleDockerSetup();
    process.exit(0);
  })();
} else {
  startBot();
}
function startBot() {
  if (process.platform === "win32") {
    console.log("\u26A0\uFE0F  Windows is not supported for direct installation.");
    console.log("   TelegramCoder uses node-pty which requires native compilation.");
    console.log("\n   \u{1F4E6} Please use Docker instead:");
    console.log("   See https://github.com/Tommertom/telegramCoder/blob/main/DOCKER_GUIDE.md\n");
  }
  const envPath = join(process.cwd(), ".env");
  const templatePath = join(__dirname, "..", "dot-env.template");
  if (!fs.existsSync(envPath)) {
    console.log("\u26A0\uFE0F  No .env file found in current directory!");
    console.log("\n\u{1F4DD} Creating .env template...\n");
    if (fs.existsSync(templatePath)) {
      fs.copyFileSync(templatePath, envPath);
      console.log("\u2705 Created .env file from template");
      console.log("\n\u{1F527} Please edit .env and configure:");
      console.log("   - TELEGRAM_BOT_TOKENS (required)");
      console.log("   - ALLOWED_USER_IDS (required)");
      console.log("\nThen run the command again.\n");
      process.exit(0);
    } else {
      console.log("\u274C Template file not found. Please create .env manually.");
      console.log("\nRequired variables:");
      console.log("   TELEGRAM_BOT_TOKENS=your_bot_token_here");
      console.log("   ALLOWED_USER_IDS=your_user_id_here\n");
      process.exit(1);
    }
  }
  const envContent = fs.readFileSync(envPath, "utf-8");
  const hasToken = /TELEGRAM_BOT_TOKENS\s*=\s*.+/.test(envContent);
  const hasUsers = /ALLOWED_USER_IDS\s*=\s*.+/.test(envContent);
  if (!hasToken || !hasUsers) {
    console.log("\u26A0\uFE0F  .env file is incomplete!\n");
    if (!hasToken) console.log("   \u274C Missing TELEGRAM_BOT_TOKENS");
    if (!hasUsers) console.log("   \u274C Missing ALLOWED_USER_IDS");
    console.log("\n\u{1F527} Please edit .env and configure the required variables.\n");
    process.exit(1);
  }
  console.log("\u{1F680} Starting TelegramCoder...\n");
  const appPath = join(__dirname, "app.js");
  const isWindows = process.platform === "win32";
  const child = spawn("node", [appPath], {
    stdio: "inherit",
    env: { ...process.env, NODE_ENV: "production" },
    // On Windows, we need shell: false for proper signal handling
    shell: false,
    windowsHide: true
  });
  child.on("exit", (code) => {
    if (code !== 0) {
      console.error(`
\u274C TelegramCoder exited with code ${code}`);
      process.exit(code || 1);
    }
  });
  child.on("error", (err) => {
    console.error(`
\u274C Failed to start TelegramCoder: ${err.message}`);
    process.exit(1);
  });
  if (isWindows) {
    if (process.stdin.isTTY) {
      const readline2 = __require("readline");
      readline2.createInterface({
        input: process.stdin,
        output: process.stdout
      });
    }
    process.on("SIGINT", () => {
      child.kill();
      process.exit(0);
    });
    process.on("SIGTERM", () => {
      child.kill();
      process.exit(0);
    });
    process.on("SIGBREAK", () => {
      child.kill();
      process.exit(0);
    });
  } else {
    process.on("SIGINT", () => child.kill("SIGINT"));
    process.on("SIGTERM", () => child.kill("SIGTERM"));
  }
}
//# sourceMappingURL=cli.js.map
