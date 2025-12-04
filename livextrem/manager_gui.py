import customtkinter as ctk
import datetime
import calendar
import json
import os
import uuid
from PIL import Image   # für das Logo-Bild
import mysql.connector  # <-- für die DB-Verbindung


# --- KONFIGURATION & FARBEN (Dein Design) ---
class Config:
    # Farben an das gemeinsame Theme angepasst
    BG_WHITE = "gray95"          # Grund-Hintergrund (passt zu CTk.fg_color)
    PANEL_BG = "gray90"          # Panels / Container
    PANEL_ACCENT = "gray80"      # leichte Absetzung / Trenner
    HEADER_ORANGE = "#1c31ba"    # <- jetzt dein Primary-Blue (Buttons, Header)
    HEADER_HOVER = "#14375e"     # Hover-Blue wie im Theme
    SIDEBAR_BLUE = "#1c31ba"     # Navigation aktiv
    SIDEBAR_HOVER = "#325882"    # Navigation hover
    TEXT_DARK = "gray14"         # Standard-Textfarbe helles Theme
    TEXT_LIGHT = "white"

    DATA_FILE = "livextrem_data.json"

    # --- DB-Konfiguration (unverändert, nur optik wollten wir ja ändern) ---
    DB_HOST = "88.218.227.14"
    DB_PORT = 3306
    DB_USER = "livextrem"
    DB_PASSWORD = "leckmeineeier"
    DB_NAME = "livextrem"

    # --- CustomTkinter Theme setzen ---
    ctk.set_appearance_mode("light")

    # JSON-Theme im gleichen Ordner wie dieses Script
    THEME_PATH = os.path.join(os.path.dirname(__file__), "style.json")
    ctk.set_default_color_theme(THEME_PATH)




# --- DATENMODEL & PERSISTENZ (MySQL/MariaDB) ---

