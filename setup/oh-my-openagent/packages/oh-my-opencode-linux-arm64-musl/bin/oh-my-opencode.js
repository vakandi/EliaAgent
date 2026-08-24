#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { join } from "node:path";

const wrapperPackageRoot = process.env.OMO_WRAPPER_PACKAGE_ROOT;
const lazyCodexInvocationNames = new Set(["lazycodex", "lazycodex-ai"]);
const lazyCodexInstallerCommands = new Set(["install", "setup", "update", "uninstall", "cleanup"]);

if (!wrapperPackageRoot) {
  console.error("oh-my-opencode: OMO_WRAPPER_PACKAGE_ROOT is required to launch the packaged CLI.");
  process.exit(2);
}

function exitFromResult(result, failureLabel) {
  if (result.error) {
    console.error(`oh-my-opencode: ${failureLabel}: ${result.error.message}`);
    process.exit(2);
  }

  if (result.signal) {
    const signalCodes = { SIGINT: 2, SIGILL: 4, SIGKILL: 9, SIGTERM: 15 };
    process.exit(128 + (signalCodes[result.signal] ?? 1));
  }

  process.exit(result.status ?? 1);
}

function shouldRunLazyCodexInstaller() {
  const args = process.argv.slice(2);
  const command = readInstallerCommand(args);
  const platformArg = readPlatformArg(args);
  if (lazyCodexInvocationNames.has(process.env.OMO_INVOCATION_NAME ?? "")) {
    if ((command === "install" || command === "setup") && platformArg !== undefined && platformArg !== "codex") {
      return false;
    }
    return command === undefined ||
    command === "--help" ||
    command === "-h" ||
    command === "--version" ||
    command === "-v" ||
    lazyCodexInstallerCommands.has(command);
  }

  return (command === "install" || command === "setup") && platformArg === "codex";
}

function readInstallerCommand(args) {
  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    if (arg === "--platform" || arg === "--repo-root") {
      index += 1;
      continue;
    }
    if (arg.startsWith("-")) continue;
    return arg;
  }
  return undefined;
}

function readPlatformArg(args) {
  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    if (arg === "--platform") {
      return args[index + 1];
    }
    if (arg.startsWith("--platform=")) {
      return arg.slice("--platform=".length);
    }
  }
  return undefined;
}

if (shouldRunLazyCodexInstaller()) {
  const lazyCodexInstallerPath = join(wrapperPackageRoot, "packages", "omo-codex", "scripts", "install-local.mjs");

  if (!existsSync(lazyCodexInstallerPath)) {
    console.error(`oh-my-opencode: lazycodex installer not found at ${lazyCodexInstallerPath}`);
    process.exit(2);
  }

  const result = spawnSync(process.execPath, [lazyCodexInstallerPath, ...process.argv.slice(2)], {
    stdio: "inherit",
    env: process.env,
  });
  exitFromResult(result, "failed to execute lazycodex Node installer");
}

const cliPath = join(wrapperPackageRoot, "dist", "cli", "index.js");
const nodeCliPath = join(wrapperPackageRoot, "dist", "cli-node", "index.js");

if (!existsSync(cliPath)) {
  console.error(`oh-my-opencode: packaged CLI not found at ${cliPath}`);
  process.exit(2);
}

function runNodeCli(reason) {
  if (!existsSync(nodeCliPath)) return;
  if (reason) {
    console.error(`oh-my-opencode: ${reason}; falling back to the node CLI at ${nodeCliPath}`);
  }
  const result = spawnSync(process.execPath, [nodeCliPath, ...process.argv.slice(2)], {
    stdio: "inherit",
    env: process.env,
  });
  exitFromResult(result, "failed to execute the node CLI");
}

if (process.env.OMO_RUNTIME === "node") {
  runNodeCli();
}

const bunBinary = process.env.BUN_BINARY || "bun";
const result = spawnSync(bunBinary, [cliPath, ...process.argv.slice(2)], {
  stdio: "inherit",
  env: process.env,
});

if (result.error) {
  runNodeCli(`bun is not available (${result.error.message})`);
}

if (result.signal === "SIGILL") {
  runNodeCli("bun crashed with SIGILL - this CPU lacks the instruction set bun requires (x86-64-v2/SSE4.2 or newer)");
}

exitFromResult(result, "failed to execute Bun");
