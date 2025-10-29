import oauth
import requests

token = oauth.execute()
print(token.atoken, token.rtoken, token.userid)

# headers = {
#     "Client-ID": token.clientid,
#     "Authorization": f"Bearer {token.atoken}"
# }

# videos = requests.get(
#     f"https://api.twitch.tv/helix/videos?user_id={token.clientid}&type=archive&first=10",
#     headers=headers
# ).json()