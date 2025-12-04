Okay, du willst die Komplett-Doku aus meinem Kopf. Guter Move.
Ich schreib dir jetzt *alles*, was ich über euer Projekt liveXtrem weiß – so detailliert wie möglich. Das kannst du 1:1 als Grundlage für Doku / Pflichtenheft / Architektur nutzen.

---

## 1. Projektüberblick

* **Projektname:** `liveXtrem`
* **Art:** Projektarbeit auf **Bachelor-Niveau**
* **Studiengang:** Wirtschaftsinformatik
* **Teamgröße:** 3 Personen
* **Ziel:** Ein **Stream Manager** für Twitch, der sich konzeptionell an ein **ERP-System** anlehnt.
* **Basissäulen / Module:**

  * **Finanzen** – z. B. Auswertung von Einnahmen (Subs, Bits, Donations etc.)
  * **Planung** – z. B. Streamplanung, Schedule, Contentplanung.
  * **Moderation** – Tools zur Live-Moderation, Auswertung von Chat / Usern.

Die Anwendung soll Streamern (konkret dir mit dem Kanal **„derFlaavius“**, Twitch-ID `800711400`) helfen, ihren Kanal professioneller zu steuern.

---

## 2. Technischer Stack

* **Sprache:** Python 3.12
* **GUI:**

  * Ursprünglich: `tkinter`
  * Ziel: **CustomTkinter (`customtkinter`)** mit Theme-Datei `style.json`.
* **HTTP / API:** `requests`
* **Socket / IRC:** `socket` + `time` für Twitch-Chat über IRC.
* **Threading:** `threading` für lokalen OAuth-Server.
* **Lokaler Webserver:** `http.server.HTTPServer` für OAuth Redirect.

---

## 3. Dateistruktur (relevant in der Unterhaltung)

Ungefähr so:

```text
livextrem/
    aaa_prov_main.py              # Start-/Launcher-Fenster
    moderator_dashboard.py        # Mod-GUI (separates Fenster)
    style.json                    # (geplant) Theme-Einstellungen für CustomTkinter

    fremdsys/
        __init__.py
        oauth.py                  # Twitch-OAuth-Logik
        tw_privdata.py            # Client-ID / Client-Secret (Daten-Klasse Daten)
        tapi_data.py              # (vermutlich) Twitch-Datenfunktionen (Follower, etc.)
        tapi_mod.py               # Moderatorfunktionen (Chat, VOD, Modtools)
```

---

## 4. Twitch OAuth – aktueller Stand

### 4.1. Privatedaten

In `fremdsys/tw_privdata.py` gibt es eine Klasse `Daten`, die mindestens enthält:

* `client_id`
* `client_secret`

Diese wird in `oauth.py` so verwendet:

```python
from . import tw_privdata
twd = tw_privdata.Daten()
CLIENT_ID = twd.client_id
CLIENT_SECRET = twd.client_secret
REDIRECT_URI = "http://localhost:8080"
```

### 4.2. Scopes

Ihr verwendet einen recht umfangreichen Satz an OAuth-Scopes:

```python
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
```

Daraus wird in der URL ein Scope-String wie:

```text
user:read:email+channel:manage:broadcast+...+moderator:manage:blocked_terms
```

gebaut.

### 4.3. Token-Objekt (Adaten)

In `oauth.gen()` definierst du eine innere Klasse `Adaten`:

```python
class Adaten:
    def __init__(self):
        self.atoken = None         # Access Token
        self.rtoken = None         # Refresh Token
        self.expire = None         # Gültigkeitsdauer (Sekunden)
        self.clientid = CLIENT_ID
        self.clientsecret = CLIENT_SECRET
        self.userid = None         # Twitch-User-ID
        self.loginname = None      # z. B. "derflaavius"
        self.displayname = None    # z. B. "derFlaavius"
```

Dieses Objekt wird am Ende von `gen()` mit den Twitch-Daten befüllt und zurückgegeben.

### 4.4. OAuth-Flow (lokaler Server)

**Ablauf in `oauth.gen()` (aktuelle Version):**

1. `auth_event` ist ein globales `threading.Event`, mit dem gewartet wird, bis Twitch den Redirect schickt.

