<p align="center">
  <img src="https://img.shields.io/badge/EliaAI-v3.0-8B5CF6?style=for-the-badge&logo=OpenAI&logoColor=white&labelColor=1E1B4B" alt="EliaAI v3.0">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/OpenCode-big--pickle-FF6B6B?style=flat&logo=openai" alt="OpenCode">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-22C55E?style=flat" alt="Status">
  <img src="https://img.shields.io/badge/Memory-1.3GB%20%7C%203400%2B%20Sessions-8B5CF6?style=flat" alt="Memory">
  <img src="https://img.shields.io/badge/Subagents-13%20Specialized-3B82F6?style=flat" alt="Subagents">
  <img src="https://img.shields.io/badge/UI-Electron%20Overlay-F59E0B?style=flat&logo=electron" alt="Electron UI">
  <img src="https://img.shields.io/badge/Voice-Whisper%20Dictation-EC4899?style=flat" alt="Voice">
  <img src="https://img.shields.io/badge/License-MIT-10B981?style=flat" alt="License">
</p>

<h1 align="center">🧠 EliaAI — The Self-Improving AI Agent</h1>

<p align="center">
  <strong>An autonomous AI agent that remembers everything, gets smarter with every session,</strong><br>
  and orchestrates 13 specialized subagents to run your digital life — from code to marketing to operations.
</p>

<p align="center">
  <code>Voice dictate → Model selection → Autonomous execution → Persistent memory → Smarter tomorrow</code>
</p>

---

<p align="center">
  <img src="https://i.imgur.com/qDhWtkl.png" alt="EliaAI Main Interface" width="700">
</p>
<p align="center"><em>The EliaAI floating overlay — model selection, voice control, cron scheduling, and status monitoring.</em></p>

---

## ✨ The Breakthrough: Persistent Memory

**EliaAI's most powerful feature: the agent remembers everything and gets smarter with every session.**

Unlike traditional AI agents that start from scratch on each interaction, EliaAI uses a **persistent memory system (codemem)** that captures every session, every decision, every fix, and every discovery — then feeds it back into future sessions.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            CODEMEM LOOP                                      │
│                                                                              │
│     ┌──────────────┐          ┌──────────────────┐          ┌────────────┐ │
│     │  Agent        │  ──→    │  Captures         │  ──→    │  SQLite DB  │ │
│     │  Session      │         │  decisions, bugs, │         │  (1.3 GB)   │ │
│     └──────┬───────┘         │  discoveries      │         └──────┬─────┘ │
│            │                  └──────────────────┘                │        │
│            │              ┌──────────────────────┐               │        │
│            └──────────────│  Next run loads      │ ←─────────────┘        │
│                           │  relevant past       │                        │
│                           │  context → avoids    │                        │
│                           │  mistakes, builds    │                        │
│                           │  on previous work    │                        │
│                           └──────────────────────┘                        │
│                                                                              │
│              🔁 Loop repeats — agent gets smarter every session              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 🖥️ Memory Viewer Dashboard

Monitor your agent's memory in real-time: session history, health metrics, and sync status.

![Codemem Sync Viewer](screenshots/codemem-sync-viewer.png)

*The codemem dashboard showing per-agent memory, health status, database size, and sync/team management.*

Key dashboard features:

| Feature | Description |
|---------|-------------|
| **Per-agent memory scoping** | Each subagent (Gilfoyle, Setbon, Picasso, etc.) has its own indexed history — no context pollution |
| **Automatic context injection** | On each run, relevant past sessions, decisions, and bug fixes are loaded automatically |
| **Hybrid search** | Combines semantic (embedding) + keyword search for maximum relevance |
| **Sync across devices** | Multiple machines share memory via the team sync system |
| **Handoff continuity** | Session summaries preserve context across task switches and agent changes |

### 📊 Track Record

| Metric | Value | Impact |
|--------|-------|--------|
| **Total sessions indexed** | 3,400+ | Years of accumulated experience |
| **Database size** | 1.3 GB | Deep knowledge across domains |
| **Active subagents** | 15+ | Specialists for every task |
| **Self-improvement** | Every session | Never makes the same mistake twice |

### 🧠 What the Agent Remembers

