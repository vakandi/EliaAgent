---
name: macos-system-health
description: "Full macOS system health diagnosis — CPU, GPU, RAM, swap, thermals, disk, and process analysis. Use this skill whenever the user asks to analyze their Mac performance, check what's using resources, diagnose slowness, investigate heat/thermal issues, check temperature sensors, or do a full system health check. TRIGGER on: 'analyze my mac', 'why is my mac slow', 'what's using my cpu/gpu/ram', 'check temperature', 'system health', 'check my mac', 'diagnose performance', 'resource usage', 'thermal throttling', 'what's eating my memory', 'my computer is hot', 'performance investigation', 'system analysis', even casual requests like 'my mac is dying' or 'what's wrong with my computer'."
compatibility: macOS only (uses native commands: top, ps, iostat, sysctl, powermetrics, pmset, log)
---

# macOS System Health Diagnostic

Full investigation of macOS system performance: resource consumers, thermal state, hardware health, and anomaly detection. Designed for diagnosing unexplained slowness, heat, or degradation.

## When to use

This skill runs when the user wants to know what's consuming resources on their Mac, or when they report slowness, heat, screen issues, or general "something is wrong" symptoms. It works on any Mac running macOS — no extra tools needed.

## Investigation workflow

Run the diagnostic scripts in order. Each script outputs structured data you interpret.

### Phase 1: Quick snapshot (always start here)

```bash
bash scripts/01-quick-snapshot.sh
```

Shows: uptime, load averages, top 10 CPU processes, top 10 RAM processes, swap usage, memory pressure. This tells you immediately if something is hogging resources.

### Phase 2: Detailed process analysis

```bash
bash scripts/02-process-deep.sh
```

Shows: all processes sorted by CPU, GPU processes (via `sudo powermetrics` if available), memory breakdown (physical + compressed + swap), open file descriptors count (leak detection), zombie processes.

### Phase 3: Thermal and hardware

```bash
bash scripts/03-thermal-hardware.sh
```

Shows: current CPU/GPU temperature sensors (via `powermetrics` — requires sudo once), SMC thermal data, battery health cycle count, fan speeds, thermal throttle events from kernel logs.

**Note:** `powermetrics` requires `sudo` — the script will prompt for password. If the user declines, it falls back to `ioreg` sensor data which is less precise.

### Phase 4: Disk and I/O

```bash
bash scripts/04-disk-io.sh
```

Shows: disk usage per volume, I/O wait times, SMART health status, spotlight indexing activity, Time Machine backup status (active backups consume heavy I/O).

### Phase 5: Historical logs

```bash
bash scripts/05-historical-logs.sh
```

Shows: kernel panic logs (last 7 days), thermal throttle events, OOM kills, crash reports for runaway processes, pmset sleep/wake history. This is where you find evidence of what happened over the past days/weeks.

### Phase 6: Network and background services

```bash
bash scripts/06-background-services.sh
```

Shows: launchd agents (user + system), network connections by process, DNS resolution speed, background upload/download activity (iCloud sync, Dropbox, etc.).

## Interpretation guide

After collecting data, synthesize findings into this structure:

### Resource consumers
- Top 3 CPU consumers (name, PID, % CPU, duration if available)
- Top 3 RAM consumers (name, PID, memory MB, virtual memory if notable)
- GPU consumers (any process using significant GPU)
- Swap usage trend (healthy: <500MB, concerning: 1-4GB, critical: >4GB)

### Thermal status
- Current temperature vs threshold (CPU >80°C = hot, >90°C = throttling risk)
- Fan RPM vs max (check if fans are spinning up or stuck)
- Thermal throttle events in last 24h

### Hardware health
- Battery cycle count vs max (MacBook models have different max cycles)
- SMART disk status (any pending/reallocation sectors)
- Screen/display connection (relevant if flickering reported)

### Anomalies detected
- Processes using >100% CPU for extended periods
- Memory leaks (process memory growing unbounded)
- Excessive swap usage indicating RAM exhaustion
- Disk I/O saturation (>80% utilization sustained)
- Kernel thermal throttle events

### Orange juice spill context
Given the user's spill history, specifically check:
- Battery health — liquid damage often affects battery first
- Screen flickering — could be liquid damage to display connector
- Thermal paste degradation — if the device was opened for cleaning, thermal paste may have been disturbed
- Fan behavior — liquid near vents could affect cooling

## Output format

Present results as a diagnostic report with:
1. **System overview** — model, RAM, disk, uptime, OS version
2. **Top resource consumers** — tables with process name, PID, resource, value
3. **Thermal analysis** — temperature, fan speed, throttle events
4. **Hardware health** — battery, disk SMART, display
5. **Historical issues** — crashes, OOM kills, throttle events
6. **Diagnosis** — what's likely causing the slowness, ranked by probability
7. **Recommendations** — actionable steps to fix or investigate further

## Tips

- If `powermetrics` fails (no sudo), the thermal section will be limited. Still valuable without it.
- On Apple Silicon Macs, GPU usage shows differently — check `sudo powermetrics --gpu` or Activity Monitor's GPU tab equivalent.
- If the user just wants a quick check, only run Phase 1 and 2. Full investigation is Phases 1-6.
- Context matters: a MacBook that was recently exposed to liquid needs extra attention on thermal and battery.
