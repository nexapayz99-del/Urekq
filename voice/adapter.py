class VoiceAdapterUnavailable(RuntimeError):
    pass

class VoiceAdapter:
    """Fail-closed adapter.

    PyTgCalls currently targets ntgcalls 3.x and advertises a pyrogrammod
    integration. This project pins original Pyrogram 2.x. A verified adapter
    must be selected before real call operations can safely be enabled.
    """
    enabled = False

    async def join(self, *args, **kwargs):
        raise VoiceAdapterUnavailable(
            "No verified PyTgCalls adapter is configured for the installed client stack."
        )

    async def leave(self, *args, **kwargs):
        raise VoiceAdapterUnavailable(
            "No verified PyTgCalls adapter is configured for the installed client stack."
        )

    async def close(self):
        return None
