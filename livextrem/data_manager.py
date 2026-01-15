# data_manager.py
import os
from pathlib import Path

import customtkinter as ctk
import mysql.connector


# -------------------- ENV LADEN --------------------
def load_env_file(filename=".env"):
    env_path = Path(__file__).resolve().parent / filename
    if not env_path.exists():
        print("❌ .env nicht gefunden:", env_path)
        return

    with env_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip().strip('"').strip("'")

load_env_file()


# -------------------- CONFIG --------------------
class Config:
    # Farben: [light, dark]
    BG_WHITE      = ["gray95", "#111111"]
    PANEL_BG      = ["gray90", "#181818"]
    PANEL_ACCENT  = ["gray80", "#262626"]

    HEADER_ORANGE = ["#1c31ba", "#D2601A"]
    HEADER_HOVER  = ["#14375e", "#B44E12"]

    SIDEBAR_BLUE  = ["#1c31ba", "#D2601A"]
    SIDEBAR_HOVER = ["#325882", "#B44E12"]

    TEXT_DARK  = ["gray14", "gray90"]
    TEXT_LIGHT = ["white",  "white"]

    DATA_FILE = "livextrem_data.json"

    # DB
    DB_HOST = "88.218.227.14"
    DB_PORT = 3306
    DB_USER = "livextrem"
    DB_PASSWORD = os.getenv("LIVEXTREM_DB_PASSWORD")  # ✅ aus .env
    DB_NAME = "livextrem"

    # Theme
    ctk.set_appearance_mode("light")
    THEME_PATH = os.path.join(os.path.dirname(__file__), "style.json")
    ctk.set_default_color_theme(THEME_PATH)


# -------------------- STREAMER FARBEN --------------------
STREAMER_COLOR_CHOICES = {
    "Grün":   "#008922",
    "Pink":   "#ff009d",
    "Rot":    "#FF0004",
    "Gelb":   "#FFD854",
    "Lila":   "#9B59B6",
    "Türkis": "#00FFCC"
}


