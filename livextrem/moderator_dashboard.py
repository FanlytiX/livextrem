import os
from pathlib import Path
import customtkinter as ctk
from PIL import Image
import tkinter.messagebox as mb
from datetime import datetime
from database_connection import DatabaseManager
from database_queries import ModeratorQueries

# ---------- Pfade robust ermitteln ----------
BASE_DIR = Path(__file__).resolve().parent
IMG_PATH = BASE_DIR / "images" / "logo.png"
THEME_PATH = BASE_DIR / "style.json"

# ---------- Appearance / Theme ----------
ctk.set_appearance_mode("dark")

# Theme laden
if THEME_PATH.exists():
    try:
        ctk.set_default_color_theme(str(THEME_PATH))
    except Exception as e:
        mb.showwarning("Theme-Fehler", f"style.json konnte nicht geladen werden:\n{e}\n=> Fallback auf 'blue'")
        ctk.set_default_color_theme("blue")
else:
    ctk.set_default_color_theme("blue")

# ---------- Globale Variablen ----------
db = None
mod_queries = None
current_moderator_id = 1  # Angemeldeter Moderator (Lisa)

# ---------- Hauptfenster ----------
app = ctk.CTk()
app.geometry("1400x800")
app.title("LiveXtrem - Moderator Dashboard")

app.grid_columnconfigure(1, weight=1)
app.grid_rowconfigure(0, weight=1)

# ---------- Datenbank initialisieren ----------
def init_database():
    global db, mod_queries
    try:
        db = DatabaseManager()
        db.connection()
        mod_queries = ModeratorQueries(db)
        # Abgelaufene Aktionen bereinigen
        mod_queries.cleanup_expired_actions()
        mb.showinfo("Hinweis", "Testdaten geladen!\nChat-Nachrichten und Moderationsaktionen\nwerden lokal gespeichert.")
        return True
    except Exception as e:
        mb.showerror("Datenbankfehler", f"Verbindung fehlgeschlagen:\n{e}")
        return False

# ---------- Sidebar ----------
sidebar_container = ctk.CTkFrame(app, fg_color="transparent")
sidebar_container.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)

sidebar = ctk.CTkFrame(sidebar_container, width=220, corner_radius=10)
sidebar.pack(fill="both", expand=True, padx=5, pady=5)
sidebar.grid_propagate(False)

# Logo
if not IMG_PATH.exists():
    logo = ctk.CTkLabel(sidebar, text="LIVE XTREM", font=("Arial", 20, "bold"))
    logo.pack(pady=(20, 30))
else:
    logo_img = ctk.CTkImage(
        light_image=Image.open(IMG_PATH),
        dark_image=Image.open(IMG_PATH),
        size=(200, 69)
    )
    logo = ctk.CTkLabel(sidebar, image=logo_img, text="")
    logo.pack(pady=(20, 30))

# Moderator Info
mod_info_frame = ctk.CTkFrame(sidebar, fg_color="#CA6931", corner_radius=8)
mod_info_frame.pack(pady=(0, 20), padx=10, fill="x")
ctk.CTkLabel(mod_info_frame, text="👤 Moderator", font=("Arial", 12, "bold")).pack(pady=(8, 2))
ctk.CTkLabel(mod_info_frame, text="Lisa", font=("Arial", 14)).pack(pady=(0, 8))

# Buttons
NORMAL_COLOR = "#1f538d"
HOVER_COLOR = "#2a5f9f"

class HoverButton(ctk.CTkButton):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.default_fg = NORMAL_COLOR
        self.hover_fg = HOVER_COLOR
        self.configure(fg_color=self.default_fg, hover_color=self.hover_fg)

btn_dashboard = HoverButton(sidebar, text="📊  Dashboard", width=180, corner_radius=6)
btn_chat = HoverButton(sidebar, text="💬  Chat Monitor", width=180, corner_radius=6)
btn_actions = HoverButton(sidebar, text="⚡  Aktionen", width=180, corner_radius=6)
btn_history = HoverButton(sidebar, text="📜  Historie", width=180, corner_radius=6)
btn_refresh = HoverButton(sidebar, text="🔄  Aktualisieren", width=180, corner_radius=6)

for b in (btn_dashboard, btn_chat, btn_actions, btn_history, btn_refresh):
    b.pack(pady=6, padx=10, fill="x")

# ---------- Content Area ----------
content = ctk.CTkFrame(app, corner_radius=10)
content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

