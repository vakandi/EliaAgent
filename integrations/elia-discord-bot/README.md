# EliaDiscord Bot v2 — Production SaaS Rebuild

## 🎯 Goal

Rebuild the EliaDiscord bot from scratch to be a high-performance, scalable, and reliable production SaaS integration. The current version has perfect logic (message queue, context injection, channel awareness) but suffers from performance bottlenecks that cause lagging and crashes after a single message.

## 🚀 Architecture Principles

1.  **Async-First**: All I/O operations (HTTP requests, file I/O) must be non-blocking.
2.  **Concurrency Control**: Use semaphores to limit concurrent OpenCode requests, preventing resource exhaustion.
3.  **Stateless Design**: Move session state out of the process (Redis/DB) or use ephemeral sessions to allow horizontal scaling.
4.  **Observability**: Structured logging and health checks for monitoring.
5.  **Graceful Degradation**: Handle OpenCode downtime or slowness without crashing the Discord bot.

## 🧩 Features (Preserved from v1)

*   **Context Injection**: Automatically injects channel context (name, ID, recent messages) into the prompt so the AI knows where to answer.
*   **MCP Integration**: Prompts are formatted to include `mcp-cli` instructions for direct Discord replies.
*   **Triggers**: Responds to bot mentions and replies.
*   **Slash Commands**:
    *   `/elia <message>`: Talk to Elia.
    *   `/elia-reset`: Reset session.
    *   `/elia-new`: Create new session.
    *   `/elia-session-list`: List sessions.
    *   `/elia-session-select`: Switch session.
*   **Error Reporting**: Logs errors to a dedicated Discord channel.
*   **Access Control**: Restrict slash commands and mention triggers to approved Discord user IDs via `DISCORD_ALLOWED_USER_IDS`.

## 🛠️ Technical Stack

*   **Language**: Python 3.11+
*   **Discord Library**: `discord.py` (async)
*   **HTTP Client**: `httpx` (async) — replacing synchronous `opencode-ai` calls.
*   **Logging**: `structlog` (structured, performant).
*   **State Management**: In-memory with TTL (or optional Redis).
*   **Deployment**: Docker container.

### Access Control

Set `DISCORD_ALLOWED_USER_IDS` to a comma-separated list of Discord user IDs. The bot will only accept `/elia`, `/elia-new`, `/elia-reset`, `/elia-session-list`, and @mention prompts from those users.

## 📦 Project Structure

```
integrations/elia-discord-bot/
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── README.md
├── src/
│   ├── __init__.py
│   ├── bot.py              # Discord bot core
│   ├── config.py           # Settings & Environment
│   ├── opencode_client.py  # Async OpenCode API wrapper
│   ├── session_manager.py  # Session lifecycle
│   ├── message_handler.py  # Message processing & formatting
│   ├── context_tracker.py  # Channel context tracking
│   └── logging_config.py   # Structured logging setup
└── .env.example
```

## 🚨 Performance Bottlenecks to Fix

1.  **Synchronous HTTP Calls**: `opencode-ai` uses synchronous `requests` under the hood. Replace with `httpx.AsyncClient`.
2.  **Busy-Wait Loop**: The current `send_message` polls session status every 2s. Replace with async polling or webhooks if available.
3.  **Single-Threaded Queue**: The `MessageQueue` processes one message at a time. Replace with a worker pool controlled by `asyncio.Semaphore`.
4.  **Memory Leaks**: `MessageTracker` grows indefinitely. Implement TTL-based eviction.
5.  **Blocking Initialization**: `_detect_opencode_host` runs synchronous HTTP checks. Make it async.

## 📋 Implementation Plan

### Phase 1: Core Infrastructure
1.  **Setup**: `pyproject.toml` with dependencies (`discord.py`, `httpx`, `structlog`).
2.  **Config**: `config.py` using `pydantic-settings` for environment variables.
3.  **Logging**: `structlog` configuration for JSON logging.

### Phase 2: Async OpenCode Client
1.  **Wrapper**: `opencode_client.py` with `httpx.AsyncClient`.
2.  **Endpoints**: `create_session`, `send_message`, `list_sessions`, `delete_session`.
3.  **Retry Logic**: Exponential backoff for transient errors.

### Phase 3: Message Handling
1.  **Formatter**: `message_handler.py` to format prompts with Discord context.
2.  **Context Tracker**: `context_tracker.py` with TTL-based message history.
3.  **Concurrency**: `asyncio.Semaphore` to limit concurrent OpenCode requests.

### Phase 4: Discord Bot Integration
1.  **Bot Core**: `bot.py` with `discord.py` client.
2.  **Events**: `on_ready`, `on_message`.
3.  **Commands**: Slash commands implementation.

### Phase 5: Deployment
1.  **Dockerfile**: Multi-stage build for small image.
2.  **Health Check**: `/health` endpoint for monitoring.

## 🧪 Testing Strategy

*   **Unit Tests**: Mock OpenCode API calls.
*   **Integration Tests**: Mock Discord API.
*   **Load Testing**: Simulate multiple concurrent users.

## 📊 Success Metrics

*   **Latency**: Response time < 2s for simple queries.
*   **Throughput**: Handle 10+ concurrent messages without queuing delays.
*   **Stability**: Run for 24h+ without crashes or memory leaks.
