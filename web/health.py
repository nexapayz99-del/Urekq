from aiohttp import web

def create_health_app(database, bot, settings):
    app = web.Application()

    async def root(request):
        return web.json_response({"service": "telegram-account-manager", "status": "running"})

    async def health(request):
        return web.json_response({"status": "ok"})

    async def ready(request):
        db_ok = await database.ready()
        bot_ok = bool(getattr(bot, "is_connected", False))
        payload = {"ready": bool(db_ok and bot_ok), "mongodb": db_ok, "telegram_client": bot_ok}
        return web.json_response(payload, status=200 if payload["ready"] else 503)

    app.router.add_get("/", root)
    app.router.add_get("/health", health)
    app.router.add_get("/ready", ready)
    return app
