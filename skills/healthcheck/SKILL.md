---
name: healthcheck
description: Host security hardening and risk-tolerance configuration for OpenClaw deployments. Use when users ask for security audits, firewall/SSH/update hardening, risk posture assessment, exposure review, OpenClaw cron scheduling for periodic checks, or version status checks on machines running OpenClaw (laptop, workstation, Pi, VPS).
---

# Healthcheck

## Overview

This skill provides comprehensive host security hardening and risk-tolerance configuration for OpenClaw deployments. It enables security audits, firewall/SSH/update hardening, risk posture assessments, exposure reviews, and periodic health checks through cron scheduling.

## Quick Start

Run a basic security healthcheck:

```bash
# Perform comprehensive security assessment
healthcheck --full-audit
```

Configure periodic security monitoring:

```bash
# Set up daily security checks
healthcheck --setup-cron --daily
```

## Core Capabilities

### 1. Security Audits
- Comprehensive system security assessment
- Vulnerability detection and reporting
- Configuration validation
- Compliance checking

### 2. Firewall & SSH Hardening
- Firewall rule optimization
- SSH security configuration
- Port management and access control
- Service exposure reduction

### 3. Risk Posture Assessment
- System exposure analysis
- Attack surface mapping
- Risk scoring and prioritization
- Mitigation recommendations

### 4. Update Management
- System package updates
- OpenClaw version management
- Security patch application
- Update scheduling and automation

### 5. Periodic Health Monitoring
- Cron-based scheduling for continuous monitoring
- Automated status reporting
- Performance metrics collection
- Alert configuration

## Usage Patterns

### One-Time Security Assessment
```bash
healthcheck --full-audit --report
```

### Continuous Monitoring Setup
```bash
healthcheck --setup-cron --daily --weekly --monthly
```

### Hardening Configuration
```bash
healthcheck --harden --firewall --ssh --backups
```

## Available Tools

The skill integrates with system tools to provide:
- Security scanning and assessment
- Firewall configuration management
- SSH security hardening
- Update automation
- Cron job management
- Reporting and logging

## Examples

### Security Audit on Workstation
```
Task: "Perform security audit on my Windows workstation"
Command: healthcheck --full-audit --os windows --report detailed
```

### Server Hardening
```
Task: "Harden my OpenClaw server for production use"
Command: healthcheck --harden --firewall --ssh --monitoring --auto-apply
```

### Version Status Check
```
Task: "Check OpenClaw version and system status"
Command: healthcheck --version --status --health-check
```

## Configuration Files

The skill supports various configuration files for customization:

- `healthcheck.conf` - Main configuration settings
- `firewall-rules.conf` - Firewall configuration
- `ssh-hardening.conf` - SSH security settings
- `monitoring.conf` - Health monitoring configuration
- `exclusions.conf` - Exclusions for specific checks