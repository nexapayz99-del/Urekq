import pytest
from database.repositories import Repository

class FakeUsers:
    async def update_one(self, *args, **kwargs): self.called = True

class FakeDB:
    users = FakeUsers()

@pytest.mark.asyncio
async def test_ensure_user_upserts():
    db = FakeDB()
    await Repository(db).ensure_user(123, "tester")
    assert db.users.called
