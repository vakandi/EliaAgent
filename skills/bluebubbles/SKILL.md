---
name: bluebubbles
description: Build or update the BlueBubbles external channel plugin for OpenClaw (extension package, REST send/probe, webhook inbound).
---

# BlueBubbles

## Overview

This skill enables building or updating the BlueBubbles external channel plugin for OpenClaw. It provides comprehensive support for creating extension packages, REST API integration for sending messages, and webhook handling for inbound communications.

## Quick Start

Initialize a new BlueBubbles plugin:

```bash
# Initialize new BlueBubbles plugin
bluebubbles init --name "My BlueBubbles Plugin" --version 1.0.0
```

Build the plugin package:

```bash
# Build the plugin
bluebubbles build
```

## Core Capabilities

### 1. Plugin Development
- Extension package creation and management
- Plugin structure generation
- Configuration file setup
- Asset bundling and management

### 2. REST API Integration
- REST API endpoint configuration
- Message sending functionality
- API authentication setup
- Rate limiting and error handling

### 3. Webhook Inbound Support
- Webhook endpoint configuration
- Message reception handling
- Event processing pipeline
- Response formatting

### 4. Plugin Packaging
- Plugin compilation and bundling
- Dependency management
- Version control integration
- Distribution preparation

## Usage Patterns

### Plugin Development Workflow
```bash
# Initialize new plugin
bluebubbles init --name "MyPlugin" --template basic

# Add REST functionality
bluebubbles add rest --send --probe

# Add webhook support
bluebubbles add webhook --inbound

# Build and test
bluebubbles build --test
```

### Plugin Update Process
```bash
# Update existing plugin
bluebubbles update --path ./my-plugin

# Add new features
bluebubbles add feature --name "new-feature" --type rest

# Rebuild and deploy
bluebubbles build --deploy
```

## Available Tools

The skill provides specialized tools for:
- Plugin initialization and scaffolding
- REST API endpoint generation
- Webhook configuration
- Package building and testing
- Deployment automation

## Examples

### Basic Plugin Creation
```
Task: "Create a basic BlueBubbles plugin for message sending"
Command: bluebubbles init --name "MessageSender" --template basic --rest --send
```

### Advanced Plugin with Webhooks
```
Task: "Build a plugin with REST API and webhook support"
Command: bluebubbles init --name "AdvancedPlugin" --template advanced --rest --send --probe --webhook --inbound
```

### Plugin Update
```
Task: "Update existing BlueBubbles plugin with new features"
Command: bluebubbles update --path ./my-plugin --add rest --probe --version 2.0.0
```

## Configuration

### Plugin Configuration File
The plugin uses a `bluebubbles.config.json` file for configuration:

```json
{
  "name": "My Plugin",
  "version": "1.0.0",
  "description": "Plugin description",
  "author": "Plugin author",
  "rest": {
    "enabled": true,
    "endpoints": {
      "send": "/api/send",
      "probe": "/api/probe"
    }
  },
  "webhook": {
    "enabled": true,
    "endpoint": "/webhook/inbound",
    "events": ["message", "status", "delivery"]
  }
}
```

## File Structure

A typical BlueBubbles plugin structure:

```
my-plugin/
├── src/
│   ├── main.js          - Main plugin file
│   ├── rest/            - REST API handlers
│   ├── webhook/         - Webhook handlers
│   └── utils/           - Utility functions
├── config/
│   └── bluebubbles.config.json
├── assets/              - Static assets and templates
├── tests/               - Test files
└── package.json         - Package metadata
```

## Testing

Run plugin tests:

```bash
# Run all tests
bluebubbles test

# Run specific test type
bluebubbles test --rest
bluebubbles test --webhook
```

## Deployment

Deploy plugin to OpenClaw:

```bash
# Deploy plugin
bluebubbles deploy --target openclaw

# Deploy with custom configuration
bluebubbles deploy --config custom.config.json
```