from twitchAPI.twitch import Twitch
import requests

import klassen
from tw_privdata import Daten

twdaten = Daten()


def userinfos(uname): # User-Infos abrufen uname = User Loginname
    response = requests.get(f'https://api.twitch.tv/helix/users?login={uname}', headers=headers)
    data = response.json()
    return data

def vods(uname): # Streamdaten abrufen
    videos_url = f"https://api.twitch.tv/helix/videos?user_id={uname}&type=archive&first=10" # first=10 bedeutet letzten 10 streams
    videos_data = requests.get(videos_url, headers=headers).json()
    return videos_data

CLIENT_ID = twdaten.client_id
CLIENT_SECRET = twdaten.client_secret

auth_url = 'https://id.twitch.tv/oauth2/token'
auth_params = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'grant_type': 'client_credentials'
}

auth_response = requests.post(auth_url, params=auth_params)
access_token = auth_response.json()['access_token']

headers = {
    'Client-ID': CLIENT_ID,
    'Authorization': f'Bearer {access_token}'
}

data = userinfos("derFlaavius")
videodata = vods("800711400")

print("=== Streamer-Infos ===")
print(videodata)