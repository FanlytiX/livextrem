import http.server
import webbrowser
import requests
import threading
import urllib.parse
from . import tw_privdata

twd = tw_privdata.Daten()
from config import Config

def twd_redirect_uri():
    # allow override via ENV
    return Config.TWITCH_REDIRECT_URI

# === Twitch OAuth Daten ===
CLIENT_ID = twd.client_id
CLIENT_SECRET = twd.client_secret
REDIRECT_URI = twd_redirect_uri()

# >>> SCOPES wurden hier sauber integriert <<<
SCOPES = [
    "user:read:email",
    "channel:manage:broadcast",
    "bits:read",
    "moderator:read:followers",
    "channel:read:subscriptions",
    "chat:read",
    "chat:edit",
    "moderation:read",
    "moderator:read:banned_users",
    "moderator:read:blocked_terms",
    "moderator:read:automod_settings",
    "moderator:manage:banned_users",
    "moderator:manage:blocked_terms"
]


# Synchronisationsobjekt
auth_event = threading.Event()
token_info = None

def gen():
    Config.validate()

    """
    Meldet den Benutzer neu an. Sollte der Benutzer bereits angemeldet sein, wird die Anmeldung übersprungen.
    """
    global token
    if 'token' in globals() and token.atoken is not None:
        print("Benutzer ist bereits angemeldet")
        return token

    token = gen_direct()
    return token


def gen_direct():
    Config.validate()

    """
    Direkte Anmeldung des Benutzers, ohne Prüfung, ob der Nutzer angemeldet ist.
    """
    class Adaten:
        def __init__(self):
            self.atoken = None
            self.rtoken = None
            self.expire = None
            self.clientid = CLIENT_ID
            self.clientsecret = CLIENT_SECRET
            self.userid = None
            self.loginname = None
            self.displayname = None

    # --- Server-Objekt später von außen erreichbar machen ---
    server_instance = None

    class OAuthHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            global token_info

            if self.path.startswith("/favicon.ico"):
                self.send_response(204)
                self.end_headers()
                return

            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if "code" in params:
                code = params["code"][0]
                print("Authorization Code erhalten:", code)

                token_url = "https://id.twitch.tv/oauth2/token"
                data = {
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": REDIRECT_URI
                }

                r = requests.post(token_url, data=data)
                token_info = r.json()

                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write("<h2>Login erfolgreich! Du kannst das Fenster schließen.</h2>".encode("utf-8"))

                auth_event.set()

                # <<< Hier das saubere, garantierte Shutdown >>>
                threading.Thread(target=server_instance.shutdown, daemon=True).start()

            else:
                self.send_response(400)
                self.end_headers()

    token = Adaten()

    # Server starten
    def start_server():
        nonlocal server_instance
        server_instance = http.server.HTTPServer(("localhost", 8080), OAuthHandler)
        server_instance.serve_forever()

    threading.Thread(target=start_server, daemon=True).start()

    # Liste → URL-kompatibler Scope-String
    scope_string = "+".join(SCOPES)

    auth_url = (
        f"https://id.twitch.tv/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={scope_string}"
)

    print("Öffne Browser zur Anmeldung ...")
    webbrowser.open(auth_url)

    # Warten bis Token da ist
    auth_event.wait()

    # Token übernehmen
    token.atoken = token_info.get("access_token")
    token.rtoken = token_info.get("refresh_token")
    token.expire = token_info.get("expires_in")

    print("\n✅ Login abgeschlossen!")

    # User-Daten laden
    def load_user_data():
        headers = {
            "Client-ID": CLIENT_ID,
            "Authorization": f"Bearer {token.atoken}"
        }
        user = requests.get("https://api.twitch.tv/helix/users", headers=headers).json()
        print("User-Response:", user)

        if "data" not in user or not user["data"]:
            raise Exception(f"Twitch-User konnte nicht abgerufen werden: {user}")

        data = user["data"][0]
        token.userid = data["id"]
        token.loginname = data["login"]
        token.displayname = data["display_name"]

    load_user_data()

    print(f"\n👤 Eingeloggter Nutzer:")
    print(f"  ID: {token.userid}")
    print(f"  Loginname: {token.loginname}")
    print(f"  Anzeigename: {token.displayname}")

    return token


def refresh(token):
    """
    Aktualisiert den Token eines bereits angemeldeten Benutzers. Der Token läuft nach 4 Stunden ab und muss durch den Refresh-Token aktualisiert werden.
    """
    if token is None:
        print("Benutzer ist nicht angemeldet.")
        return

    r = requests.post(
        "https://id.twitch.tv/oauth2/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": token.rtoken,
            "client_id": token.clientid,
            "client_secret": token.clientsecret
        }
    )
    new_token_info = r.json()
    token.atoken = new_token_info.get("access_token")
    token.rtoken = new_token_info.get("refresh_token")
    token.expire = new_token_info.get("expires_in")
