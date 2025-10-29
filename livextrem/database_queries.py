from database_connection import DatabaseManager
from datetime import datetime, timedelta


def display_table_data(db, table_name):
    """Zeigt alle Daten einer Tabelle formatiert an"""
    print(f"\n=== TABELLE: {table_name} ===")
    
    # Tabellenstruktur anzeigen
    structure = db.get_table_structure(table_name)
    if structure and "data" in structure:
        print("Struktur:")
        for column in structure["data"]:
            null_info = "NULL" if column[2] == "YES" else "NOT NULL"
            default = f"DEFAULT {column[4]}" if column[4] else ""
            print(f"  - {column[0]} ({column[1]}) {null_info} {default}".strip())
    
    # Tabellendaten anzeigen
    data = db.get_table_data(table_name)
    if data and "data" in data and data["data"]:
        print(f"\nDaten ({len(data['data'])} Einträge):")
        
        # Spaltennamen anzeigen
        if data["columns"]:
            # Maximale Spaltenbreiten berechnen
            col_widths = []
            for i, col_name in enumerate(data["columns"]):
                max_width = len(str(col_name))
                for row in data["data"]:
                    max_width = max(max_width, len(str(row[i] if i < len(row) else "")))
                col_widths.append(min(max_width, 30))  # Maximale Breite begrenzen
            
            # Spaltenüberschriften anzeigen
            header = " | ".join(f"{col_name:<{col_widths[i]}}" for i, col_name in enumerate(data["columns"]))
            print(header)
            print("-" * len(header))
        
            # Alle Zeilen anzeigen
            for row in data["data"]:
                formatted_row = []
                for i, value in enumerate(row):
                    if value is None:
                        formatted_value = "NULL"
                    else:
                        formatted_value = str(value)
                    # Text auf maximale Breite kürzen
                    if len(formatted_value) > col_widths[i]:
                        formatted_value = formatted_value[:col_widths[i]-3] + "..."
                    formatted_row.append(f"{formatted_value:<{col_widths[i]}}")
                print(" | ".join(formatted_row))
    else:
        print("Keine Daten vorhanden")
    print("=" * 80)

def main():
    # Datenbank-Manager erstellen und verbinden
    db = DatabaseManager()
    db.connection()
    
    try:
        # Tabellen über information_schema abrufen (das funktioniert)
        print("Lade Datenbank-Struktur...")
        tables_result = db.get_tables_info()
        
        if tables_result and "data" in tables_result:
            table_names = [table[0] for table in tables_result["data"]]
            print(f"Gefundene Tabellen: {', '.join(table_names)}")
            
            # Für jede Tabelle die Daten anzeigen
            for table_name in table_names:
                display_table_data(db, table_name)
        else:
            print("Keine Tabellen in der Datenbank gefunden")
            
    except Exception as e:
        print(f"Fehler beim Abrufen der Daten: {e}")
    finally:
        # Verbindung immer schließen
        db.connClose()
     

if __name__ == "__main__":
    main()
   
   
   




