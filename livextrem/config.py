import os
from pathlib import Path
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# Konfiguration
# -----------------------------------------------------------------------------
# Sensible Konfigurationswerte werden zentral aus keydata.env geladen.
# Die restliche Anwendung greift weiterhin unverändert über Config.* zu.
# -----------------------------------------------------------------------------

ENV_FILE = Path(__file__).with_name("keydata.env")
load_dotenv(ENV_FILE)


def _cfg(name: str, default: str = "") -> str:
    v = os.getenv(name)
    if v is not None and v != "":
        return v
    return default


class Config:
    # DB
    DB_HOST = _cfg("LIVEXTREM_DB_HOST", "127.0.0.1")
    DB_PORT = int(_cfg("LIVEXTREM_DB_PORT", "3306"))
    DB_NAME = _cfg("LIVEXTREM_DB_NAME", "livextrem")
    DB_USER = _cfg("LIVEXTREM_DB_USER", "")
    DB_PASS = _cfg("LIVEXTREM_DB_PASS", "")

    # Twitch OAuth
    TWITCH_CLIENT_ID = _cfg("LIVEXTREM_TWITCH_CLIENT_ID", "")
    TWITCH_CLIENT_SECRET = _cfg("LIVEXTREM_TWITCH_CLIENT_SECRET", "")
    TWITCH_REDIRECT_URI = _cfg("LIVEXTREM_TWITCH_REDIRECT_URI", "http://localhost:8080")

    @classmethod
    def validate(cls):
        missing = []
        if not cls.DB_USER:
            missing.append("LIVEXTREM_DB_USER")
        if not cls.DB_PASS:
            missing.append("LIVEXTREM_DB_PASS")
        if not cls.TWITCH_CLIENT_ID:
            missing.append("LIVEXTREM_TWITCH_CLIENT_ID")
        if not cls.TWITCH_CLIENT_SECRET:
            missing.append("LIVEXTREM_TWITCH_CLIENT_SECRET")

        if missing:
            hint = (
                "Konfiguration unvollständig. Bitte setzen: " + ", ".join(missing) + "\n\n"
                f"Quelle: {ENV_FILE}\n\n"
                "Erwartete Einträge in keydata.env:\n"
                "LIVEXTREM_DB_HOST=<db-host>\n"
                "LIVEXTREM_DB_PORT=<db-port>\n"
                "LIVEXTREM_DB_NAME=<db-name>\n"
                "LIVEXTREM_DB_USER=<db-user>\n"
                "LIVEXTREM_DB_PASS=<db-pass>\n"
                "LIVEXTREM_TWITCH_CLIENT_ID=<client-id>\n"
                "LIVEXTREM_TWITCH_CLIENT_SECRET=<client-secret>\n"
                "LIVEXTREM_TWITCH_REDIRECT_URI=http://localhost:8080"
            )
            raise RuntimeError(hint)
