import { Bot, Context, InputFile, Keyboard } from "grammy";
import { OpenCodeService } from "./opencode.service.js";
import { ConfigService } from "../../services/config.service.js";
import { MessageUtils } from "../../utils/message.utils.js";
import { ErrorUtils } from "../../utils/error.utils.js";
import { formatAsHtml, escapeHtml } from "./event-handlers/utils.js";
import { AccessControlMiddleware } from "../../middleware/access-control.middleware.js";
import * as fs from "fs";
import * as path from "path";

export class AnalyzeBottleneckBot {
    private opencodeService: OpenCodeService;
    private configService: ConfigService;

    constructor(
        opencodeService: OpenCodeService,
        configService: ConfigService
    ) {
        this.opencodeService = opencodeService;
        this.configService = configService;
    }

    registerHandlers(bot: Bot): void {
        bot.command("analyse_your_bottleneck", AccessControlMiddleware.requireAccess, this.handleAnalyzeBottleneck.bind(this));
    }

    private async handleAnalyzeBottleneck(ctx: Context): Promise<void> {
        try {
            const eventsDir = path.join(process.cwd(), 'events');
            
            const analysis: string[] = [
                "🔍 <b>RAPPORT D'ANALYSE - Goulots d'étranglement AI</b>\n",
                "═".repeat(40) + "\n"
            ];
            
            let totalIssues = 0;
            
            const errorLogPath = path.join(eventsDir, 'session-errors.json');
            if (fs.existsSync(errorLogPath)) {
                try {
                    const errorLog = JSON.parse(fs.readFileSync(errorLogPath, 'utf8'));
                    if (errorLog.length > 0) {
                        analysis.push(`📊 <b>Errors détectés:</b> ${errorLog.length}\n`);
                        
                        const errorTypes: Record<string, number> = {};
                        errorLog.forEach((e: any) => {
                            const errorKey = e.error || 'Unknown';
                            errorTypes[errorKey] = (errorTypes[errorKey] || 0) + 1;
                        });
                        
                        Object.entries(errorTypes).forEach(([error, count]) => {
                            analysis.push(`  • ${error}: ${count}x`);
                        });
                        analysis.push("");
                        totalIssues += errorLog.length;
                    }
                } catch (e) {}
            }
            
            const lastErrorPath = path.join(eventsDir, 'session-error.last.json');
            if (fs.existsSync(lastErrorPath)) {
                try {
                    const lastError = JSON.parse(fs.readFileSync(lastErrorPath, 'utf8'));
                    analysis.push("📌 <b>Dernière erreur:</b>");
                    analysis.push(`  Error: ${lastError.properties?.error || 'N/A'}`);
                    analysis.push(`  Message: ${lastError.properties?.message || 'N/A'}`);
                    if (lastError.properties?.stack) {
                        analysis.push(`  Stack: ${lastError.properties.stack.substring(0, 200)}...`);
                    }
                    analysis.push("");
                } catch (e) {}
            }
            
            const sessions = await this.opencodeService.getSessions(10);
            if (sessions.length > 0) {
                analysis.push(`📋 <b>Sessions récentes:</b> ${sessions.length}\n`);
                sessions.forEach((s, i) => {
                    analysis.push(`  ${i+1}. ${s.title.substring(0, 40)}`);
                });
                analysis.push("");
            }
            
            const messageUpdatedPath = path.join(eventsDir, 'message-updated.last.json');
            if (fs.existsSync(messageUpdatedPath)) {
                try {
                    const lastMsg = JSON.parse(fs.readFileSync(messageUpdatedPath, 'utf8'));
                    if (lastMsg.properties?.parts) {
                        const textParts = lastMsg.properties.parts.filter((p: any) => p.type === 'text');
                        const toolParts = lastMsg.properties.parts.filter((p: any) => p.type === 'tool');
                        const reasoningParts = lastMsg.properties.parts.filter((p: any) => p.type === 'reasoning');
                        
                        analysis.push("💬 <b>Dernier message:</b>");
                        analysis.push(`  Text parts: ${textParts.length}`);
                        analysis.push(`  Tool calls: ${toolParts.length}`);
                        analysis.push(`  Reasoning: ${reasoningParts.length}`);
                        analysis.push("");
                    }
                } catch (e) {}
            }
            
            const lspPath = path.join(eventsDir, 'lsp-client-diagnostics.last.json');
            if (fs.existsSync(lspPath)) {
                try {
                    const lspDiags = JSON.parse(fs.readFileSync(lspPath, 'utf8'));
                    if (lspDiags.properties?.diagnostics) {
                        const diags = lspDiags.properties.diagnostics;
                        const errors = diags.filter((d: any) => d.severity === 1);
                        const warnings = diags.filter((d: any) => d.severity === 2);
                        
                        analysis.push("🔧 <b>LSP Diagnostics:</b>");
                        analysis.push(`  Errors: ${errors.length}`);
                        analysis.push(`  Warnings: ${warnings.length}`);
                        
                        if (errors.length > 0) {
                            analysis.push("\n  📕 <b>Errors:</b>");
                            errors.slice(0, 5).forEach((e: any) => {
                                analysis.push(`    - ${e.message?.substring(0, 80)}`);
                            });
                        }
                        analysis.push("");
                    }
                } catch (e) {}
            }
            
            const sessionDiffPath = path.join(eventsDir, 'session-diff.last.json');
            if (fs.existsSync(sessionDiffPath)) {
                try {
                    const sessionDiff = JSON.parse(fs.readFileSync(sessionDiffPath, 'utf8'));
                    analysis.push("📊 <b>Session Diff:</b>");
                    if (sessionDiff.properties?.diffs) {
                        const diffs = sessionDiff.properties.diffs;
                        analysis.push(`  Total changes: ${diffs.length}`);
                        
                        const fileEdits = diffs.filter((d: any) => d.type === 'file_edit');
                        const fileCreations = diffs.filter((d: any) => d.type === 'file_creation');
                        const fileDeletions = diffs.filter((d: any) => d.type === 'file_deletion');
                        
                        analysis.push(`  File edits: ${fileEdits.length}`);
                        analysis.push(`  File creations: ${fileCreations.length}`);
                        analysis.push(`  File deletions: ${fileDeletions.length}`);
                    }
                    analysis.push("");
                } catch (e) {}
            }
            
            const commandExecutedPath = path.join(eventsDir, 'command-executed.last.json');
            if (fs.existsSync(commandExecutedPath)) {
                try {
                    const cmdExec = JSON.parse(fs.readFileSync(commandExecutedPath, 'utf8'));
                    analysis.push("🖥️ <b>Last Command:</b>");
                    analysis.push(`  Command: ${cmdExec.properties?.command || 'N/A'}`);
                    analysis.push(`  Exit code: ${cmdExec.properties?.exitCode || 'N/A'}`);
                    analysis.push("");
                } catch (e) {}
            }
            
            analysis.push("═".repeat(40));
            analysis.push("\n🎯 <b>RÉSUMÉ:</b>");
            analysis.push(`  Total issues: ${totalIssues}`);
            
            if (totalIssues === 0) {
                analysis.push("\n✅ <b>Pas de problèmes détectés!</b>");
                analysis.push("Le système fonctionne correctement.");
            } else {
                analysis.push("\n⚠️ <b>Problèmes détectés - Analyse recommandée:</b>");
                analysis.push("1. Vérifier les logs d'erreur ci-dessus");
                analysis.push("2. Examiner les diagnostics LSP");
                analysis.push("3. Considérer les outils utilisés");
            }
            
            const report = analysis.join("\n");
            
            await ctx.reply(report, { parse_mode: "HTML" });
            
        } catch (error) {
            await ctx.reply(ErrorUtils.createErrorMessage('analyze bottleneck', error));
        }
    }
}
