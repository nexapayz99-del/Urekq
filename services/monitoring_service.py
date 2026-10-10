from telegram_manager.channel_operations import add_channel, remove_channel, list_channels

class MonitoringService:
    def __init__(self, db):
        self.db = db

    async def add(self, owner_id, channel_id, title=None):
        await add_channel(self.db, owner_id, channel_id, title)

    async def remove(self, owner_id, channel_id):
        return await remove_channel(self.db, owner_id, channel_id)

    async def list(self, owner_id):
        return await list_channels(self.db, owner_id)
