from telegram_manager.account_operations import AccountOperations
from telegram_manager.account_login import decrypt_session

class AccountService:
    def __init__(self, db, settings):
        self.db, self.settings = db, settings
        self.ops = AccountOperations(settings)

    async def get_owned_session(self, owner_id, account_id):
        doc = await self.db.sessions.find_one({"owner_id": owner_id, "account_id": account_id})
        if not doc:
            raise PermissionError("Account not found or not owned by this user")
        return doc

    async def info(self, owner_id, account_id):
        doc = await self.get_owned_session(owner_id, account_id)
        return await self.ops.get_info(doc["encrypted_session"])

    async def delete(self, owner_id, account_id, confirmed=False):
        if not confirmed:
            raise ValueError("Explicit confirmation required")
        result = await self.db.sessions.delete_one({"owner_id": owner_id, "account_id": account_id})
        return result.deleted_count == 1
