"""Start Rally: the Discord bot and the web API, in one process. Run with `python -m rally`."""

import asyncio
import logging
import sys

import uvicorn

from . import config
from .api import create_app
from .bot import RallyBot
from .db import DB


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    if not config.DISCORD_TOKEN:
        sys.exit("DISCORD_TOKEN is not set. Copy .env.example to .env and fill it in (see README).")
    if not config.ANTHROPIC_API_KEY:
        logging.warning("ANTHROPIC_API_KEY is not set: using the simple keyword parser for preferences.")

    db = DB()
    await db.open()
    bot = RallyBot(db)
    server = uvicorn.Server(uvicorn.Config(create_app(bot), host="0.0.0.0", port=config.PORT, log_level="info"))
    try:
        await asyncio.gather(bot.start(config.DISCORD_TOKEN), server.serve())
    finally:
        await bot.close()
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
