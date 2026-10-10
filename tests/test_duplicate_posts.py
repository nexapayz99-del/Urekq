import pytest
from pymongo.errors import DuplicateKeyError
from services.engagement_service import EngagementService

class FakePosts:
    def __init__(self): self.seen = set()
    async def insert_one(self, doc):
        key = (doc["channel_id"], doc["message_id"])
        if key in self.seen: raise DuplicateKeyError("duplicate")
        self.seen.add(key)

class FakeDB:
    def __init__(self): self.processed_posts = FakePosts()

@pytest.mark.asyncio
async def test_duplicate_post_is_not_claimed_twice():
    service = EngagementService(FakeDB())
    assert await service.claim_post(1, 2, 3) is True
    assert await service.claim_post(1, 2, 3) is False
