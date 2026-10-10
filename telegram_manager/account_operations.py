from pyrogram import Client
from telegram_manager.account_login import decrypt_session

class AccountOperations:
    def __init__(self, settings):
        self.settings = settings

    async def with_account(self, encrypted_session, operation):
        session = decrypt_session(self.settings.session_encryption_key, encrypted_session)
        client = Client(
            "managed_account", api_id=self.settings.api_id,
            api_hash=self.settings.api_hash, session_string=session,
            in_memory=True, workdir=str(self.settings.data_dir),
        )
        await client.start()
        try:
            return await operation(client)
        finally:
            await client.stop()

    async def get_info(self, encrypted_session):
        async def operation(client):
            me = await client.get_me()
            return {"id": me.id, "username": me.username, "first_name": me.first_name,
                    "last_name": me.last_name, "phone_number": me.phone_number}
        return await self.with_account(encrypted_session, operation)

    async def update_profile(self, encrypted_session, first_name=None, last_name=None, bio=None):
        async def operation(client):
            if first_name is not None or last_name is not None:
                me = await client.get_me()
                await client.update_profile(
                    first_name=first_name if first_name is not None else me.first_name,
                    last_name=last_name if last_name is not None else me.last_name,
                )
            if bio is not None:
                await client.update_profile(bio=bio)
            return True
        return await self.with_account(encrypted_session, operation)

    async def mark_read(self, encrypted_session, chat_id):
        async def operation(client):
            await client.read_chat_history(chat_id)
            return True
        return await self.with_account(encrypted_session, operation)

    async def list_authorizations(self, encrypted_session):
        async def operation(client):
            result = await client.invoke(__import__("pyrogram").raw.functions.account.GetAuthorizations())
            return [{"current": x.current, "device_model": x.device_model,
                     "platform": x.platform, "date_created": x.date_created,
                     "date_active": x.date_active, "hash": x.hash}
                    for x in result.authorizations]
        return await self.with_account(encrypted_session, operation)
