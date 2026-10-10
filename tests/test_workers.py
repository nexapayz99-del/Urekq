import asyncio
import pytest
from workers.task_queue import TaskQueue

@pytest.mark.asyncio
async def test_task_queue_cancels_cleanly():
    queue = TaskQueue()
    await queue.start(1)
    await queue.put(lambda: asyncio.sleep(0))
    await asyncio.wait_for(queue.queue.join(), timeout=1)
    await queue.close()
    assert queue._workers == []
