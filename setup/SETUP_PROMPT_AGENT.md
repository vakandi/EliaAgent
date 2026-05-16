# Quick Setup - EliaAI for Friend

Your friend has EliaAI. You have the repo and bot token. Make it work for YOU.

## Step 1: Verify Bot Config
```bash
cat ~/EliaAI/telegram-opencode-bot/.env
```
YOUR .env needs:
- `TELEGRAM_BOT_TOKENS=` (YOUR bot from @BotFather)
- `ALLOWED_USER_IDS=` (YOUR Telegram user ID)

## Step 2: Test Bot
```bash
cd ~/EliaAI/telegram-opencode-bot && npm start
```
Stop with Ctrl+C. Should connect in 5s.

## Step 3: Test Agent
```bash
cd ~/EliaAI && ./start_agents.sh --model=big-pickle --extra-prompt="Hello"
```

## Step 4: Install Cron (Optional)
```bash
cd ~/EliaAI && ./manage_cron.sh install --interval 2h --start 10 --end 22
```

---

## Customize Later

Replace placeholder content in:
- `context/business.md` → YOUR businesses
- `context/TOOLS.md` → YOUR MCP servers, channels
- `PROMPT.md` → YOUR personality
- `memory/MEMORY.md` → YOUR memory

Full guide: `setup/README.md` lines 936-1043.