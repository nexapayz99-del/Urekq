import asyncio
import logging
from aiohttp import web
from pyrogram import Client
from config.settings import Settings
from database.connection import Database
from database.indexes import create_indexes
from telegram_manager.bot import register_handlers
from web.health import create_health_app

async def main():
    settings = Settings.from_env()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    log = logging.getLogger("telegram_manager")
    db = Database(settings.mongo_uri, settings.db_name)
    await db.connect()
    await create_indexes(db.db)
    bot = Client(
        "manager_bot",
        api_id=settings.api_id,
        api_hash=settings.api_hash,
        bot_token=settings.bot_token,
        workdir=str(settings.data_dir),
    )
    bot.db = db.db
    bot.settings = settings
    register_handlers(bot)
    health_app = create_health_app(db, bot, settings)
    runner = web.AppRunner(health_app)
    await runner.setup()
    site = web.TCPSite(runner, settings.host, settings.port)
    await site.start()
    try:
        await bot.start()
        log.info("Telegram Account Manager started")
        await asyncio.Event().wait()
    finally:
        try:
            await bot.stop()
        except Exception:
            log.exception("Error stopping Telegram bot")
        await runner.cleanup()
        await db.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
