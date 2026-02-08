import customtkinter as ctk
import os
import sys
import csv
import locale
import tkinter.messagebox as mb
from tkinter import filedialog
from pathlib import Path
from datetime import datetime
from PIL import Image

import mariadb
from config import Config
from security import hash_password
# Kalender-Widget Import (muss installiert sein: pip install tkcalendar)
try:
    from tkcalendar import DateEntry
    HAS_CALENDAR = True
except ImportError:
    HAS_CALENDAR = False
    print("Bitte 'pip install tkcalendar' installieren für die Kalender-Funktion.")

# PDF Export Check
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

# ---------- KONFIGURATION & PFADE ----------
BASE_DIR = Path(__file__).resolve().parent
IMG_PATH = BASE_DIR / "images" / "logo.png"
THEME_PATH = BASE_DIR / "style.json"

COLOR_PRIMARY = ["#1c31ba", "#4C72FF"] 
COLOR_HOVER   = ["#325882", "#B44E12"]
COLOR_CARD    = ["gray90", "#2b2b2b"]
COLOR_TEXT    = ["gray10", "gray90"]
COLOR_SUCCESS = "#008922"
COLOR_DANGER  = "#c92a2a"

# Versuche deutsches Locale für Datum zu setzen
try:
    locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'de_DE')
    except:
        pass

# ---------- MOCK DATEN ----------
class MockData:
    stats = {
        "followers": 12450,
        "new_followers_7d": 128,
        "subscribers": 456,
        "avg_viewers": 185
    }

    todos = [
        {"id": 1, "task": "Overlay Design überarbeiten", "done": False},
        {"id": 2, "task": "Sponsor Email beantworten", "done": True},
        {"id": 3, "task": "Discord Community Event planen", "done": False}
    ]

    finances = [
        {"id": 1, "date": "2025-11-01 10:00", "desc": "Twitch Payout", "amount": 1250.00, "type": "Einnahme"},
        {"id": 2, "date": "2025-11-03 14:30", "desc": "Neues Mikrofon", "amount": 149.99, "type": "Ausgabe"},
        {"id": 3, "date": "2025-11-05 18:15", "desc": "Spende (Ko-fi)", "amount": 25.00, "type": "Einnahme"},
        {"id": 4, "date": "2025-11-10 09:45", "desc": "Adobe Abo", "amount": 65.00, "type": "Ausgabe"},
    ]

    team = [
        {"name": "ModMaster99", "role": "Moderator", "since": "2024-01-15 12:00"},
        {"name": "ManagerLisa", "role": "Manager", "since": "2024-06-01 09:30"}
    ]

    planned_streams = [
        {"id": 101, "title": "Just Chatting + React", "game": "Just Chatting", "date": "2025-11-22 18:00", "score": 85},
        {"id": 102, "title": "Elden Ring DLC Hardcore", "game": "Elden Ring", "date": "2025-11-24 19:30", "score": 92},
        {"id": 103, "title": "Retro Sunday", "game": "Mario 64", "date": "2023-01-01 12:00", "score": 40}, # Altes Datum zum Testen
    ]

