import { spawn, ChildProcess } from "child_process";
import { access, constants } from "fs/promises";
import { join } from "path";

export class OpenCodeServerService {
    private serverProcess: ChildProcess | null = null;
    private serverUrl: string;
    private startupTimeout = 30000; // 30 seconds

    constructor(serverUrl?: string) {
        this.serverUrl = serverUrl || process.env.OPENCODE_SERVER_URL || "http://localhost:4096";
    }

    async isServerRunning(): Promise<boolean> {
        try {
            const url = new URL(this.serverUrl);
            const response = await fetch(this.serverUrl, {
                method: "HEAD",
                signal: AbortSignal.timeout(5000),
            });
            return response.ok || response.status < 500;
        } catch (error) {
            return false;
        }
    }

    private async isOpenCodeInstalled(): Promise<boolean> {
        try {
            // Check if opencode command is available
            const { execSync } = require("child_process");
            execSync("opencode --version", { stdio: "ignore" });
            return true;
        } catch {
            return false;
        }
    }

    async startServer(): Promise<{ success: boolean; message: string }> {
        // Check if server is already running
        if (await this.isServerRunning()) {
            return { success: true, message: "OpenCode server is already running" };
        }

        // Check if opencode is available
        if (!(await this.isOpenCodeInstalled())) {
            return {
                success: false,
                message: "opencode command is not available. Please install OpenCode: npm install -g opencode-ai",
            };
        }

        try {
            // Extract port and hostname from URL
            const url = new URL(this.serverUrl);
            const port = url.port || "4096";
            const hostname = url.hostname || "localhost";

            // Start OpenCode server using: opencode serve --port <number> --hostname <string>
            const args = ["serve", "--port", port, "--hostname", hostname];

            this.serverProcess = spawn("opencode", args, {
                detached: true,
                stdio: "ignore",
            });

            // Unref so the parent process can exit independently
            this.serverProcess.unref();

            // Wait for server to start
            const startTime = Date.now();
            while (Date.now() - startTime < this.startupTimeout) {
                if (await this.isServerRunning()) {
                    return {
                        success: true,
                        message: `OpenCode server started successfully on ${this.serverUrl}`,
                    };
                }
                await new Promise((resolve) => setTimeout(resolve, 1000));
            }

            return {
                success: false,
                message: "OpenCode server started but did not respond within 30 seconds",
            };
        } catch (error) {
            return {
                success: false,
                message: `Failed to start OpenCode server: ${error instanceof Error ? error.message : String(error)}`,
            };
        }
    }

    stopServer(): void {
        if (this.serverProcess && !this.serverProcess.killed) {
            this.serverProcess.kill();
            this.serverProcess = null;
        }
    }
}