2. `OAuthHandler` erbt von `BaseHTTPRequestHandler` und:

   * fängt `/favicon.ico` ab
   * liest bei `/callback?code=...` den `code`-Parameter
   * tauscht den Code gegen einen Access Token via `https://id.twitch.tv/oauth2/token`
   * speichert das JSON in `token_info`
   * schickt eine HTML-Antwort „Login erfolgreich! …“
   * setzt `auth_event.set()`
   * ruft `self.server.shutdown()` in einem Thread → HTTP-Server beendet sich

3. `start_server()`:

```python
def start_server():
    server = http.server.HTTPServer(("localhost", 8080), OAuthHandler)
    server.serve_forever()
```

4. `start_server()` wird in einem **Daemon-Thread** gestartet:

```python
threading.Thread(target=start_server, daemon=True).start()
```

5. Es wird die OAuth-URL gebaut und im Browser geöffnet:

```python
scope_string = "+".join(SCOPES)

auth_url = (
    "https://id.twitch.tv/oauth2/authorize"
    f"?client_id={CLIENT_ID}"
    f"&redirect_uri={REDIRECT_URI}"
    f"&response_type=code"
    f"&scope={scope_string}"
)
webbrowser.open(auth_url)
```

6. `auth_event.wait()` blockiert, bis Twitch den Code zurückschickt und `OAuthHandler` `auth_event.set()` aufruft.

7. Danach wird `token` befüllt:

```python
token.atoken  = token_info.get("access_token")
token.rtoken  = token_info.get("refresh_token")
token.expire  = token_info.get("expires_in")
```

8. Es werden Userdaten über Helix geladen:

```python
user = requests.get(
    "https://api.twitch.tv/helix/users",
    headers={"Client-ID": CLIENT_ID, "Authorization": f"Bearer {token.atoken}"}
).json()
data = user["data"][0]
token.userid      = data["id"]
token.loginname   = data["login"]
token.displayname = data["display_name"]
```

9. `gen()` gibt das `token`-Objekt zurück.

### 4.5. Refresh-Funktion

In `refresh(token)`:

```python
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
token.atoken   = new_token_info.get("access_token")
token.rtoken   = new_token_info.get("refresh_token")
token.expire   = new_token_info.get("expires_in")
```

→ Der vorhandene `token` wird aktualisiert.

---

## 5. Launcher-GUI (aaa_prov_main.py)

Aktuell (in der letzten Version, die du gezeigt hast):

```python
from fremdsys import oauth, tapi_data, tapi_mod
import tkinter as tk
import moderator_dashboard
import os
import subprocess
import sys

root = tk.Tk()
root.geometry("200x150")
root.title("Starthilfe")

token = None  # global (implizit gesetzt über f_bn1)

def f_bn1():
    print("Anmeldung geklickt")
    global token
    token = oauth.gen()
    if token != []:  # logisch immer True, weil token ein Objekt ist
        tk.Label(root, text="Angemeldet", fg="green").pack()

def f_bn2():
    print("Mod Dashboard geklickt")
    def starte_dashboard():
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(current_dir, "moderator_dashboard.py")
        subprocess.Popen([sys.executable, script_path])
    starte_dashboard()

def f_bn3():
    print("Manager Dashboard geklickt")

tk.Label(root, text="").pack()
tk.Button(root, text="Twitch Anmelden", command=f_bn1).pack()
tk.Button(root, text="Mod Dashboard", command=f_bn2).pack()
tk.Button(root, text="Manager Dashboard", command=f_bn3).pack()

root.mainloop()
```

Später hast du auch eine **CustomTkinter-Version** angefangen, die `style.json` lädt (mit Keys `appearance_mode` und `color_theme`), aber dort gab es einen `KeyError: 'appearance_mode'`, weil die JSON-Datei diesen Key (noch) nicht enthielt.

---

## 6. Live-Chat (Moderation / Monitoring)

### 6.1. IRC-Chat lesen

Du hast mehrere Varianten gehabt, u. a.:

```python
import socket
import time

def get_live_messages(token):
    oauth_token = f"oauth:{token.atoken}"
    nickname = token.loginname
    channel = token.displayname
    duration = 10.0

    server = "irc.chat.twitch.tv"
    port = 6667

    sock = socket.socket()
    sock.connect((server, port))
    sock.settimeout(1.0)

    sock.send(f"PASS {oauth_token}\r\n".encode("utf-8"))
    sock.send(f"NICK {nickname}\r\n".encode("utf-8"))
    sock.send(f"JOIN #{channel}\r\n".encode("utf-8"))

    messages = []
    start_time = time.time()

    while time.time() - start_time < duration:
        try:
            resp = sock.recv(2048).decode("utf-8")

            if resp.startswith("PING"):
                sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                continue

            if "PRIVMSG" in resp:
                prefix, msg = resp.split(" PRIVMSG ", 1)
                user = prefix.split("!", 1)[0][1:]
                _, text = msg.split(" :", 1)

                messages.append({
                    "user": user,
                    "message": text.strip()
                })
        except socket.timeout:
            continue
        except Exception:
            continue

    sock.close()
    return messages
```