# ---------- Dashboard View ----------
def show_dashboard():
    clear_content()
    
    # Header
    header_frame = ctk.CTkFrame(content, fg_color="transparent")
    header_frame.pack(fill="x", pady=20, padx=20)
    
    ctk.CTkLabel(header_frame, text="Moderator Dashboard", 
                font=("Arial", 24, "bold")).pack(side="left")
    
    # Info Badge
    info_badge = ctk.CTkFrame(header_frame, fg_color="#CA6931", corner_radius=6)
    info_badge.pack(side="right")
    ctk.CTkLabel(info_badge, text="💾 Testdaten-Modus", 
                font=("Arial", 11)).pack(padx=12, pady=6)
    
    # Stats Frame
    stats_frame = ctk.CTkFrame(content, fg_color="transparent")
    stats_frame.pack(fill="x", padx=20, pady=10)
    stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
    
    # Statistiken laden
    stats = mod_queries.get_moderator_stats()
    if stats and "data" in stats and stats["data"]:
        data = stats["data"][0]
        aktive = data[0] if len(data) > 0 else 0
        geloescht = data[1] if len(data) > 1 else 0
        gebannt = data[2] if len(data) > 2 else 0
        gemutet = data[3] if len(data) > 3 else 0
    else:
        aktive = geloescht = gebannt = gemutet = 0
    
    # Stat Boxen
    def create_stat_box(parent, col, title, value, icon):
        box = ctk.CTkFrame(parent, fg_color="#CA6931", corner_radius=12)
        box.grid(row=0, column=col, sticky="nsew", padx=8, pady=5)
        ctk.CTkLabel(box, text=f"{icon} {title}", 
                    font=("Arial", 14, "bold")).pack(pady=(12, 5))
        ctk.CTkLabel(box, text=str(value), 
                    font=("Arial", 28, "bold")).pack(pady=(0, 12))
    
    create_stat_box(stats_frame, 0, "Aktive Fälle", aktive, "⚡")
    create_stat_box(stats_frame, 1, "Gelöschte Nachrichten", geloescht, "🗑️")
    create_stat_box(stats_frame, 2, "Gebannte User", gebannt, "🚫")
    create_stat_box(stats_frame, 3, "Gemutete User", gemutet, "🔇")
    
    # Aktive Moderationsfälle
    aktionen_frame = ctk.CTkFrame(content, fg_color="#1c1c1c", corner_radius=10)
    aktionen_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    ctk.CTkLabel(aktionen_frame, text="🔴 Aktive Moderationsfälle", 
                font=("Arial", 18, "bold")).pack(pady=15)
    
    # Scrollable Frame für Aktionen
    scroll_frame = ctk.CTkScrollableFrame(aktionen_frame, fg_color="transparent")
    scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    aktionen = mod_queries.get_active_moderation_actions()
    if aktionen and "data" in aktionen and aktionen["data"]:
        for aktion in aktionen["data"]:
            aktion_id, typ, grund, dauer, timestamp, ablauf, user, mod_name = aktion
            
            action_box = ctk.CTkFrame(scroll_frame, fg_color="#2a2a2a", corner_radius=8)
            action_box.pack(fill="x", pady=5, padx=5)
            
            info_text = f"🎯 {typ.upper()} | User: {user} | Von: {mod_name}"
            if dauer:
                info_text += f" | Dauer: {dauer}min"
            if grund:
                info_text += f"\n💬 Grund: {grund}"
            
            ctk.CTkLabel(action_box, text=info_text, 
                        font=("Arial", 12), anchor="w").pack(pady=10, padx=10, fill="x")
    else:
        ctk.CTkLabel(scroll_frame, text="✅ Keine aktiven Moderationsfälle", 
                    font=("Arial", 14), text_color="green").pack(pady=20)

