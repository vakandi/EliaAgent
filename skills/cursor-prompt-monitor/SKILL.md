# Cursor Prompt Monitor Skill

## Description
Automatically monitor and collect prompts and work sessions from Cursor, Windsurf, and Kiro IDEs throughout the day. This allows the AI assistant to stay updated on your work progress and provide contextual help.

## Features
- ✅ Monitor Cursor IDE prompt history
- ✅ Track Windsurf work sessions
- ✅ Collect Kiro development activities
- ✅ Real-time prompt extraction
- ✅ Project context analysis
- ✅ Daily work summary generation

## Configuration

### Cursor IDE
```javascript
// Cursor stores prompts in:
// Windows: C:\Users\{user}\AppData\Roaming\Cursor\History\
// macOS: ~/Library/Application Support/Cursor/History/
// Linux: ~/.config/Cursor/History/

const cursorConfig = {
  historyPath: "C:\\Users\\your-username\\AppData\\Roaming\\Cursor\\History",
  extractPrompts: true,
  analyzeContext: true,
  maxFiles: 100
};
```

### Windsurf IDE
```javascript
const windsurfConfig = {
  historyPath: "C:\\Users\\your-username\\AppData\\Roaming\\Windsurf\\History",
  monitorInterval: 300000, // 5 minutes
  extractPatterns: [
    "user_prompt",
    "ai_response",
    "code_generation"
  ]
};
```

### Kiro IDE
```javascript
const kiroConfig = {
  historyPath: "C:\\Users\\your-username\\AppData\\Roaming\\Kiro\\History",
  sessionTracking: true,
  projectAssociation: true
};
```

## Usage

### Basic Monitoring
```javascript
const prompts = await cursor_monitor({
  action: "get_recent_prompts",
  timeframe: "today",
  limit: 50
});

console.log(prompts);
// Returns: Array of prompts with timestamps and context
```

### Project Analysis
```javascript
const projectContext = await cursor_monitor({
  action: "analyze_project",
  projectPath: "C:\\Users\\your-username\\Documents\\projects\\AccForge",
  includePrompts: true,
  summarizeSession: true
});
```

### Daily Summary
```javascript
const dailySummary = await cursor_monitor({
  action: "daily_summary",
  date: "2026-02-05",
  includeInsights: true
});
```

## Output Structure

### Prompt Object
```javascript
{
  id: "uuid",
  timestamp: "2026-02-05T10:30:00Z",
  ide: "cursor", // cursor, windsurf, or kiro
  prompt: "User's actual prompt text...",
  response: "AI response (if available)",
  project: "AccForge",
  file: "backend/main.py",
  context: {
    language: "python",
    framework: "fastapi",
    task: "security_audit"
  },
  metadata: {
    model: "claude-3-5-sonnet",
    tokens: 2450,
    duration: 1200 // ms
  }
}
```

### Daily Summary
```javascript
{
  date: "2026-02-05",
  totalPrompts: 45,
  totalTokens: 125000,
  projects: [
    {
      name: "AccForge",
      prompts: 25,
      focus: "Security audit and API development"
    },
    {
      name: "your-brand",
      prompts: 20,
      focus: "Frontend optimization"
    }
  ],
  topTasks: [
    "Security vulnerability analysis",
    "API endpoint implementation",
    "Database optimization"
  ],
  insights: [
    "Heavy focus on security today",
    "Multiple API endpoints created",
    "Performance improvements made"
  ],
  recommendations: [
    "Consider adding automated security tests",
    "Review rate limiting implementation",
    "Update API documentation"
  ]
}
```

## Monitoring Schedule

### Automatic Monitoring
```javascript
// Set up automatic monitoring
await cursor_monitor({
  action: "setup_schedule",
  interval: "30min", // Check every 30 minutes
  activeHours: {
    start: "09:00",
    end: "18:00"
  },
  notifications: {
    onNewPrompt: false,
    dailySummary: true,
    weeklyReport: true
  }
});
```

### Manual Check
```javascript
// Manually check for new prompts
const newPrompts = await cursor_monitor({
  action: "check_new",
  since: "2026-02-05T10:00:00Z"
});
```

## Integration with OpenClaw

### Heartbeat Integration
```javascript
// Add to HEARTBEAT.md
- Check Cursor/Windsurf/Kiro prompts
- Analyze recent work context
- Generate insights and recommendations
```

### Memory Integration
```javascript
// Store important prompts in memory
await cursor_monitor({
  action: "store_important",
  criteria: {
    containsKeywords: ["security", "bug", "optimization"],
    minTokens: 1000,
    projectRelevance: "high"
  }
});
```

## Privacy & Security
- All data stored locally
- No external transmission
- Encrypted storage option
- Auto-cleanup after 30 days
- User-controlled data retention

## Performance
- Minimal system impact
- Background processing
- Efficient file parsing
- Cached results
- Incremental updates

## Error Handling
- Missing history directory
- Corrupted log files
- Permission issues
- IDE not running
- Large file handling

## Future Enhancements
- Cross-project analysis
- Code pattern recognition
- Automatic task creation
- Team collaboration insights
- Integration with Git commits

---

**Note**: This skill respects user privacy and operates entirely locally on your machine.