Wichtige Punkte:

* `PASS oauth:...` → Passwort ist dein Access Token mit Prefix `oauth:`.
* `NICK` → dein Login.
* `JOIN #channel` → Kanal joinen (`displayname` vs `loginname`: du hast beides getestet).
* `settimeout(1.0)` verhindert, dass `recv()` ewig blockiert – ermöglicht sauberen Abbruch.
* PING/PONG-Handling eingebaut.

Es gibt auch `test_irc_connection(token)`, das rohe IRC-Nachrichten für einige Sekunden ausgibt, um die Verbindung zu debuggen.

---

## 7. VOD-Chat & VOD-Handling

### 7.1. get_vod_chat(token)

Du hast eine Funktion erstellt, die:

1. Über Helix das **letzte VOD** deines Kanals holt:

```python
vod_url = f"https://api.twitch.tv/helix/videos?user_id={user_id}&type=archive&first=1"
```

2. Dann holt sie einen **App Access Token** via `client_credentials`.
3. Mit diesem Token ruft sie die (deprecated) V5-API auf:

```python
comments_url = f"https://api.twitch.tv/v5/videos/{video_id}/comments"
```

4. Sie läuft über alle Pages via `cursor` und sammelt:

```python
{
    "user": display_name des Commenters,
    "message": body,
    "timestamp": created_at
}
```

### 7.2. Problem: 404 / Leere Responses

Für deinen Kanal ergab sich konstant:

* V5-API gibt **404** oder leeres Response zurück.
* Das bedeutet:

  * Entweder hat das VOD **kein Chat Replay**, oder
  * Twitch liefert für deinen Kanal keinen VOD-Chat mehr aus (häufig bei kleinen Kanälen / neueren VODs / interner Policy).

### 7.3. list_vods_with_chat_status(token)

Du hast eine Funktion gebaut, die:

* Alle VODs holt (Helix):

```python
vod_url = f"https://api.twitch.tv/helix/videos?user_id={user_id}&type=archive&first=100"
```

* Für jedes VOD die V5-Comments-URL testet:

  * `200 + Inhalt` → `chat_status = "processed"`, `chat_available = True`
  * `200 + leer` → `pending_or_none`
  * `401/403` → `restricted`
  * Sonst → `error_<status>`

* Am Ende:

  * Wenn **mindestens ein VOD** `chat_available == True` → Rückgabecode `0`
  * Wenn **kein einziges** VOD Chat hat → Rückgabecode `404`

Für dich: alle VODs haben `error_404` → Chat ist de facto nicht abrufbar.

### 7.4. Wichtige Erkenntnis

* Für **euer Projekt** ist VOD-Chat über die API **praktisch tot**.
* Sinnvoller Ansatz: **Chat während des Streams selbst loggen** (via IRC) und lokal speichern (z. B. SQLite / JSON), wenn ihr Chat-Replay-Funktionen bauen wollt.

---

## 8. Moderationsfunktionen (Ban / Timeout / Unban)

Du wolltest Moderation aus dem Tool heraus ermöglichen.

### 8.1. Ban / Timeout

Die Funktion:

```python
def ban_or_timeout_user(token, username, duration=0, reason=""):
    client_id = token.clientid
    access_token = token.atoken
    broadcaster_id = token.userid

    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}"
    }

    # 1) User-ID auflösen
    user_lookup = requests.get(
        f"https://api.twitch.tv/helix/users?login={username}",
        headers=headers
    ).json()

    if "data" not in user_lookup or not user_lookup["data"]:
        print("❌ User nicht gefunden:", username)
        return 404

    target_user_id = user_lookup["data"][0]["id"]

    # 2) Ban / Timeout
    ban_url = (
        f"https://api.twitch.tv/helix/moderation/bans"
        f"?broadcaster_id={broadcaster_id}"
        f"&moderator_id={broadcaster_id}"
    )

    payload = {
        "data": {
            "user_id": target_user_id,
            "duration": duration if duration > 0 else None,
            "reason": reason
        }
    }
    if duration == 0:
        del payload["data"]["duration"]

    headers_json = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    resp = requests.post(ban_url, json=payload, headers=headers_json)

    if resp.status_code in (200, 201, 204):
        return 0

    return resp.status_code
```

