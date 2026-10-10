import asyncio
import logging

log = logging.getLogger(__name__)

class TaskQueue:
    def __init__(self, concurrency=4, maxsize=100):
        self.queue = asyncio.Queue(maxsize=maxsize)
        self.semaphore = asyncio.Semaphore(concurrency)
        self._workers = []
        self._closed = False

    async def put(self, coro_factory):
        if self._closed:
            raise RuntimeError("Task queue is closed")
        await self.queue.put(coro_factory)

    async def _worker(self):
        while True:
            factory = await self.queue.get()
            try:
                async with self.semaphore:
                    await factory()
            except asyncio.CancelledError:
                raise
            except Exception:
                log.exception("Queued task failed")
            finally:
                self.queue.task_done()

    async def start(self, count=2):
        if not self._workers:
            self._closed = False
            self._workers = [asyncio.create_task(self._worker(), name=f"task-queue-{i}") for i in range(count)]

    async def close(self):
        self._closed = True
        for task in self._workers:
            task.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