| Capability | Why It Matters |
|------------|---------------|
| **Bug fixes & root causes** | Never makes the same mistake twice |
| **Business decisions** | Remembers why certain choices were made |
| **User preferences** | Adapts to your communication style and workflow |
| **Discovered solutions** | Reuses past solutions instead of reinventing |
| **Project context** | Understands the full scope of each project |
| **Dependencies & gotchas** | Remembers which versions work and which break |

> 💡 **The memory system is what makes EliaAI not just an AI assistant, but a continuously improving digital colleague that learns from experience.**

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ELIA — SYSTEM ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │                   USER INTERFACES                               │       │
│  │  ┌────────────┐  ┌──────────┐  ┌────────────┐  ┌─────────────┐ │       │
│  │  │  Elia UI   │  │   CLI    │  │  Discord   │  │  Telegram   │ │       │
│  │  │ (Electron) │  │ (Manual) │  │   Bot      │  │   Bot       │ │       │
│  │  └─────┬──────┘  └────┬─────┘  └──────┬─────┘  └──────┬──────┘ │       │
│  └────────┼──────────────┼───────────────┼───────────────┼────────┘       │
│           │              │               │               │                 │
│           └──────────────┴───────┬───────┴───────────────┘                 │
│                                  ▼                                         │
│                   ┌──────────────────────────┐                             │
│                   │   start_agents.sh        │                             │
│                   │   trigger_opencode_      │                             │
│                   │   interactive.sh         │                             │
│                   └────────────┬─────────────┘                             │
│                                ▼                                           │
│                   ┌──────────────────────────┐                             │
│                   │     oh-my-opencode       │                             │
│                   │  Rich logging · ULW/Ralph│                             │
│                   └────────────┬─────────────┘                             │
│                                ▼                                           │
│                   ┌──────────────────────────┐                             │
│                   │        OpenCode          │                             │
│                   │   AI Agent Engine        │                             │
│                   └────────────┬─────────────┘                             │
│                                │                                           │
│           ┌────────────────────┼────────────────────┐                      │
│           ▼                    ▼                    ▼                      │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │  13 Specialized │  │   Persistent     │  │  Proxy Rotation  │          │
│  │   Subagents     │  │   Memory (SQLite)│  │  (Auto/Manual)   │          │
│  └─────────────────┘  └──────────────────┘  └──────────────────┘          │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │                  SCHEDULING & AUTOMATION                        │       │
│  │  ┌────────────┐  ┌────────────────┐  ┌──────────────────────┐ │       │
│  │  │   Cron     │  │  LaunchAgent   │  │  Morning Routine     │ │       │
│  │  │ (manage_   │  │  (macOS)       │  │  (Automated Briefing)│ │       │
│  │  │  cron.sh)  │  │                │  │                      │ │       │
│  │  └────────────┘  └────────────────┘  └──────────────────────┘ │       │
│  └─────────────────────────────────────────────────────────────────┘       │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │                   TELEMETRY & OBSERVABILITY                    │       │
│  │  ┌────────────┐  ┌────────────────┐  ┌────────────────────────┐│       │
│  │  │  Langfuse  │  │  Session Logs  │  │  OpenTelemetry Tracing ││       │
│  │  │ Dashboard  │  │  (oh-my-opencode)│  │                       ││       │
│  │  └────────────┘  └────────────────┘  └────────────────────────┘│       │
│  └─────────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Features

| Feature | Details | Impact |
|---------|---------|--------|
| **🧠 Persistent Memory** | SQLite-backed, hybrid search (semantic + keyword), per-agent scoping | Never repeats mistakes, builds on past knowledge |
| **📡 Sync Across Devices** | Shared memory via team sync — multiple machines share the same knowledge base | Consistent context everywhere |
| **🔄 Handoff Continuity** | Session summaries preserve context across task switches and agent changes | No context loss between sessions |
| **🎤 Voice Control** | Whisper dictation via Elia UI orb click | Hands-free operation |
| **🔄 Automatic Scheduling** | Cron / LaunchAgent with configurable intervals (20min–4h) | 24/7 autonomous operation |
| **🔀 Proxy Rotation** | Auto/manual proxy switching with health checks and history | Bypass geo-restrictions, avoid rate limits |
| **🧩 13 Subagents** | Specialists for backend, frontend, marketing, sales, content, ops, etc. | Domain expertise for every task |
| **🎨 Model Selection** | BigPickle (200K ctx), Kimi2.5 (128K), MiniMax2.5 (1M ctx) | Flexibility for any task size |
| **🔁 ULW/Ralph Loops** | Unlimited iterations / 50-iteration max autonomous work loops | Self-directed task completion |
| **💬 Discord Integration** | Chat with Elia via `@elia_bot` with persistent sessions | Access from any device |
| **📊 Langfuse Telemetry** | OpenTelemetry tracing, cost tracking, performance metrics | Full observability |
| **🌅 Morning Briefing** | Automated daily reports via Telegram/WhatsApp | Start informed |

