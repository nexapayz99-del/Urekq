async def create_indexes(db):
    await db.users.create_index("user_id", unique=True)
    await db.sessions.create_index([("owner_id", 1), ("account_id", 1)], unique=True)
    await db.sessions.create_index("owner_id")
    await db.admins.create_index("user_id", unique=True)
    await db.monitored_channels.create_index([("channel_id", 1), ("owner_id", 1)], unique=True)
    await db.processed_posts.create_index([("channel_id", 1), ("message_id", 1)], unique=True)
    await db.active_voice_chats.create_index([("account_id", 1), ("chat_id", 1)], unique=True)
    await db.task_history.create_index("created_at")
