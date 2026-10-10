import json
import os
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from pyrogram import Client
from telegram_manager.account_login import encrypt_session

ALLOWED_EXTENSIONS = {".txt", ".json", ".session"}

def validate_zip_members(zf, max_bytes):
    total = 0
    safe = []
    for info in zf.infolist():
        path = PurePosixPath(info.filename)
        if path.is_absolute() or ".." in path.parts or info.is_dir():
            if info.is_dir():
                continue
            raise ValueError("Unsafe ZIP archive path")
        total += info.file_size
        if total > max_bytes:
            raise ValueError("Archive exceeds configured size limit")
        if Path(info.filename).suffix.lower() in ALLOWED_EXTENSIONS:
            safe.append(info)
    return safe

def parse_session_text(text):
    value = text.strip()
    if not value:
        raise ValueError("Empty session file")
    try:
        parsed = json.loads(value)
        if isinstance(parsed, dict):
            for key in ("session_string", "session", "string"):
                if isinstance(parsed.get(key), str) and parsed[key].strip():
                    return parsed[key].strip()
        raise ValueError("JSON must contain a session_string field")
    except json.JSONDecodeError:
        if len(value) >= 80 and "\n" not in value:
            return value
        raise ValueError("Unsupported text session format")

async def verify_session(settings, session_string):
    client = Client("session_import_verify", api_id=settings.api_id,
                    api_hash=settings.api_hash, session_string=session_string,
                    in_memory=True, workdir=str(settings.data_dir))
    try:
        await client.start()
        me = await client.get_me()
        return me.id, me.username, me.first_name
    finally:
        try:
            await client.stop()
        except Exception:
            pass

async def import_file(settings, file_path):
    path = Path(file_path)
    if path.suffix.lower() in (".txt", ".json"):
        if path.stat().st_size > settings.max_import_bytes:
            raise ValueError("File exceeds configured size limit")
        session = parse_session_text(path.read_text(encoding="utf-8"))
        return session, await verify_session(settings, session)
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            members = validate_zip_members(zf, settings.max_import_bytes)
            for info in members:
                if Path(info.filename).suffix.lower() in (".txt", ".json"):
                    content = zf.read(info).decode("utf-8")
                    session = parse_session_text(content)
                    return session, await verify_session(settings, session)
        raise ValueError("ZIP contains no supported text or JSON session")
    if path.suffix.lower() == ".session":
        raise ValueError("SQLite session import requires a dedicated isolated validation workflow; export a session string from the authorized client instead.")
    raise ValueError("Unsupported import file type")
