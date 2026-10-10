from functools import wraps
from pyrogram.enums import ChatType

def is_private(message):
    return bool(message.chat and message.chat.type == ChatType.PRIVATE)

async def require_private(message):
    if not is_private(message):
        await message.reply_text("Please use this bot in a private chat.")
        return False
    return True

async def role_for(db, user_id: int, owner_id: int):
    if user_id == owner_id:
        return "OWNER"
    doc = await db.admins.find_one({"user_id": user_id, "active": True})
    return doc.get("role", "ADMIN") if doc else "USER"

async def owns_account(db, user_id: int, account_id: int):
    return await db.sessions.find_one({"owner_id": user_id, "account_id": account_id}) is not None

def owner_or_admin(func):
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        role = await role_for(client.db, message.from_user.id, client.settings.owner_id)
        if role not in ("OWNER", "ADMIN"):
            await message.reply_text("You are not authorized to use this operation.")
            return
        return await func(client, message, *args, **kwargs)
    return wrapper
