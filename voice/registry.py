import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class VoiceTask:
    account_id: int
    chat_id: int
    task: asyncio.Task
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class VoiceRegistry:
    def __init__(self):
        self._tasks = {}
        self._lock = asyncio.Lock()

    async def add(self, account_id, chat_id, task):
        key = (int(account_id), int(chat_id))
        async with self._lock:
            existing = self._tasks.get(key)
            if existing and not existing.task.done():
                return False
            self._tasks[key] = VoiceTask(*key, task)
            return True

    async def remove(self, account_id, chat_id):
        async with self._lock:
            return self._tasks.pop((int(account_id), int(chat_id)), None)

    async def cancel(self, account_id, chat_id):
        item = await self.remove(account_id, chat_id)
        if item and not item.task.done():
            item.task.cancel()
            try:
                await item.task
            except asyncio.CancelledError:
                pass
            return True
        return False

    async def close(self):
        async with self._lock:
            items = list(self._tasks.values())
            self._tasks.clear()
        for item in items:
            item.task.cancel()
        await asyncio.gather(*(x.task for x in items), return_exceptions=True)
