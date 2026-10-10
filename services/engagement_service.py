class EngagementService:
    """Provides duplicate-safe accounting only; no artificial views or fake campaigns."""
    def __init__(self, db):
        self.db = db

    async def claim_post(self, owner_id, channel_id, message_id):
        try:
            await self.db.processed_posts.insert_one({
                "owner_id": owner_id, "channel_id": channel_id,
                "message_id": message_id,
            })
            return True
        except Exception as exc:
            # Only duplicate-key errors should be treated as already processed.
            from pymongo.errors import DuplicateKeyError
            if isinstance(exc, DuplicateKeyError):
                return False
            raise