class DataManager:
    """
    DataManager mit echter MySQL/MariaDB-Anbindung.
    Nutzt Tabellen:
      - streamer
      - stream_planung
    Die GUI spricht weiterhin über dieselben Methoden wie vorher.
    """

    def __init__(self, data_file):
        # data_file bleibt nur wegen der Signatur, wird nicht genutzt.
        self.data_file = data_file
        self._connect_db()

    def _connect_db(self):
        """Stellt die Verbindung zur Datenbank her."""
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
        """Liest alle Streamer aus der Tabelle streamer."""
        self.cursor.execute("""
            SELECT 
                streamer_id AS id,
                name,
                COALESCE(status, 'Aktiv') AS status
            FROM streamer
            ORDER BY name
        """)
        return self.cursor.fetchall()

    def add_streamer(self, name, status='Aktiv'):
        """Neuen Streamer in der DB anlegen."""
        self.cursor.execute("""
            INSERT INTO streamer (name, plattform, email, status)
            VALUES (%s, %s, %s, %s)
        """, (name, '', '', status))
        self.conn.commit()

        new_id = self.cursor.lastrowid
        return {'id': new_id, 'name': name, 'status': status}

    def update_streamer(self, streamer_id, name, status):
        """Streamer in der DB aktualisieren."""
        self.cursor.execute("""
            UPDATE streamer
            SET name = %s,
                status = %s
            WHERE streamer_id = %s
        """, (name, status, streamer_id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_streamer(self, streamer_id):
        """Streamer aus der DB löschen."""
        self.cursor.execute(
            "DELETE FROM streamer WHERE streamer_id = %s",
            (streamer_id,)
        )
        self.conn.commit()
        return self.cursor.rowcount > 0

    

    # ------------ EVENT-FUNKTIONEN (stream_planung) ------------

    def add_event(self, date_key, title, streamer_id, streamer_name):
        try:
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

        except mysql.connector.Error as err:
            print("DB-Fehler beim Event speichern:", err)
            raise



    def delete_event(self, event_id, date_key):
        """Event über seine ID löschen (date_key wird nicht benötigt, bleibt nur für die Signatur)."""
        self.cursor.execute(
            "DELETE FROM stream_planung WHERE plan_id = %s",
            (event_id,)
        )
        self.conn.commit()
        return self.cursor.rowcount > 0

    def update_event(self, event_id, old_date_key, new_date_key,
                     new_title, new_streamer_id, new_streamer_name):
        """Event-Daten in stream_planung updaten."""

        # Aus dem Datum-String ein richtiges DATETIME für MySQL machen
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



    def get_event_by_id(self, event_id, date_key):
        """Ein einzelnes Event über seine ID holen."""
        self.cursor.execute("""
            SELECT 
                sp.plan_id AS id,
                DATE(sp.datum) AS date_key,
                sp.thema AS title,
                sp.streamer_id AS streamerId,
                s.name AS streamerName,
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
        """Alle Events für einen bestimmten Tag (YYYY-MM-DD)."""
        self.cursor.execute("""
            SELECT 
                sp.plan_id AS id,
                DATE(sp.datum) AS date_key,
                sp.thema AS title,
                sp.streamer_id AS streamerId,
                s.name AS streamerName,
                sp.datum AS createdAt
            FROM stream_planung sp
            JOIN streamer s ON sp.streamer_id = s.streamer_id
            WHERE DATE(sp.datum) = %s
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
        """Alle Events, sortiert nach Datum."""
        self.cursor.execute("""
            SELECT 
                sp.plan_id AS id,
                DATE(sp.datum) AS date_key,
                sp.thema AS title,
                sp.streamer_id AS streamerId,
                s.name AS streamerName,
                sp.datum AS createdAt
            FROM stream_planung sp
            JOIN streamer s ON sp.streamer_id = s.streamer_id
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
        """Die nächsten 5 anstehenden Events."""
        self.cursor.execute("""
            SELECT 
                sp.plan_id AS id,
                DATE(sp.datum) AS date_key,
                sp.thema AS title,
                sp.streamer_id AS streamerId,
                s.name AS streamerName,
                sp.datum AS createdAt
            FROM stream_planung sp
            JOIN streamer s ON sp.streamer_id = s.streamer_id
            WHERE sp.datum >= NOW()
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


# --- CustomTkinter GUI KLASSE ---

class ManagerDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("LiveXtrem Manager-Dashboard")
        self.geometry("1200x700")
        self.data_manager = DataManager(Config.DATA_FILE)
        self.current_date = datetime.date.today()

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.nav_buttons = {}

        self._setup_sidebar()

        self.main_content_area = ctk.CTkFrame(self, fg_color=Config.BG_WHITE, corner_radius=0)
        self.main_content_area.grid(row=0, column=1, sticky="nsew", padx=(20, 20), pady=(10, 20))
        self.main_content_area.grid_columnconfigure(0, weight=1)
        self.main_content_area.grid_rowconfigure(1, weight=1)

        self.show_view("Startseite")

    # --- VIEW MANAGER ---
    def show_view(self, view_name):

        for widget in self.main_content_area.winfo_children():
            widget.destroy()

        self._highlight_active_nav(view_name)

        if view_name == "Startseite":
            self._render_dashboard_view()
        elif view_name == "Streamer":
            self._render_streamer_view()
        elif view_name == "Termine":
            self._render_all_events_view()
        elif view_name == "Kalender":
            self._render_full_calendar_view()
        elif view_name == "Einstellungen":
            self._render_placeholder_view(view_name)

        self.main_title = ctk.CTkLabel(self.main_content_area,
                                       text=f"Manager-Dashboard: {view_name}",
                                       font=ctk.CTkFont(size=28, weight="bold"),
                                       text_color=Config.TEXT_DARK,
                                       anchor="w")
        self.main_title.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 20), sticky="ew")

    # --- Full Calendar View ---
    def _render_full_calendar_view(self):
        calendar_view_container = ctk.CTkFrame(self.main_content_area, fg_color=Config.PANEL_BG, corner_radius=12)
        calendar_view_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        calendar_view_container.grid_columnconfigure(0, weight=1)
        calendar_view_container.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(calendar_view_container, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        nav_frame = ctk.CTkFrame(header, fg_color="transparent")
        nav_frame.grid(row=0, column=1, sticky="e")

        ctk.CTkButton(nav_frame, text="◀", command=lambda: self.change_month(-1),
                      width=30, height=30, corner_radius=15,
                      fg_color=Config.HEADER_ORANGE, hover_color=Config.HEADER_HOVER, text_color=Config.TEXT_LIGHT).grid(row=0, column=0, padx=5)

        self.month_year_label_full = ctk.CTkLabel(nav_frame, text="Loading...", font=ctk.CTkFont(size=18, weight="bold"))
        self.month_year_label_full.grid(row=0, column=1, padx=10)

        ctk.CTkButton(nav_frame, text="▶", command=lambda: self.change_month(1),
                      width=30, height=30, corner_radius=15,
                      fg_color=Config.HEADER_ORANGE, hover_color=Config.HEADER_HOVER, text_color=Config.TEXT_LIGHT).grid(row=0, column=2, padx=5)

        self.calendar_grid_container_full = ctk.CTkFrame(calendar_view_container, fg_color=Config.BG_WHITE, corner_radius=10)
        self.calendar_grid_container_full.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        weekdays = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        for i, day in enumerate(weekdays):
            color = "red" if i >= 5 else Config.SIDEBAR_BLUE
            ctk.CTkLabel(self.calendar_grid_container_full, text=day,
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=color).grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            self.calendar_grid_container_full.grid_columnconfigure(i, weight=1)

        self.calendar_day_buttons_full = []
        self.update_calendar(full_view=True)

    # --- Dashboard View ---
    def _render_dashboard_view(self):

        dashboard_frame = ctk.CTkFrame(self.main_content_area, fg_color=Config.BG_WHITE, corner_radius=0)
        dashboard_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        dashboard_frame.grid_columnconfigure((0, 1, 2), weight=1)
        dashboard_frame.grid_rowconfigure((0, 1), weight=0)

        # oben: Event-Panel + Kalender
        self._create_event_planning_panel(dashboard_frame, 0, 0)
        self._create_calendar_panel(dashboard_frame, 0, 1, columnspan=2)

        # unten: Bevorstehende Termine über die ganze Breite
        self._create_upcoming_events_panel(dashboard_frame, 1, 0, columnspan=3)

        self.update_calendar()
        self.update_upcoming_events()

    # --- Termine View ---
    def _render_all_events_view(self):
        events_view_container = ctk.CTkFrame(self.main_content_area, fg_color=Config.PANEL_BG, corner_radius=12)
        events_view_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        events_view_container.grid_columnconfigure(0, weight=1)
        events_view_container.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(events_view_container, text="Übersicht aller geplanten Events",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=Config.TEXT_DARK).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.all_events_list_frame = ctk.CTkScrollableFrame(events_view_container, fg_color=Config.BG_WHITE, corner_radius=10, label_text="Alle Events (Historisch und Zukünftig)")
        self.all_events_list_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.all_events_list_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.all_events_list_frame.grid_columnconfigure(4, weight=0)

        self.update_all_events_list()

    def update_all_events_list(self):

        if not hasattr(self, 'all_events_list_frame') or not self.all_events_list_frame.winfo_exists():
            return

        try:
            for widget in self.all_events_list_frame.winfo_children():
                widget.destroy()
        except ctk.TclError:
            return

        events = self.data_manager.get_all_events_sorted()

        if not events:
            ctk.CTkLabel(self.all_events_list_frame, text="Keine Events in der Datenbank gefunden.",
                        text_color=Config.TEXT_DARK, font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=10, pady=10, sticky="ew", columnspan=5)
            return

        # Header
        header_row = 0
        ctk.CTkLabel(self.all_events_list_frame, text="Datum", font=ctk.CTkFont(weight="bold"), text_color=Config.SIDEBAR_BLUE).grid(row=header_row, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.all_events_list_frame, text="Wochentag", font=ctk.CTkFont(weight="bold"), text_color=Config.SIDEBAR_BLUE).grid(row=header_row, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.all_events_list_frame, text="Event-Titel", font=ctk.CTkFont(weight="bold"), text_color=Config.SIDEBAR_BLUE).grid(row=header_row, column=2, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.all_events_list_frame, text="Streamer", font=ctk.CTkFont(weight="bold"), text_color=Config.SIDEBAR_BLUE).grid(row=header_row, column=3, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.all_events_list_frame, text="Aktionen", font=ctk.CTkFont(weight="bold"), text_color=Config.SIDEBAR_BLUE).grid(row=header_row, column=4, padx=10, pady=5, sticky="w")

        ctk.CTkFrame(self.all_events_list_frame, height=2, fg_color=Config.PANEL_ACCENT).grid(row=header_row + 1, column=0, columnspan=5, sticky="ew", padx=5)

        # Deutsche Wochentage Mapping
        de_weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

        for i, event in enumerate(events):
            row = i + 2

            date_obj = datetime.date.fromisoformat(event['date_key'])
            formatted_date = date_obj.strftime("%d.%m.%Y")

            weekday_name = de_weekdays[date_obj.weekday()]

            # Datum
            ctk.CTkLabel(self.all_events_list_frame, text=formatted_date, anchor="w").grid(row=row, column=0, padx=10, pady=5, sticky="w")

            # Wochentag Deutsch
            ctk.CTkLabel(self.all_events_list_frame, text=weekday_name, anchor="w").grid(row=row, column=1, padx=10, pady=5, sticky="w")

            # Titel
            ctk.CTkLabel(self.all_events_list_frame, text=event['title'], anchor="w").grid(row=row, column=2, padx=10, pady=5, sticky="w")

            # Streamer
            ctk.CTkLabel(self.all_events_list_frame, text=event['streamerName'], anchor="w", text_color=Config.SIDEBAR_BLUE).grid(row=row, column=3, padx=10, pady=5, sticky="w")

            # Buttons
            action_frame = ctk.CTkFrame(self.all_events_list_frame, fg_color="transparent")
            action_frame.grid(row=row, column=4, padx=10, pady=5, sticky="e")

            ctk.CTkButton(action_frame, text="Bearbeiten",
                        command=lambda e=event: self._show_edit_event_dialog(e),
                        fg_color=Config.SIDEBAR_BLUE, hover_color=Config.SIDEBAR_HOVER,
                        width=80, height=25, font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=(0, 5))

            ctk.CTkButton(action_frame, text="Löschen",
                        command=lambda e=event: self._confirm_delete_event(e),
                        fg_color="red", hover_color="#A00000",
                        width=80, height=25, font=ctk.CTkFont(size=12)).grid(row=0, column=1)

            # Linie
            ctk.CTkFrame(self.all_events_list_frame, height=1, fg_color=Config.PANEL_ACCENT).grid(row=row+1, column=0, columnspan=5, sticky="ew", padx=5)


    def _show_edit_event_dialog(self, event):
        """Opens the dialog to edit an existing event."""
        if not hasattr(self, 'event_dialog') or not self.event_dialog.winfo_exists():
            self.event_dialog = EventDialog(self, date_key=event['date_key'], existing_event=event)
            self.event_dialog.grab_set()
        else:
            self.event_dialog.lift()

    def _confirm_delete_event(self, event):
        """Shows a confirmation dialog for deleting an event."""

        dialog = ctk.CTkToplevel(self)
        dialog.title("Löschen bestätigen")
        dialog.geometry("400x150")
        dialog.configure(fg_color=Config.BG_WHITE)
        dialog.grab_set()

        ctk.CTkLabel(
        dialog,
        text=f"Sicher, dass du das Event '{event['title']}' löschen willst?",
        text_color=Config.TEXT_DARK,
        font=ctk.CTkFont(size=12, weight="bold"),   # 🔥 kleinere Schrift
        wraplength=350,                             # 🔥 Zeilenumbruch aktiv
        justify="center"                            # 🔥 Text schön zentrieren
        ).pack(padx=20, pady=15)


        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=10)

        def delete_confirmed():
            success = self.data_manager.delete_event(event['id'], event['date_key'])
            if success:
                self.show_message_box('Event erfolgreich gelöscht.', 'success')
                self.update_all_events_list()
                self.update_calendar()
                self.update_upcoming_events()
            else:
                self.show_message_box('Fehler beim Löschen des Events.', 'error')
            dialog.destroy()

        ctk.CTkButton(button_frame, text="Löschen", command=delete_confirmed,
                      fg_color="red", hover_color="#A00000", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10)

        ctk.CTkButton(button_frame, text="Abbrechen", command=dialog.destroy,
                      fg_color="gray", hover_color="darkgray").grid(row=0, column=1, padx=10)

    def _render_streamer_view(self):
        streamer_frame = ctk.CTkFrame(self.main_content_area, fg_color=Config.BG_WHITE)
        streamer_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # WICHTIG: Diese Zeile sorgt dafür, dass die Liste mitwächst
        streamer_frame.grid_rowconfigure(0, weight=1)
        streamer_frame.grid_rowconfigure(1, weight=0)
        streamer_frame.grid_columnconfigure(0, weight=1)

        # --- OBERER BEREICH: Streamer-Liste ---
        list_container = ctk.CTkFrame(streamer_frame, fg_color=Config.PANEL_ACCENT, corner_radius=12)
        list_container.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(list_container, text="Alle Streamer verwalten",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color=Config.TEXT_DARK).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.streamer_list_frame = ctk.CTkScrollableFrame(
            list_container, fg_color=Config.BG_WHITE, corner_radius=8
        )
        self.streamer_list_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        self.update_streamer_list(self.streamer_list_frame)

        # --- UNTERER BEREICH: Streamer hinzufügen ---
        add_container = ctk.CTkFrame(streamer_frame, fg_color=Config.PANEL_BG, corner_radius=12)
        add_container.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        add_container.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(add_container, text="Neuen Streamer hinzufügen",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=Config.TEXT_DARK).grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        self.new_streamer_entry = ctk.CTkEntry(add_container, placeholder_text="Name des neuen Streamers", corner_radius=8)
        self.new_streamer_entry.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")

        ctk.CTkButton(add_container, text="Hinzufügen",
                    command=self._add_new_streamer,
                    fg_color=Config.SIDEBAR_BLUE,
                    hover_color=Config.SIDEBAR_HOVER,
                    corner_radius=10).grid(row=2, column=0, padx=20, pady=(0, 15), sticky="ew")


    def update_streamer_list(self, list_frame):
        """Updates the streamer list in the streamer view."""

        for widget in list_frame.winfo_children():
            widget.destroy()

        streamers = self.data_manager.get_all_streamers()

        # Header
        ctk.CTkLabel(list_frame, text="NAME", font=ctk.CTkFont(weight="bold"), text_color=Config.SIDEBAR_BLUE).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(list_frame, text="STATUS", font=ctk.CTkFont(weight="bold"), text_color=Config.SIDEBAR_BLUE).grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkLabel(list_frame, text="AKTIONEN", font=ctk.CTkFont(weight="bold"), text_color=Config.SIDEBAR_BLUE).grid(row=0, column=2, padx=10, pady=5)

        # Spaltenbreiten sauber einstellen
        list_frame.grid_columnconfigure(0, weight=4)   # Name
        list_frame.grid_columnconfigure(1, weight=1)   # Status
        list_frame.grid_columnconfigure(2, weight=2)   # Aktionen

        ctk.CTkFrame(list_frame, height=1, fg_color=Config.PANEL_ACCENT).grid(row=1, column=0, columnspan=3, sticky="ew")

        if not streamers:
            ctk.CTkLabel(list_frame, text="Keine Streamer vorhanden.", text_color="gray").grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="w")
            return

        for i, streamer in enumerate(streamers):
            row = i + 2

            name = streamer.get('name', 'Unbekannt')
            status = streamer.get('status', 'Aktiv')

            # Name
            ctk.CTkLabel(list_frame, text=name, anchor="w").grid(row=row, column=0, padx=10, pady=5, sticky="w")

            # Farbpunkte
            if status == 'Aktiv':
                dot_color = "#34C759"
            else:
                dot_color = "#FFD60A"

            ctk.CTkLabel(
                list_frame,
                text="●",
                text_color=dot_color,
                font=ctk.CTkFont(size=28)
            ).grid(row=row, column=1, padx=10, pady=0)

            # Aktionen
            action_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
            action_frame.grid(row=row, column=2, padx=10, pady=5, sticky="e")

            ctk.CTkButton(action_frame, text="Bearbeiten",
                        command=lambda s=streamer: self._show_streamer_edit_dialog(s),
                        fg_color=Config.SIDEBAR_BLUE, hover_color=Config.SIDEBAR_HOVER,
                        width=80, height=25, font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=(0, 5))

            ctk.CTkButton(action_frame, text="Löschen",
                        command=lambda s=streamer: self._confirm_delete_streamer(s),
                        fg_color="red", hover_color="#A00000",
                        width=80, height=25, font=ctk.CTkFont(size=12)).grid(row=0, column=1)

            ctk.CTkFrame(list_frame, height=1, fg_color=Config.PANEL_ACCENT).grid(row=row+1, column=0, columnspan=3, sticky="ew")


    def _show_streamer_edit_dialog(self, streamer):
        """Opens the dialog to edit a streamer."""
        dialog = StreamerDialog(self, streamer)
        dialog.grab_set()

    def _confirm_delete_streamer(self, streamer):
        """Shows a confirmation dialog for deleting a streamer."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Streamer löschen")
        dialog.geometry("400x150")
        dialog.configure(fg_color=Config.BG_WHITE)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"Sicher, dass du '{streamer['name']}' löschen willst?",
                     text_color=Config.TEXT_DARK, font=ctk.CTkFont(size=14, weight="bold")).pack(padx=20, pady=15)

        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=10)

        def delete_confirmed():
            success = self.data_manager.delete_streamer(streamer['id'])
            if success:
                self.show_message_box('Streamer erfolgreich gelöscht.', 'success')
                self.update_streamer_list(self.streamer_list_frame)
                self.update_calendar()
                self.update_upcoming_events()
            else:
                self.show_message_box('Fehler beim Löschen des Streamers.', 'error')
            dialog.destroy()

        ctk.CTkButton(button_frame, text="Löschen", command=delete_confirmed,
                      fg_color="red", hover_color="#A00000", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10)

        ctk.CTkButton(button_frame, text="Abbrechen", command=dialog.destroy,
                      fg_color="gray", hover_color="darkgray").grid(row=0, column=1, padx=10)

    def _add_new_streamer(self):
        name = self.new_streamer_entry.get().strip()
        if name:
            self.data_manager.add_streamer(name)
            self.new_streamer_entry.delete(0, 'end')
            self.show_message_box(f"Streamer '{name}' hinzugefügt.", 'success')

            if hasattr(self, 'streamer_list_frame') and self.streamer_list_frame.winfo_exists():
                self.update_streamer_list(self.streamer_list_frame)

            self._update_event_dialog_streamer_options()
        else:
            self.show_message_box("Bitte gib einen Namen ein.", 'warning')

    def _update_event_dialog_streamer_options(self):
        """Aktualisiert die Streamer-Auswahl im Event-Dialog, falls dieser offen ist."""
        if hasattr(self, "event_dialog") and self.event_dialog.winfo_exists():
            streamers = self.data_manager.get_all_streamers()
            names = [s.get('name', 'Unbekannt') for s in streamers]

            if not names:
                names = ["Keine Streamer gefunden"]
                self.event_dialog.streamer_map_names_to_id = {}
            else:
                self.event_dialog.streamer_map_names_to_id = {
                    s.get('name', 'Unbekannt'): s.get('id') for s in streamers
                }

            self.event_dialog.streamer_optionmenu.configure(values=names)

            current = self.event_dialog.streamer_var.get()
            if current not in names:
                self.event_dialog.streamer_var.set(names[0])

    def _render_placeholder_view(self, view_name):
        placeholder_frame = ctk.CTkFrame(self.main_content_area, fg_color=Config.PANEL_BG, corner_radius=12)
        placeholder_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        placeholder_frame.grid_columnconfigure(0, weight=1)
        placeholder_frame.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(placeholder_frame,
                     text=f"Funktionalität für '{view_name}' wird bald implementiert!",
                     font=ctk.CTkFont(size=24, weight="bold"),
                     text_color=Config.TEXT_DARK).grid(row=0, column=0, padx=50, pady=50, sticky="nsew")

    # --- SETUP DER SIDEBAR ---
    def _setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=Config.BG_WHITE)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        # Logo laden
        logo_path = os.path.join(os.path.dirname(__file__), "images",
        "logo.png")
        try:
            self.logo_image = ctk.CTkImage(
                light_image=Image.open(logo_path),
                size=(180, 60)
            )
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, image=self.logo_image, text="")
        except Exception as e:
            print(f"Logo konnte nicht geladen werden: {e}")
            self.logo_label = ctk.CTkLabel(self.sidebar_frame,
                                           text="LIVE XTREM",
                                           font=ctk.CTkFont(size=24, weight="bold", family="Inter"),
                                           text_color=Config.HEADER_ORANGE)

        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        nav_items = [
            ("Startseite", 1),
            ("Termine", 2),
            ("Kalender", 3),
            ("Streamer", 4),
        ]

        for i, (text, row) in enumerate(nav_items):
            button = ctk.CTkButton(self.sidebar_frame,
                                   text=text,
                                   command=lambda t=text: self.show_view(t),
                                   fg_color="transparent",
                                   hover_color=Config.PANEL_ACCENT,
                                   text_color=Config.TEXT_DARK,
                                   anchor="w",
                                   compound="left",
                                   corner_radius=10)
            button.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
            self.nav_buttons[text] = button

        

        self.user_id_label = ctk.CTkLabel(self.sidebar_frame,
                                          text="Premium Edition",
                                          text_color="gray",
                                          font=ctk.CTkFont(size=10))
        self.user_id_label.grid(row=9, column=0, padx=10, pady=(0, 10), sticky="w")

    def _highlight_active_nav(self, active_view):
        for name, button in self.nav_buttons.items():
            if name == active_view:
                button.configure(fg_color=Config.SIDEBAR_BLUE, text_color=Config.TEXT_LIGHT, hover_color=Config.SIDEBAR_HOVER)
            else:
                button.configure(fg_color="transparent", text_color=Config.TEXT_DARK, hover_color=Config.PANEL_ACCENT)

    def _get_icon(self, icon_name=None):
        return None

    # --- PANEL 1: Event & Terminplanung ---
    def _create_event_planning_panel(self, parent_frame, row, column):
        frame = ctk.CTkFrame(parent_frame, fg_color=Config.PANEL_BG, corner_radius=12)
        frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text="Event & Terminplanung",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=Config.TEXT_DARK, anchor="w").grid(row=0, column=0, padx=20, pady=(20, 5), sticky="ew")

        ctk.CTkLabel(frame, text="Plane und koordiniere zukünftige Livestream-Events mit den Streamern.",
                     font=ctk.CTkFont(size=12),
                     text_color=Config.TEXT_DARK, anchor="w", wraplength=250).grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.new_event_btn = ctk.CTkButton(frame,
                                           text="+ Neues Event planen",
                                           command=lambda: self._show_event_dialog(datetime.date.today().isoformat()),
                                           fg_color=Config.HEADER_ORANGE,
                                           hover_color=Config.HEADER_HOVER,
                                           text_color=Config.TEXT_LIGHT,
                                           font=ctk.CTkFont(size=16, weight="bold"),
                                           corner_radius=10)
        self.new_event_btn.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")

    # --- PANEL 2: Kalender-/Terminübersicht (Klein) ---
    def _create_calendar_panel(self, parent_frame, row, column, columnspan=1):
        self.calendar_frame_container = ctk.CTkFrame(parent_frame, fg_color=Config.PANEL_BG, corner_radius=12)
        self.calendar_frame_container.grid(row=row, column=column, columnspan=columnspan, padx=10, pady=10, sticky="nsew")
        self.calendar_frame_container.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self.calendar_frame_container, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text="Kalenderübersicht",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=Config.TEXT_DARK, anchor="w").grid(row=0, column=0, sticky="w")

        nav_frame = ctk.CTkFrame(header, fg_color="transparent")
        nav_frame.grid(row=0, column=1, sticky="e")

        ctk.CTkButton(nav_frame, text="◀", command=lambda: self.change_month(-1),
                      width=30, height=30, corner_radius=15,
                      fg_color=Config.HEADER_ORANGE, hover_color=Config.HEADER_HOVER, text_color=Config.TEXT_LIGHT).grid(row=0, column=0, padx=5)

        self.month_year_label = ctk.CTkLabel(nav_frame, text="Loading...", font=ctk.CTkFont(size=14, weight="bold"))
        self.month_year_label.grid(row=0, column=1, padx=10)

        ctk.CTkButton(nav_frame, text="▶", command=lambda: self.change_month(1),
                      width=30, height=30, corner_radius=15,
                      fg_color=Config.HEADER_ORANGE, hover_color=Config.HEADER_HOVER, text_color=Config.TEXT_LIGHT).grid(row=0, column=2, padx=5)

        self.calendar_grid_container = ctk.CTkFrame(self.calendar_frame_container, fg_color=Config.BG_WHITE, corner_radius=10)
        self.calendar_grid_container.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

        weekdays = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        for i, day in enumerate(weekdays):
            color = "red" if i >= 5 else Config.SIDEBAR_BLUE
            ctk.CTkLabel(self.calendar_grid_container, text=day,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=color).grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            self.calendar_grid_container.grid_columnconfigure(i, weight=1)

        self.calendar_day_buttons = []

    def update_calendar(self, full_view=False):

        # Welcher Kalender soll aktualisiert werden?
        if full_view:
            if not hasattr(self, 'calendar_grid_container_full') or not self.calendar_grid_container_full.winfo_exists():
                return
            container = self.calendar_grid_container_full
            day_buttons_list = self.calendar_day_buttons_full
            month_label = self.month_year_label_full
        else:
            if not hasattr(self, 'calendar_grid_container') or not self.calendar_grid_container.winfo_exists():
                return
            container = self.calendar_grid_container
            day_buttons_list = self.calendar_day_buttons
            month_label = self.month_year_label

        # Alte Buttons löschen
        for button in day_buttons_list:
            button.destroy()
        day_buttons_list.clear()

        # Monat / Jahr setzen
        year, month = self.current_date.year, self.current_date.month
        month_label.configure(text=self.current_date.strftime("%B %Y"))

        cal = calendar.Calendar(firstweekday=calendar.MONDAY)
        month_days = cal.itermonthdays2(year, month)

        row = 1
        col = 0
        today_iso = datetime.date.today().isoformat()

        for day, weekday in month_days:
            # Leere Felder am Monatsanfang überspringen
            if day == 0:
                col = (col + 1) % 7
                if col == 0:
                    row += 1
                continue

            date_obj = datetime.date(year, month, day)
            date_key = date_obj.isoformat()

            # Events für diesen Tag holen
            events_for_day = self.data_manager.get_events_for_day(date_key)
            has_events = bool(events_for_day)

            # Heute markieren
            is_today = date_key == today_iso

            fg_color = Config.HEADER_ORANGE if is_today else Config.PANEL_BG
            text_color = Config.TEXT_LIGHT if is_today else Config.TEXT_DARK
            hover_color = Config.HEADER_HOVER if is_today else Config.PANEL_ACCENT

            # --------- GROSSER KALENDER (Kalender-View) ----------
            if full_view:
                text = f"{day}"
                height = 70

                if has_events:
                    text += f"\n({len(events_for_day)} Events)"
                    fg_color = Config.PANEL_ACCENT
                    text_color = Config.TEXT_DARK

                day_button = ctk.CTkButton(
                    container,
                    text=text,
                    command=lambda k=date_key: self._show_event_dialog(k),
                    fg_color=fg_color,
                    hover_color=hover_color,
                    text_color=text_color,
                    height=height,
                    corner_radius=8,
                    font=ctk.CTkFont(size=14, weight="bold")
                )

            # --------- KLEINER KALENDER (Dashboard) ----------
            else:
                text = f"{day}"

                # Basis-Style vom Button (wie bisher)
                btn_fg_color = fg_color
                btn_hover_color = hover_color
                btn_text_color = text_color
                btn_font = ctk.CTkFont(size=12)

                # Wenn Events vorhanden sind (aber nicht heute):
                # -> Hintergrund leicht anders, Text orange + fett
                if has_events and not is_today:
                    btn_fg_color = "#ffd854"     # 🔥 GELB für Events
                    btn_hover_color = "#ffcc33"  # etwas dunkler beim Hover
                    btn_text_color = "#000000"   # schwarzer Text
                    btn_font = ctk.CTkFont(size=12, weight="bold")

                day_button = ctk.CTkButton(
                    container,
                    text=text,
                    command=lambda k=date_key: self._show_event_dialog(k),
                    fg_color=btn_fg_color,
                    hover_color=btn_hover_color,
                    text_color=btn_text_color,
                    width=40,
                    height=40,
                    corner_radius=8,
                    font=btn_font
                )

            # Button platzieren
            day_button.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            day_buttons_list.append(day_button)

            # Spalte/Zeile weiterschalten
            col = (col + 1) % 7
            if col == 0:
                row += 1


    def change_month(self, delta):
        new_month = self.current_date.month + delta
        new_year = self.current_date.year

        if new_month > 12:
            new_month = 1
            new_year += 1
        elif new_month < 1:
            new_month = 12
            new_year -= 1

        self.current_date = datetime.date(new_year, new_month, 1)

        if hasattr(self, "main_title") and self.main_title.cget("text").endswith(": Kalender"):
            self.update_calendar(full_view=True)
        else:
            self.update_calendar(full_view=False)

    # --- PANEL 3: Upcoming Events ---
    def _create_upcoming_events_panel(self, parent_frame, row, column, columnspan=1):
        self.upcoming_frame = ctk.CTkFrame(parent_frame, fg_color=Config.PANEL_BG, corner_radius=12)
        self.upcoming_frame.grid(row=row, column=column, columnspan=columnspan, padx=10, pady=10, sticky="nsew")
        self.upcoming_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.upcoming_frame, text="Bevorstehende Termine",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=Config.TEXT_DARK, anchor="w").grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.upcoming_list_frame = ctk.CTkFrame(self.upcoming_frame, fg_color=Config.BG_WHITE, corner_radius=10)
        self.upcoming_list_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.upcoming_list_frame.grid_columnconfigure(0, weight=1)

    def update_upcoming_events(self):

        if not hasattr(self, 'upcoming_list_frame') or not self.upcoming_list_frame.winfo_exists():
            return

        for widget in self.upcoming_list_frame.winfo_children():
            widget.destroy()

        upcoming_events = self.data_manager.get_upcoming_events()

        if not upcoming_events:
            ctk.CTkLabel(self.upcoming_list_frame, text="Keine bevorstehenden Events geplant.",
                         text_color=Config.TEXT_DARK, font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=10, pady=10, sticky="ew")
            return

        for i, event in enumerate(upcoming_events):
            event_frame = ctk.CTkFrame(self.upcoming_list_frame, fg_color="transparent")
            event_frame.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            event_frame.grid_columnconfigure(0, weight=1)

            date_obj = datetime.date.fromisoformat(event['date_key'])
            formatted_date = date_obj.strftime("%d.%m")

            ctk.CTkLabel(event_frame, text=event['title'],
                         font=ctk.CTkFont(size=14, weight="normal"),
                         text_color=Config.TEXT_DARK, anchor="w").grid(row=0, column=0, sticky="w")

            ctk.CTkLabel(event_frame, text=formatted_date,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=Config.SIDEBAR_BLUE, anchor="e").grid(row=0, column=1, sticky="e")

            ctk.CTkLabel(event_frame, text=event['streamerName'],
                         font=ctk.CTkFont(size=10),
                         text_color=Config.TEXT_DARK, anchor="w").grid(row=1, column=0, columnspan=2, sticky="w")

            ctk.CTkFrame(self.upcoming_list_frame, height=1, fg_color=Config.PANEL_ACCENT).grid(row=i+1, column=0, sticky="ew", padx=5)

    # --- DIALOG (Modal) for Event Creation ---
    def _show_event_dialog(self, date_key=None, existing_event=None):
        if not hasattr(self, 'event_dialog') or not self.event_dialog.winfo_exists():
            if date_key is None:
                date_key = datetime.date.today().isoformat()

            if existing_event and existing_event.get('date_key'):
                date_key = existing_event['date_key']

            self.event_dialog = EventDialog(self, date_key, existing_event)
            self.event_dialog.grab_set()
        else:
            self.event_dialog.lift()

    # --- MESSAGE BOX ---
    def show_message_box(self, message, type='info'):
        """Zeigt ein Popup IMMER im Vordergrund mit OK-Button."""
        popup = ctk.CTkToplevel(self)
        popup.title("Info")
        popup.geometry("350x130")
        popup.configure(fg_color=Config.BG_WHITE)

        # immer im Vordergrund
        popup.transient(self)   # an dieses Fenster binden
        popup.grab_set()        # Modales Fenster
        popup.lift()
        try:
            popup.attributes("-topmost", True)
            popup.after(200, lambda: popup.attributes("-topmost", False))
        except Exception:
            pass

        color_map = {
            'info': 'blue',
            'success': 'green',
            'warning': '#CC9900',
            'error': 'red'
        }
        color = color_map.get(type, 'blue')

        frame = ctk.CTkFrame(popup, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=15, pady=10)

        ctk.CTkLabel(
            frame,
            text=message,
            text_color=color,
            font=ctk.CTkFont(size=14, weight="bold"),
            wraplength=300
        ).pack(padx=10, pady=(5, 10))

        ctk.CTkButton(
            frame,
            text="OK",
            command=popup.destroy,
            fg_color=Config.SIDEBAR_BLUE,
            hover_color=Config.SIDEBAR_HOVER
        ).pack(pady=(0, 5))


# --- DIALOG CLASS FOR EDITING/ADDING EVENTS ---

class EventDialog(ctk.CTkToplevel):
    def __init__(self, master, date_key, existing_event=None):
        super().__init__(master)
        self.master = master
        self.old_date_key = date_key
        self.existing_event = existing_event
        self.is_editing = existing_event is not None

        date_obj = datetime.date.fromisoformat(date_key)
        date_display = date_obj.strftime("%A, %d. %B %Y")

        self.title("Event bearbeiten" if self.is_editing else "Event planen")

        self.geometry("450x650" if self.is_editing else "450x550")
        self.resizable(False, False)
        self.configure(fg_color=Config.BG_WHITE)
        self.columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text=f"Event für {date_display}",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=Config.TEXT_DARK, anchor="w").grid(row=0, column=0, sticky="w")

        ctk.CTkButton(header, text="X", command=self.destroy, width=30, height=30, corner_radius=15,
                      fg_color="transparent", hover_color=Config.PANEL_ACCENT, text_color="gray").grid(row=0, column=1, sticky="e")

        # Existing Events (only show if NEW event)
        current_row = 1
        if not self.is_editing:
            ctk.CTkLabel(self, text="Vorhandene Termine:", text_color=Config.SIDEBAR_BLUE,
                         font=ctk.CTkFont(size=14, weight="bold"),
                         anchor="w").grid(row=current_row, column=0, padx=20, pady=(10, 5), sticky="ew")
            current_row += 1

            events_list_frame = ctk.CTkScrollableFrame(self, fg_color=Config.PANEL_ACCENT, corner_radius=8, height=60)
            events_list_frame.grid(row=current_row, column=0, padx=20, pady=(0, 15), sticky="ew")
            events_list_frame.columnconfigure(0, weight=1)
            current_row += 1

            existing_events_day = master.data_manager.get_events_for_day(date_key)
            if existing_events_day:
                for i, event in enumerate(existing_events_day):
                    streamer_text = f" - {event['streamerName']}" if event.get('streamerName') else ""
                    ctk.CTkLabel(events_list_frame, text=f"{event['title']}{streamer_text}",
                                 text_color=Config.TEXT_DARK, anchor="w").grid(row=i, column=0, padx=10, pady=2, sticky="ew")
            else:
                ctk.CTkLabel(events_list_frame, text="Keine Events für diesen Tag.", text_color="gray", anchor="w").grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Title Input
        ctk.CTkLabel(self, text="Event-Titel:", text_color=Config.TEXT_DARK, font=ctk.CTkFont(size=14, weight="normal"), anchor="w").grid(row=current_row, column=0, padx=20, pady=(10, 5), sticky="ew")
        current_row += 1
        self.title_entry = ctk.CTkEntry(self, placeholder_text="Titel des Streams", corner_radius=8)
        self.title_entry.grid(row=current_row, column=0, padx=20, pady=(0, 15), sticky="ew")
        current_row += 1

        if self.is_editing:
            self.title_entry.insert(0, existing_event['title'])

            # Edit Date (only in edit mode)
            ctk.CTkLabel(self, text="Datum ändern (YYYY-MM-DD):", text_color=Config.TEXT_DARK, font=ctk.CTkFont(size=14, weight="normal"), anchor="w").grid(row=current_row, column=0, padx=20, pady=(0, 5), sticky="ew")
            current_row += 1
            self.date_entry = ctk.CTkEntry(self, placeholder_text="Datum", corner_radius=8)
            self.date_entry.grid(row=current_row, column=0, padx=20, pady=(0, 15), sticky="ew")
            self.date_entry.insert(0, date_key)
            current_row += 1

        # Streamer Dropdown
        ctk.CTkLabel(self, text="Zugeordneter Streamer:", text_color=Config.TEXT_DARK, font=ctk.CTkFont(size=14, weight="normal"), anchor="w").grid(row=current_row, column=0, padx=20, pady=(0, 5), sticky="ew")
        current_row += 1

        # NEU: Streamer aus der DB holen, nicht aus .streamers Dict
        streamers = self.master.data_manager.get_all_streamers()
        streamer_names = [s.get('name', 'Unbekannt') for s in streamers]

        if streamer_names:
            default_value = streamer_names[0]
        else:
            default_value = "Keine Streamer gefunden"

        self.streamer_var = ctk.StringVar(value=default_value)
        self.streamer_map_names_to_id = {s.get('name', 'Unbekannt'): s.get('id') for s in streamers}

        if self.is_editing and self.existing_event.get('streamerName') in streamer_names:
            self.streamer_var.set(self.existing_event['streamerName'])

        self.streamer_optionmenu = ctk.CTkOptionMenu(self, values=streamer_names or ["Keine Streamer gefunden"],
                                                     variable=self.streamer_var, corner_radius=8)
        self.streamer_optionmenu.grid(row=current_row, column=0, padx=20, pady=(0, 30), sticky="ew")
        current_row += 1

        # Save Button
        button_text = "Änderungen speichern" if self.is_editing else "Event speichern"
        ctk.CTkButton(self, text=button_text, command=self._save_event,
                      fg_color=Config.HEADER_ORANGE, hover_color=Config.HEADER_HOVER, corner_radius=10,
                      font=ctk.CTkFont(size=16, weight="bold")).grid(row=current_row, column=0, padx=20, pady=(10, 20), sticky="ew")
        current_row += 1

    def _save_event(self):
        title = self.title_entry.get().strip()
        streamer_name = self.streamer_var.get()
        streamer_id = self.streamer_map_names_to_id.get(streamer_name)

        new_date_key = self.old_date_key

        if self.is_editing:
            new_date_key = self.date_entry.get().strip()

            try:
                datetime.date.fromisoformat(new_date_key)
            except ValueError:
                self.master.show_message_box('Ungültiges Datumsformat (YYYY-MM-DD).', 'error')
                return

        if not title:
            self.master.show_message_box('Titel darf nicht leer sein.', 'warning')
            return
        if not streamer_id or streamer_name == "Keine Streamer gefunden":
            self.master.show_message_box('Bitte wähle einen gültigen Streamer aus.', 'warning')
            return

        if self.is_editing:
            success = self.master.data_manager.update_event(
                self.existing_event['id'],
                self.old_date_key,
                new_date_key,
                title,
                streamer_id,
                streamer_name
            )
            if success:
                self.master.show_message_box('Event erfolgreich aktualisiert!', 'success')
            else:
                self.master.show_message_box('Fehler beim Aktualisieren des Events.', 'error')
        else:
            self.master.data_manager.add_event(self.old_date_key, title, streamer_id, streamer_name)
            self.master.show_message_box('Event erfolgreich gespeichert!', 'success')

        self.master.update_all_events_list()
        self.master.update_calendar()
        self.master.update_upcoming_events()

        self.destroy()


# --- DIALOG CLASS FOR EDITING/ADDING STREAMERS ---

class StreamerDialog(ctk.CTkToplevel):
    def __init__(self, master, existing_streamer):
        super().__init__(master)
        self.master = master
        self.streamer = existing_streamer

        self.title(f"Streamer bearbeiten: {self.streamer['name']}")
        self.geometry("400x300")
        self.resizable(False, False)
        self.configure(fg_color=Config.BG_WHITE)
        self.columnconfigure(0, weight=1)
        self.grab_set()

        # Header
        ctk.CTkLabel(self, text=f"Streamer-Details ({self.streamer['id']})",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=Config.TEXT_DARK).grid(row=0, column=0, padx=20, pady=(15, 10))

        # Name
        ctk.CTkLabel(self, text="Name:", text_color=Config.TEXT_DARK, anchor="w").grid(row=1, column=0, padx=20, pady=(5, 0), sticky="ew")
        self.name_entry = ctk.CTkEntry(self, corner_radius=8)
        self.name_entry.insert(0, self.streamer['name'])
        self.name_entry.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Status
        ctk.CTkLabel(self, text="Status:", text_color=Config.TEXT_DARK, anchor="w").grid(row=3, column=0, padx=20, pady=(5, 0), sticky="ew")
        self.status_var = ctk.StringVar(value=self.streamer.get('status', 'Aktiv'))
        self.status_optionmenu = ctk.CTkOptionMenu(self, values=["Aktiv", "Pause"],
                                                   variable=self.status_var, corner_radius=8)
        self.status_optionmenu.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Save Button
        ctk.CTkButton(self, text="Speichern", command=self._save_streamer,
                      fg_color=Config.SIDEBAR_BLUE, hover_color=Config.SIDEBAR_HOVER, corner_radius=10,
                      font=ctk.CTkFont(size=16, weight="bold")).grid(row=5, column=0, padx=20, pady=(10, 20), sticky="ew")

    def _save_streamer(self):
        new_name = self.name_entry.get().strip()
        new_status = self.status_var.get()

        if not new_name:
            self.master.show_message_box('Name darf nicht leer sein.', 'warning')
            return

        success = self.master.data_manager.update_streamer(
            self.streamer['id'], new_name, new_status
        )

        if success:
            self.master.show_message_box(f"Streamer '{new_name}' aktualisiert.", 'success')

            # Update lists
            self.master.update_streamer_list(self.master.streamer_list_frame)
            self.master.update_calendar()
            self.master.update_upcoming_events()
            self.master.update_all_events_list()

        else:
            self.master.show_message_box('Fehler beim Speichern des Streamers.', 'error')

        self.destroy()


# --- Main Execution ---
if __name__ == "__main__":
    app = ManagerDashboard()
    app.mainloop()