# ---------- Chat Monitor View ----------
def show_chat_monitor():
    clear_content()
    
    # Header mit Button
    header_frame = ctk.CTkFrame(content, fg_color="transparent")
    header_frame.pack(fill="x", pady=20, padx=20)
    
    ctk.CTkLabel(header_frame, text="💬 Live Chat Monitor", 
                font=("Arial", 24, "bold")).pack(side="left")
    
    ctk.CTkButton(header_frame, text="➕ Test-Nachricht", 
                 command=add_test_message_dialog, width=150, height=35).pack(side="right")
    
    # Haupt-Container
    main_container = ctk.CTkFrame(content, fg_color="transparent")
    main_container.pack(fill="both", expand=True, padx=20, pady=10)
    main_container.grid_columnconfigure(0, weight=2)
    main_container.grid_columnconfigure(1, weight=1)
    main_container.grid_rowconfigure(0, weight=1)
    
    # Chat Nachrichten (links)
    chat_frame = ctk.CTkFrame(main_container, fg_color="#1c1c1c", corner_radius=10)
    chat_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    
    ctk.CTkLabel(chat_frame, text="📨 Chat Nachrichten", 
                font=("Arial", 16, "bold")).pack(pady=10)
    
    chat_scroll = ctk.CTkScrollableFrame(chat_frame, fg_color="transparent")
    chat_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    messages = mod_queries.get_all_messages(limit=50, include_deleted=False)
    if messages and "data" in messages and messages["data"]:
        for msg in reversed(messages["data"]):
            msg_id, user_id, username, text, timestamp = msg
            
            msg_box = ctk.CTkFrame(chat_scroll, fg_color="#2a2a2a", corner_radius=8)
            msg_box.pack(fill="x", pady=3, padx=5)
            
            # Header mit Username und Zeit
            header_frame = ctk.CTkFrame(msg_box, fg_color="transparent")
            header_frame.pack(fill="x", padx=10, pady=(8, 2))
            
            ctk.CTkLabel(header_frame, text=f"👤 {username}", 
                        font=("Arial", 11, "bold"), anchor="w").pack(side="left")
            ctk.CTkLabel(header_frame, text=timestamp.strftime("%H:%M:%S") if hasattr(timestamp, 'strftime') else str(timestamp), 
                        font=("Arial", 9), text_color="gray", anchor="e").pack(side="right")
            
            # Nachricht
            ctk.CTkLabel(msg_box, text=text, font=("Arial", 12), 
                        anchor="w", wraplength=600).pack(padx=10, pady=(0, 5), fill="x")
            
            # Löschen Button
            def delete_msg(msg_id=msg_id, username=username):
                if mb.askyesno("Nachricht löschen", 
                             f"Nachricht von '{username}' wirklich löschen?"):
                    mod_queries.delete_message(msg_id, current_moderator_id)
                    show_chat_monitor()  # Refresh
            
            btn_delete = ctk.CTkButton(msg_box, text="🗑️ Löschen", width=80, height=25,
                                      font=("Arial", 10), fg_color="#dc3545",
                                      hover_color="#c82333", command=delete_msg)
            btn_delete.pack(pady=(0, 8), padx=10, anchor="e")
    
    # Gelöschte Nachrichten (rechts)
    deleted_frame = ctk.CTkFrame(main_container, fg_color="#1c1c1c", corner_radius=10)
    deleted_frame.grid(row=0, column=1, sticky="nsew")
    
    ctk.CTkLabel(deleted_frame, text="🗑️ Gelöscht", 
                font=("Arial", 16, "bold")).pack(pady=10)
    
    deleted_scroll = ctk.CTkScrollableFrame(deleted_frame, fg_color="transparent")
    deleted_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    deleted = mod_queries.get_deleted_messages(limit=30)
    if deleted and "data" in deleted and deleted["data"]:
        for msg in deleted["data"]:
            msg_id, username, text, timestamp, deleted_at, mod_name = msg
            
            del_box = ctk.CTkFrame(deleted_scroll, fg_color="#3a2020", corner_radius=8)
            del_box.pack(fill="x", pady=3, padx=5)
            
            info = f"👤 {username}\n💬 {text[:50]}..."
            if mod_name:
                info += f"\n🛡️ Von: {mod_name}"
            
            ctk.CTkLabel(del_box, text=info, font=("Arial", 10), 
                        anchor="w", justify="left").pack(pady=8, padx=8, fill="x")