# ---------- HELPER ----------
def format_date_de(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        return dt.strftime("%d.%m.%Y %H:%M")
    except ValueError:
        return date_str

def get_next_stream():
    """Findet den chronologisch nächsten Stream in der Zukunft."""
    now = datetime.now()
    future_streams = []
    
    for s in MockData.planned_streams:
        try:
            dt = datetime.strptime(s["date"], "%Y-%m-%d %H:%M")
            if dt > now:
                future_streams.append((dt, s))
        except ValueError:
            continue
            
    # Sortieren nach Datum aufsteigend
    future_streams.sort(key=lambda x: x[0])
    
    if future_streams:
        return future_streams[0][1] # Gib das Stream-Objekt zurück
    return None

# ---------- HAUPTKLASSE ----------
class StreamerDashboard(ctk.CTk):
    def __init__(self, session=None):
        super().__init__()

        self.session = session
        self.streamer_id = None
        try:
            if self.session and getattr(self.session, "streamer", None) and self.session.streamer.get("streamer_id"):
                self.streamer_id = int(self.session.streamer.get("streamer_id"))
        except Exception:
            self.streamer_id = None

        self.title("LiveXtrem - Streamer Dashboard")
        self.geometry("1400x900")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._setup_sidebar()
        self._setup_content_area()
        self.show_view("Overview")

    # --- SIDEBAR ---
    # ---------- DB HELPERS ----------
    def _db(self):
        """Öffnet eine DB-Verbindung (Config via ENV oder config_local.json)."""
        Config.validate()
        return mariadb.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASS,
            database=Config.DB_NAME
        )

    def _load_team_from_db(self):
        """Lädt Moderator/Manager Nutzer aus der DB."""
        team = []
        db = self._db()
        try:
            cur = db.cursor(dictionary=True)
            if self.streamer_id:
                # Moderatoren, die diesem Streamer zugewiesen sind
                cur.execute(
                    """SELECT u.user_id, u.username, u.email, u.created_at
                        FROM streamer_moderator sm
                        JOIN moderator m ON m.moderator_id = sm.moderator_id
                        JOIN users u ON u.user_id = m.user_id
                        WHERE sm.streamer_id = ?
                        ORDER BY u.username""",
                    (self.streamer_id,)
                )
                mapped_mods = cur.fetchall() or []

                # Moderatoren ohne Zuordnung (Fallback)
                cur.execute(
                    """SELECT u.user_id, u.username, u.email, u.created_at
                        FROM users u
                        JOIN user_roles ur ON ur.user_id = u.user_id
                        WHERE ur.role_id = 2
                          AND NOT EXISTS (
                              SELECT 1
                              FROM moderator m
                              JOIN streamer_moderator sm ON sm.moderator_id = m.moderator_id
                              WHERE m.user_id = u.user_id
                          )
                        ORDER BY u.username"""
                )
                unmapped_mods = cur.fetchall() or []

                # Manager, die diesem Streamer zugewiesen sind
                cur.execute(
                    """SELECT u.user_id, u.username, u.email, u.created_at
                        FROM streamer_manager smg
                        JOIN users u ON u.user_id = smg.user_id
                        JOIN user_roles ur ON ur.user_id = u.user_id
                        WHERE smg.streamer_id = ?
                          AND ur.role_id = 3
                        ORDER BY u.username""",
                    (self.streamer_id,)
                )
                mapped_mgrs = cur.fetchall() or []

                # Manager ohne Zuordnung (Fallback)
                cur.execute(
                    """SELECT u.user_id, u.username, u.email, u.created_at
                        FROM users u
                        JOIN user_roles ur ON ur.user_id = u.user_id
                        WHERE ur.role_id = 3
                          AND NOT EXISTS (
                              SELECT 1 FROM streamer_manager smg WHERE smg.user_id = u.user_id
                          )
                        ORDER BY u.username"""
                )
                managers = (mapped_mgrs + (cur.fetchall() or []))
                for r in mapped_mods + unmapped_mods:
                    team.append({
                        "user_id": r["user_id"],
                        "name": r["username"],
                        "email": r["email"],
                        "role": "Moderator",
                        "role_id": 2,
                        "since": r["created_at"].strftime("%Y-%m-%d %H:%M") if hasattr(r["created_at"], "strftime") else str(r["created_at"])
                    })
                for r in managers:
                    team.append({
                        "user_id": r["user_id"],
                        "name": r["username"],
                        "email": r["email"],
                        "role": "Manager",
                        "role_id": 3,
                        "since": r["created_at"].strftime("%Y-%m-%d %H:%M") if hasattr(r["created_at"], "strftime") else str(r["created_at"])
                    })
            else:
                cur.execute(
                    """SELECT u.user_id, u.username, u.email, u.created_at, ur.role_id
                        FROM users u
                        JOIN user_roles ur ON ur.user_id = u.user_id
                        WHERE ur.role_id IN (2,3)
                        ORDER BY ur.role_id, u.username"""
                )
                rows = cur.fetchall() or []
                seen = set()
                for r in rows:
                    uid = r["user_id"]
                    if uid in seen:
                        continue
                    seen.add(uid)
                    role_id = int(r["role_id"])
                    team.append({
                        "user_id": uid,
                        "name": r["username"],
                        "email": r["email"],
                        "role": "Moderator" if role_id == 2 else "Manager",
                        "role_id": role_id,
                        "since": r["created_at"].strftime("%Y-%m-%d %H:%M") if hasattr(r["created_at"], "strftime") else str(r["created_at"])
                    })
        finally:
            try:
                db.close()
            except Exception:
                pass
        return team

    def _setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)

        if IMG_PATH.exists():
            try:
                logo_img = ctk.CTkImage(light_image=Image.open(IMG_PATH), dark_image=Image.open(IMG_PATH), size=(180, 60))
                self.logo_lbl = ctk.CTkLabel(self.sidebar, image=logo_img, text="")
            except:
                self.logo_lbl = ctk.CTkLabel(self.sidebar, text="LIVE XTREM", font=ctk.CTkFont(size=24, weight="bold"))
        else:
             self.logo_lbl = ctk.CTkLabel(self.sidebar, text="LIVE XTREM", font=ctk.CTkFont(size=24, weight="bold"))
        
        self.logo_lbl.grid(row=0, column=0, padx=20, pady=(20, 10))
        ctk.CTkLabel(self.sidebar, text="Streamer Edition", text_color="gray").grid(row=1, column=0, padx=20, pady=(0, 20))

        self.nav_buttons = {}
        nav_items = [
            ("🏠 Übersicht", "Overview"),
            ("📅 Content Planung", "Content"),
            ("💰 Finanzen (EÜR)", "Finance"),
            ("👥 Team / Rollen", "Team")
        ]

        for i, (label, view_name) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar, 
                text=label,
                command=lambda v=view_name: self.show_view(v),
                fg_color="transparent",
                text_color=COLOR_TEXT,
                hover_color=COLOR_CARD,
                anchor="w",
                height=40,
                font=ctk.CTkFont(size=14, weight="bold")
            )
            btn.grid(row=i+2, column=0, padx=10, pady=5, sticky="ew")
            self.nav_buttons[view_name] = btn

        self.btn_theme = ctk.CTkButton(self.sidebar, text="🌙 Modus wechseln", command=self._toggle_theme, fg_color=COLOR_PRIMARY)
        self.btn_theme.grid(row=7, column=0, padx=20, pady=20, sticky="ew")

    # --- CONTENT MANAGER ---
    def _setup_content_area(self):
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def show_view(self, view_name):
        self.focus() # Prevent Widget Focus Error
        
        # Frame leeren
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Navigation Highlight
        for name, btn in self.nav_buttons.items():
            if name == view_name:
                btn.configure(fg_color=COLOR_PRIMARY, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=COLOR_TEXT)

        # View laden
        if view_name == "Overview": self._view_overview()
        elif view_name == "Content": self._view_content()
        elif view_name == "Finance": self._view_finance()
        elif view_name == "Team": self._view_team()

    # --- VIEW: OVERVIEW ---
    def _view_overview(self):
        self._add_title("Dashboard Übersicht")

        stats_grid = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_grid.pack(fill="x", pady=10)
        stats_grid.columnconfigure((0,1,2), weight=1)

        self._create_stat_card(stats_grid, 0, "Aktuelle Follower", str(MockData.stats["followers"]), "+12 diese Woche", COLOR_PRIMARY)
        self._create_stat_card(stats_grid, 1, "Subscriber", str(MockData.stats["subscribers"]), "Level 2 Hype Train", "#D2601A")
        self._create_stat_card(stats_grid, 2, "Ø Zuschauer", str(MockData.stats["avg_viewers"]), "Stabil", COLOR_SUCCESS)

        bottom_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        bottom_frame.pack(fill="both", expand=True, pady=20)
        bottom_frame.columnconfigure((0, 1), weight=1)
        bottom_frame.rowconfigure(0, weight=1)

        # ToDo Liste
        todo_frame = ctk.CTkFrame(bottom_frame, fg_color=COLOR_CARD)
        todo_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ctk.CTkLabel(todo_frame, text="✅ Meine To-Do Liste", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15, padx=15, anchor="w")
        
        input_frame = ctk.CTkFrame(todo_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=15, pady=(0,10))
        
        self.todo_var = ctk.StringVar()
        def limit_char(*args):
            val = self.todo_var.get()
            if len(val) > 60: self.todo_var.set(val[:60])
        self.todo_var.trace_add("write", limit_char)

        self.todo_entry = ctk.CTkEntry(input_frame, textvariable=self.todo_var, placeholder_text="Neue Aufgabe (max 60 Zeichen)...")
        self.todo_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(input_frame, text="+", width=40, command=self._add_todo).pack(side="right")

        self.todo_list_scroll = ctk.CTkScrollableFrame(todo_frame, fg_color="transparent")
        self.todo_list_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        self._refresh_todo_list()

        # Nächster Stream Info
        next_frame = ctk.CTkFrame(bottom_frame, fg_color=COLOR_CARD)
        next_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        ctk.CTkLabel(next_frame, text="🚀 Nächster Stream", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15, padx=15, anchor="w")
        
        # LOGIK ÄNDERUNG: Nächsten Stream aus Zukunft holen
        nxt = get_next_stream()
        
        if nxt:
            de_date = format_date_de(nxt["date"])
            date_part = de_date.split(" ")[0]
            time_part = de_date.split(" ")[1] if " " in de_date else ""

            ctk.CTkLabel(next_frame, text=f"{date_part}\n{time_part} Uhr", font=ctk.CTkFont(size=32, weight="bold"), text_color=COLOR_PRIMARY[1]).pack(pady=(20, 5))
            ctk.CTkLabel(next_frame, text=nxt["title"], font=ctk.CTkFont(size=22)).pack(pady=5)
            ctk.CTkLabel(next_frame, text=f"Game: {nxt['game']}", font=ctk.CTkFont(size=16, slant="italic")).pack(pady=5)
            
            score_color = COLOR_SUCCESS if nxt["score"] > 80 else "#D2601A"
            ctk.CTkLabel(next_frame, text=f"📈 KI-Potenzial Score: {nxt['score']}/100", text_color=score_color, font=ctk.CTkFont(weight="bold")).pack(pady=20)
        else:
            ctk.CTkLabel(next_frame, text="Keine zukünftigen\nStreams geplant.", font=ctk.CTkFont(size=20), text_color="gray").pack(pady=50)

    # --- VIEW: CONTENT PLANNING ---
    def _view_content(self):
        self._add_title("Content & Stream Planung")
        
        grid = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        grid.columnconfigure(0, weight=2)
        grid.columnconfigure(1, weight=1)
        grid.rowconfigure(0, weight=1)

        # Liste
        plan_frame = ctk.CTkFrame(grid, fg_color=COLOR_CARD)
        plan_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(plan_frame, text="Geplante Streams", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15, padx=15, anchor="w")
        
        self.scroll_plan = ctk.CTkScrollableFrame(plan_frame, fg_color="transparent")
        self.scroll_plan.pack(fill="both", expand=True, padx=10, pady=10)
        self._refresh_content_list()

        ctk.CTkButton(plan_frame, text="+ Neuen Stream planen", fg_color=COLOR_PRIMARY, height=40, command=lambda: self._content_popup(None)).pack(fill="x", padx=15, pady=15)

        # KI Chat
        ai_frame = ctk.CTkFrame(grid, fg_color=COLOR_CARD)
        ai_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ctk.CTkLabel(ai_frame, text="🤖 KI Content Assistent", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15, padx=15, anchor="w")
        
        self.chat_box = ctk.CTkTextbox(ai_frame, fg_color="transparent", border_width=1)
        self.chat_box.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        self.chat_box.insert("0.0", "KI: Hallo! Welches Spiel möchtest du analysieren?\n")
        self.chat_box.configure(state="disabled")

        entry_frame = ctk.CTkFrame(ai_frame, fg_color="transparent")
        entry_frame.pack(fill="x", padx=15, pady=15)
        self.ai_entry = ctk.CTkEntry(entry_frame, placeholder_text="Frag die KI...")
        self.ai_entry.pack(side="left", fill="x", expand=True, padx=(0,5))
        ctk.CTkButton(entry_frame, text="Senden", width=60, command=self._send_ai_message).pack(side="right")

    # --- VIEW: FINANCE ---
    def _view_finance(self):
        self._add_title("Finanzen & EÜR")

        top_grid = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        top_grid.pack(fill="x", pady=10)
        top_grid.columnconfigure((0,1,2), weight=1)

        income = sum(x["amount"] for x in MockData.finances if x["type"] == "Einnahme")
        expenses = sum(x["amount"] for x in MockData.finances if x["type"] == "Ausgabe")
        profit = income - expenses

        self._create_stat_card(top_grid, 0, "Gesamteinnahmen", f"{income:.2f} €", "Dieser Monat", COLOR_SUCCESS)
        self._create_stat_card(top_grid, 1, "Gesamtausgaben", f"{expenses:.2f} €", "Dieser Monat", "#D2601A")
        
        color_profit = COLOR_SUCCESS if profit >= 0 else COLOR_DANGER
        self._create_stat_card(top_grid, 2, "Gewinn / Verlust", f"{profit:.2f} €", "Vor Steuern", color_profit)

        list_container = ctk.CTkFrame(self.content_frame, fg_color=COLOR_CARD)
        list_container.pack(fill="both", expand=True, pady=20)
        
        header = ctk.CTkFrame(list_container, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(header, text="Buchungen", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")
        ctk.CTkButton(btn_frame, text="Eintrag hinzufügen", command=self._finance_popup, fg_color=COLOR_PRIMARY, width=150).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="📄 PDF Export", command=self._export_pdf, fg_color="gray50", width=120).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="📊 CSV Export", command=self._export_csv, fg_color="gray50", width=120).pack(side="left", padx=5)

        self.scroll_fin = ctk.CTkScrollableFrame(list_container, fg_color="transparent")
        self.scroll_fin.pack(fill="both", expand=True, padx=10, pady=10)

        self._refresh_finance_list()

    # --- VIEW: TEAM ---
    def _view_team(self):
        self._add_title("Team & Rollenverwaltung")
        
        # ... (Rest wie vorher)
        list_frame = ctk.CTkFrame(self.content_frame, fg_color=COLOR_CARD)
        list_frame.pack(fill="both", expand=True)
        
        header = ctk.CTkFrame(list_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(header, text="Aktive Rollen", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")
        ctk.CTkButton(header, text="+ Neuen Nutzer anlegen", command=self._role_popup, fg_color=COLOR_PRIMARY).pack(side="right")

        self.scroll_team = ctk.CTkScrollableFrame(list_frame, fg_color="transparent")
        self.scroll_team.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self._refresh_team_list()

    # --- HELPERS / REFRESHERS ---
    def _add_title(self, text):
        ctk.CTkLabel(self.content_frame, text=text, font=ctk.CTkFont(size=28, weight="bold"), anchor="w").pack(fill="x", pady=(0, 20))

    def _create_stat_card(self, parent, col, title, value, subtext, color):
        card = ctk.CTkFrame(parent, fg_color=COLOR_CARD)
        card.grid(row=0, column=col, sticky="nsew", padx=10)
        ctk.CTkFrame(card, height=5, fg_color=color, corner_radius=0).pack(fill="x")
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(padx=20, pady=20, fill="both")
        ctk.CTkLabel(content, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color="gray").pack(anchor="w")
        ctk.CTkLabel(content, text=value, font=ctk.CTkFont(size=32, weight="bold")).pack(anchor="w", pady=(5, 0))
        ctk.CTkLabel(content, text=subtext, font=ctk.CTkFont(size=12), text_color=color).pack(anchor="w", pady=(5, 0))

    def _refresh_todo_list(self):
        for w in self.todo_list_scroll.winfo_children(): w.destroy()
        
        for item in MockData.todos:
            row = ctk.CTkFrame(self.todo_list_scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            var = ctk.BooleanVar(value=item["done"])
            chk = ctk.CTkCheckBox(row, text=item["task"], variable=var, 
                                  command=lambda i=item, v=var: self._toggle_todo(i, v),
                                  font=ctk.CTkFont(overstrike=item["done"]),
                                  text_color="gray50" if item["done"] else COLOR_TEXT)
            chk.pack(side="left", padx=5)
            
            btn_box = ctk.CTkFrame(row, fg_color="transparent")
            btn_box.pack(side="right")
            
            ctk.CTkButton(btn_box, text="✏️", width=30, fg_color="transparent", text_color="gray",
                         command=lambda i=item: self._edit_todo_popup(i)).pack(side="left", padx=2)
            ctk.CTkButton(btn_box, text="🗑", width=30, fg_color="transparent", text_color=COLOR_DANGER, 
                          command=lambda i=item: self._delete_todo(i)).pack(side="left", padx=2)

    def _refresh_content_list(self):
        for w in self.scroll_plan.winfo_children(): w.destroy()
        
        # Sortierte Anzeige (nur für die Liste, Originaldaten bleiben)
        sorted_streams = sorted(MockData.planned_streams, key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d %H:%M"))

        for stream in sorted_streams:
            card = ctk.CTkFrame(self.scroll_plan, fg_color="gray80" if ctk.get_appearance_mode()=="Light" else "gray20")
            card.pack(fill="x", pady=5)
            
            de_date = format_date_de(stream["date"])
            
            ctk.CTkLabel(card, text=de_date, width=150, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
            ctk.CTkLabel(card, text=f"{stream['title']} ({stream['game']})", anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkButton(card, text="Bearbeiten", width=80, fg_color="transparent", border_width=1, text_color=COLOR_TEXT,
                         command=lambda s=stream: self._content_popup(s)).pack(side="right", padx=10, pady=5)

    def _refresh_finance_list(self):
        # Frame leeren
        for w in self.scroll_fin.winfo_children(): w.destroy()
            
        head_row = ctk.CTkFrame(self.scroll_fin, fg_color="transparent")
        head_row.pack(fill="x", pady=5)
        ctk.CTkLabel(head_row, text="Datum", width=120, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(head_row, text="Beschreibung", width=250, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(head_row, text="Typ", width=80, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(head_row, text="Betrag", width=80, anchor="e", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(head_row, text="Aktion", width=80, anchor="e", font=ctk.CTkFont(weight="bold")).pack(side="right", padx=15)
        ctk.CTkFrame(self.scroll_fin, height=2, fg_color="gray50").pack(fill="x", pady=5)

        # Sortiere Finanzen nach Datum absteigend (neueste oben)
        sorted_fin = sorted(MockData.finances, key=lambda x: x["date"], reverse=True)

        for entry in sorted_fin:
            row = ctk.CTkFrame(self.scroll_fin, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            de_date = format_date_de(entry["date"])
            
            ctk.CTkLabel(row, text=de_date, width=120, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=entry["desc"], width=250, anchor="w").pack(side="left", padx=5)
            
            type_color = COLOR_SUCCESS if entry["type"] == "Einnahme" else "#D2601A"
            ctk.CTkLabel(row, text=entry["type"], width=80, text_color=type_color, anchor="w").pack(side="left", padx=5)
            
            ctk.CTkLabel(row, text=f"{entry['amount']:.2f} €", width=80, anchor="e").pack(side="left", padx=5)

            btn_box = ctk.CTkFrame(row, fg_color="transparent")
            btn_box.pack(side="right", padx=5)
            ctk.CTkButton(btn_box, text="✏️", width=30, fg_color="transparent", text_color="gray",
                         command=lambda e=entry: self._finance_popup(e)).pack(side="left")
            ctk.CTkButton(btn_box, text="🗑", width=30, fg_color="transparent", text_color=COLOR_DANGER,
                         command=lambda e=entry: self._delete_finance(e)).pack(side="left")


    def _refresh_team_list(self):
        for w in self.scroll_team.winfo_children():
            w.destroy()

        try:
            team = self._load_team_from_db()
        except Exception as e:
            mb.showerror("DB Fehler", f"Team konnte nicht geladen werden:\n{e}")
            team = []

        if not team:
            ctk.CTkLabel(self.scroll_team, text="Keine Team-Mitglieder gefunden.", text_color="gray").pack(pady=15)
            return

        for user in team:
            card = ctk.CTkFrame(
                self.scroll_team,
                fg_color="gray80" if ctk.get_appearance_mode() == "Light" else "gray25",
                corner_radius=10
            )
            card.pack(fill="x", pady=5)

            ctk.CTkLabel(card, text="👤", font=ctk.CTkFont(size=24)).pack(side="left", padx=15, pady=10)

            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="y", pady=5)

            ctk.CTkLabel(info, text=user.get("name", ""), font=ctk.CTkFont(size=16, weight="bold"), anchor="w").pack(fill="x")

            de_since = format_date_de(user.get("since", ""))
            ctk.CTkLabel(info, text=f"Seit: {de_since}", font=ctk.CTkFont(size=12), text_color="gray", anchor="w").pack(fill="x")

            badge_color = "#1c31ba" if user.get("role") == "Manager" else COLOR_SUCCESS

            btn_box = ctk.CTkFrame(card, fg_color="transparent")
            btn_box.pack(side="right", padx=10)

            ctk.CTkButton(btn_box, text=user.get("role", ""), fg_color=badge_color, width=100, hover=False).pack(side="top", pady=2)

            action_row = ctk.CTkFrame(btn_box, fg_color="transparent")
            action_row.pack(side="bottom", pady=2)

            # Passwort ändern
            ctk.CTkButton(
                action_row, text="🔑", width=30, fg_color="transparent", text_color=COLOR_PRIMARY[1],
                command=lambda u=user: self._change_password_popup(u)
            ).pack(side="left")

            # Rolle bearbeiten
            ctk.CTkButton(
                action_row, text="✏️", width=30, fg_color="transparent", text_color="gray",
                command=lambda u=user: self._role_popup(u)
            ).pack(side="left")

            # Löschen
            ctk.CTkButton(
                action_row, text="🗑", width=30, fg_color="transparent", text_color=COLOR_DANGER,
                command=lambda u=user: self._delete_team_member(u)
            ).pack(side="left")

    def _toggle_todo(self, item, var):
        item["done"] = var.get()
        self._refresh_todo_list()

    def _add_todo(self):
        txt = self.todo_var.get()
        if txt:
            MockData.todos.append({"id": len(MockData.todos)+1, "task": txt, "done": False})
            self.todo_var.set("")
            self._refresh_todo_list()

    def _delete_todo(self, item):
        if item in MockData.todos:
            MockData.todos.remove(item)
            self._refresh_todo_list()

    def _send_ai_message(self):
        msg = self.ai_entry.get()
        if msg:
            self.chat_box.configure(state="normal")
            self.chat_box.insert("end", f"Du: {msg}\n")
            self.chat_box.insert("end", "KI: Das ist eine interessante Frage! Die Daten zeigen, dass... [Simuliert]\n\n")
            self.chat_box.configure(state="disabled")
            self.chat_box.see("end")
            self.ai_entry.delete(0, "end")

    def _delete_finance(self, entry):
        if entry in MockData.finances:
            MockData.finances.remove(entry)
            self.show_view("Finance") # Refresh mit Clean


    def _delete_team_member(self, user):
        if not user or not user.get("user_id"):
            return

        # eigenen Benutzer nicht löschen
        try:
            if self.session and int(user["user_id"]) == int(self.session.user_id):
                mb.showwarning("Nicht möglich", "Du kannst deinen eigenen Benutzer nicht löschen.")
                return
        except Exception:
            pass

        if not mb.askyesno("Nutzer löschen", f"Soll der Nutzer '{user.get('name')}' wirklich gelöscht werden?"):
            return

        db = None
        try:
            db = self._db()
            cur = db.cursor()
            cur.execute("DELETE FROM users WHERE user_id=?", (int(user["user_id"]),))
            db.commit()
            self._refresh_team_list()
        except Exception as e:
            mb.showerror("Fehler", f"Löschen fehlgeschlagen:\n{e}")
        finally:
            try:
                if db:
                    db.close()
            except Exception:
                pass

    # ---------- TEAM / USER MANAGEMENT ----------
    def _create_user(self, username: str, email: str, password: str, role_id: int):
        username = (username or "").strip()
        email = (email or "").strip()

        if role_id not in (2, 3):
            raise RuntimeError("Es dürfen nur Moderator (2) oder Manager (3) angelegt werden.")

        if not username or not email or not password:
            raise RuntimeError("Bitte alle Felder ausfüllen.")

        if len(password) < 6:
            raise RuntimeError("Passwort ist zu kurz (mind. 6 Zeichen).")

        pw_hash = hash_password(password)

        db = self._db()
        try:
            cur = db.cursor()
            cur.execute("SELECT user_id FROM users WHERE username=? OR email=? LIMIT 1", (username, email))
            if cur.fetchone():
                raise RuntimeError("Benutzername oder E-Mail existiert bereits.")

            cur.execute(
                "INSERT INTO users (email, username, password_hash, created_at) VALUES (?,?,?, NOW())",
                (email, username, pw_hash)
            )
            user_id = cur.lastrowid

            # sicherstellen: genau 1 Rolle
            cur.execute("DELETE FROM user_roles WHERE user_id=?", (user_id,))
            cur.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?,?)", (user_id, role_id))

            # Moderator zusätzlich in moderator + streamer_moderator eintragen
            if role_id == 2:
                cur.execute("INSERT INTO moderator (name, rechte_level, user_id) VALUES (?, 1, ?)", (username, user_id))
                moderator_id = cur.lastrowid
                if self.streamer_id:
                    cur.execute("INSERT INTO streamer_moderator (streamer_id, moderator_id) VALUES (?,?)", (self.streamer_id, moderator_id))


            # Manager zusätzlich in streamer_manager eintragen
            if role_id == 3 and self.streamer_id:
                # avoid duplicates
                cur.execute("SELECT 1 FROM streamer_manager WHERE streamer_id=? AND user_id=? LIMIT 1", (self.streamer_id, user_id))
                if not cur.fetchone():
                    cur.execute("INSERT INTO streamer_manager (streamer_id, user_id) VALUES (?,?)", (self.streamer_id, user_id))
            db.commit()
            return user_id
        finally:
            try:
                db.close()
            except Exception:
                pass

    def _update_user_role(self, user_id: int, role_id: int):
        if role_id not in (2, 3):
            raise RuntimeError("Ungültige Rolle (nur Moderator/Manager).")

        db = self._db()
        try:
            cur = db.cursor()
            cur.execute("DELETE FROM user_roles WHERE user_id=?", (int(user_id),))
            cur.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?,?)", (int(user_id), int(role_id)))

            # falls jetzt Moderator: ensure moderator row + optional mapping
            if int(role_id) == 2:
                cur.execute("SELECT moderator_id FROM moderator WHERE user_id=? LIMIT 1", (int(user_id),))
                row = cur.fetchone()
                if row:
                    moderator_id = row[0]
                else:
                    cur.execute("SELECT username FROM users WHERE user_id=? LIMIT 1", (int(user_id),))
                    urow = cur.fetchone()
                    uname = urow[0] if urow else "Moderator"
                    cur.execute("INSERT INTO moderator (name, rechte_level, user_id) VALUES (?, 1, ?)", (uname, int(user_id)))
                    moderator_id = cur.lastrowid
                if self.streamer_id:
                    # avoid duplicates
                    cur.execute("SELECT 1 FROM streamer_moderator WHERE streamer_id=? AND moderator_id=? LIMIT 1", (self.streamer_id, moderator_id))
                    if not cur.fetchone():
                        cur.execute("INSERT INTO streamer_moderator (streamer_id, moderator_id) VALUES (?,?)", (self.streamer_id, moderator_id))

                # falls weg von Manager: Mapping entfernen (optional)
                cur.execute("DELETE FROM streamer_manager WHERE user_id=?", (int(user_id),))
            else:
                # falls jetzt Manager: ensure mapping
                if int(role_id) == 3 and self.streamer_id:
                    cur.execute("SELECT 1 FROM streamer_manager WHERE streamer_id=? AND user_id=? LIMIT 1", (self.streamer_id, int(user_id)))
                    if not cur.fetchone():
                        cur.execute("INSERT INTO streamer_manager (streamer_id, user_id) VALUES (?,?)", (self.streamer_id, int(user_id)))

                # falls weg von Moderator: Mapping entfernen (optional)
                cur.execute("SELECT moderator_id FROM moderator WHERE user_id=? LIMIT 1", (int(user_id),))
                row = cur.fetchone()
                if row:
                    cur.execute("DELETE FROM streamer_moderator WHERE moderator_id=?", (row[0],))

                # falls weg von Manager: Mapping entfernen (optional)
                if int(role_id) != 3:
                    cur.execute("DELETE FROM streamer_manager WHERE user_id=?", (int(user_id),))

            db.commit()
        finally:
            try:
                db.close()
            except Exception:
                pass

    def _set_user_password(self, user_id: int, new_password: str):
        new_password = (new_password or "").strip()
        if len(new_password) < 6:
            raise RuntimeError("Passwort ist zu kurz (mind. 6 Zeichen).")

        new_hash = hash_password(new_password)

        db = self._db()
        try:
            cur = db.cursor()
            cur.execute("UPDATE users SET password_hash=? WHERE user_id=?", (new_hash, int(user_id)))
            db.commit()
        finally:
            try:
                db.close()
            except Exception:
                pass

    def _toggle_theme(self):
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("Light")
            self.btn_theme.configure(text="☀️ Modus wechseln")
        else:
            ctk.set_appearance_mode("Dark")
            self.btn_theme.configure(text="🌙 Modus wechseln")
        self.show_view("Overview") 

    # --- POPUPS ---
    def _edit_todo_popup(self, item):
        d = ctk.CTkToplevel(self)
        d.geometry("300x150")
        d.title("ToDo Bearbeiten")
        d.transient(self)
        d.grab_set()
        
        var = ctk.StringVar(value=item["task"])
        def limit(*args):
             if len(var.get()) > 60: var.set(var.get()[:60])
        var.trace_add("write", limit)
        
        entry = ctk.CTkEntry(d, textvariable=var)
        entry.pack(pady=20, padx=20, fill="x")
        
        def save():
            item["task"] = var.get()
            self._refresh_todo_list()
            d.destroy()
            
        ctk.CTkButton(d, text="Speichern", command=save, fg_color=COLOR_PRIMARY).pack()

    def _content_popup(self, stream_data):
        d = ctk.CTkToplevel(self)
        title = "Neuen Stream planen" if stream_data is None else "Stream bearbeiten"
        d.title(title)
        d.geometry("400x500")
        d.transient(self)
        d.grab_set()

        ctk.CTkLabel(d, text=title, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        ctk.CTkLabel(d, text="Titel").pack(anchor="w", padx=20)
        e_title = ctk.CTkEntry(d)
        e_title.pack(fill="x", padx=20, pady=(0,10))

        ctk.CTkLabel(d, text="Game / Kategorie").pack(anchor="w", padx=20)
        e_game = ctk.CTkEntry(d)
        e_game.pack(fill="x", padx=20, pady=(0,10))

        # DATE PICKER
        ctk.CTkLabel(d, text="Datum & Uhrzeit").pack(anchor="w", padx=20)
        
        date_frame = ctk.CTkFrame(d, fg_color="transparent")
        date_frame.pack(fill="x", padx=20, pady=(0,10))
        
        if HAS_CALENDAR:
            cal = DateEntry(date_frame, width=12, background=COLOR_PRIMARY[0],
                            foreground='white', borderwidth=2, locale='de_DE', date_pattern='dd.mm.yyyy')
            cal.pack(side="left", padx=(0,10))
        else:
            # Fallback wenn tkcalendar nicht installiert ist
            cal = ctk.CTkEntry(date_frame, placeholder_text="DD.MM.YYYY")
            cal.pack(side="left", fill="x", expand=True)

        # Time Pickers
        hours = [f"{i:02d}" for i in range(24)]
        minutes = [f"{i:02d}" for i in range(0, 60, 15)] # 15 min schritte
        
        time_h = ctk.CTkComboBox(date_frame, values=hours, width=60)
        time_h.pack(side="left", padx=2)
        ctk.CTkLabel(date_frame, text=":").pack(side="left")
        time_m = ctk.CTkComboBox(date_frame, values=minutes, width=60)
        time_m.pack(side="left", padx=2)

        if stream_data:
            e_title.insert(0, stream_data["title"])
            e_game.insert(0, stream_data["game"])
            
            # Datum/Zeit parsing
            dt = datetime.strptime(stream_data["date"], "%Y-%m-%d %H:%M")
            if HAS_CALENDAR:
                cal.set_date(dt)
            else:
                cal.insert(0, dt.strftime("%d.%m.%Y"))
            
            time_h.set(dt.strftime("%H"))
            time_m.set(dt.strftime("%M"))
        else:
            time_h.set("18")
            time_m.set("00")

        def save():
            try:
                if HAS_CALENDAR:
                    d_obj = cal.get_date()
                    d_str = d_obj.strftime("%d.%m.%Y")
                else:
                    d_str = cal.get()
                
                t_str = f"{time_h.get()}:{time_m.get()}"
                
                dt = datetime.strptime(f"{d_str} {t_str}", "%d.%m.%Y %H:%M")
                iso_date = dt.strftime("%Y-%m-%d %H:%M")
                
                if stream_data:
                    stream_data["title"] = e_title.get()
                    stream_data["game"] = e_game.get()
                    stream_data["date"] = iso_date
                else:
                    MockData.planned_streams.append({
                        "id": len(MockData.planned_streams)+100,
                        "title": e_title.get(),
                        "game": e_game.get(),
                        "date": iso_date,
                        "score": 50 
                    })
                self._refresh_content_list()
                d.destroy()
            except ValueError:
                mb.showerror("Fehler", "Ungültiges Datum.")

        ctk.CTkButton(d, text="Speichern", command=save, fg_color=COLOR_PRIMARY).pack(pady=20)

    def _finance_popup(self, entry_data=None):
        d = ctk.CTkToplevel(self)
        t_text = "Eintrag bearbeiten" if entry_data else "Eintrag hinzufügen"
        d.title(t_text)
        d.geometry("400x450")
        d.transient(self)
        d.grab_set()
        
        ctk.CTkLabel(d, text=t_text, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        ctk.CTkLabel(d, text="Beschreibung").pack(anchor="w", padx=20)
        desc = ctk.CTkEntry(d)
        desc.pack(pady=(0,10), padx=20, fill="x")
        
        ctk.CTkLabel(d, text="Betrag (mit Komma)").pack(anchor="w", padx=20)
        amount = ctk.CTkEntry(d)
        amount.pack(pady=(0,10), padx=20, fill="x")
        
        ctk.CTkLabel(d, text="Typ").pack(anchor="w", padx=20)
        ftype = ctk.CTkComboBox(d, values=["Einnahme", "Ausgabe"], state="readonly")
        ftype.pack(pady=(0,10), padx=20, fill="x")
        ftype.set("Ausgabe")

        ctk.CTkLabel(d, text="Datum").pack(anchor="w", padx=20)
        
        if HAS_CALENDAR:
            cal = DateEntry(d, width=12, background=COLOR_PRIMARY[0],
                            foreground='white', borderwidth=2, locale='de_DE', date_pattern='dd.mm.yyyy')
            cal.pack(pady=(0,10), padx=20, anchor="w")
        else:
            cal = ctk.CTkEntry(d)
            cal.pack(pady=(0,10), padx=20, fill="x")
            cal.insert(0, datetime.now().strftime("%d.%m.%Y"))

        if entry_data:
            desc.insert(0, entry_data["desc"])
            amount.insert(0, str(entry_data["amount"]).replace(".", ","))
            ftype.set(entry_data["type"])
            if HAS_CALENDAR:
                dt_obj = datetime.strptime(entry_data["date"].split(" ")[0], "%Y-%m-%d")
                cal.set_date(dt_obj)
            else:
                cal.delete(0, "end")
                cal.insert(0, format_date_de(entry_data["date"]).split(" ")[0])

        def save():
            txt = desc.get()
            amt_str = amount.get()
            
            # AUTOMATIC ,00 FIX
            if amt_str and "," not in amt_str and "." not in amt_str:
                amt_str += ",00"

            if not txt or not amt_str:
                mb.showerror("Fehler", "Bitte Text UND Betrag eingeben.")
                return
            
            try:
                real_amt = float(amt_str.replace(",", "."))
                
                if HAS_CALENDAR:
                    d_obj = cal.get_date()
                    iso_date = d_obj.strftime("%Y-%m-%d 12:00") # Default Time
                else:
                    try:
                        dt = datetime.strptime(cal.get(), "%d.%m.%Y")
                        iso_date = dt.strftime("%Y-%m-%d 12:00")
                    except ValueError:
                         mb.showerror("Fehler", "Datum muss DD.MM.YYYY sein.")
                         return

                if entry_data:
                    entry_data["desc"] = txt
                    entry_data["amount"] = real_amt
                    entry_data["type"] = ftype.get()
                    entry_data["date"] = iso_date
                else:
                    MockData.finances.append({
                        "id": 999, 
                        "date": iso_date, 
                        "desc": txt, 
                        "amount": real_amt, 
                        "type": ftype.get()
                    })
                
                # BUG FIX: Hier wichtig show_view aufrufen, um das Content Frame zu clearen!
                self.show_view("Finance")
                d.destroy()
            except ValueError:
                mb.showerror("Fehler", "Ungültiger Betrag (Format: 00,00)")

        ctk.CTkButton(d, text="Speichern", command=save, fg_color=COLOR_PRIMARY).pack(pady=20)


    def _role_popup(self, user_data=None):
        d = ctk.CTkToplevel(self)
        is_edit = bool(user_data)
        t_text = "Nutzer bearbeiten" if is_edit else "Neuen Nutzer anlegen"
        d.title(t_text)
        d.geometry("420x520" if not is_edit else "420x360")
        d.transient(self)
        d.grab_set()

        ctk.CTkLabel(d, text=t_text, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)

        name = ctk.CTkEntry(d, placeholder_text="Benutzername (bei Moderator: Twitch Username)")
        name.pack(pady=10, padx=20, fill="x")

        email = ctk.CTkEntry(d, placeholder_text="E-Mail")
        email.pack(pady=10, padx=20, fill="x")

        role = ctk.CTkComboBox(d, values=["Moderator", "Manager"], state="readonly")
        role.pack(pady=10, padx=20, fill="x")
        role.set("Moderator")

        pw1 = None
        pw2 = None
        if not is_edit:
            pw1 = ctk.CTkEntry(d, placeholder_text="Passwort", show="*")
            pw1.pack(pady=10, padx=20, fill="x")

            pw2 = ctk.CTkEntry(d, placeholder_text="Passwort wiederholen", show="*")
            pw2.pack(pady=10, padx=20, fill="x")

            ctk.CTkLabel(d, text="Hinweis: Das Passwort wird gehasht in der DB gespeichert.", text_color="gray").pack(pady=(5, 0))

        if user_data:
            name.insert(0, user_data.get("name", ""))
            email.insert(0, user_data.get("email", ""))
            role.set(user_data.get("role", "Moderator"))
            name.configure(state="disabled")  # Username nicht ändern

        def save():
            try:
                selected = role.get()
                role_id = 2 if selected == "Moderator" else 3

                if is_edit:
                    self._update_user_role(int(user_data["user_id"]), role_id)
                else:
                    u = name.get().strip()
                    em = email.get().strip()
                    p1 = (pw1.get() if pw1 else "").strip()
                    p2 = (pw2.get() if pw2 else "").strip()
                    if p1 != p2:
                        raise RuntimeError("Passwörter stimmen nicht überein.")
                    self._create_user(u, em, p1, role_id)

                self._refresh_team_list()
                d.destroy()
            except Exception as e:
                mb.showerror("Fehler", str(e))

        ctk.CTkButton(d, text="Speichern", command=save, fg_color=COLOR_PRIMARY).pack(pady=20)


    def _change_password_popup(self, user_data):
        if not user_data or not user_data.get("user_id"):
            return

        d = ctk.CTkToplevel(self)
        d.title("Passwort ändern")
        d.geometry("380x260")
        d.transient(self)
        d.grab_set()

        ctk.CTkLabel(d, text=f"Passwort ändern: {user_data.get('name','')}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))

        pw1 = ctk.CTkEntry(d, placeholder_text="Neues Passwort", show="*")
        pw1.pack(pady=10, padx=20, fill="x")

        pw2 = ctk.CTkEntry(d, placeholder_text="Passwort wiederholen", show="*")
        pw2.pack(pady=10, padx=20, fill="x")

        def save_pw():
            try:
                p1 = pw1.get().strip()
                p2 = pw2.get().strip()
                if p1 != p2:
                    raise RuntimeError("Passwörter stimmen nicht überein.")
                self._set_user_password(int(user_data["user_id"]), p1)
                mb.showinfo("OK", "Passwort wurde gespeichert (gehasht).")
                d.destroy()
            except Exception as e:
                mb.showerror("Fehler", str(e))

        ctk.CTkButton(d, text="Speichern", command=save_pw, fg_color=COLOR_PRIMARY).pack(pady=20)

    def _export_csv(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if filename:
            try:
                with open(filename, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f, delimiter=';')
                    writer.writerow(["Datum", "Beschreibung", "Typ", "Betrag"])
                    for row in MockData.finances:
                         writer.writerow([
                             format_date_de(row["date"]),
                             row["desc"],
                             row["type"],
                             f"{row['amount']:.2f}".replace(".", ",")
                         ])
                mb.showinfo("Export", f"CSV erfolgreich gespeichert:\n{filename}")
            except Exception as e:
                mb.showerror("Fehler", str(e))

    def _export_pdf(self):
        if not HAS_REPORTLAB:
            mb.showerror("Fehler", "Bibliothek 'reportlab' fehlt.\nBitte 'pip install reportlab' ausführen.")
            return

        filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if filename:
            try:
                c = canvas.Canvas(filename, pagesize=A4)
                c.setTitle("EÜR Export")
                
                c.setFont("Helvetica-Bold", 16)
                c.drawString(50, 800, "Einnahmenüberschussrechnung (EÜR)")
                
                c.setFont("Helvetica", 10)
                y = 750
                c.drawString(50, y, "Datum")
                c.drawString(150, y, "Beschreibung")
                c.drawString(400, y, "Typ")
                c.drawString(500, y, "Betrag")
                y -= 20
                c.line(50, y+15, 550, y+15)

                total = 0
                for row in MockData.finances:
                    if y < 50:
                        c.showPage()
                        y = 800
                    
                    val = row['amount']
                    if row['type'] == "Ausgabe": val = -val
                    total += val
                    
                    c.drawString(50, y, format_date_de(row["date"]).split(" ")[0])
                    c.drawString(150, y, row["desc"][:40])
                    c.drawString(400, y, row["type"])
                    c.drawRightString(550, y, f"{row['amount']:.2f} €")
                    y -= 20
                
                c.line(50, y+10, 550, y+10)
                y -= 20
                c.setFont("Helvetica-Bold", 12)
                c.drawString(400, y, "Gewinn/Verlust:")
                color = (0, 0.5, 0) if total >= 0 else (0.8, 0, 0)
                c.setFillColorRGB(*color)
                c.drawRightString(550, y, f"{total:.2f} €")
                
                c.save()
                mb.showinfo("Export", f"PDF erfolgreich erstellt:\n{filename}")
                
                if sys.platform == "win32": os.startfile(filename)
                elif sys.platform == "darwin": os.system(f"open '{filename}'")
                else: os.system(f"xdg-open '{filename}'")

            except Exception as e:
                mb.showerror("Fehler", f"PDF Fehler: {str(e)}")


if __name__ == "__main__":
    app = StreamerDashboard()
    app.mainloop()