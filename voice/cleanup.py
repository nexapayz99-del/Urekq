async def cleanup_voice_resources(manager):
    await manager.registry.close()
    await manager.adapter.close()
