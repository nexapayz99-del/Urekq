import pytest
from telegram_manager.authorization import role_for

class FakeCollection:
    def __init__(self, doc=None): self.doc = doc
    async def find_one(self, query): return self.doc

class FakeDB:
    def __init__(self, doc=None): self.admins = FakeCollection(doc)

@pytest.mark.asyncio
async def test_owner_role():
    assert await role_for(FakeDB(), 7, 7) == "OWNER"

@pytest.mark.asyncio
async def test_user_role():
    assert await role_for(FakeDB(), 8, 7) == "USER"