---

## 🧩 The Subagent System

EliaAI orchestrates **13 specialized subagents**, each with a unique personality, domain expertise, and signature style.

| Category | Name | Role | Signature Phrase |
|----------|:----:|------|-----------------|
| **Backend** | 🛠️ Oliver | APIs, databases, Docker, CI/CD | *"The solution is straightforward."* |
| **Frontend** | 🎨 James | React, UI/UX, animations | *"It should make you want to click."* |
| **Finance** | 💰 William | Invoicing, payments, MayaVanta | *"Money follows when work is done well."* |
| **Marketing** | 📢 Victoria | TikTok, YouTube, Snapchat campaigns | *"The best marketing doesn't feel like marketing."* |
| **Sales** | 🤝 Charles | Lead generation, conversion, closing | *"The deal isn't closed until it's signed."* |
| **HR** | 👥 Elizabeth | Hiring, recruitment, employee management | *"The best hires are the ones where you don't hesitate."* |
| **Content** | 🎬 Marcus | Videos, thumbnails, scheduling, FFmpeg | *"Content is king, but distribution is queen."* |
| **E-commerce** | 👗 Charlotte | Luxury fashion resale | *"Luxury is in the details. And in authenticity."* |
| **Partnerships** | 🤝 Alexander | MayaKech coordination, relationship mgmt | *"Strong partnership, strong business."* |
| **Operations** | ⚙️ Sebastian | Jira, workflows, multi-SaaS deployment | *"A good system runs itself. A great system improves itself."* |
| **Customer Comms** | 💬 Catherine | WhatsApp, Telegram, Discord support | *"Every message is an impression. Make it count."* |
| **Growth** | 🚀 Ethan | Bot farms, account creation, ad campaigns | *"In growth, speed beats perfection."* |
| **Automation** | 🤖 Eleanor | TikTok/YouTube automation, Python/FastAPI | *"Work smart, automate the rest."* |

### How Subagents Work

```
User Request
     │
     ▼
┌─────────────────┐     ┌────────────────────┐
│  Sisyphus       │ ──→ │  Delegates to      │
│  (Orchestrator) │     │  best subagent     │
└─────────────────┘     └─────────┬──────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
     ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
     │  Oliver        │ │  James         │ │  Victoria      │
     │  (Backend)     │ │  (Frontend)    │ │  (Marketing)   │
     └────────────────┘ └────────────────┘ └────────────────┘
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  ▼
                      ┌────────────────────┐
                      │  Result returned   │
                      │  to user           │
                      └────────────────────┘
```

**Invocation methods:**
- `/ulw-loop` — Unlimited autonomous iterations
- `/ralph-loop` — 50 iterations max
- `task(category="backend-dev", prompt="...")` — Direct delegation

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| **OpenCode** | Latest | AI agent engine |
| **Node.js** | 18+ | For Elia UI Electron app |
| **Whisper** | Any | Voice dictation (optional) |

### 1. Clone

```bash
git clone https://github.com/user/EliaAgent.git
cd EliaAgent
```

### 2. Launch the UI

```bash
cd ui_electron
npm install
npm start
```

### 3. Select a Model

| Badge | Model | Context Window | Best For |
|-------|-------|:-------------:|:--------:|
| 🔴 **BigPickle** | `opencode/big-pickle` | 200K | General tasks, coding |
| 🟢 **Kimi2.5** | `mistralai/mixtral-8x7b` | 128K | Fast responses |
| 🟡 **MiniMax2.5** | `opencode/minimax-m2.5-free` | **1M** | Large context, documents |

