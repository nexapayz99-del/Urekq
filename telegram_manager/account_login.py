import logging
from datetime import datetime, timezone
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid, PhoneCodeExpired
from cryptography.fernet import Fernet
from telegram_manager.states import StateStore

log = logging.getLogger(__name__)

def encrypt_session(key: str, value: str) -> str:
    if not key:
        raise RuntimeError("SESSION_ENCRYPTION_KEY must be configured before storing sessions")
    return Fernet(key.encode()).encrypt(value.encode()).decode()

def decrypt_session(key: str, value: str) -> str:
    return Fernet(key.encode()).decrypt(value.encode()).decode()

class LoginManager:
    def __init__(self):
        self.states = StateStore(ttl_seconds=300)
        self.clients = {}

    async def begin(self, bot, user_id: int, phone: str):
        name = f"login_{user_id}"
        client = Client(
            name, api_id=bot.settings.api_id, api_hash=bot.settings.api_hash,
            in_memory=True, workdir=str(bot.settings.data_dir),
        )
        await client.connect()
        sent = await client.send_code(phone)
        self.clients[user_id] = client
        self.states.set(user_id, "login_code", phone=phone, phone_code_hash=sent.phone_code_hash)
        return

    async def submit_code(self, bot, user_id: int, code: str):
        state = self.states.get(user_id)
        client = self.clients.get(user_id)
        if not state or state.name != "login_code" or not client:
            raise ValueError("Login expired. Start again.")
        try:
            user = await client.sign_in(state.data["phone"], state.data["phone_code_hash"], code)
        except SessionPasswordNeeded:
            self.states.set(user_id, "login_password", **state.data)
            return "PASSWORD_REQUIRED"
        session = await client.export_session_string()
        me = await client.get_me()
        await self._close(user_id)
        self.states.cancel(user_id)
        return {"session": session, "account_id": me.id, "username": me.username, "first_name": me.first_name}

    async def submit_password(self, user_id: int, password: str):
        state = self.states.get(user_id)
        client = self.clients.get(user_id)
        if not state or state.name != "login_password" or not client:
            raise ValueError("Login expired. Start again.")
        await client.check_password(password)
        me = await client.get_me()
        session = await client.export_session_string()
        await self._close(user_id)
        self.states.cancel(user_id)
        return {"session": session, "account_id": me.id, "username": me.username, "first_name": me.first_name}

    async def _close(self, user_id):
        client = self.clients.pop(user_id, None)
        if client:
            try:
                await client.disconnect()
            except Exception:
                log.warning("Temporary login client cleanup failed", exc_info=True)

    async def cancel(self, user_id):
        self.states.cancel(user_id)
        await self._close(user_id)
