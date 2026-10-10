import asyncio
import logging
from datetime import datetime, timezone

log = logging.getLogger(__name__)

class ChannelWatcher:
    def __init__(self, db, interval=10):
        self.db, self.interval = db, max(1, interval)
        self._task = None
        self._stop = asyncio.Event()

    async def start(self):
        if self._task and not self._task.done():
            return
        self._stop.clear()
        self._task = asyncio.create_task(self.run(), name="channel-watcher")

    async def run(self):
        while not self._stop.is_set():
            try:
                # Telegram updates are handled by the bot; this worker records that
                # configured channel monitoring is enabled and leaves event handling
                # to the update dispatcher to avoid unreliable history scraping.
                await self.db.monitored_channels.update_many(
                    {"enabled": True},
                    {"$set": {"last_worker_check": datetime.now(timezone.utc)}},
                )
            except asyncio.CancelledError:
                raise
            except Exception:
                log.exception("Channel watcher cycle failed")
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
