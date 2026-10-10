import asyncio
from voice.adapter import VoiceAdapter, VoiceAdapterUnavailable
from voice.registry import VoiceRegistry

class VoiceManager:
    def __init__(self, db):
        self.db = db
        self.adapter = VoiceAdapter()
        self.registry = VoiceRegistry()

    async def join(self, owner_id, account_id, chat_id, duration_seconds=300):
        if not await self.db.sessions.find_one({"owner_id": owner_id, "account_id": account_id}):
            raise PermissionError("Account does not belong to this user")
        raise VoiceAdapterUnavailable("Voice operations are disabled until a compatible adapter is verified.")

    async def leave(self, owner_id, account_id, chat_id):
        if not await self.db.sessions.find_one({"owner_id": owner_id, "account_id": account_id}):
            raise PermissionError("Account does not belong to this user")
        return await self.registry.cancel(account_id, chat_id)
