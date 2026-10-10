import asyncio
import logging
from datetime import datetime, timezone
from telegram_manager.session_security import validate_session

log = logging.getLogger(__name__)

class SessionHealthWorker:
    def __init__(self, db, settings, interval=3600):
        self.db, self.settings, self.interval = db, settings, max(60, interval)
        self._task = None
        self._stop = asyncio.Event()

    async def start(self):
        if not self._task or self._task.done():
            self._stop.clear()
            self._task = asyncio.create_task(self.run(), name="session-health")

    async def run(self):
        while not self._stop.is_set():
            try:
                cursor = self.db.sessions.find({}, {"encrypted_session": 1, "owner_id": 1, "account_id": 1})
                async for doc in cursor:
                    try:
                        result = await validate_session(self.settings, doc["encrypted_session"])
                        await self.db.sessions.update_one(
                            {"_id": doc["_id"]},
                            {"$set": {"last_checked_at": datetime.now(timezone.utc),
                                      "session_valid": result["valid"]}},
                        )
                    except asyncio.CancelledError:
                        raise
                    except Exception:
                        log.warning("Session health check failed for account %s", doc.get("account_id"), exc_info=True)
            except asyncio.CancelledError:
                raise
            except Exception:
                log.exception("Session health cycle failed")
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=self.interval)
            except asyncio.TimeoutError:
                pass

    async def stop(self):
        self._stop.set()
        if self._task:
            self._task.cancel()
            await asyncio.gather(self._task, return_exceptions=True)
            self._task = None