### 4. Run Your First Task

**Voice:** Click the orb → dictate → agent runs with selected model.

**Manual CLI:**
```bash
./start_agents.sh --model=big-pickle --extra-prompt="Analyze my current project structure"
```

**Scheduled:**
```bash
./manage_cron.sh install --interval 2h --start 10 --end 22
```

---

## 🎮 Usage Modes

### 🎤 Voice (Elia UI)

Click the central orb → Whisper transcribes your voice → prompt is sent to `start_agents.sh` with the currently selected model.

### ⌨️ CLI Manual

```bash
# Basic run
./start_agents.sh --model=big-pickle

# With specific task
./start_agents.sh --model=big-pickle --extra-prompt="Review my Jira tickets and suggest priorities"

# Interactive with rich logging
OPENCODE_MODEL=opencode/big-pickle ./trigger_opencode_interactive.sh
```

### ⏰ Scheduled (Cron)

```bash
./manage_cron.sh install --interval 2h --start 10 --end 22
./manage_cron.sh install --interval 30min
./manage_cron.sh show
./manage_cron.sh uninstall
```

### 🍎 Scheduled (LaunchAgent — macOS)

```bash
./install_launchagent.sh
```

### 💬 Discord Bot

```bash
cd integrations/elia-discord-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python bot.py
```

---

## 🔄 Self-Improvement Cycle

```
  🔵 Session Runs
     │
     ▼
  📝 Key Insights Captured
     │
     ▼
  💾 Indexed in SQLite (per-agent, full-text + semantic search)
     │
     ▼
  🚀 Next Session Loads Relevant Memory
     │
     ▼
  🧠 Agent Gets Smarter — knows more, fewer mistakes, works faster
     │
     └─── 🔁 Loop repeats indefinitely
```

**3,400+ sessions and counting.**

---

## 📋 Session Continuity & Memory Management

### Session Continuity Commands (Start of Every Session)

To ensure the agent never repeats work or loses context, each session starts with these verification steps:

```bash
session_list(limit=20, from_date="YYYY-MM-DD")          # Check recent runs
session_search(query="topic name", limit=10)             # Find relevant discussions
session_read(session_id="ses_abc123", include_todos=true) # Read specific session
```

This workflow prevents duplicate work and ensures every session builds on past results rather than starting from scratch.

### 🛡️ Compaction Protection Protocol

OpenCode compacts context every 20–30 actions, which can cause the agent to forget what it was doing. EliaAI's memory system is hardened against this through several safeguards:

**Survival Checklist (used by the agent at every session start):**
1. **Restate the task** — Begin each response with one sentence restating the current task. If you can't formulate it, you've lost context — re-read the last user message immediately.
2. **Read the last message** — Before any action, verify you know exactly what was asked.
3. **Check scope** — Is this file/change explicitly in the scope of the request?
4. **Verify before proceeding** — Confirm the result of the last action before moving to the next.
5. **One task at a time** — New message = new task. Never continue old work in parallel.

**For the user — when the agent seems to "forget":**
- Simply repeat the instruction or reference the previous message
- The memory system will reload relevant context from the codemem database
- The agent automatically re-reads session history to recover continuity

### How Memory Survives Compaction

