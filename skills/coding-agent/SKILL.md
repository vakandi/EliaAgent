---
name: coding-agent
description: Run Codex CLI, Claude Code, OpenCode, or Pi Coding Agent via background process for programmatic control. Use when Codex needs to execute coding agents, run development tools, or perform software development tasks programmatically through background processes.
---

# Coding Agent

## Overview

This skill enables running coding agents and development tools through background processes for programmatic control and software development tasks.

## Quick Start

Use the sessions_spawn function to run coding agents in isolated sessions:

```python
# Spawn a coding agent session
sessions_spawn(
    task="Your coding task here",
    agentId="coding-agent",
    timeoutSeconds=300
)
```

## Core Capabilities

### 1. Running Codex CLI
Execute Codex CLI commands through background processes for code generation and analysis.

### 2. Claude Code Integration
Run Claude Code for advanced coding assistance and refactoring tasks.

### 3. OpenCode Operations
Utilize OpenCode for various programming languages and frameworks.

### 4. Pi Coding Agent
Deploy Pi Coding Agent for specific development workflows and automation.

## Usage Patterns

### Background Process Execution
All coding agents run in isolated background sessions to maintain system stability and prevent resource conflicts.

### Task-Based Execution
Specify coding tasks that need to be executed programmatically through the spawn system.

### Timeout Management
Configure appropriate timeouts for different types of coding operations based on complexity.

## Available Tools

The skill integrates with the OpenClaw sessions system to provide:
- Background process management
- Session isolation for safety
- Timeout and error handling
- Result capture and reporting

## Examples

### Code Generation
```
Task: "Generate a React component for user authentication"
Agent: coding-agent
Timeout: 300 seconds
```

### Code Analysis
```
Task: "Analyze this Python code for security vulnerabilities"
Agent: coding-agent
Timeout: 180 seconds
```

### Development Automation
```
Task: "Automate database schema migration"
Agent: coding-agent
Timeout: 600 seconds
```
