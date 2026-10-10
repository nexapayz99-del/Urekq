from datetime import datetime, timezone

async def add_channel(db, owner_id: int, channel_id: int, title=None):
    await db.monitored_channels.update_one(
        {"owner_id": owner_id, "channel_id": channel_id},
        {"$set": {"title": title, "enabled": True, "updated_at": datetime.now(timezone.utc)},
         "$setOnInsert": {"created_at": datetime.now(timezone.utc), "post_monitoring": True,
                          "voice_monitoring": False}},
        upsert=True,
    )

async def remove_channel(db, owner_id: int, channel_id: int):
    result = await db.monitored_channels.delete_one({"owner_id": owner_id, "channel_id": channel_id})
    return result.deleted_count > 0

async def list_channels(db, owner_id: int):
    return await db.monitored_channels.find({"owner_id": owner_id}).sort("created_at", -1).to_list(100)
