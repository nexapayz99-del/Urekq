import logging
import time
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from telegram_manager.keyboards import main_menu
from telegram_manager.callbacks import register_callbacks
from telegram_manager.authorization import require_private, role_for
from telegram_manager.account_login import LoginManager, encrypt_session
from telegram_manager.channel_operations import add_channel, remove_channel, list_channels

log = logging.getLogger(__name__)
login_manager = LoginManager()

def register_handlers(bot):
    @bot.on_message(filters.command("start"))
    async def start(client, message):
        if not await require_private(message):
            return
        await client.db.users.update_one(
            {"user_id": message.from_user.id},
            {"$set": {"username": message.from_user.username},
             "$setOnInsert": {"role": "USER", "created_at": time.time()}},
            upsert=True,
        )
        await message.reply_text("Telegram Account Manager\nChoose an action:", reply_markup=main_menu())

    @bot.on_message(filters.command("ping"))
    async def ping(client, message):
        await message.reply_text("🏓 Pong")

    @bot.on_message(filters.command("cancel"))
    async def cancel(client, message):
        await login_manager.cancel(message.from_user.id)
        await message.reply_text("Current interaction cancelled.")

    @bot.on_message(filters.command("addaccount"))
    async def add_account(client, message):
        if not await require_private(message):
            return
        parts = message.text.split(maxsplit=1)
        if len(parts) != 2 or not parts[1].startswith("+"):
            await message.reply_text("Usage: /addaccount +<countrycode><number>\nUse only your own account.")
            return
        if not client.settings.session_encryption_key:
            await message.reply_text("Session encryption is not configured. Set SESSION_ENCRYPTION_KEY first.")
            return
        try:
            await login_manager.begin(client, message.from_user.id, parts[1].strip())
            await message.reply_text("Telegram sent a login code. Send it here, or /cancel.")
        except Exception:
            log.warning("Login initiation failed for user %s", message.from_user.id, exc_info=True)
            await message.reply_text("Could not start login. Check the phone number and Telegram limits.")

    @bot.on_message(filters.command("importsession"))
    async def import_session_help(client, message):
        await message.reply_text(
            "Send an authorized Pyrogram session string only through a private chat. "
            "For safety, this bot's import command accepts files through the document handler only in a future hardened upload workflow. "
            "Never share session strings with strangers."
        )

    @bot.on_message(filters.command("addchannel"))
    async def add_channel_cmd(client, message):
        if not await require_private(message):
            return
        role = await role_for(client.db, message.from_user.id, client.settings.owner_id)
        if role not in ("OWNER", "ADMIN"):
            await message.reply_text("Admin permission required.")
            return
        parts = message.text.split(maxsplit=1)
        if len(parts) != 2:
            await message.reply_text("Usage: /addchannel <numeric_channel_id>")
            return
        try:
            channel_id = int(parts[1])
            chat = await client.get_chat(channel_id)
            await add_channel(client.db, message.from_user.id, channel_id, chat.title)
            await message.reply_text(f"Monitoring configuration saved for {chat.title or channel_id}.")
        except Exception:
            log.warning("Channel add failed", exc_info=True)
            await message.reply_text("Could not access that channel. Ensure the bot has access and the ID is correct.")

    @bot.on_message(filters.command("channels"))
    async def channels_cmd(client, message):
        if not await require_private(message):
            return
        docs = await list_channels(client.db, message.from_user.id)
        if not docs:
            await message.reply_text("No channels configured by you.")
            return
        await message.reply_text("Configured channels:\n" + "\n".join(
            f"• {x.get('title') or x['channel_id']} (`{x['channel_id']}`)"
            for x in docs
        ))

    @bot.on_message(filters.command("removechannel"))
    async def remove_channel_cmd(client, message):
        if not await require_private(message):
            return
        role = await role_for(client.db, message.from_user.id, client.settings.owner_id)
        if role not in ("OWNER", "ADMIN"):
            await message.reply_text("Admin permission required.")
            return
        parts = message.text.split(maxsplit=1)
        if len(parts) != 2:
            await message.reply_text("Usage: /removechannel <numeric_channel_id>")
            return
        try:
            removed = await remove_channel(client.db, message.from_user.id, int(parts[1]))
            await message.reply_text("Channel removed." if removed else "No matching channel configuration found.")
        except ValueError:
            await message.reply_text("Channel ID must be numeric.")

    @bot.on_message(filters.command(["stopvc", "leavevc"]))
    async def voice_stop(client, message):
        await message.reply_text(
            "Voice-chat control is unavailable because no compatible PyTgCalls adapter is configured. "
            "No account was joined or disconnected."
        )

    @bot.on_message(filters.private & filters.text & ~filters.command(["start", "ping", "cancel", "addaccount", "importsession", "addchannel", "channels", "removechannel", "stopvc", "leavevc"]))
    async def login_text(client, message):
        uid = message.from_user.id
        state = login_manager.states.get(uid)
        if not state:
            return
        try:
            if state.name == "login_code":
                result = await login_manager.submit_code(client, uid, message.text.strip().replace(" ", ""))
                if result == "PASSWORD_REQUIRED":
                    await message.reply_text("Two-step verification is enabled. Send your password, or /cancel.")
                    return
            elif state.name == "login_password":
                result = await login_manager.submit_password(uid, message.text)
            else:
                return
            encrypted = encrypt_session(client.settings.session_encryption_key, result["session"])
            doc = {
                "owner_id": uid, "account_id": result["account_id"],
                "username": result["username"], "first_name": result["first_name"],
                "encrypted_session": encrypted, "created_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
                "source": "login",
            }
            inserted = await client.db.sessions.insert_one(doc)
            await client.db.task_history.insert_one({
                "owner_id": uid, "kind": "account_login", "status": "success",
                "details": {"account_id": result["account_id"]},
                "created_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            })
            await message.reply_text("Account authorized and encrypted session stored." if inserted.inserted_id else "Account login completed.")
        except Exception:
            log.warning("Account login step failed for user %s", uid, exc_info=True)
            await login_manager.cancel(uid)
            await message.reply_text("Login failed or expired. Start again with /addaccount. Never send codes to anyone else.")

    register_callbacks(bot)
