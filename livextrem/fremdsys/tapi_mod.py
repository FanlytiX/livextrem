import socket
import time
import requests

def get_live_messages(token):
    oauth_token = f"oauth:{token.atoken}"
    print(oauth_token)
    nickname = token.loginname
    channel = token.displayname
    duration = 10.0

    server = "irc.chat.twitch.tv"
    port = 6667

    # Socket erstellen
    sock = socket.socket()
    sock.connect((server, port))
    sock.settimeout(1.0)  # <<< WICHTIG: verhindert Blockieren!

    # Login
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
            # Nach Timeout einfach nächste Runde – kein Blockieren
            continue
        except Exception:
            continue

    sock.close()
    return messages


def live_test_irc_connection(token):
    oauth_token = f"oauth:{token.atoken}"
    nickname = token.loginname.lower()
    channel = token.loginname.lower()

    server = "irc.chat.twitch.tv"
    port = 6667

    sock = socket.socket()
    sock.connect((server, port))
    sock.settimeout(1.0)  # <<< WICHTIG: verhindert Blockieren!

    sock.send(f"PASS {oauth_token}\r\n".encode("utf-8"))
    sock.send(f"NICK {nickname}\r\n".encode("utf-8"))
    sock.send(f"JOIN #{channel}\r\n".encode("utf-8"))

    print("Verbunden – lese 10 Sekunden alle RAW-Nachrichten...")

    start = time.time()
    while time.time() - start < 10:
        try:
            resp = sock.recv(2048).decode("utf-8")
            print("RAW:", resp)
        except socket.timeout:
            # Kein Chat → kein Problem → weiter
            continue
        except Exception:
            continue

    sock.close()


def get_vod_chat(token):
    """
    Kombinierte Funktion:
    - Listet alle VODs mit Chat-Status
    - Findet das neueste VOD mit Chat (processed)
    - Lädt seinen kompletten Chat
    - Gibt (chat_messages, selected_vod, status_code) zurück

    Status 0   = Chat gefunden und geladen
    Status 404 = Kein einziges VOD mit Chat verfügbar
    """

    client_id = token.clientid
    client_secret = token.clientsecret
    access_token = token.atoken
    user_id = token.userid

    # === 1. VOD-Liste holen (Helix) ===
    vod_url = f"https://api.twitch.tv/helix/videos?user_id={user_id}&type=archive&first=100"
    headers_helix = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}",
    }

    vod_resp = requests.get(vod_url, headers=headers_helix).json()

    if "data" not in vod_resp or not vod_resp["data"]:
        print("❌ Keine VODs gefunden.")
        return [], None, 404

    vods = vod_resp["data"]

    # === 2. App Access Token (für V5 Chat API) ===
    app_token = requests.post(
        "https://id.twitch.tv/oauth2/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        },
    ).json()["access_token"]

    v5_headers = {
        "Client-ID": client_id,
        "Accept": "application/vnd.twitchtv.v5+json",
        "Authorization": f"OAuth {app_token}",
    }

    vod_status_list = []
    vod_with_chat = None

    # === 3. Prüfung aller VODs auf Chat ===
    for vod in vods:
        vod_id = vod["id"]
        title = vod["title"]

        comments_url = f"https://api.twitch.tv/v5/videos/{vod_id}/comments"
        resp = requests.get(comments_url, headers=v5_headers)

        # Chat OK
        if resp.status_code == 200 and resp.text.strip():
            vod_status_list.append({
                "video_id": vod_id,
                "title": title,
                "chat_status": "processed",
                "chat_available": True
            })

            # Das NEUESTE VOD mit Chat auswählen
            if vod_with_chat is None:
                vod_with_chat = vod  # Speichere vollständiges Helix-VOD
            continue

        # Chat pending / none
        if resp.status_code == 200 and not resp.text.strip():
            vod_status_list.append({
                "video_id": vod_id,
                "title": title,
                "chat_status": "pending_or_none",
                "chat_available": False
            })
            continue

        # Zugriff verweigert
        if resp.status_code in (401, 403):
            vod_status_list.append({
                "video_id": vod_id,
                "title": title,
                "chat_status": "restricted",
                "chat_available": False
            })
            continue

        # Unbekannt
        vod_status_list.append({
            "video_id": vod_id,
            "title": title,
            "chat_status": f"error_{resp.status_code}",
            "chat_available": False
        })

    # === 4. Kein VOD mit Chat gefunden? ===
    if vod_with_chat is None:
        print("❌ Kein VOD enthält Chat.")
        return vod_status_list, None, 404

    # === 5. Chat des gefundenen VODs laden ===
    selected_vod_id = vod_with_chat["id"]
    print(f"📺 VOD mit Chat gefunden! Video-ID: {selected_vod_id}")

    comments_url = f"https://api.twitch.tv/v5/videos/{selected_vod_id}/comments"

    all_messages = []
    cursor = None

    while True:
        params = {"cursor": cursor} if cursor else {}

        resp_raw = requests.get(comments_url, headers=v5_headers, params=params)
        if resp_raw.status_code != 200:
            print("❌ Fehler beim Laden des Chats:", resp_raw.text)
            break

        resp = resp_raw.json()

        if "comments" not in resp:
            break

        for c in resp["comments"]:
            all_messages.append({
                "user": c["commenter"]["display_name"] if c["commenter"] else "Unknown",
                "message": c["message"]["body"],
                "timestamp": c["created_at"]
            })

        cursor = resp.get("_next")
        if not cursor:
            break

    print(f"✅ Chat geladen: {len(all_messages)} Nachrichten")

    return all_messages, vod_with_chat, 0