from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError

def utcnow():
    return datetime.now(timezone.utc)

class Repository:
    def __init__(self, db):
        self.db = db

    async def ensure_user(self, user_id: int, username=None):
        await self.db.users.update_one(
            {"user_id": user_id},
            {"$set": {"username": username, "updated_at": utcnow()},
             "$setOnInsert": {"created_at": utcnow(), "role": "USER"}},
            upsert=True,
        )

    async def role(self, user_id: int, owner_id: int) -> str:
        if user_id == owner_id:
            return "OWNER"
        doc = await self.db.admins.find_one({"user_id": user_id, "active": True})
        return doc.get("role", "ADMIN") if doc else "USER"

    async def list_sessions(self, owner_id: int):
        cursor = self.db.sessions.find(
            {"owner_id": owner_id},
            {"encrypted_session": 0, "session_string": 0},
        ).sort("created_at", -1)
        return await cursor.to_list(length=100)

    async def save_session(self, doc):
        try:
            await self.db.sessions.insert_one(doc)
            return True
        except DuplicateKeyError:
            return False

    async def record_task(self, owner_id, kind, status, details=None):
        await self.db.task_history.insert_one({
            "owner_id": owner_id, "kind": kind, "status": status,
            "details": details or {}, "created_at": utcnow(),
        })

    async def mark_post_once(self, channel_id: int, message_id: int, owner_id: int) -> bool:
        try:
            await self.db.processed_posts.insert_one({
                "channel_id": channel_id, "message_id": message_id,
                "owner_id": owner_id, "processed_at": utcnow(),
            })
            return True
        except DuplicateKeyError:
            return False
