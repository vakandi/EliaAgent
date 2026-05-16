/**
 * Parser for extracting @file mentions from text
 */

import type { FileMention } from "./file-mentions.types.js";

export class FileMentionParser {
    // Pattern: @path/to/file.ext or @"path with spaces/file.ext"
    private readonly MENTION_PATTERN = /@(?:"([^"]+)"|([^\s]+))/g;
    
    /**
     * Parse all @mentions from text
     */
    parse(text: string): FileMention[] {
        const mentions: FileMention[] = [];
        let match: RegExpExecArray | null;
        
        // Reset regex state
        this.MENTION_PATTERN.lastIndex = 0;
        
        while ((match = this.MENTION_PATTERN.exec(text)) !== null) {
            const raw = match[0];
            const query = match[1] || match[2]; // Quoted or unquoted path
            
            // Skip if it looks like an email (has @ before or after)
            const before = text[match.index - 1];
            const after = text[match.index + raw.length];
            if (before === '@' || after === '@') {
                continue;
            }
            
            mentions.push({
                raw,
                query,
                startIndex: match.index,
                endIndex: match.index + raw.length
            });
        }
        
        return mentions;
    }
    
    /**
     * Replace @mentions in text with resolved file references
     */
    replace(text: string, replacements: Map<string, string>): string {
        let result = text;
        
        // Sort replacements by position (descending) to avoid offset issues
        const sorted = Array.from(replacements.entries())
            .sort((a, b) => b[0].length - a[0].length);
        
        for (const [mention, replacement] of sorted) {
            result = result.replace(mention, replacement);
        }
        
        return result;
    }
    
    /**
     * Check if text contains any @mentions
     */
    hasMentions(text: string): boolean {
        this.MENTION_PATTERN.lastIndex = 0;
        return this.MENTION_PATTERN.test(text);
    }
}
