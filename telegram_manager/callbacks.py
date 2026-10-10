import logging
from pyrogram import filters
from telegram_manager.authorization import role_for
from telegram_manager.keyboards import main_menu

log = logging.getLogger(__name__)

def register_callbacks(bot):
    @bot.on_callback_query(filters.regex(r"^menu:"))
    async def menu_callback(client, query):
        if query.message.chat.type.value != "private":
            await query.answer("Use this in a private chat.", show_alert=True)
            return
        action = query.data.split(":", 1)[1]
        uid = query.from_user.id
        await client.db.users.update_one({"user_id": uid},
            {"$setOnInsert": {"created_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc),
                              "role": "USER"}}, upsert=True)
        if action == "ping":
            await query.answer("Pong")
            await query.message.reply_text("🏓 Pong")
        elif action == "accounts":
            docs = await client.db.sessions.find({"owner_id": uid}, {"encrypted_session": 0}).to_list(50)
            if not docs:
                text = "No accounts registered yet."
            else:
                text = "Your accounts:\n" + "\n".join(
                    f"• {d.get('first_name') or 'Account'} — ID `{d['account_id']}`"
                    for d in docs
                )
            await query.message.reply_text(text)
        elif action == "stats":
            count = await client.db.sessions.count_documents({"owner_id": uid})
            tasks = await client.db.task_history.count_documents({"owner_id": uid})
            await query.message.reply_text(f"📊 Your accounts: {count}\nRecorded tasks: {tasks}")
        elif action == "channels":
            role = await role_for(client.db, uid, client.settings.owner_id)
            if role not in ("OWNER", "ADMIN"):
                await query.answer("Admin permission required.", show_alert=True)
                return
            await query.message.reply_text("Use /addchannel <numeric_channel_id> and /channels.")
        elif action == "voice":
            await query.message.reply_text(
                "Voice-chat adapter is not enabled: the selected PyTgCalls client stack must be verified first. "
                "No join operation was attempted."
            )
        elif action == "reactions":
            await query.message.reply_text(
                "Manual authorized reactions can be added after channel permissions and the supported reaction API are verified. "
                "Artificial view inflation and fake-engagement automation are not supported."
            )
        elif action == "security":
            await query.message.reply_text("Session credentials are encrypted at rest when SESSION_ENCRYPTION_KEY is configured.")
        elif action == "cleanup":
            await query.message.reply_text("Account cleanup is available through explicit per-account confirmation. No data was changed.")
        elif action == "add":
            await query.message.reply_text("Send /addaccount followed by your phone number in international format. Use only your own account.")
        elif action == "import":
            await query.message.reply_text("Session import accepts authorized session strings in .txt/.json files. Send /importsession as a command for instructions.")
        await query.answer()
