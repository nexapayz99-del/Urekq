from telegram_manager.session_security import validate_session

class SecurityService:
    def __init__(self, db, settings):
        self.db, self.settings = db, settings

    async def validate_owned(self, owner_id, account_id):
        doc = await self.db.sessions.find_one({"owner_id": owner_id, "account_id": account_id})
        if not doc:
            raise PermissionError("Account not found or not owned by this user")
        result = await validate_session(self.settings, doc["encrypted_session"])
        await self.db.sessions.update_one({"_id": doc["_id"]}, {"$set": {"session_valid": result["valid"]}})
        return result