# ---------- Aktionen View ----------
def show_actions():
    clear_content()
    
    header = ctk.CTkLabel(content, text="⚡ Moderationsaktionen", 
                          font=("Arial", 24, "bold"))
    header.pack(pady=20)
    
    # Form Frame
    form_frame = ctk.CTkFrame(content, fg_color="#1c1c1c", corner_radius=10)
    form_frame.pack(fill="x", padx=20, pady=10)
    
    # Inner Frame für besseres Layout
    inner_form = ctk.CTkFrame(form_frame, fg_color="transparent")
    inner_form.pack(padx=30, pady=20)
    
    # User Selection
    ctk.CTkLabel(inner_form, text="User auswählen:", 
                font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 10))
    
    users = mod_queries.get_all_users()
    user_names = [u[1] for u in users["data"]] if users and "data" in users else []
    user_var = ctk.StringVar(value=user_names[0] if user_names else "")
    user_dropdown = ctk.CTkOptionMenu(inner_form, variable=user_var, values=user_names, width=300)
    user_dropdown.grid(row=0, column=1, padx=(10, 0), pady=(0, 10))
    
    # Action Type
    ctk.CTkLabel(inner_form, text="Aktion:", 
                font=("Arial", 14, "bold")).grid(row=1, column=0, sticky="w", pady=(0, 10))
    
    action_var = ctk.StringVar(value="Mute")
    action_dropdown = ctk.CTkOptionMenu(inner_form, variable=action_var, 
                                       values=["Mute", "Timeout", "Bann"], width=300)
    action_dropdown.grid(row=1, column=1, padx=(10, 0), pady=(0, 10))
    
    # Duration
    ctk.CTkLabel(inner_form, text="Dauer (Minuten):", 
                font=("Arial", 14, "bold")).grid(row=2, column=0, sticky="w", pady=(0, 10))
    
    duration_entry = ctk.CTkEntry(inner_form, width=300, placeholder_text="5")
    duration_entry.grid(row=2, column=1, padx=(10, 0), pady=(0, 10))
    duration_entry.insert(0, "5")
    
    # Reason
    ctk.CTkLabel(inner_form, text="Grund:", 
                font=("Arial", 14, "bold")).grid(row=3, column=0, sticky="w", pady=(0, 10))
    
    reason_entry = ctk.CTkEntry(inner_form, width=300, placeholder_text="Grund eingeben...")
    reason_entry.grid(row=3, column=1, padx=(10, 0), pady=(0, 10))
    
    # Status Label
    status_label = ctk.CTkLabel(inner_form, text="", font=("Arial", 12))
    status_label.grid(row=5, column=0, columnspan=2, pady=(10, 0))
    
    # Submit Button
    def execute_action():
        username = user_var.get()
        action = action_var.get()
        duration = duration_entry.get()
        reason = reason_entry.get()
        
        if not username:
            status_label.configure(text="❌ Bitte User auswählen", text_color="red")
            return
        
        # User ID finden
        user_result = mod_queries.get_user_by_username(username)
        if not user_result or not user_result["data"]:
            status_label.configure(text="❌ User nicht gefunden", text_color="red")
            return
        
        user_id = user_result["data"][0][0]
        
        try:
            if action == "Bann":
                mod_queries.ban_user(current_moderator_id, user_id, reason)
                status_label.configure(text=f"✅ {username} wurde gebannt", text_color="green")
            else:
                dauer = int(duration) if duration else 5
                if action == "Mute":
                    mod_queries.mute_user(current_moderator_id, user_id, dauer, reason)
                    status_label.configure(text=f"✅ {username} wurde für {dauer}min gemutet", text_color="green")
                elif action == "Timeout":
                    mod_queries.timeout_user(current_moderator_id, user_id, dauer, reason)
                    status_label.configure(text=f"✅ {username} hat {dauer}min Timeout", text_color="green")
            
            # Clear form
            reason_entry.delete(0, 'end')
            app.after(3000, lambda: status_label.configure(text=""))
        except ValueError:
            status_label.configure(text="❌ Ungültige Dauer", text_color="red")
        except Exception as e:
            status_label.configure(text=f"❌ Fehler: {str(e)}", text_color="red")
    
    btn_execute = ctk.CTkButton(inner_form, text="⚡ Aktion ausführen", 
                                font=("Arial", 14, "bold"), height=40,
                                fg_color="#28a745", hover_color="#218838",
                                command=execute_action)
    btn_execute.grid(row=4, column=0, columnspan=2, pady=(20, 0))
    
    # Schnellaktionen
    quick_frame = ctk.CTkFrame(content, fg_color="#1c1c1c", corner_radius=10)
    quick_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    ctk.CTkLabel(quick_frame, text="⚡ Schnellaktionen", 
                font=("Arial", 18, "bold")).pack(pady=15)
    
    quick_buttons_frame = ctk.CTkFrame(quick_frame, fg_color="transparent")
    quick_buttons_frame.pack(pady=10)
    
    def quick_mute_5():
        execute_quick_action("Mute", 5, "Schnell-Mute")
    
    def quick_timeout_10():
        execute_quick_action("Timeout", 10, "Schnell-Timeout")
    
    def execute_quick_action(action_type, dauer, grund):
        username = user_var.get()
        if not username:
            return
        user_result = mod_queries.get_user_by_username(username)
        if user_result and user_result["data"]:
            user_id = user_result["data"][0][0]
            if action_type == "Mute":
                mod_queries.mute_user(current_moderator_id, user_id, dauer, grund)
            else:
                mod_queries.timeout_user(current_moderator_id, user_id, dauer, grund)
            mb.showinfo("Erfolg", f"{username}: {action_type} für {dauer}min")
    
    ctk.CTkButton(quick_buttons_frame, text="🔇 Mute 5min", width=150,
                 command=quick_mute_5).pack(side="left", padx=5)
    ctk.CTkButton(quick_buttons_frame, text="⏸️ Timeout 10min", width=150,
                 command=quick_timeout_10).pack(side="left", padx=5)

