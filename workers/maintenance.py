from datetime import datetime, timezone

async def run_maintenance(db, older_than_days=90):
    # Only non-sensitive task history is pruned; session records are never deleted here.
    from datetime import timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)
    result = await db.task_history.delete_many({"created_at": {"$lt": cutoff}})
    return {"task_history_deleted": result.deleted_count}