class ModeratorQueries:
    def __init__(self, db_manager):
        self.db = db_manager
        
        # Lokale Datenspeicher (simulieren später Twitch API Daten)
        self.chat_messages = []
        self.moderation_actions = []
        self.message_id_counter = 1
        self.action_id_counter = 1
        
        # Testdaten initialisieren
        self._init_test_data()
    
    def _init_test_data(self):
        """Erstellt initiale Testdaten"""
        # Test-Chat-Nachrichten
        test_messages = [
            {"user_id": 1, "username": "RoadKing", "nachricht": "Hey Leute, willkommen im Stream!", "timestamp": datetime.now() - timedelta(minutes=30)},
            {"user_id": 3, "username": "NightWolf", "nachricht": "Geiler Stream heute!", "timestamp": datetime.now() - timedelta(minutes=28)},
            {"user_id": 4, "username": "StreamQueen", "nachricht": "Können wir mehr Drift sehen?", "timestamp": datetime.now() - timedelta(minutes=25)},
            {"user_id": 5, "username": "DenChill", "nachricht": "Das Setup ist der Hammer!", "timestamp": datetime.now() - timedelta(minutes=22)},
            {"user_id": 3, "username": "NightWolf", "nachricht": "Spam Spam Spam", "timestamp": datetime.now() - timedelta(minutes=20)},
            {"user_id": 4, "username": "StreamQueen", "nachricht": "Nice, weiter so!", "timestamp": datetime.now() - timedelta(minutes=18)},
            {"user_id": 1, "username": "RoadKing", "nachricht": "Danke für die ganzen Subs!", "timestamp": datetime.now() - timedelta(minutes=15)},
            {"user_id": 3, "username": "NightWolf", "nachricht": "Wann kommt das nächste Event?", "timestamp": datetime.now() - timedelta(minutes=12)},
            {"user_id": 5, "username": "DenChill", "nachricht": "Ich liebe diese Community!", "timestamp": datetime.now() - timedelta(minutes=10)},
            {"user_id": 4, "username": "StreamQueen", "nachricht": "Kann jemand den Discord Link posten?", "timestamp": datetime.now() - timedelta(minutes=8)},
        ]
        
        for msg in test_messages:
            self.add_test_message(msg["user_id"], msg["username"], msg["nachricht"], msg["timestamp"])
        
        # Test-Moderationsaktionen
        self.timeout_user(1, 3, 10, "Spam im Chat", timestamp=datetime.now() - timedelta(minutes=19))
        self.mute_user(2, 5, 5, "Unangemessene Sprache", timestamp=datetime.now() - timedelta(minutes=40))
    
    # ========== CHAT-NACHRICHTEN ==========
    
    def get_all_messages(self, limit=100, include_deleted=False):
        """Lädt alle Chat-Nachrichten"""
        messages = self.chat_messages if include_deleted else [m for m in self.chat_messages if not m.get("geloescht", False)]
        messages = sorted(messages, key=lambda x: x["timestamp"], reverse=True)[:limit]
        
        # Simuliere Datenbankformat
        data = []
        for msg in messages:
            if include_deleted:
                data.append((
                    msg["nachricht_id"], msg["user_id"], msg["username"], 
                    msg["nachricht"], msg["timestamp"], msg.get("geloescht", False),
                    msg.get("geloescht_von"), msg.get("geloescht_am")
                ))
            else:
                data.append((
                    msg["nachricht_id"], msg["user_id"], msg["username"], 
                    msg["nachricht"], msg["timestamp"]
                ))
        
        return {"columns": [], "data": data}
    
    def get_deleted_messages(self, limit=50):
        """Lädt gelöschte Nachrichten"""
        deleted = [m for m in self.chat_messages if m.get("geloescht", False)]
        deleted = sorted(deleted, key=lambda x: x.get("geloescht_am", datetime.now()), reverse=True)[:limit]
        
        data = []
        for msg in deleted:
            mod_name = msg.get("moderator_name", "Unbekannt")
            data.append((
                msg["nachricht_id"], msg["username"], msg["nachricht"],
                msg["timestamp"], msg.get("geloescht_am"), mod_name
            ))
        
        return {"columns": [], "data": data}
    
    def delete_message(self, nachricht_id, moderator_id):
        """Löscht eine Chat-Nachricht"""
        for msg in self.chat_messages:
            if msg["nachricht_id"] == nachricht_id:
                msg["geloescht"] = True
                msg["geloescht_von"] = moderator_id
                msg["geloescht_am"] = datetime.now()
                
                # Moderator-Namen hinzufügen
                mod_result = self.db.execute_query("SELECT name FROM moderator WHERE moderator_id = ?", (moderator_id,))
                if mod_result and mod_result["data"]:
                    msg["moderator_name"] = mod_result["data"][0][0]
                
                return {"affected_rows": 1}
        return {"affected_rows": 0}
    
    def add_test_message(self, user_id, username, nachricht, timestamp=None):
        """Fügt eine Test-Nachricht hinzu"""
        msg = {
            "nachricht_id": self.message_id_counter,
            "user_id": user_id,
            "username": username,
            "nachricht": nachricht,
            "timestamp": timestamp or datetime.now(),
            "geloescht": False,
            "geloescht_von": None,
            "geloescht_am": None
        }
        self.chat_messages.append(msg)
        self.message_id_counter += 1
        return {"affected_rows": 1}
    
    # ========== MODERATIONSAKTIONEN ==========
    
    def mute_user(self, moderator_id, user_id, dauer_minuten, grund="", timestamp=None):
        """Schaltet einen User stumm"""
        ts = timestamp or datetime.now()
        ablauf_zeit = ts + timedelta(minutes=dauer_minuten)
        
        # Moderator- und User-Namen holen
        mod_result = self.db.execute_query("SELECT name FROM moderator WHERE moderator_id = ?", (moderator_id,))
        user_result = self.db.execute_query("SELECT username FROM users WHERE user_id = ?", (user_id,))
        
        mod_name = mod_result["data"][0][0] if mod_result and mod_result["data"] else "Unbekannt"
        username = user_result["data"][0][0] if user_result and user_result["data"] else "Unbekannt"
        
        action = {
            "aktion_id": self.action_id_counter,
            "moderator_id": moderator_id,
            "moderator_name": mod_name,
            "betroffener_user_id": user_id,
            "betroffener_user": username,
            "aktion_typ": "mute",
            "grund": grund,
            "dauer_minuten": dauer_minuten,
            "timestamp": ts,
            "aktiv": True,
            "ablauf_zeit": ablauf_zeit
        }
        self.moderation_actions.append(action)
        self.action_id_counter += 1
        return {"affected_rows": 1}
    
    def timeout_user(self, moderator_id, user_id, dauer_minuten, grund="", timestamp=None):
        """Gibt einem User einen Timeout"""
        ts = timestamp or datetime.now()
        ablauf_zeit = ts + timedelta(minutes=dauer_minuten)
        
        mod_result = self.db.execute_query("SELECT name FROM moderator WHERE moderator_id = ?", (moderator_id,))
        user_result = self.db.execute_query("SELECT username FROM users WHERE user_id = ?", (user_id,))
        
        mod_name = mod_result["data"][0][0] if mod_result and mod_result["data"] else "Unbekannt"
        username = user_result["data"][0][0] if user_result and user_result["data"] else "Unbekannt"
        
        action = {
            "aktion_id": self.action_id_counter,
            "moderator_id": moderator_id,
            "moderator_name": mod_name,
            "betroffener_user_id": user_id,
            "betroffener_user": username,
            "aktion_typ": "timeout",
            "grund": grund,
            "dauer_minuten": dauer_minuten,
            "timestamp": ts,
            "aktiv": True,
            "ablauf_zeit": ablauf_zeit
        }
        self.moderation_actions.append(action)
        self.action_id_counter += 1
        return {"affected_rows": 1}
    
    def ban_user(self, moderator_id, user_id, grund=""):
        """Bannt einen User permanent"""
        mod_result = self.db.execute_query("SELECT name FROM moderator WHERE moderator_id = ?", (moderator_id,))
        user_result = self.db.execute_query("SELECT username FROM users WHERE user_id = ?", (user_id,))
        
        mod_name = mod_result["data"][0][0] if mod_result and mod_result["data"] else "Unbekannt"
        username = user_result["data"][0][0] if user_result and user_result["data"] else "Unbekannt"
        
        action = {
            "aktion_id": self.action_id_counter,
            "moderator_id": moderator_id,
            "moderator_name": mod_name,
            "betroffener_user_id": user_id,
            "betroffener_user": username,
            "aktion_typ": "bann",
            "grund": grund,
            "dauer_minuten": None,
            "timestamp": datetime.now(),
            "aktiv": True,
            "ablauf_zeit": None
        }
        self.moderation_actions.append(action)
        self.action_id_counter += 1
        return {"affected_rows": 1}
    
    def get_active_moderation_actions(self):
        """Lädt alle aktiven Moderationsaktionen"""
        now = datetime.now()
        active = [a for a in self.moderation_actions 
                 if a["aktiv"] and (a["ablauf_zeit"] is None or a["ablauf_zeit"] > now)]
        
        data = []
        for action in active:
            data.append((
                action["aktion_id"], action["aktion_typ"], action["grund"],
                action["dauer_minuten"], action["timestamp"], action["ablauf_zeit"],
                action["betroffener_user"], action["moderator_name"]
            ))
        
        return {"columns": [], "data": data}
    
    def get_moderation_history(self, limit=50):
        """Lädt Moderations-Historie"""
        history = sorted(self.moderation_actions, key=lambda x: x["timestamp"], reverse=True)[:limit]
        
        data = []
        for action in history:
            data.append((
                action["aktion_id"], action["aktion_typ"], action["grund"],
                action["dauer_minuten"], action["timestamp"], action["ablauf_zeit"],
                action["aktiv"], action["betroffener_user"], action["moderator_name"]
            ))
        
        return {"columns": [], "data": data}
    
    def deactivate_moderation(self, aktion_id):
        """Deaktiviert eine Moderationsaktion vorzeitig"""
        for action in self.moderation_actions:
            if action["aktion_id"] == aktion_id:
                action["aktiv"] = False
                action["ablauf_zeit"] = datetime.now()
                return {"affected_rows": 1}
        return {"affected_rows": 0}
    
    def get_user_by_username(self, username):
        """Sucht einen User nach Username"""
        query = "SELECT user_id, username, email FROM users WHERE username = ?"
        return self.db.execute_query(query, (username,))
    
    def get_all_users(self):
        """Lädt alle User"""
        query = "SELECT user_id, username, email FROM users ORDER BY username"
        return self.db.execute_query(query)
    
    def get_moderator_stats(self):
        """Statistiken für Dashboard"""
        now = datetime.now()
        
        aktive_aktionen = len([a for a in self.moderation_actions 
                              if a["aktiv"] and (a["ablauf_zeit"] is None or a["ablauf_zeit"] > now)])
        
        geloeschte_nachrichten = len([m for m in self.chat_messages if m.get("geloescht", False)])
        
        gebannte_user = len([a for a in self.moderation_actions 
                           if a["aktiv"] and a["aktion_typ"] == "bann"])
        
        gemutete_user = len([a for a in self.moderation_actions 
                           if a["aktiv"] and a["aktion_typ"] in ["mute", "timeout"] 
                           and a["ablauf_zeit"] and a["ablauf_zeit"] > now])
        
        return {"columns": [], "data": [(aktive_aktionen, geloeschte_nachrichten, gebannte_user, gemutete_user)]}
    
    def cleanup_expired_actions(self):
        """Deaktiviert abgelaufene Moderationsaktionen"""
        now = datetime.now()
        count = 0
        for action in self.moderation_actions:
            if action["aktiv"] and action["ablauf_zeit"] and action["ablauf_zeit"] < now:
                action["aktiv"] = False
                count += 1
        return {"affected_rows": count} 
    
