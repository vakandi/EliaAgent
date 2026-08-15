import asyncio
import sys
import os
import signal
from pathlib import Path
from src.logging_config import setup_logging
from src.config import get_settings
from src.bot import EliaDiscordBot

PID_FILE = Path(__file__).parent / "bot.pid"


def acquire_pid_lock():
    if PID_FILE.exists():
        old_pid = int(PID_FILE.read_text().strip())
        try:
            os.kill(old_pid, 0)
            print(f"Another instance is running (PID {old_pid}). Kill it first.", file=sys.stderr)
            sys.exit(1)
        except ProcessLookupError:
            pass
    PID_FILE.write_text(str(os.getpid()))


def release_pid_lock():
    if PID_FILE.exists():
        try:
            if int(PID_FILE.read_text().strip()) == os.getpid():
                PID_FILE.unlink()
        except (ValueError, FileNotFoundError):
            pass


async def main():
    settings = get_settings()
    setup_logging(settings.LOG_DIR)
    acquire_pid_lock()

    bot = EliaDiscordBot(settings)

    try:
        await bot.start(settings.DISCORD_BOT_TOKEN)
    except KeyboardInterrupt:
        await bot.close()
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        await bot.close()
        sys.exit(1)
    finally:
        release_pid_lock()


if __name__ == "__main__":
    asyncio.run(main())
