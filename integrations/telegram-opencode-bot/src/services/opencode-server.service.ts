import { spawn, ChildProcess } from "child_process";
import { access, constants } from "fs/promises";
import { join } from "path";
import { existsSync, readFileSync } from "fs";

export class OpenCodeServerService {
    private serverProcess: ChildProcess | null = null;
    private serverUrl: string;
    private startupTimeout = 30000;

    constructor(serverUrl?: string) {
        this.serverUrl = serverUrl || process.env.OPENCODE_SERVER_URL || "http://localhost:4096";
    }

    private isProxyEnabled(): boolean {
        return existsSync(join(process.env.HOME || "", "EliaAI", ".proxy_enabled"));
    }

    private loadProxyEnv(): Record<string, string> {
        const proxyConf = join(process.env.HOME || "", ".proxychains.conf");
        if (!existsSync(proxyConf)) return {};
        try {
            const content = readFileSync(proxyConf, "utf-8");
            for (const line of content.split("\n")) {
                const trimmed = line.trim();
                if (trimmed.startsWith("http ") || trimmed.startsWith("https ")) {
                    const parts = trimmed.split(/\s+/);
                    if (parts.length >= 3) {
                        const [, ip, port, user, pass] = parts;
                        const proxyUrl = `http://${user}:${pass}@${ip}:${port}`;
                        return {
                            HTTPS_PROXY: proxyUrl,
                            HTTP_PROXY: proxyUrl,
                            https_proxy: proxyUrl,
                            http_proxy: proxyUrl,
                        };
                    }
                }
            }
        } catch {}
        return {};
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
            const { execSync } = require("child_process");
            execSync("opencode --version", { stdio: "ignore" });
            return true;
        } catch {
            return false;
        }
    }

    async startServer(): Promise<{ success: boolean; message: string }> {
        if (await this.isServerRunning()) {
            return { success: true, message: "OpenCode server is already running" };
        }

        if (!(await this.isOpenCodeInstalled())) {
            return {
                success: false,
                message: "opencode command is not available. Please install OpenCode: npm install -g opencode-ai",
            };
        }

        try {
            const url = new URL(this.serverUrl);
            const port = url.port || "4096";
            const hostname = url.hostname || "localhost";

            const args = ["serve", "--port", port, "--hostname", hostname];
            const useProxy = this.isProxyEnabled();
            const spawnOpts: Record<string, unknown> = {
                detached: true,
                stdio: "ignore",
            };

            if (useProxy) {
                const proxyEnv = this.loadProxyEnv();
                spawnOpts.env = { ...process.env, ...proxyEnv };
            }

const cmd = useProxy ? "proxychains4" : "opencode";
            const finalArgs = useProxy ? ["-f", join(process.env.HOME || "", ".proxychains.conf"), ...args] : args;

            const spawnEnv = useProxy ? { ...process.env, ...this.loadProxyEnv() } : process.env;
            this.serverProcess = spawn(cmd, finalArgs, {
                detached: true,
                stdio: "ignore",
                env: spawnEnv,
            });

            this.serverProcess.unref();

            const startTime = Date.now();
            while (Date.now() - startTime < this.startupTimeout) {
                if (await this.isServerRunning()) {
                    return {
                        success: true,
                        message: `OpenCode server started ${useProxy ? "with proxy " : ""}on ${this.serverUrl}`,
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
