"""
Moderator Queries - Integration mit Twitch API
Chat-Nachrichten von VODs und echte Moderationsaktionen
"""

from database_connection import DatabaseManager
from datetime import datetime, timedelta

class ModeratorQueries:
    def __init__(self, db_manager, twitch_token=None):
        self.db = db_manager
        self.token = twitch_token  # OAuth Token von oauth.gen()
        
        # Lokale Datenspeicher für Moderationsaktionen
        self.moderation_actions = []
        self.action_id_counter = 1
        
        # Chat-Nachrichten (werden aus VODs geladen)
        self.chat_messages = []
        self.vod_info = None
        self.chat_load_error = None
    
    # ========== CHAT-NACHRICHTEN AUS VOD ==========
    
    def load_vod_chat(self):
        """Lädt Chat-Nachrichten vom letzten VOD via Twitch API"""
        if not self.token:
            self.chat_load_error = "Kein Twitch-Token vorhanden"
            return False
        
        try:
            # Importiere tapi_mod dynamisch
            from fremdsys import tapi_mod
            
            # Chat vom VOD laden
            all_messages, vod_with_chat, error_code = tapi_mod.get_vod_chat(self.token)
            
            if error_code == 404:
                self.chat_load_error = "Leider ist Chat-Replay für diesen Twitch Account nicht verfügbar"
                return False
            
            if error_code != 0:
                self.chat_load_error = f"Fehler beim Laden des Chats (Code: {error_code})"
                return False
            
            # Nachrichten konvertieren
            self.chat_messages = []
            msg_id = 1
            for msg in all_messages:
                self.chat_messages.append({
                    "nachricht_id": msg_id,
                    "username": msg["user"],
                    "nachricht": msg["message"],
                    "timestamp": msg["timestamp"]
                })
                msg_id += 1
            
            self.vod_info = vod_with_chat
            self.chat_load_error = None
            return True
            
        except Exception as e:
            self.chat_load_error = f"Fehler beim Laden: {str(e)}"
            return False
    
    def get_all_messages(self, limit=100):
        """Gibt Chat-Nachrichten zurück"""
        messages = sorted(self.chat_messages, key=lambda x: x["timestamp"], reverse=True)[:limit]
        
        data = []
        for msg in messages:
            data.append((
                msg["nachricht_id"], msg["username"], 
                msg["nachricht"], msg["timestamp"]
            ))
        
        return {"columns": [], "data": data}
    
    def get_vod_info(self):
        """Gibt VOD-Informationen zurück"""
        return self.vod_info
    
    def get_chat_error(self):
        """Gibt Chat-Fehler zurück"""
        return self.chat_load_error
    
    # ========== MODERATIONSAKTIONEN MIT TWITCH API ==========
    
    def ban_user(self, username, grund=""):
        """Bannt einen User permanent via Twitch API"""
        if not self.token:
            return {"success": False, "message": "Kein Twitch-Token vorhanden"}
        
        try:
            from fremdsys import tapi_mod
            result = tapi_mod.ban_or_timeout_user(self.token, username, duration=0, reason=grund)
            
            if result == 0:
                # Aktion lokal speichern
                self._add_local_action(username, "bann", grund, None)
                return {"success": True, "message": f"User '{username}' wurde gebannt"}
            elif result == 404:
                return {"success": False, "message": f"User '{username}' nicht gefunden"}
            elif result == 403:
                return {"success": False, "message": "Keine Berechtigung (fehlende Scopes)"}
            else:
                return {"success": False, "message": f"Fehler: HTTP {result}"}
                
        except Exception as e:
            return {"success": False, "message": f"Fehler: {str(e)}"}
    
    def timeout_user(self, username, dauer_minuten, grund=""):
        """Gibt einem User einen Timeout via Twitch API"""
        if not self.token:
            return {"success": False, "message": "Kein Twitch-Token vorhanden"}
        
        try:
            from fremdsys import tapi_mod
            dauer_sekunden = dauer_minuten * 60
            result = tapi_mod.ban_or_timeout_user(self.token, username, duration=dauer_sekunden, reason=grund)
            
            if result == 0:
                # Aktion lokal speichern
                self._add_local_action(username, "timeout", grund, dauer_minuten)
                return {"success": True, "message": f"User '{username}' hat {dauer_minuten}min Timeout"}
            elif result == 404:
                return {"success": False, "message": f"User '{username}' nicht gefunden"}
            elif result == 403:
                return {"success": False, "message": "Keine Berechtigung (fehlende Scopes)"}
            else:
                return {"success": False, "message": f"Fehler: HTTP {result}"}
                
        except Exception as e:
            return {"success": False, "message": f"Fehler: {str(e)}"}
    
    def unban_user(self, username):
        """Hebt einen Bann auf via Twitch API"""
        if not self.token:
            return {"success": False, "message": "Kein Twitch-Token vorhanden"}
        
        try:
            from fremdsys import tapi_mod
            result = tapi_mod.unban_user(self.token, username)
            
            if result == 0:
                # Aktion lokal speichern
                self._add_local_action(username, "unban", "Bann aufgehoben", None)
                return {"success": True, "message": f"User '{username}' wurde entbannt"}
            elif result == 404:
                return {"success": False, "message": f"User '{username}' nicht gefunden"}
            elif result == 403:
                return {"success": False, "message": "Keine Berechtigung"}
            else:
                return {"success": False, "message": f"Fehler: HTTP {result}"}
                
        except Exception as e:
            return {"success": False, "message": f"Fehler: {str(e)}"}
    
    def _add_local_action(self, username, aktion_typ, grund, dauer_minuten):
        """Fügt eine Moderationsaktion lokal hinzu (für Historie)"""
        ts = datetime.now()
        ablauf_zeit = ts + timedelta(minutes=dauer_minuten) if dauer_minuten else None
        
        moderator_name = self.token.displayname if self.token else "Moderator"
        
        action = {
            "aktion_id": self.action_id_counter,
            "moderator_name": moderator_name,
            "betroffener_user": username,
            "aktion_typ": aktion_typ,
            "grund": grund,
            "dauer_minuten": dauer_minuten,
            "timestamp": ts,
            "aktiv": True if aktion_typ != "unban" else False,
            "ablauf_zeit": ablauf_zeit
        }
        self.moderation_actions.append(action)
        self.action_id_counter += 1
    
    def get_moderation_history(self, limit=20):
        """Gibt die Moderations-Historie zurück"""
        history = sorted(self.moderation_actions, key=lambda x: x["timestamp"], reverse=True)[:limit]
        
        data = []
        for action in history:
            data.append((
                action["aktion_id"], action["aktion_typ"], action["grund"],
                action["dauer_minuten"], action["timestamp"], action["ablauf_zeit"],
                action["aktiv"], action["betroffener_user"], action["moderator_name"]
            ))
        
        return {"columns": [], "data": data}
    
    def get_moderator_stats(self):
        """Statistiken für Dashboard"""
        now = datetime.now()
        
        aktive_aktionen = len([a for a in self.moderation_actions 
                              if a["aktiv"] and (a["ablauf_zeit"] is None or a["ablauf_zeit"] > now)])
        
        gebannte_user = len([a for a in self.moderation_actions 
                           if a["aktiv"] and a["aktion_typ"] == "bann"])
        
        timeouts_mutes = len([a for a in self.moderation_actions 
                             if a["aktiv"] and a["aktion_typ"] in ["timeout"] 
                             and a["ablauf_zeit"] and a["ablauf_zeit"] > now])
        
        total_actions = len(self.moderation_actions)
        
        return {"columns": [], "data": [(aktive_aktionen, gebannte_user, timeouts_mutes, total_actions)]}
    
    def cleanup_expired_actions(self):
        """Deaktiviert abgelaufene Moderationsaktionen"""
        now = datetime.now()
        count = 0
        for action in self.moderation_actions:
            if action["aktiv"] and action["ablauf_zeit"] and action["ablauf_zeit"] < now:
                action["aktiv"] = False
                count += 1
        return {"affected_rows": count}
    
    # ========== DATENBANK-QUERIES ==========
    
    def get_all_users(self):
        """Lädt alle User aus der Datenbank"""
        query = "SELECT user_id, username, email FROM users ORDER BY username"
        return self.db.execute_query(query)