* `duration > 0` → Timeout (Sekunden).
* `duration == 0` → permanenter Ban.
* Rückgabewert: `0` bei Erfolg, sonst HTTP-Statuscode.

### 8.2. Unban

Die dazugehörige **Unban-Funktion**:

```python
def unban_user(token, username):
    client_id = token.clientid
    access_token = token.atoken
    broadcaster_id = token.userid

    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}"
    }

    user_lookup = requests.get(
        f"https://api.twitch.tv/helix/users?login={username}",
        headers=headers
    ).json()

    if "data" not in user_lookup or not user_lookup["data"]:
        print("❌ User nicht gefunden:", username)
        return 404

    target_user_id = user_lookup["data"][0]["id"]

    unban_url = (
        f"https://api.twitch.tv/helix/moderation/bans"
        f"?broadcaster_id={broadcaster_id}"
        f"&moderator_id={broadcaster_id}"
        f"&user_id={target_user_id}"
    )

    resp = requests.delete(unban_url, headers=headers)

    if resp.status_code in (200, 204):
        return 0

    return resp.status_code
```

→ ebenfalls `0` bei Erfolg, sonst HTTP-Code.

### 8.3. Mod-Historie

Wir haben versucht, mit:

```python
GET https://api.twitch.tv/helix/moderation/banned/events
```

eine Moderationshistorie zu bekommen und herausgefunden:

* 404 / Not Found für deinen Kanal.
* Gründe:

  * Twitch gibt **nicht die eigene Broadcaster-Selbstmod-Historie** aus.
  * Logs gibt es nur, wenn ein *anderer Moderator* Aktionen ausführt (mit bestimmten Scopes).
* Praktische Konsequenz:

  * Für euer Tool ist es sinnvoller, eine **eigene Moderations-Logik** aufzusetzen (z. B. über IRC-Commands oder direkt bei euren Ban/Timeout-Requests loggen).

---

## 9. Bekannte Baustellen / offene Punkte

* **Token-Wiederverwendung:**
  Es gibt (mehrfach) Versuche, ein globales `token`-Objekt wiederzuverwenden und zu verhindern, dass `gen()` mehrfach läuft – ist aber nicht konsistent eingebaut (teilweise `global token`, teilweise gar nicht).
* **Abbruch des OAuth-Logins:**
  Wenn der User das Browserfenster schließt, ohne zu authorisieren, hängt `auth_event.wait()` → klassischer Deadlock.
  (Wir hatten eine Variante mit `wait(timeout=60)`, aber du bist wieder auf die einfache Variante zurück.)
* **CustomTkinter-Integration:**

  * Style-Datei `style.json` war geplant, hatte aber nicht die Keys `appearance_mode` und `color_theme`.
  * Der aktuelle Starter nutzt in der letzten Version wieder reines `tkinter`.
* **VOD-Chat:**

  * Für deinen Kanal praktisch nicht nutzbar → Konzept sollte auf Live-Logging ausweichen.

---

## 10. Zusammenfassung in einem Satz

**liveXtrem** ist ein in Python/CustomTkinter entwickelter Stream-Manager für Twitch, der sich wie ein ERP-System verhält (Module Finanzen, Planung, Moderation), sich per lokalem OAuth-Flow authentifiziert, ein zentrales `token`-Objekt mit allen relevanten Twitch-Daten verwaltet, Live-Chat über IRC liest, VOD-Chat (theoretisch) via V5-API auslesen kann (praktisch bei deinem Kanal nicht), und Moderation direkt über die Twitch-Helix-API (Ban/Timeout/Unban + perspektivisch mehr) steuert.

---

Wenn du magst, kann ich dir als nächsten Schritt:

* eine **Architekturübersicht** als Diagramm (textuell) erstellen,
* oder eine **Pflichtenheft-Section** formulieren (Zweck, Anforderungen, Schnittstellen),
* oder eine **Doku-Seite** für genau dieses OAuth-/Modul-Verhalten schreiben.

Sag einfach, in welche Richtung du die Doku als Nächstes brauchst.