# ---------- Historie View ----------
def show_history():
    clear_content()
    
    header = ctk.CTkLabel(content, text="📜 Moderations-Historie", 
                          font=("Arial", 24, "bold"))
    header.pack(pady=20)
    
    # Scroll Frame
    scroll_frame = ctk.CTkScrollableFrame(content, fg_color="#1c1c1c", corner_radius=10)
    scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    history = mod_queries.get_moderation_history(limit=100)
    if history and "data" in history and history["data"]:
        for entry in history["data"]:
            aktion_id, typ, grund, dauer, timestamp, ablauf, aktiv, user, mod_name = entry
            
            # Farbe basierend auf Typ
            if typ == "bann":
                bg_color = "#4a1a1a"
            elif typ == "timeout":
                bg_color = "#4a3a1a"
            elif typ == "mute":
                bg_color = "#3a3a1a"
            else:
                bg_color = "#2a2a2a"
            
            entry_box = ctk.CTkFrame(scroll_frame, fg_color=bg_color, corner_radius=8)
            entry_box.pack(fill="x", pady=5, padx=10)
            
            # Status Icon
            status_icon = "🟢" if aktiv else "⚫"
            
            # Info Text
            info_text = f"{status_icon} {typ.upper()} | User: {user} | Moderator: {mod_name}"
            if dauer:
                info_text += f" | Dauer: {dauer}min"
            info_text += f"\n🕒 {timestamp}"
            if grund:
                info_text += f"\n💬 Grund: {grund}"
            
            ctk.CTkLabel(entry_box, text=info_text, font=("Arial", 11), 
                        anchor="w", justify="left").pack(pady=10, padx=10, fill="x")
    else:
        ctk.CTkLabel(scroll_frame, text="Keine Historie vorhanden", 
                    font=("Arial", 14)).pack(pady=20)

# ---------- Helper Functions ----------
def clear_content():
    for widget in content.winfo_children():
        widget.destroy()

def refresh_data():
    if mod_queries:
        mod_queries.cleanup_expired_actions()
        show_dashboard()
        mb.showinfo("Aktualisiert", "Daten wurden aktualisiert")

def add_test_message_dialog():
    """Dialog zum Hinzufügen von Test-Nachrichten"""
    dialog = ctk.CTkToplevel(app)
    dialog.title("Test-Nachricht hinzufügen")
    dialog.geometry("400x250")
    dialog.transient(app)
    dialog.grab_set()
    
    ctk.CTkLabel(dialog, text="Test-Nachricht erstellen", 
                font=("Arial", 16, "bold")).pack(pady=15)
    
    # User auswählen
    users = mod_queries.get_all_users()
    user_names = [u[1] for u in users["data"]] if users and "data" in users else []
    
    ctk.CTkLabel(dialog, text="User:").pack(pady=(10, 5))
    user_var = ctk.StringVar(value=user_names[0] if user_names else "")
    ctk.CTkOptionMenu(dialog, variable=user_var, values=user_names, width=300).pack()
    
    # Nachricht
    ctk.CTkLabel(dialog, text="Nachricht:").pack(pady=(10, 5))
    msg_entry = ctk.CTkEntry(dialog, width=300, placeholder_text="Nachricht eingeben...")
    msg_entry.pack()
    
    def add_msg():
        username = user_var.get()
        message = msg_entry.get()
        if username and message:
            user_result = mod_queries.get_user_by_username(username)
            if user_result and user_result["data"]:
                user_id = user_result["data"][0][0]
                mod_queries.add_test_message(user_id, username, message)
                dialog.destroy()
                show_chat_monitor()
    
    ctk.CTkButton(dialog, text="Hinzufügen", command=add_msg).pack(pady=20)

# ---------- Button Commands ----------
btn_dashboard.configure(command=show_dashboard)
btn_chat.configure(command=show_chat_monitor)
btn_actions.configure(command=show_actions)
btn_history.configure(command=show_history)
btn_refresh.configure(command=refresh_data)

# ---------- Start ----------
if __name__ == "__main__":
    if init_database():
        show_dashboard()
        app.mainloop()
        if db:
            db.connClose()
    else:
        app.quit()