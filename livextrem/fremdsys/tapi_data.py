import requests

def header(token):
    CLIENT_ID = token.clientid
    ACCESS_TOKEN = token.atoken
    USER_ID = token.userid

    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    return headers

def laststreams(token, limit_per_page=100):
    """
    Ruft alle verfügbaren archivierten Streams (VODs) eines Nutzers ab.
    Twitch speichert VODs normalerweise 14-60 Tage (je nach Accounttyp).
    """
    
    CLIENT_ID = token.clientid
    ACCESS_TOKEN = token.atoken
    USER_ID = token.userid

    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    url = f"https://api.twitch.tv/helix/videos?user_id={USER_ID}&type=archive&first={limit_per_page}"
    all_streams = []
    cursor = None  # für Pagination

    while True:
        # Falls Pagination vorhanden, Cursor anhängen
        final_url = url + (f"&after={cursor}" if cursor else "")
        response = requests.get(final_url, headers=headers)
        data = response.json()

        if "data" not in data:
            raise Exception(f"Fehler beim Abruf der Twitch-Daten: {data}")

        # Keine weiteren Ergebnisse mehr
        if not data["data"]:
            break

        for video in data["data"]:
            stream_info = {
                "id": video["id"],
                "title": video["title"],
                "created_at": video["created_at"],
                "duration": video["duration"],
                "views": video["view_count"],
                "language": video.get("language"),
                "game_id": video.get("game_id"),
                "thumbnail_url": video.get("thumbnail_url"),
                "url": video.get("url")
            }

            # Kategorie (Spiel) abrufen
            if video.get("game_id"):
                game_req = requests.get(
                    f"https://api.twitch.tv/helix/games?id={video['game_id']}",
                    headers=headers
                ).json()
                if "data" in game_req and game_req["data"]:
                    stream_info["game_name"] = game_req["data"][0]["name"]
                else:
                    stream_info["game_name"] = None
            else:
                stream_info["game_name"] = None

            all_streams.append(stream_info)

        # Pagination: Nächste Seite abrufen, falls vorhanden
        cursor = data.get("pagination", {}).get("cursor")
        if not cursor:
            break

    return all_streams

# [{'id': '2607193563', 'title': 'Stream Together mit Tim 🎮🤝 | REPO + Chained Together', 'created_at': '2025-11-01T19:21:55Z', 'duration': '3h56m22s', 'views': 28, 'language': 'de', 'game_id': None, 'thumbnail_url': 'https://static-cdn.jtvnw.net/cf_vods/d3fi1amfgojobc/c6ed1943ca34bece2dd5_derflaavius_315023494631_1762024907//thumb/thumb0-%{width}x%{height}.jpg', 'url': 'https://www.twitch.tv/videos/2607193563', 'game_name': None}, {'id': '2602889239', 'title': 'Genesungsstream 🤒 | Ihr Entscheidet! 🎮', 'created_at': '2025-10-27T19:15:07Z', 'duration': '2h42m33s', 'views': 35, 'language': 'de', 'game_id': None, 'thumbnail_url': 'https://static-cdn.jtvnw.net/cf_vods/d3fi1amfgojobc/bc058d5aa3c07c15b8fe_derflaavius_314970933607_1761592501//thumb/thumb0-%{width}x%{height}.jpg', 'url': 'https://www.twitch.tv/videos/2602889239', 'game_name': None}]


def topbits(token):
    headers = header(token)
    bits = requests.get("https://api.twitch.tv/helix/bits/leaderboard", headers=headers).json()
    print(bits)
    return bits


def followlist(token): # Ruft alle Follower ab und gibt sie als Liste zurück
    def extract_usernames(flwrlist): # Filtert die Nutzernamen heraus, mehr wird nicht benötigt
        usernames = []
        for entry in flwrlist["data"]:
            usernames.append(entry["user_name"])
        return usernames
    
    headers = header(token)
    flwrlist = requests.get(f"https://api.twitch.tv/helix/channels/followers?broadcaster_id={token.userid}&first=100", headers=headers).json()
    flwrlist = extract_usernames(flwrlist)
    return flwrlist


def sublist(token): # Ruft alle Abonnenten von Twitch eines Kanals ab und gibt NUR DIE NAMEN als Liste zurück.
    def extract_usernames(subslist): # Filtert die Nutzernamen heraus, mehr wird nicht benötigt
        usernames = []
        for entry in subslist["data"]:
            usernames.append(entry["user_name"])
        return usernames

    headers = header(token)
    subslist = requests.get(f"https://api.twitch.tv/helix/subscriptions?broadcaster_id={token.userid}", headers=headers).json()
    subslist = extract_usernames(subslist)
    return subslist

