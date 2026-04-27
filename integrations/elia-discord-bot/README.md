# EliaDiscord Bot

Discord integration for EliaAI - Talk to Elia from any channel in your Discord server.

## Quick Start

### 1. Create a Discord Bot

1. Go to https://discord.com/developers/applications
2. Create a new application
3. Go to "Bot" section and create a bot
4. Enable **Message Content Intent** in Bot settings
5. Copy the bot token

### 2. Invite Bot to Server

1. Go to "OAuth2" → "URL Generator"
2. Select scopes: `bot`
3. Select permissions: `Send Messages`, `Read Message History`, `Use Slash Commands`
4. Use the generated URL to invite the bot

### 3. Configure

```bash
cd elia-discord-bot
cp .env.example .env
```

Edit `.env`:
```
DISCORD_BOT_TOKEN=your_token_here
OPENCODE_HOST=http://localhost:8080
OPENCODE_API_KEY=
```

### 4. Install & Run

```bash
# Via script
../scripts/start_elias_discord.sh

# Or manually
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python bot.py
```

## Usage

### Mention Elia
```
@YourBotName hey, can you help me with something?
```

### Slash Commands
- `/elia <message>` - Talk to Elia directly
- `/elia-reset` - Reset session and start fresh

## Commands

```bash
# Start bot
./scripts/start_elias_discord.sh

# Stop bot
./scripts/stop_elias_discord.sh
```