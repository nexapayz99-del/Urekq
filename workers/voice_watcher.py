import asyncio
import logging

log = logging.getLogger(__name__)

class VoiceWatcher:
    """Lifecycle worker. Live call detection requires a verified voice adapter."""
    def __init__(self, interval=5):
        self.interval = max(1, interval)
        self._stop = asyncio.Event()
        self._task = None

    async def start(self):
        if not self._task or self._task.done():
            self._stop.clear()
            self._task = asyncio.create_task(self.run(), name="voice-watcher")

    async def run(self):
        while not self._stop.is_set():
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=self.interval)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                raise

    async def stop(self):
        self._stop.set()
        if self._task:
            self._task.cancel()
            await asyncio.gather(self._task, return_exceptions=True)
            self._task = None
