import http.server
import webbrowser
import requests
import threading
import urllib.parse
from tw_privdata import Daten


twd = Daten()

CLIENT_ID = twd.client_id
CLIENT_SECRET = twd.client_secret
REDIRECT_URI = "http://localhost:8080"
SCOPES = "user:read:email channel:manage:broadcast"

# Synchronisationsobjekt, damit das Programm wartet bis der Code da ist
auth_event = threading.Event()
token_info = None


def execute():
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

    # Lokaler HTTP-Handler für Redirect
    class OAuthHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            global token_info

            # Browser-Anfrage nach favicon ignorieren
            if self.path.startswith("/favicon.ico"):
                self.send_response(204)
                self.end_headers()
                return

            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if "code" in params:
                code = params["code"][0]
                print("Authorization Code erhalten:", code)

                # Access Token anfordern
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

                # Antwort an Browser (korrekt als Bytes)
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write("<h2>Login erfolgreich! Du kannst das Fenster schließen.</h2>".encode("utf-8"))

                # Signalisiere Hauptprogramm, dass wir fertig sind
                auth_event.set()

                # Server sauber beenden
                threading.Thread(target=self.server.shutdown, daemon=True).start()
            else:
                self.send_response(400)
                self.end_headers()

    token = Adaten()  # Objekt mit den Tokens und Gültigkeit

    # Server im Hintergrund starten
    def start_server():
        server = http.server.HTTPServer(("localhost", 8080), OAuthHandler)
        server.serve_forever()

    def safe():
        print("\n✅ Login abgeschlossen!")
        token.atoken = token_info.get("access_token")
        token.rtoken = token_info.get("refresh_token")
        token.expire = token_info.get("expires_in")

    def load_user_data():
        """Lädt User-ID, Loginname und Anzeigename"""
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

    # === Hauptlogik ===
    threading.Thread(target=start_server, daemon=True).start()

    # Twitch Login-Seite öffnen
    auth_url = (
        f"https://id.twitch.tv/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={SCOPES.replace(' ', '+')}"
    )
    print("Öffne Browser zur Anmeldung ...")
    webbrowser.open(auth_url)

    # Auf erfolgreiche Anmeldung warten
    auth_event.wait()

    safe()
    load_user_data()

    print(f"\n👤 Eingeloggter Nutzer:")
    print(f"  ID: {token.userid}")
    print(f"  Loginname: {token.loginname}")
    print(f"  Anzeigename: {token.displayname}")

    return token


# Wenn du das direkt testen willst:
# execute()
