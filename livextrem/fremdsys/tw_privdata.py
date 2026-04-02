from config import Config

class Daten:
    def __init__(self):
        # Lade aus ENV (keine Secrets im Code!)
        self.client_id = Config.TWITCH_CLIENT_ID
        self.client_secret = Config.TWITCH_CLIENT_SECRET