```
┌─────────────────────────────────────────────────────────────────┐
│                     MEMORY PERSISTENCE LAYER                      │
│                                                                  │
│  ┌──────────────┐    ┌─────────────────┐    ┌───────────────┐  │
│  │  Context     │ →  │  codemem DB     │ →  │  Reload on    │  │
│  │  Captured    │    │  (SQLite, 1.3GB)│    │  Next Session │  │
│  └──────────────┘    └─────────────────┘    └───────────────┘  │
│                                                                  │
│  Even if agent's working memory (context) is compacted,          │
│  the codemem database preserves all decisions, bugs, and         │
│  discoveries for the next session to reload automatically.       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Configuration

### Model Selection Flow

```
Elia UI (click badge) → saves to .opencode_model → cron/LaunchAgent reads it → uses same model
```

| UI Badge | `.opencode_model` | Model Used |
|----------|:-----------------:|:----------:|
| 🔴 BigPickle | `big-pickle` | `opencode/big-pickle` |
| 🟢 Kimi2.5 | `nvidia` | `mistralai/mixtral-8x7b-instruct-v0.1` |
| 🟡 MiniMax2.5 | `minimax` | `opencode/minimax-m2.5-free` |

### Proxy System

```bash
sp    # Auto mode — picks oldest unused proxy
spm   # Manual mode — show list, you pick
```

| Feature | Description |
|---------|-------------|
| **Auto mode** | Picks least recently used proxy |
| **Health check** | Tests each proxy before selecting |
| **History tracking** | Records usage timestamps and duration |
| **IP verification** | Shows new IP via ipify.org |

### Oh-My-OpenCode

```bash
touch .omo_disabled     # Use raw opencode instead
touch .ralph_mode       # 50-iteration limit instead of unlimited
```

---

## 🗂️ Project Structure

```
EliaAgent/
├── .opencode_model           # Current model selection
├── start_agents.sh           # Entry point for all runs
├── trigger_opencode_interactive.sh  # Main execution script
├── manage_cron.sh            # Cron install/uninstall/show
├── install_launchagent.sh    # macOS LaunchAgent setup
│
├── ui_electron/              # 🖥️ Elia floating overlay
│   ├── src/
│   │   ├── main.js
│   │   ├── preload.js
│   │   └── index.html
│   └── config.json
│
├── context/                  # 📄 Agent knowledge base
│   ├── business.md
│   ├── MEMORY.md
│   ├── TOOLS.md
│   └── jira-projects.md
│
├── integrations/             # 🔗 Third-party integrations
│   └── elia-discord-bot/
│
├── scripts/                  # 🔧 Automation scripts
├── setup/                    # ⚙️ Proxy & configuration
├── memory/                   # 💾 Persistent memory storage
├── brain/                    # 🧠 Agent brain configurations
│
├── PROMPT.md                 # Default system prompt
├── MORNING_PROMPT.md         # Morning briefing prompt
└── logs/                     # 📝 Execution logs
```

---

## 🛠️ Configuration Importante

**This system uses ONLY free OpenCode models.** No Claude, GPT, or paid models.

```json
{
  "model_fallback": false,
  "default_run_agent": "sisyphus",
  "agents": {
    "sisyphus": { "model": "opencode/big-pickle", "fallback_models": [] },
    "oliver-backend": { "model": "opencode/big-pickle", "fallback_models": [] }
  }
}
```

---

## 📡 Telemetry (Langfuse)

```bash
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."
export LANGFUSE_BASEURL="https://cloud.langfuse.com"
```

| Feature | Description |
|---------|-------------|
| **Session traces** | Every AI interaction, tool execution, timing |
| **Cost tracking** | Token usage and associated costs |
| **Visual dashboard** | Traces, spans, and metrics at Langfuse Cloud |

---

## ❓ Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| **Cron not firing** | macOS permissions | `./manage_cron.sh install --sudo` |
| **Wrong model** | `.opencode_model` outdated | Select model in Elia UI |
| **UI unresponsive** | Badges not rendering | `./ui_electron/run-debug.sh` |
| **Voice not working** | Whisper missing | Check microphone permissions |
| **Proxy not routing** | SIP blocking | Use HTTP_PROXY env vars |
| **Discord bot offline** | Token expired | Regenerate in Discord portal |
| **Agent forgets context** | Compaction cycle | Re-state the task — memory system reloads on next cycle |

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Agent Engine** | OpenCode |
| **UI** | Electron (Node.js) |
| **Voice** | Whisper (speech-to-text) |
| **Memory** | SQLite with embedding + keyword search |
| **Memory Dashboard** | Codemem Sync Viewer |
| **Scheduling** | Cron / macOS LaunchAgent |
| **Logging** | oh-my-opencode |
| **Telemetry** | Langfuse (OpenTelemetry) |
| **Integration** | Discord.py, Python |
| **Proxy** | HTTP_PROXY env vars, auto-rotation |

---

## 📄 License

**MIT** — Free to use, modify, and distribute.

---

<p align="center">
  <sub>Built with ❤️ by <strong>YourName YourSurname</strong> · © 2026</sub>
  <br>
  <sub><em>"The agent that remembers everything and gets smarter every session."</em></sub>
</p>
