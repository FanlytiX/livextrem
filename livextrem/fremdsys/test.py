import oauth
import requests
import tapi_data


token = oauth.gen()
print(token.atoken, token.rtoken, token.userid)


#abc = tapi_data.laststreams(token)
#tapi_data.topbits(token)
#abc = tapi_data.followlist(token)
abc = tapi_data.sublist(token)
print(abc)

def test_laststream(token):
    last = tapi_data.laststreams(token)

    print(f"📺 {len(last)} Streams gefunden:\n")

    for s in last:
        print(f"🎬 {s['title']}")
        print(f"📅 Datum: {s['created_at']}")
        print(f"⌛ Dauer: {s['duration']}")
        print(f"🎮 Spiel: {s.get('game_name', 'Unbekannt')}")
        print(f"👀 Views: {s['views']}")
        print(f"🔗 URL: {s['url']}")
        print("-" * 60)

# headers = {
#     "Client-ID": token.clientid,
#     "Authorization": f"Bearer {token.atoken}"
# }

# videos = requests.get(
#     f"https://api.twitch.tv/helix/videos?user_id={token.clientid}&type=archive&first=10",
#     headers=headers
# ).json()