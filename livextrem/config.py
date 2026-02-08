import os
import json
from pathlib import Path

# -----------------------------------------------------------------------------
# Konfiguration
# -----------------------------------------------------------------------------
# Ziel (Messe/Abgabe):
# - Keine Twitch Access-/Refresh-Tokens in der DB speichern (Login regelt das).
# - App soll "out of the box" laufen: daher unterstützen wir eine lokale
#   config_local.json neben dieser Datei als Fallback zu ENV Variablen.
#
# Sicherheitshinweis:
# - Twitch CLIENT_SECRET ist ein Secret. In echten Deployments gehört es in einen
#   Secret-Store/ENV, nicht in ein öffentlich verteiltes ZIP.
# - Für Messe/Schulabgabe ist die config_local.json praktisch, weil keine
#   PowerShell/ENV-Setups nötig sind.
# -----------------------------------------------------------------------------

CONFIG_FILE = Path(os.getenv("LIVEXTREM_CONFIG_PATH", Path(__file__).with_name("config_local.json")))

def _load_file_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with CONFIG_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            # Absichtlich still: validate() gibt eine klare Fehlermeldung aus.
            return {}
    return {}

_FILE_CFG = _load_file_config()

def _cfg(name: str, default: str = "") -> str:
    # Priorität: ENV > config_local.json > default
    v = os.getenv(name)
    if v is not None and v != "":
        return v
    # Map ENV-Name -> JSON-Key (gleicher Name)
    if name in _FILE_CFG and _FILE_CFG[name] not in (None, ""):
        return str(_FILE_CFG[name])
    return default

class Config:
    # DB
    DB_HOST = _cfg("LIVEXTREM_DB_HOST", "88.218.227.14")
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
        if not cls.DB_USER: missing.append("LIVEXTREM_DB_USER")
        if not cls.DB_PASS: missing.append("LIVEXTREM_DB_PASS")
        if not cls.TWITCH_CLIENT_ID: missing.append("LIVEXTREM_TWITCH_CLIENT_ID")
        if not cls.TWITCH_CLIENT_SECRET: missing.append("LIVEXTREM_TWITCH_CLIENT_SECRET")

        if missing:
            # Hinweis, wie man ohne ENV auskommt
            hint = (
                "Konfiguration unvollständig. Bitte setzen: " + ", ".join(missing) + "\n\n"
                "Option A (ohne PowerShell): Lege neben config.py eine Datei 'config_local.json' an.\n"
                f"Pfad: {CONFIG_FILE}\n\n"
                "Beispielinhalt:\n"
                "{\n"
                "  \"LIVEXTREM_DB_HOST\": \"88.218.227.14\",\n"
                "  \"LIVEXTREM_DB_PORT\": \"3306\",\n"
                "  \"LIVEXTREM_DB_NAME\": \"livextrem\",\n"
                "  \"LIVEXTREM_DB_USER\": \"<db-user>\",\n"
                "  \"LIVEXTREM_DB_PASS\": \"<db-pass>\",\n"
                "  \"LIVEXTREM_TWITCH_CLIENT_ID\": \"<client-id>\",\n"
                "  \"LIVEXTREM_TWITCH_CLIENT_SECRET\": \"<client-secret>\",\n"
                "  \"LIVEXTREM_TWITCH_REDIRECT_URI\": \"http://localhost:8080\"\n"
                "}\n\n"
                "Option B: ENV Variablen setzen (siehe SETUP_ENV.txt)."
            )
            raise RuntimeError(hint)
