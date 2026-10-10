# Telegram Account Manager

A Python 3.11, Pyrogram, MongoDB and Docker project for managing authorized Telegram accounts, basic channel monitoring, and operational diagnostics.

## Important capability boundaries

- Use only Telegram accounts and channels you own or are explicitly authorized to administer.
- Session strings are bearer credentials. This project encrypts them at rest when `SESSION_ENCRYPTION_KEY` is configured; configure it before importing or adding accounts.
- Pyrogram is an unofficial client library. Telegram may change behavior, enforce limits, or revoke sessions.
- PyTgCalls integration is intentionally not enabled in this initial package. The current PyTgCalls release line uses `ntgcalls` 3.x and a `pyrogrammod` integration extra, while the original Pyrogram 2.x dependency requested here is a separate client. Do not mix APIs blindly. Voice commands report that no compatible adapter is configured instead of pretending a call was joined. Verify and select a single supported client stack before enabling live voice operations.
- No artificial view inflation or coordinated fake engagement is implemented.
- Channel post monitoring in this version uses supported updates delivered to the bot. A bot cannot read arbitrary channel history unless it has the appropriate access and updates; event delivery is not guaranteed to be instantaneous.

## Setup

1. Copy `.env.example` to `.env`.
2. Set `API_ID`, `API_HASH`, `BOT_TOKEN`, `OWNER_ID`, MongoDB credentials, and a Fernet key in `SESSION_ENCRYPTION_KEY`.
3. Generate an encryption key locally:
   `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
4. Start:
   `docker compose build && docker compose up -d`
5. Logs:
   `docker compose logs -f --tail=100 telegram-account-manager`
6. Tests:
   `python -m pip install -r requirements.txt && pytest -q`

Do not commit `.env`, session files, database dumps, or encryption keys.

## Supported commands and UI

- `/start`, `/ping`, `/cancel`
- Account listing and information for accounts imported/added through this application
- Channel monitoring configuration for authorized admins
- `/stopvc` and `/leavevc` explain that voice integration is unavailable until a verified adapter is configured

## Session security

The account-login wizard is intentionally conservative: credentials are never logged and the exported session is encrypted before persistence. Restrict bot access to a private chat. Telegram login codes/passwords should only be entered by the account owner. Imported SQLite sessions are validated and copied only after authorization checks; arbitrary database files are not executed.

## Production checklist

- Use a private MongoDB network and strong unique credentials.
- Set a strong `SESSION_ENCRYPTION_KEY`; back it up separately from MongoDB.
- Restrict VPS firewall access to the health port if public health checks are needed.
- Configure MongoDB backups and test restore procedures.
- Review Telegram API terms and user consent before managing any account.
