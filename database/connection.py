from pymongo import AsyncMongoClient

class Database:
    def __init__(self, uri: str, db_name: str):
        self.uri, self.db_name = uri, db_name
        self.client = None
        self.db = None

    async def connect(self):
        self.client = AsyncMongoClient(self.uri, serverSelectionTimeoutMS=5000)
        await self.client.admin.command("ping")
        self.db = self.client[self.db_name]
        return self.db

    async def close(self):
        if self.client is not None:
            await self.client.close()
            self.client = None
            self.db = None

    async def ready(self) -> bool:
        if self.client is None:
            return False
        try:
            await self.client.admin.command("ping")
            return True
        except Exception:
            return False
