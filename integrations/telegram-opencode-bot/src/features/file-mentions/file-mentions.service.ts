/**
 * Service for handling file mentions using OpenCode find.files API
 */

import { createOpencodeClient } from "@opencode-ai/sdk";
import type { FileMention, FileMatch, ResolvedMention, FileMentionConfig } from "./file-mentions.types.js";
import { FileMentionParser } from "./file-mentions.parser.js";

export class FileMentionService {
    private parser: FileMentionParser;
    private baseUrl: string;
    private config: FileMentionConfig;
    
    constructor(baseUrl?: string, config?: Partial<FileMentionConfig>) {
        this.baseUrl = baseUrl || process.env.OPENCODE_SERVER_URL || "http://localhost:4096";
        this.parser = new FileMentionParser();
        this.config = {
            enabled: config?.enabled ?? true,
            maxResults: config?.maxResults ?? 10,
            maxFileSize: config?.maxFileSize ?? 100000, // 100KB
            includeContent: config?.includeContent ?? true,
            cacheEnabled: config?.cacheEnabled ?? false,
            cacheTTL: config?.cacheTTL ?? 300000, // 5 minutes
        };
    }
    
    /**
     * Parse @mentions from text
     */
    parseMentions(text: string): FileMention[] {
        return this.parser.parse(text);
    }
    
    /**
     * Find files matching a query using OpenCode find.files API
     */
    async findFiles(query: string, directory?: string): Promise<FileMatch[]> {
        const client = createOpencodeClient({ baseUrl: this.baseUrl });
        
        try {
            const result = await client.find.files({
                query: {
                    query,
                    directory,
                    dirs: "false" // Only files, not directories
                }
            });
            
            if (!result.data) {
                return [];
            }
            
            // Convert array of paths to FileMatch objects
            // OpenCode returns results already sorted by relevance
            return result.data.slice(0, this.config.maxResults).map((path, index) => ({
                path,
                // Score based on position (first result = 1.0, decreasing)
                score: 1.0 - (index * 0.1)
            }));
        } catch (error) {
            console.error("Failed to find files:", error);
            return [];
        }
    }
    
    /**
     * Search for files matching all mentions
     */
    async searchMentions(
        mentions: FileMention[],
        directory?: string
    ): Promise<Map<FileMention, FileMatch[]>> {
        const results = new Map<FileMention, FileMatch[]>();
        
        for (const mention of mentions) {
            const matches = await this.findFiles(mention.query, directory);
            results.set(mention, matches);
        }
        
        return results;
    }
    
    /**
     * Read file content using OpenCode file.read API
     */
    async readFile(path: string): Promise<string | null> {
        const client = createOpencodeClient({ baseUrl: this.baseUrl });
        
        try {
            const result = await client.file.read({
                query: { path }
            });
            
            if (!result.data) {
                return null;
            }
            
            // OpenCode returns { type: "raw" | "patch", content: string }
            return result.data.content;
        } catch (error) {
            console.error(`Failed to read file ${path}:`, error);
            return null;
        }
    }
    
    /**
     * Resolve mentions to files with optional content
     */
    async resolveMentions(
        mentions: FileMention[],
        selectedFiles: Map<FileMention, FileMatch>,
        includeContent: boolean = this.config.includeContent
    ): Promise<ResolvedMention[]> {
        const resolved: ResolvedMention[] = [];
        
        for (const mention of mentions) {
            const file = selectedFiles.get(mention);
            if (!file) continue;
            
            let content: string | undefined;
            if (includeContent) {
                const fileContent = await this.readFile(file.path);
                if (fileContent !== null) {
                    // Check file size
                    if (fileContent.length <= this.config.maxFileSize) {
                        content = fileContent;
                    } else {
                        console.warn(`File ${file.path} too large (${fileContent.length} bytes), skipping content`);
                    }
                }
            }
            
            resolved.push({
                mention,
                file,
                content
            });
        }
        
        return resolved;
    }
    
    /**
     * Format resolved mentions for inclusion in prompt
     */
    formatForPrompt(resolved: ResolvedMention[]): string {
        if (resolved.length === 0) return "";
        
        let context = "📎 Referenced Files:\n\n";
        
        for (const item of resolved) {
            context += `File: ${item.file.path}\n`;
            if (item.content) {
                context += "```\n" + item.content + "\n```\n\n";
            } else {
                context += "(Content not included)\n\n";
            }
        }
        
        return context;
    }
    
    /**
     * Check if the service is enabled
     */
    isEnabled(): boolean {
        return this.config.enabled;
    }
}
