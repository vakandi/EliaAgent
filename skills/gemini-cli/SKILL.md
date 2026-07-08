---
name: gemini-cli
description: Use Gemini CLI to access Gemini 2.5 free tier (1000 requests/day) for quick AI assistance on Windows
allowed-tools: bash
---

# Gemini CLI Watson Skill

This Watson skill enables you to use the Gemini CLI tool to access Google's Gemini 2.5 free tier model (1000 requests per day limit) for quick AI assistance.

## Prerequisites

1. **Gemini CLI must be installed** and available in your PATH
   - Verify installation: `gemini --version` or `gemini chat --help`
   - If not installed, installation instructions: https://github.com/google-gemini/gemini-cli

2. **API Key configured**
   - The Gemini CLI should be configured with your API key (via environment variable or `.gemini/settings.json`)
   - Never hardcode API keys in commands or files

## Quota Management (CRITICAL)

**IMPORTANT**: Gemini free tier has a limit of **1000 requests per day**. You MUST check quota before making requests.

### Before Every Request:

1. **Check quota status** by reading `runtime/gemini-quota.json`:
   ```bash
   cat runtime/gemini-quota.json
   ```
   Or on Windows PowerShell:
   ```bash
   type runtime\gemini-quota.json
   ```

2. **Verify quota is available**:
   - Check if `count < limit` (limit is 1000)
   - Check if `date` matches today's date (quota resets daily)
   - If quota is exceeded, DO NOT make the request. Instead:
     - Inform the user that quota is exhausted
     - Suggest waiting until the next day (quota resets at midnight)
     - Consider alternative approaches that don't require Gemini

3. **After successful request**, the quota will be automatically incremented by the agentd system

## Command Patterns

### Basic Usage

```bash
gemini chat "your prompt here"
```

### Specify Model (Recommended)

```bash
gemini chat --model gemini-2.5-pro "your prompt here"
```

### With Output Redirection (For Long Responses)

When you expect a long response or need to save it:

```bash
gemini chat --model gemini-2.5-pro "your prompt" > output.txt
```

Then read the file:
```bash
cat output.txt
# Or on Windows:
type output.txt
```

### Windows Path Handling

- Use forward slashes `/` or escaped backslashes `\\` in paths
- When redirecting output, use relative paths when possible
- Example: `gemini chat "prompt" > .tmp/gemini-response.txt`

## Best Practices

1. **Use for quick questions**, not long conversations
   - Gemini CLI is best for single-turn queries
   - For complex multi-turn conversations, consider other tools

2. **Always redirect long outputs to files**
   - Prevents token limits and makes responses easier to process
   - Use: `gemini chat "prompt" > output.txt`

3. **Combine with other tools**
   - Use `bash` to call Gemini CLI
   - Use `Read` to read the output file
   - Use `Write` or `Edit` to incorporate results into your work

4. **Be quota-aware**
   - Check quota before every request
   - Log quota usage in your responses
   - Example: "Used Gemini CLI (quota: 42/1000 remaining today)"

## Error Handling

### CLI Not Found

If `gemini` command is not found:
- Verify Gemini CLI is installed: `where gemini` (Windows) or `which gemini` (Unix)
- Check if it's in PATH
- Inform the user that Gemini CLI needs to be installed

### Quota Exceeded

If quota is exceeded:
- DO NOT make the request
- Inform the user: "Gemini quota exceeded (1000/1000 requests used today). Quota resets at midnight."
- Suggest alternatives or waiting until reset

### API Errors

If Gemini CLI returns an error:
- Read the error message carefully
- Common issues:
  - Invalid API key
  - Network issues
  - Model unavailable
- Report the error to the user with the actual error message

## Example Workflow

1. **Check quota**:
   ```bash
   type runtime\gemini-quota.json
   ```

2. **Make request** (if quota available):
   ```bash
   gemini chat --model gemini-2.5-pro "Generate a color palette for a modern e-commerce website" > .tmp/gemini-colors.txt
   ```

3. **Read result**:
   ```bash
   type .tmp\gemini-colors.txt
   ```

4. **Use the result** in your work (via Write/Edit tools)

## Configuration

The Gemini CLI uses project-level configuration from `.gemini/settings.json` if present. Default model and settings are configured there.

## Security Notes

- Never hardcode API keys in commands
- API keys should be in environment variables or `.gemini/settings.json` (which should be in `.gitignore`)
- The `bash` tool allows execution of any command - use responsibly
