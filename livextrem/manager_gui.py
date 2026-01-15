# manager_gui.py
import customtkinter as ctk
import datetime
import calendar
import os
from PIL import Image

# ✅ Alles Wichtige (Config, Theme, DB, DataManager, Farben) kommt aus data_manager.py
from data_manager import DataManager, Config, STREAMER_COLOR_CHOICES


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

        self.main_title = ctk.CTkLabel(
            self.main_content_area,
            text=f"Manager-Dashboard: {view_name}",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=Config.TEXT_DARK,
            anchor="w"
        )
        self.main_title.grid(row=0, column=0, columnspan=3,
                             padx=10, pady=(10, 20), sticky="ew")

    def _toggle_theme(self):
        """Light/Dark-Mode umschalten."""
        current = ctk.get_appearance_mode().lower()  # "light" / "dark"

        if current == "light":
            ctk.set_appearance_mode("dark")
            if hasattr(self, "theme_toggle_button"):
                self.theme_toggle_button.configure(text="☀")
        else:
            ctk.set_appearance_mode("light")
            if hasattr(self, "theme_toggle_button"):
                self.theme_toggle_button.configure(text="🌙")

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
        dashboard_frame.grid_rowconfigure(0, weight=0)   # obere Zeile (Panels)
        dashboard_frame.grid_rowconfigure(1, weight=1)   # unten: Bevorstehende Termine füllt den Rest

        # oben: Event-Panel + Kalender
        self._create_event_planning_panel(dashboard_frame, 0, 0)
        self._create_calendar_panel(dashboard_frame, 0, 1, columnspan=2)

        # unten: Bevorstehende Termine über die ganze Breite
        self._create_upcoming_events_panel(dashboard_frame, 1, 0, columnspan=3)

        self.update_calendar()
        self.update_upcoming_events()

    # --- Termine View ---
    def _render_all_events_view(self):
        events_view_container = ctk.CTkFrame(
            self.main_content_area,
            fg_color=Config.PANEL_BG,
            corner_radius=12
        )
        events_view_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        events_view_container.grid_columnconfigure(0, weight=1)
        events_view_container.grid_rowconfigure(2, weight=1)

        # Titel
        ctk.CTkLabel(
            events_view_container,
            text="Übersicht aller geplanten Events",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=Config.TEXT_DARK
        ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # --- Suchfeld für Streamername ---
        search_frame = ctk.CTkFrame(events_view_container, fg_color="transparent")
        search_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)

        self.event_search_var = ctk.StringVar(value="")

        self.event_search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Streamer-Namen eingeben...",
            textvariable=self.event_search_var,
            corner_radius=8
        )
        self.event_search_entry.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="ew")

        ctk.CTkButton(
            search_frame,
            text="Suchen",
            command=self.update_all_events_list,
            fg_color=Config.SIDEBAR_BLUE,
            hover_color=Config.SIDEBAR_HOVER,
            width=80
        ).grid(row=0, column=1, padx=(0, 10), pady=0)

        ctk.CTkButton(
            search_frame,
            text="Alle",
            command=self._reset_event_search,
            fg_color="gray",
            hover_color="darkgray",
            width=60
        ).grid(row=0, column=2, pady=0)

        # Scroll-Liste
        self.all_events_list_frame = ctk.CTkScrollableFrame(
            events_view_container,
            fg_color=Config.BG_WHITE,
            corner_radius=10,
            label_text="Alle Events (Historisch und Zukünftig)"
        )
        self.all_events_list_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.all_events_list_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        self.all_events_list_frame.grid_columnconfigure(5, weight=0)

        self.update_all_events_list()

    def update_all_events_list(self):

        # Deutsche Wochentage Mapping
        de_weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag",
                       "Freitag", "Samstag", "Sonntag"]

        # HEUTIGES DATUM für Vergleich
        today = datetime.date.today()

        if not hasattr(self, 'all_events_list_frame') or not self.all_events_list_frame.winfo_exists():
            return

        # alte Einträge entfernen
        try:
            for widget in self.all_events_list_frame.winfo_children():
                widget.destroy()
        except ctk.TclError:
            return

        # --- Suchbegriff lesen (Streamername) ---
        search_term = ""
        if hasattr(self, "event_search_var"):
            value = self.event_search_var.get()
            if value is not None:
                search_term = value.strip().lower()

        # Events aus DB holen
        events = self.data_manager.get_all_events_sorted()

        # --- Falls Suchbegriff vorhanden ist, Events filtern ---
        if search_term != "":
            gefilterte_events = []
            for event in events:
                name = (event.get("streamerName", "") or "").lower()
                title = (event.get("title", "") or "").lower()

                if search_term in name or search_term in title:
                    gefilterte_events.append(event)

            events = gefilterte_events


        # Keine Events (oder nix gefunden)
        if not events:
            ctk.CTkLabel(
                self.all_events_list_frame,
                text="Keine Events in der Datenbank gefunden.",
                text_color=Config.TEXT_DARK,
                font=ctk.CTkFont(size=14)
            ).grid(row=0, column=0, padx=10, pady=10, sticky="ew", columnspan=6)
            return

        # Header
        header_row = 0
        ctk.CTkLabel(self.all_events_list_frame, text="Datum",
                     font=ctk.CTkFont(weight="bold"),
                     text_color=Config.SIDEBAR_BLUE).grid(row=header_row, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.all_events_list_frame, text="Wochentag",
                     font=ctk.CTkFont(weight="bold"),
                     text_color=Config.SIDEBAR_BLUE).grid(row=header_row, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.all_events_list_frame, text="Event-Titel",
                     font=ctk.CTkFont(weight="bold"),
                     text_color=Config.SIDEBAR_BLUE).grid(row=header_row, column=2, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.all_events_list_frame, text="Streamer",
                     font=ctk.CTkFont(weight="bold"),
                     text_color=Config.SIDEBAR_BLUE).grid(row=header_row, column=3, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.all_events_list_frame, text="Farbe",
                     font=ctk.CTkFont(weight="bold"),
                     text_color=Config.SIDEBAR_BLUE).grid(row=header_row, column=4, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(
            self.all_events_list_frame,
            text="Aktionen",
            font=ctk.CTkFont(weight="bold"),
            text_color=Config.SIDEBAR_BLUE
        ).grid(row=header_row, column=5, padx=10, pady=5, sticky="e")

        ctk.CTkFrame(
            self.all_events_list_frame,
            height=2,
            fg_color=Config.PANEL_ACCENT
        ).grid(row=header_row + 1, column=0, columnspan=6, sticky="ew", padx=5)

        # Zeilen füllen
        for i, event in enumerate(events):
            row = i + 2

            date_obj = datetime.date.fromisoformat(event['date_key'])
            formatted_date = date_obj.strftime("%d.%m.%Y")
            weekday_name = de_weekdays[date_obj.weekday()]

            # ✅ Prüfen, ob der Termin in der Vergangenheit liegt
            is_past = date_obj < today

            # Farben je nach Vergangenheit / Zukunft
            normal_text = Config.TEXT_DARK
            past_text = "gray60"

            normal_link = Config.SIDEBAR_BLUE
            past_link = "gray60"

            row_text_color = past_text if is_past else normal_text
            row_link_color = past_link if is_past else normal_link

            # Datum
            ctk.CTkLabel(
                self.all_events_list_frame,
                text=formatted_date,
                anchor="w",
                text_color=row_text_color
            ).grid(row=row, column=0, padx=10, pady=5, sticky="w")

            # Wochentag
            ctk.CTkLabel(
                self.all_events_list_frame,
                text=weekday_name,
                anchor="w",
                text_color=row_text_color
            ).grid(row=row, column=1, padx=10, pady=5, sticky="w")

            # Titel
            ctk.CTkLabel(
                self.all_events_list_frame,
                text=event['title'],
                anchor="w",
                text_color=row_text_color
            ).grid(row=row, column=2, padx=10, pady=5, sticky="w")

            # Streamer-Name (Link-Optik)
            ctk.CTkLabel(
                self.all_events_list_frame,
                text=event['streamerName'],
                anchor="w",
                text_color=row_link_color
            ).grid(row=row, column=3, padx=10, pady=5, sticky="w")

            # FARBPUNKT (Streamer-Farbe)
            color_hex = event.get("streamerColor") or Config.SIDEBAR_BLUE
            ctk.CTkLabel(
                self.all_events_list_frame,
                text="●",
                text_color=color_hex,
                font=ctk.CTkFont(size=26, weight="bold")
            ).grid(row=row, column=4, padx=10, pady=0, sticky="w")

            # Buttons
            action_frame = ctk.CTkFrame(self.all_events_list_frame, fg_color="transparent")
            action_frame.grid(row=row, column=5, padx=10, pady=5, sticky="e")

            ctk.CTkButton(
                action_frame,
                text="Bearbeiten",
                command=lambda e=event: self._show_edit_event_dialog(e),
                fg_color=Config.SIDEBAR_BLUE,
                hover_color=Config.SIDEBAR_HOVER,
                width=80,
                height=25,
                font=ctk.CTkFont(size=12)
            ).grid(row=0, column=0, padx=(0, 5))

            ctk.CTkButton(
                action_frame,
                text="Löschen",
                command=lambda e=event: self._confirm_delete_event(e),
                fg_color="red",
                hover_color="#A00000",
                width=80,
                height=25,
                font=ctk.CTkFont(size=12)
            ).grid(row=0, column=1)

            # Trennlinie
            ctk.CTkFrame(
                self.all_events_list_frame,
                height=1,
                fg_color=Config.PANEL_ACCENT
            ).grid(row=row + 1, column=0, columnspan=6, sticky="ew", padx=5)

    def _reset_event_search(self):
        """Suchfeld leeren und alle Events anzeigen."""
        if hasattr(self, "event_search_var"):
            self.event_search_var.set("")
        self.update_all_events_list()

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
            font=ctk.CTkFont(size=12, weight="bold"),
            wraplength=350,
            justify="center"
        ).pack(padx=20, pady=15)

        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=10)

        def delete_confirmed():
            success = self.data_manager.delete_event(event['id'], event.get('date_key'))
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

        streamer_frame.grid_rowconfigure(0, weight=1)
        streamer_frame.grid_rowconfigure(1, weight=0)
        streamer_frame.grid_columnconfigure(0, weight=1)

        # --- OBERER BEREICH: Streamer-Liste ---
        list_container = ctk.CTkFrame(streamer_frame, fg_color=Config.PANEL_ACCENT, corner_radius=12)
        list_container.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(1, weight=1)

        header_row = ctk.CTkFrame(list_container, fg_color="transparent")
        header_row.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_row.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_row,
            text="Alle Streamer verwalten",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=Config.TEXT_DARK
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            header_row,
            text="Archiv anzeigen",
            command=self._show_archived_streamers_window,
            fg_color="gray",
            hover_color="darkgray",
            corner_radius=10,
            width=140
        ).grid(row=0, column=1, sticky="e")

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

    def _add_new_streamer(self):
        name = self.new_streamer_entry.get().strip()

        if not name:
            self.show_message_box("Bitte einen Namen eingeben.", "warning")
            return

        try:
            default_status = "Aktiv"
            default_color = "#34C759"  # grün

            self.data_manager.add_streamer(name, status=default_status, color=default_color)

            self.show_message_box(f"Streamer '{name}' wurde hinzugefügt.", "success")

            self.new_streamer_entry.delete(0, "end")

            if hasattr(self, "streamer_list_frame") and self.streamer_list_frame.winfo_exists():
                self.update_streamer_list(self.streamer_list_frame)

            self.update_calendar()
            self.update_upcoming_events()
            self.update_all_events_list()

            self._update_event_dialog_streamer_options()

        except Exception as err:
            print("Fehler beim Streamer hinzufügen:", err)
            self.show_message_box(f"Fehler: {err}", "error")

    def update_streamer_list(self, list_frame):
        """Updates the streamer list in the streamer view."""

        for widget in list_frame.winfo_children():
            widget.destroy()

        streamers = self.data_manager.get_all_streamers()

        header_font = ctk.CTkFont(weight="bold")

        ctk.CTkLabel(
            list_frame, text="NAME",
            font=header_font,
            text_color=Config.SIDEBAR_BLUE,
            anchor="w"
        ).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(
            list_frame, text="STATUS",
            font=header_font,
            text_color=Config.SIDEBAR_BLUE,
            anchor="w"
        ).grid(row=0, column=1, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(
            list_frame, text="FARBE DES STREAMERS",
            font=header_font,
            text_color=Config.SIDEBAR_BLUE,
            anchor="center",
            justify="center"
        ).grid(row=0, column=2, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(
            list_frame, text="AKTIONEN",
            font=header_font,
            text_color=Config.SIDEBAR_BLUE,
            anchor="center",
            justify="center"
        ).grid(row=0, column=3, padx=10, pady=5, sticky="ew")

        list_frame.grid_columnconfigure(0, weight=4)
        list_frame.grid_columnconfigure(1, weight=1)
        list_frame.grid_columnconfigure(2, weight=1)
        list_frame.grid_columnconfigure(3, weight=2)

        if not streamers:
            ctk.CTkLabel(
                list_frame,
                text="Keine Streamer vorhanden.",
                text_color="gray"
            ).grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="w")
            return

        for i, streamer in enumerate(streamers):
            row = i + 2

            name = streamer.get("name", "Unbekannt")
            status = streamer.get("status", "Aktiv")
            color_hex = streamer.get("color_hex", "#34C759")

            ctk.CTkLabel(
                list_frame, text=name, anchor="w"
            ).grid(row=row, column=0, padx=10, pady=5, sticky="w")

            if status == "Aktiv":
                status_text = "AKTIV"
                status_color = "#34C759"
            elif status == "Pause":
                status_text = "PAUSE"
                status_color = "#FFD60A"
            else:
                status_text = status.upper()
                status_color = "#FF3B30"

            ctk.CTkLabel(
                list_frame,
                text=status_text,
                text_color=status_color,
                font=ctk.CTkFont(size=14, weight="bold")
            ).grid(row=row, column=1, padx=10, pady=5, sticky="w")

            ctk.CTkLabel(
                list_frame,
                text="●",
                text_color=color_hex,
                font=ctk.CTkFont(size=28)
            ).grid(row=row, column=2, padx=10, pady=0, sticky="n")

            action_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
            action_frame.grid(row=row, column=3, padx=10, pady=5, sticky="")

            ctk.CTkButton(
                action_frame,
                text="Bearbeiten",
                command=lambda s=streamer: self._show_streamer_edit_dialog(s),
                fg_color=Config.SIDEBAR_BLUE,
                hover_color=Config.SIDEBAR_HOVER,
                width=80, height=25,
                font=ctk.CTkFont(size=12)
            ).grid(row=0, column=0, padx=(0, 5))

            ctk.CTkButton(
                action_frame,
                text="Archivieren",
                command=lambda s=streamer: self._confirm_archive_streamer(s),
                fg_color="red",
                hover_color="#A00000",
                width=80, height=25,
                font=ctk.CTkFont(size=12)
            ).grid(row=0, column=1)

            ctk.CTkFrame(
                list_frame, height=1, fg_color=Config.PANEL_ACCENT
            ).grid(row=row + 1, column=0, columnspan=4, sticky="ew")

    def _show_streamer_edit_dialog(self, streamer):
        dialog = StreamerDialog(self, streamer)
        dialog.grab_set()

    def _confirm_archive_streamer(self, streamer):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Streamer archivieren")
        dialog.geometry("400x150")
        dialog.configure(fg_color=Config.BG_WHITE)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text=f"Sicher, dass du '{streamer['name']}' archivieren willst?",
            text_color=Config.TEXT_DARK,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(padx=20, pady=15)

        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=10)

        def archive_confirmed():
            success = self.data_manager.archive_streamer(streamer["id"])

            if success:
                self.show_message_box("Streamer wurde archiviert.", "success")
                self.update_streamer_list(self.streamer_list_frame)
                self.update_calendar()
                self.update_upcoming_events()
                self.update_all_events_list()
            else:
                self.show_message_box("Fehler beim Archivieren des Streamers.", "error")

            dialog.destroy()

        ctk.CTkButton(
            button_frame,
            text="Archivieren",
            command=archive_confirmed,
            fg_color="red",
            hover_color="#A00000",
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            button_frame,
            text="Abbrechen",
            command=dialog.destroy,
            fg_color="gray",
            hover_color="darkgray"
        ).grid(row=0, column=1, padx=10)

    def _show_archived_streamers_window(self):
        win = ctk.CTkToplevel(self)
        win.title("Archivierte Streamer")
        win.geometry("700x500")
        win.configure(fg_color=Config.BG_WHITE)
        win.grab_set()

        container = ctk.CTkFrame(win, fg_color=Config.PANEL_BG, corner_radius=12)
        container.pack(fill="both", expand=True, padx=15, pady=15)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            container,
            text="Archivierte Streamer",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=Config.TEXT_DARK
        ).grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        self.archived_list_frame = ctk.CTkScrollableFrame(
            container, fg_color=Config.BG_WHITE, corner_radius=10
        )
        self.archived_list_frame.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="nsew")
        self.archived_list_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.archived_list_frame.grid_columnconfigure(3, weight=0)

        self._refresh_archived_streamers_list()

    def _refresh_archived_streamers_list(self):
        if not hasattr(self, "archived_list_frame") or not self.archived_list_frame.winfo_exists():
            return

        for w in self.archived_list_frame.winfo_children():
            w.destroy()

        streamers = self.data_manager.get_archived_streamers()

        header_font = ctk.CTkFont(weight="bold")
        ctk.CTkLabel(self.archived_list_frame, text="NAME", font=header_font,
                     text_color=Config.SIDEBAR_BLUE).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.archived_list_frame, text="STATUS", font=header_font,
                     text_color=Config.SIDEBAR_BLUE).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.archived_list_frame, text="FARBE", font=header_font,
                     text_color=Config.SIDEBAR_BLUE).grid(row=0, column=2, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.archived_list_frame, text="AKTION", font=header_font,
                     text_color=Config.SIDEBAR_BLUE).grid(row=0, column=3, padx=10, pady=5, sticky="e")

        if not streamers:
            ctk.CTkLabel(self.archived_list_frame, text="Keine archivierten Streamer gefunden.",
                         text_color="gray").grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="w")
            return

        for i, s in enumerate(streamers):
            r = i + 1
            name = s.get("name", "Unbekannt")
            status = s.get("status", "Archiviert")
            color_hex = s.get("color_hex", "#34C759")

            ctk.CTkLabel(self.archived_list_frame, text=name, text_color=Config.TEXT_DARK)\
                .grid(row=r, column=0, padx=10, pady=6, sticky="w")

            ctk.CTkLabel(self.archived_list_frame, text=status.upper(), text_color="gray40",
                         font=ctk.CTkFont(weight="bold"))\
                .grid(row=r, column=1, padx=10, pady=6, sticky="w")

            ctk.CTkLabel(self.archived_list_frame, text="●", text_color=color_hex,
                         font=ctk.CTkFont(size=26, weight="bold"))\
                .grid(row=r, column=2, padx=10, pady=0, sticky="w")

            ctk.CTkButton(
                self.archived_list_frame,
                text="Reaktivieren",
                command=lambda sid=s["id"]: self._reactivate_streamer(sid),
                fg_color=Config.SIDEBAR_BLUE,
                hover_color=Config.SIDEBAR_HOVER,
                width=110,
                height=28
            ).grid(row=r, column=3, padx=10, pady=6, sticky="e")

    def _reactivate_streamer(self, streamer_id):
        success = self.data_manager.reactivate_streamer(streamer_id)
        if success:
            self.show_message_box("Streamer wurde reaktiviert (Status: Aktiv).", "success")

            if hasattr(self, "streamer_list_frame") and self.streamer_list_frame.winfo_exists():
                self.update_streamer_list(self.streamer_list_frame)

            self._refresh_archived_streamers_list()
            self.update_calendar()
            self.update_upcoming_events()
            self.update_all_events_list()
        else:
            self.show_message_box("Fehler beim Reaktivieren.", "error")

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
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

        # Logo laden
        logo_path = os.path.join(os.path.dirname(__file__), "images", "logo.png")
        try:
            self.logo_image = ctk.CTkImage(
                light_image=Image.open(logo_path),
                size=(180, 60)
            )
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, image=self.logo_image, text="")
        except Exception:
            self.logo_label = ctk.CTkLabel(
                self.sidebar_frame,
                text="LIVE XTREM",
                font=ctk.CTkFont(size=24, weight="bold", family="Inter"),
                text_color=Config.HEADER_ORANGE
            )

        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        # 🌙 Dark/Light Toggle Button
        self.theme_toggle_button = ctk.CTkButton(
            self.sidebar_frame,
            text="🌙",
            width=30,
            height=30,
            command=self._toggle_theme,
            fg_color="transparent",
            hover_color=Config.PANEL_ACCENT,
            text_color=Config.TEXT_DARK,
            corner_radius=15
        )
        self.theme_toggle_button.grid(row=0, column=1, padx=(0, 10), pady=(20, 0), sticky="ne")

        # Navigation
        nav_items = [
            ("Startseite", 2),
            ("Termine", 3),
            ("Kalender", 4),
            ("Streamer", 5),
        ]

        for text, row in nav_items:
            button = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                command=lambda t=text: self.show_view(t),
                fg_color="transparent",
                hover_color=Config.PANEL_ACCENT,
                text_color=Config.TEXT_DARK,
                anchor="w",
                compound="left",
                corner_radius=10
            )
            button.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
            self.nav_buttons[text] = button

        self.user_id_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Premium Edition",
            text_color="gray",
            font=ctk.CTkFont(size=10)
        )
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

        for button in day_buttons_list:
            button.destroy()
        day_buttons_list.clear()

        year, month = self.current_date.year, self.current_date.month
        months_de = [
            "Januar", "Februar", "März", "April", "Mai", "Juni",
            "Juli", "August", "September", "Oktober", "November", "Dezember"
        ]

        month_name = months_de[self.current_date.month - 1]
        month_label.configure(text=f"{month_name} {self.current_date.year}")


        cal = calendar.Calendar(firstweekday=calendar.MONDAY)
        month_days = cal.itermonthdays2(year, month)

        row = 1
        col = 0
        today_iso = datetime.date.today().isoformat()

        for day, weekday in month_days:
            if day == 0:
                col = (col + 1) % 7
                if col == 0:
                    row += 1
                continue

            date_obj = datetime.date(year, month, day)
            date_key = date_obj.isoformat()

            events_for_day = self.data_manager.get_events_for_day(date_key)
            has_events = bool(events_for_day)

            is_today = date_key == today_iso

            fg_color = Config.HEADER_ORANGE if is_today else Config.PANEL_BG
            text_color = Config.TEXT_LIGHT if is_today else Config.TEXT_DARK
            hover_color = Config.HEADER_HOVER if is_today else Config.PANEL_ACCENT

            border_width = 0
            border_color = None

            colors = []
            if has_events:
                for e in events_for_day:
                    c = e.get("streamerColor")
                    if c and c not in colors:
                        colors.append(c)

            has_multiple_colors = len(colors) > 1
            single_color = colors[0] if len(colors) == 1 else None

            if full_view:
                text = f"{day}"
                height = 70

                if has_events:
                    text += f"\n({len(events_for_day)} Events)"

                    if not is_today:
                        if has_multiple_colors:
                            fg_color = "white"
                            text_color = "#000000"
                            hover_color = "#F2F2F2"
                            border_width = 3
                            border_color = "#FFD854"
                        else:
                            if single_color:
                                fg_color = single_color
                                text_color = "#000000"

                day_button = ctk.CTkButton(
                    container,
                    text=text,
                    command=lambda k=date_key: self._show_event_dialog(k),
                    fg_color=fg_color,
                    hover_color=hover_color,
                    text_color=text_color,
                    height=height,
                    corner_radius=8,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    border_width=border_width,
                    border_color=border_color
                )
            else:
                text = f"{day}"

                btn_fg_color = fg_color
                btn_hover_color = hover_color
                btn_text_color = text_color
                btn_font = ctk.CTkFont(size=12)
                btn_border_width = 0
                btn_border_color = None

                if has_events and not is_today:
                    if has_multiple_colors:
                        btn_fg_color = "white"
                        btn_hover_color = "white"
                        btn_text_color = "#000000"
                        btn_font = ctk.CTkFont(size=12, weight="bold")
                        btn_border_width = 2
                        btn_border_color = "#FFD854"
                    else:
                        if single_color:
                            btn_fg_color = single_color
                            btn_hover_color = single_color
                            btn_text_color = "#000000"
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
                    font=btn_font,
                    border_width=btn_border_width,
                    border_color=btn_border_color
                )

            day_button.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            day_buttons_list.append(day_button)

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
        self.upcoming_frame = ctk.CTkFrame(
            parent_frame,
            fg_color=Config.PANEL_BG,
            corner_radius=12
        )
        self.upcoming_frame.grid(
            row=row,
            column=column,
            columnspan=columnspan,
            padx=10,
            pady=10,
            sticky="nsew"
        )

        self.upcoming_frame.grid_rowconfigure(1, weight=1)
        self.upcoming_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.upcoming_frame,
            text="Bevorstehende Termine",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=Config.TEXT_DARK,
            anchor="w"
        ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.upcoming_list_frame = ctk.CTkScrollableFrame(
            self.upcoming_frame,
            fg_color=Config.BG_WHITE,
            corner_radius=10
        )
        self.upcoming_list_frame.grid(
            row=1,
            column=0,
            padx=20,
            pady=(0, 20),
            sticky="nsew"
        )
        self.upcoming_list_frame.grid_columnconfigure(0, weight=1)

    def update_upcoming_events(self):

        if not hasattr(self, 'upcoming_list_frame') or not self.upcoming_list_frame.winfo_exists():
            return

        for widget in self.upcoming_list_frame.winfo_children():
            widget.destroy()

        upcoming_events = self.data_manager.get_upcoming_events()

        if not upcoming_events:
            ctk.CTkLabel(
                self.upcoming_list_frame,
                text="Keine bevorstehenden Events geplant.",
                text_color=Config.TEXT_DARK,
                font=ctk.CTkFont(size=12)
            ).grid(row=0, column=0, padx=10, pady=10, sticky="ew")
            return

        for i, event in enumerate(upcoming_events):
            event_frame = ctk.CTkFrame(
                self.upcoming_list_frame,
                fg_color="transparent"
            )
            event_frame.grid(row=i * 2, column=0, padx=10, pady=5, sticky="ew")
            event_frame.grid_columnconfigure(1, weight=1)

            date_obj = datetime.date.fromisoformat(event["date_key"])
            formatted_date = date_obj.strftime("%d.%m.%Y")

            color_hex = event.get("streamerColor") or Config.SIDEBAR_BLUE

            ctk.CTkLabel(
                event_frame,
                text="●",
                text_color=color_hex,
                font=ctk.CTkFont(size=26, weight="bold")
            ).grid(row=0, column=0, rowspan=2, padx=(5, 10), pady=0, sticky="n")

            ctk.CTkLabel(
                event_frame,
                text=event["title"],
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=Config.TEXT_DARK,
                anchor="w"
            ).grid(row=0, column=1, sticky="w")

            ctk.CTkLabel(
                event_frame,
                text=event["streamerName"],
                font=ctk.CTkFont(size=11),
                text_color="gray25",
                anchor="w"
            ).grid(row=1, column=1, pady=(0, 2), sticky="w")

            ctk.CTkLabel(
                event_frame,
                text=formatted_date,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=Config.SIDEBAR_BLUE,
                anchor="e"
            ).grid(row=0, column=2, rowspan=2, padx=(10, 5), sticky="e")

            ctk.CTkFrame(
                self.upcoming_list_frame,
                height=1,
                fg_color=Config.PANEL_ACCENT
            ).grid(row=i * 2 + 1, column=0, sticky="ew", padx=5)

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
        popup = ctk.CTkToplevel(self)
        popup.title("Info")
        popup.geometry("350x130")
        popup.configure(fg_color=Config.BG_WHITE)

        popup.transient(self)
        popup.grab_set()
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

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text=f"Event für {date_display}",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=Config.TEXT_DARK, anchor="w").grid(row=0, column=0, sticky="w")

        ctk.CTkButton(header, text="X", command=self.destroy, width=30, height=30, corner_radius=15,
                      fg_color="transparent", hover_color=Config.PANEL_ACCENT, text_color="gray").grid(row=0, column=1, sticky="e")

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

        ctk.CTkLabel(self, text="Event-Titel:", text_color=Config.TEXT_DARK, font=ctk.CTkFont(size=14, weight="normal"), anchor="w").grid(row=current_row, column=0, padx=20, pady=(10, 5), sticky="ew")
        current_row += 1
        self.title_entry = ctk.CTkEntry(self, placeholder_text="Titel des Streams", corner_radius=8)
        self.title_entry.grid(row=current_row, column=0, padx=20, pady=(0, 15), sticky="ew")
        current_row += 1

        if self.is_editing:
            self.title_entry.insert(0, existing_event['title'])

            ctk.CTkLabel(self, text="Datum ändern (YYYY-MM-DD):", text_color=Config.TEXT_DARK, font=ctk.CTkFont(size=14, weight="normal"), anchor="w").grid(row=current_row, column=0, padx=20, pady=(0, 5), sticky="ew")
            current_row += 1
            self.date_entry = ctk.CTkEntry(self, placeholder_text="Datum", corner_radius=8)
            self.date_entry.grid(row=current_row, column=0, padx=20, pady=(0, 15), sticky="ew")
            self.date_entry.insert(0, date_key)
            current_row += 1

        ctk.CTkLabel(self, text="Zugeordneter Streamer:", text_color=Config.TEXT_DARK, font=ctk.CTkFont(size=14, weight="normal"), anchor="w").grid(row=current_row, column=0, padx=20, pady=(0, 5), sticky="ew")
        current_row += 1

        streamers = self.master.data_manager.get_all_streamers()
        streamer_names = [s.get('name', 'Unbekannt') for s in streamers]

        default_value = streamer_names[0] if streamer_names else "Keine Streamer gefunden"

        self.streamer_var = ctk.StringVar(value=default_value)
        self.streamer_map_names_to_id = {s.get('name', 'Unbekannt'): s.get('id') for s in streamers}

        if self.is_editing and self.existing_event.get('streamerName') in streamer_names:
            self.streamer_var.set(self.existing_event['streamerName'])

        self.streamer_optionmenu = ctk.CTkOptionMenu(self, values=streamer_names or ["Keine Streamer gefunden"],
                                                     variable=self.streamer_var, corner_radius=8)
        self.streamer_optionmenu.grid(row=current_row, column=0, padx=20, pady=(0, 30), sticky="ew")
        current_row += 1

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
        self.geometry("400x380")
        self.resizable(False, False)
        self.configure(fg_color=Config.BG_WHITE)
        self.columnconfigure(0, weight=1)
        self.grab_set()

        ctk.CTkLabel(self, text=f"Streamer-Details ({self.streamer['id']})",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=Config.TEXT_DARK).grid(row=0, column=0, padx=20, pady=(15, 10))

        ctk.CTkLabel(self, text="Name:", text_color=Config.TEXT_DARK, anchor="w").grid(row=1, column=0, padx=20, pady=(5, 0), sticky="ew")
        self.name_entry = ctk.CTkEntry(self, corner_radius=8)
        self.name_entry.insert(0, self.streamer['name'])
        self.name_entry.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(self, text="Status:", text_color=Config.TEXT_DARK, anchor="w").grid(row=3, column=0, padx=20, pady=(5, 0), sticky="ew")
        self.status_var = ctk.StringVar(value=self.streamer.get('status', 'Aktiv'))
        self.status_optionmenu = ctk.CTkOptionMenu(
            self,
            values=["Aktiv", "Pause", "Archiviert"],
            variable=self.status_var,
            corner_radius=8
        )
        self.status_optionmenu.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(self, text="Farbe:", text_color=Config.TEXT_DARK, anchor="w").grid(row=5, column=0, padx=20, pady=(5, 0), sticky="ew")

        current_color_hex = self.streamer.get('color_hex', '#34C759')
        default_color_name = "Grün"
        for name, hex_value in STREAMER_COLOR_CHOICES.items():
            if hex_value == current_color_hex:
                default_color_name = name
                break

        self.color_var = ctk.StringVar(value=default_color_name)
        self.color_optionmenu = ctk.CTkOptionMenu(
            self,
            values=list(STREAMER_COLOR_CHOICES.keys()),
            variable=self.color_var,
            corner_radius=8
        )
        self.color_optionmenu.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="ew")

        ctk.CTkButton(self, text="Speichern", command=self._save_streamer,
                      fg_color=Config.SIDEBAR_BLUE, hover_color=Config.SIDEBAR_HOVER, corner_radius=10,
                      font=ctk.CTkFont(size=16, weight="bold")).grid(row=7, column=0, padx=20, pady=(10, 20), sticky="ew")

    def _save_streamer(self):
        new_name = self.name_entry.get().strip()
        new_status = self.status_var.get()
        color_name = self.color_var.get()
        new_color = STREAMER_COLOR_CHOICES.get(color_name, "#34C759")

        if not new_name:
            self.master.show_message_box('Name darf nicht leer sein.', 'warning')
            return

        success = self.master.data_manager.update_streamer(
            self.streamer['id'], new_name, new_status, new_color
        )

        if success:
            self.master.show_message_box(f"Streamer '{new_name}' aktualisiert.", 'success')

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
