import pytest
from config.settings import Settings

def test_missing_required_env(monkeypatch):
    for key in ("API_ID", "API_HASH", "BOT_TOKEN", "MONGO_URI", "OWNER_ID"):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(ValueError, match="Missing required"):
        Settings.from_env()
