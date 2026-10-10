from dataclasses import dataclass
from time import monotonic

@dataclass
class UserState:
    name: str
    data: dict
    expires_at: float

class StateStore:
    def __init__(self, ttl_seconds=300):
        self.ttl = ttl_seconds
        self._states = {}

    def set(self, user_id: int, name: str, **data):
        self._states[user_id] = UserState(name, data, monotonic() + self.ttl)

    def get(self, user_id: int):
        state = self._states.get(user_id)
        if not state:
            return None
        if state.expires_at < monotonic():
            self._states.pop(user_id, None)
            return None
        return state

    def pop(self, user_id: int):
        state = self.get(user_id)
        self._states.pop(user_id, None)
        return state

    def cancel(self, user_id: int):
        self._states.pop(user_id, None)
