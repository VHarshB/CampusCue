"""Settings, read from environment variables (see .env.example)."""

import os
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
DATA_DIR = ROOT / "data"

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", "")
# Optional: a test server ID makes slash commands appear instantly instead of in up to an hour.
DISCORD_GUILD_ID = int(os.environ["DISCORD_GUILD_ID"]) if os.environ.get("DISCORD_GUILD_ID") else None

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
RALLY_MODEL = os.environ.get("RALLY_MODEL", "claude-opus-5-5")

DB_PATH = os.environ.get("RALLY_DB_PATH", str(ROOT / "rally.db"))
PORT = int(os.environ.get("PORT", "8080"))

# ASU is in Arizona, which does not observe daylight saving time.
TZ = ZoneInfo(os.environ.get("RALLY_TZ", "America/Phoenix"))

# How long a Decide session collects answers before Rally picks automatically.
DECIDE_DEFAULT_MINUTES = int(os.environ.get("RALLY_DECIDE_MINUTES", "10"))
# Private answers are deleted this long after a plan's time (or after it was created, if it had no time).
ANSWER_RETENTION_HOURS = 24
