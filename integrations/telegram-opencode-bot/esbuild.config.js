#!/usr/bin/env node

import * as esbuild from "esbuild";
import { join, dirname } from "path";
import { fileURLToPath } from "url";
import { copyFileSync, mkdirSync, existsSync, rmSync } from "fs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const isProd = process.env.NODE_ENV === "production";

// Common build options
const commonOptions = {
  bundle: true,
  platform: "node",
  target: "node18",
  format: "esm",
  sourcemap: !isProd,
  minify: isProd,
  treeShaking: true,
  external: [
    // Node built-ins (both node: prefix and bare names)
    "node:*",
    "http",
    "https",
    "fs",
    "path",
    "os",
    "crypto",
    "stream",
    "util",
    "events",
    "buffer",
    "child_process",
    "url",
    "readline",
    "net",
    "tls",
    "zlib",
    // Dependencies that shouldn't be bundled (native modules)
    "node-pty",
    "puppeteer",
    // Other dependencies that might have issues when bundled
    "@google/genai",
    "@ai-sdk/google",
    "@ai-sdk/openai",
    "grammy",
    "dotenv",
    "ai",
    "archiver",
    "zod",
  ],
  banner: {
    js: "#!/usr/bin/env node",
  },
};

async function build() {
  try {
    console.log("🔨 Building with esbuild...");
    console.log(
      `   Mode: ${isProd ? "production (minified)" : "development"}\n`
    );

    // Clean dist directory
    if (existsSync("dist")) {
      rmSync("dist", { recursive: true, force: true });
      console.log("🧹 Cleaned dist directory");
    }

    // Create fresh dist directory
    mkdirSync("dist", { recursive: true });

    // Build CLI entry point
    await esbuild.build({
      ...commonOptions,
      entryPoints: ["src/cli.ts"],
      outfile: "dist/cli.js",
    });
    console.log("✅ Built cli.js");

    // Build main app entry point
    await esbuild.build({
      ...commonOptions,
      entryPoints: ["src/app.ts"],
      outfile: "dist/app.js",
      banner: {
        js: "", // No shebang for app.js
      },
    });
    console.log("✅ Built app.js");

    // Copy the dot-env template to dist (needed for CLI)
    if (existsSync("dot-env.template")) {
      copyFileSync("dot-env.template", "dist/dot-env.template");
      console.log("✅ Copied dot-env.template");
    }

    console.log("\n✨ Build complete!");
  } catch (error) {
    console.error("❌ Build failed:", error);
    process.exit(1);
  }
}

build();
