class SessionUser:
    """
    Repräsentiert den aktuell angemeldeten Benutzer + Rollen + Streamerinfo + TwitchTokens.
    Dieses Objekt wird an das Dashboard und alle weiteren Programme weitergegeben.
    """

    def __init__(self, user_row, roles, streamer_row, tokens_row):
        self.user_id = user_row["user_id"]
        self.email = user_row["email"]
        self.username = user_row["username"]
        self.created_at = user_row["created_at"]

        self.roles = roles                    # Liste von Rollen z.B. ['STREAMER']
        self.streamer = streamer_row          # Streamer-Eintrag oder None
        self.tokens = tokens_row              # Twitch OAuth Token-Daten

    # Komfort-Properties
    @property
    def is_streamer(self):
        return "STREAMER" in self.roles

    @property
    def is_moderator(self):
        return "MODERATOR" in self.roles

    @property
    def is_manager(self):
        return "MANAGER" in self.roles

    @property
    def display_name(self):
        if self.streamer:
            return self.streamer.get("name", self.username)
        return self.username

    def __repr__(self):
        return f"<SessionUser {self.username} Roles={self.roles}>"
