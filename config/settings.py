import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

@dataclass(frozen=True)
class Settings:
    api_id: int
    api_hash: str
    bot_token: str
    mongo_uri: str
    owner_id: int
    db_name: str = "telegram_manager"
    channel_post_poll_seconds: int = 10
    vc_livestream_poll_seconds: int = 5
    vc_join_delay_seconds: int = 1
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 7860
    session_encryption_key: str = ""
    max_import_bytes: int = 10 * 1024 * 1024
    data_dir: Path = Path("data")

    @classmethod
    def from_env(cls):
        load_dotenv()
        required = ("API_ID", "API_HASH", "BOT_TOKEN", "MONGO_URI", "OWNER_ID")
        missing = [name for name in required if not os.getenv(name, "").strip()]
        if missing:
            raise ValueError("Missing required environment variables: " + ", ".join(missing))
        try:
            api_id = int(os.environ["API_ID"])
            owner_id = int(os.environ["OWNER_ID"])
            port = int(os.getenv("PORT", "7860"))
            max_bytes = int(os.getenv("MAX_IMPORT_BYTES", str(10 * 1024 * 1024)))
            post_poll = int(os.getenv("CHANNEL_POST_POLL_SECONDS", "10"))
            vc_poll = int(os.getenv("VC_LIVESTREAM_POLL_SECONDS", "5"))
            join_delay = int(os.getenv("VC_JOIN_DELAY_SECONDS", "1"))
        except ValueError as exc:
            raise ValueError("API_ID, OWNER_ID, PORT and interval settings must be integers") from exc
        if api_id <= 0 or owner_id <= 0 or not 1 <= port <= 65535:
            raise ValueError("API_ID/OWNER_ID must be positive and PORT must be 1..65535")
        if min(post_poll, vc_poll, join_delay) < 0 or max_bytes < 1:
            raise ValueError("Intervals must be non-negative and MAX_IMPORT_BYTES positive")
        key = os.getenv("SESSION_ENCRYPTION_KEY", "").strip()
        return cls(
            api_id=api_id, api_hash=os.environ["API_HASH"].strip(),
            bot_token=os.environ["BOT_TOKEN"].strip(),
            mongo_uri=os.environ["MONGO_URI"].strip(), owner_id=owner_id,
            db_name=os.getenv("DB_NAME", "telegram_manager"),
            channel_post_poll_seconds=post_poll,
            vc_livestream_poll_seconds=vc_poll,
            vc_join_delay_seconds=join_delay,
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            host=os.getenv("HOST", "0.0.0.0"), port=port,
            session_encryption_key=key, max_import_bytes=max_bytes,
            data_dir=Path(os.getenv("DATA_DIR", "data")),
        )
