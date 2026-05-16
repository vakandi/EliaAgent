/**
 * Types for file mentions (@-mentions) feature
 */

export interface FileMention {
    raw: string;           // Original @mention text (e.g., "@src/api/auth.ts")
    query: string;         // Path query to search for
    startIndex: number;    // Position in message
    endIndex: number;      // End position in message
}

export interface FileMatch {
    path: string;          // Full file path from OpenCode
    score: number;         // Match relevance (1.0 for exact match)
}

export interface ResolvedMention {
    mention: FileMention;
    file: FileMatch;
    content?: string;      // Optional file content
}

export interface FileMentionConfig {
    enabled: boolean;
    maxResults: number;
    maxFileSize: number;
    includeContent: boolean;
    cacheEnabled: boolean;
    cacheTTL: number;
}
