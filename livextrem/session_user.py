from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class TwitchIdentity:
    userid: Optional[str] = None
    login: Optional[str] = None
    displayname: Optional[str] = None

class SessionUser:
    """Aktuell angemeldeter Benutzer (keine Tokens in der DB!)."""

    def __init__(self, user_row: dict, role_id: int, streamer_row: Optional[dict], twitch_identity: TwitchIdentity, twitch_token: Any = None):
        self.user_id = user_row["user_id"]
        self.email = user_row["email"]
        self.username = user_row["username"]
        self.created_at = user_row.get("created_at")

        self.role_id = int(role_id)
        self.streamer = streamer_row
        self.twitch_identity = twitch_identity

        # Token nur im RAM (Session) – niemals in DB speichern
        self.twitch_token = twitch_token

    @property
    def is_streamer(self) -> bool:
        return self.role_id == 1

    @property
    def is_moderator(self) -> bool:
        return self.role_id == 2

    @property
    def is_manager(self) -> bool:
        return self.role_id == 3

    @property
    def display_name(self) -> str:
        if self.streamer and self.streamer.get("name"):
            return self.streamer["name"]
        if self.twitch_identity and self.twitch_identity.displayname:
            return self.twitch_identity.displayname
        return self.username

    def __repr__(self) -> str:
        return f"<SessionUser {self.username} role_id={self.role_id}>"
