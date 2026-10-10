from pyrogram import Client
from pyrogram.errors import AuthKeyUnregistered, SessionRevoked, UserDeactivated, UserDeactivatedBan
from telegram_manager.account_login import decrypt_session

async def validate_session(settings, encrypted_session: str):
    session = decrypt_session(settings.session_encryption_key, encrypted_session)
    client = Client(
        "session_check", api_id=settings.api_id, api_hash=settings.api_hash,
        session_string=session, in_memory=True,
        workdir=str(settings.data_dir),
    )
    try:
        await client.start()
        me = await client.get_me()
        return {"valid": True, "account_id": me.id, "username": me.username}
    except (AuthKeyUnregistered, SessionRevoked, UserDeactivated, UserDeactivatedBan):
        return {"valid": False, "account_id": None, "username": None}
    finally:
        try:
            await client.stop()
        except Exception:
            pass
