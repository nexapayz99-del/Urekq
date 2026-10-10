from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    rows = [
        [InlineKeyboardButton("➕ Add Account", callback_data="menu:add"),
         InlineKeyboardButton("📂 Import Sessions", callback_data="menu:import")],
        [InlineKeyboardButton("👤 Manage Accounts", callback_data="menu:accounts"),
         InlineKeyboardButton("📊 Statistics", callback_data="menu:stats")],
        [InlineKeyboardButton("📡 Channel Monitoring", callback_data="menu:channels"),
         InlineKeyboardButton("❤️ Reactions", callback_data="menu:reactions")],
        [InlineKeyboardButton("🎙 Voice Chat Manager", callback_data="menu:voice"),
         InlineKeyboardButton("🔐 Security", callback_data="menu:security")],
        [InlineKeyboardButton("🧹 Account Cleanup", callback_data="menu:cleanup"),
         InlineKeyboardButton("⚡ Ping", callback_data="menu:ping")],
    ]
    return InlineKeyboardMarkup(rows)

def confirm_keyboard(action, token):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("Confirm", callback_data=f"confirm:{action}:{token}"),
        InlineKeyboardButton("Cancel", callback_data="cancel"),
    ]])