# -------------------- DATA MANAGER (DB) --------------------
class DataManager:
    def __init__(self, data_file):
        self.data_file = data_file  # bleibt nur wegen Signatur
        self._connect_db()

    def _connect_db(self):
        if not Config.DB_PASSWORD:
            raise RuntimeError("❌ DB-Passwort fehlt. Prüfe .env (LIVEXTREM_DB_PASSWORD).")

        self.conn = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        self.cursor = self.conn.cursor(dictionary=True)

    # ----------- STREAMER-FUNKTIONEN -----------

    def get_all_streamers(self):
        self.cursor.execute("""
            SELECT 
                streamer_id AS id,
                name,
                COALESCE(status, 'Aktiv') AS status,
                COALESCE(farbe, '#34C759') AS color_hex
            FROM streamer
            WHERE status <> 'Archiviert'
            ORDER BY name
        """)
        return self.cursor.fetchall()

    def get_archived_streamers(self):
        self.cursor.execute("""
            SELECT 
                streamer_id AS id,
                name,
                COALESCE(status, 'Archiviert') AS status,
                COALESCE(farbe, '#34C759') AS color_hex
            FROM streamer
            WHERE status = 'Archiviert'
            ORDER BY name
        """)
        return self.cursor.fetchall()

    def reactivate_streamer(self, streamer_id):
        self.cursor.execute("""
            UPDATE streamer
            SET status = 'Aktiv'
            WHERE streamer_id = %s
        """, (streamer_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def add_streamer(self, name, status='Aktiv', color='#34C759'):
        self.cursor.execute("""
            INSERT INTO streamer (name, plattform, email, status, farbe)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, None, None, status, color))
        self.conn.commit()
        new_id = self.cursor.lastrowid
        return {'id': new_id, 'name': name, 'status': status, 'color': color}

    def update_streamer(self, streamer_id, name, status, color):
        self.cursor.execute("""
            UPDATE streamer
            SET name = %s,
                status = %s,
                farbe = %s
            WHERE streamer_id = %s
        """, (name, status, color, streamer_id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def archive_streamer(self, streamer_id):
        self.cursor.execute("""
            UPDATE streamer
            SET status = 'Archiviert'
            WHERE streamer_id = %s
        """, (streamer_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    # ------------ EVENT-FUNKTIONEN (stream_planung) ------------

    def add_event(self, date_key, title, streamer_id, streamer_name):
        self.cursor.execute("""
            INSERT INTO stream_planung 
            (streamer_id, content_id, datum, thema, status)
            VALUES (%s, NULL, %s, %s, 'geplant')
        """, (streamer_id, date_key + " 00:00:00", title))
        self.conn.commit()

        plan_id = self.cursor.lastrowid
        return {
            'id': plan_id,
            'title': title,
            'streamerId': streamer_id,
            'streamerName': streamer_name,
            'createdAt': f"{date_key} 00:00:00",
            'date_key': date_key
        }

    def delete_event(self, event_id, date_key=None):
        self.cursor.execute("DELETE FROM stream_planung WHERE plan_id = %s", (event_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def update_event(self, event_id, old_date_key, new_date_key,
                     new_title, new_streamer_id, new_streamer_name):
        neues_datum = new_date_key + " 00:00:00"
        self.cursor.execute("""
            UPDATE stream_planung
            SET thema = %s,
                streamer_id = %s,
                datum = %s
            WHERE plan_id = %s
        """, (new_title, new_streamer_id, neues_datum, event_id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_event_by_id(self, event_id, date_key=None):
        self.cursor.execute("""
            SELECT 
                sp.plan_id AS id,
                DATE(sp.datum) AS date_key,
                sp.thema AS title,
                sp.streamer_id AS streamerId,
                s.name AS streamerName,
                s.farbe AS streamerColor,
                sp.datum AS createdAt
            FROM stream_planung sp
            JOIN streamer s ON sp.streamer_id = s.streamer_id
            WHERE sp.plan_id = %s
        """, (event_id,))
        row = self.cursor.fetchone()
        if row:
            if hasattr(row['createdAt'], 'isoformat'):
                row['createdAt'] = row['createdAt'].isoformat()
            if hasattr(row['date_key'], 'isoformat'):
                row['date_key'] = row['date_key'].isoformat()
        return row

    def get_events_for_day(self, date_key):
        self.cursor.execute("""
            SELECT 
                sp.plan_id AS id,
                DATE(sp.datum) AS date_key,
                sp.thema AS title,
                sp.streamer_id AS streamerId,
                s.name AS streamerName,
                s.farbe AS streamerColor,
                sp.datum AS createdAt
            FROM stream_planung sp
            JOIN streamer s ON sp.streamer_id = s.streamer_id
            WHERE DATE(sp.datum) = %s
            AND s.status <> 'Archiviert'
            ORDER BY sp.datum
        """, (date_key,))
        rows = self.cursor.fetchall()
        for row in rows:
            if hasattr(row['createdAt'], 'isoformat'):
                row['createdAt'] = row['createdAt'].isoformat()
            if hasattr(row['date_key'], 'isoformat'):
                row['date_key'] = row['date_key'].isoformat()
        return rows

    def get_all_events_sorted(self):
        self.cursor.execute("""
            SELECT 
                sp.plan_id AS id,
                DATE(sp.datum) AS date_key,
                sp.thema AS title,
                sp.streamer_id AS streamerId,
                s.name AS streamerName,
                s.farbe AS streamerColor,
                sp.datum AS createdAt
            FROM stream_planung sp
            JOIN streamer s ON sp.streamer_id = s.streamer_id
            WHERE s.status <> 'Archiviert'
            ORDER BY sp.datum
        """)
        rows = self.cursor.fetchall()
        for row in rows:
            if hasattr(row['createdAt'], 'isoformat'):
                row['createdAt'] = row['createdAt'].isoformat()
            if hasattr(row['date_key'], 'isoformat'):
                row['date_key'] = row['date_key'].isoformat()
        return rows

    def get_upcoming_events(self):
        self.cursor.execute("""
            SELECT 
                sp.plan_id AS id,
                DATE(sp.datum) AS date_key,
                sp.thema AS title,
                sp.streamer_id AS streamerId,
                s.name AS streamerName,
                s.farbe AS streamerColor,
                sp.datum AS createdAt
            FROM stream_planung sp
            JOIN streamer s ON sp.streamer_id = s.streamer_id
            WHERE sp.datum >= NOW()
            AND s.status <> 'Archiviert'
            ORDER BY sp.datum
            LIMIT 5
        """)
        rows = self.cursor.fetchall()
        for row in rows:
            if hasattr(row['createdAt'], 'isoformat'):
                row['createdAt'] = row['createdAt'].isoformat()
            if hasattr(row['date_key'], 'isoformat'):
                row['date_key'] = row['date_key'].isoformat()
        return rows
