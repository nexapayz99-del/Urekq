class StatisticsService:
    def __init__(self, db):
        self.db = db

    async def user_stats(self, owner_id):
        return {
            "accounts": await self.db.sessions.count_documents({"owner_id": owner_id}),
            "channels": await self.db.monitored_channels.count_documents({"owner_id": owner_id}),
            "tasks": await self.db.task_history.count_documents({"owner_id": owner_id}),
        }

    async def system_stats(self):
        return {
            "users": await self.db.users.count_documents({}),
            "accounts": await self.db.sessions.count_documents({}),
            "channels": await self.db.monitored_channels.count_documents({}),
            "tasks": await self.db.task_history.count_documents({}),
        }
