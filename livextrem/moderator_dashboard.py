import os
import sys 
from pathlib import Path
import customtkinter as ctk
from PIL import Image
import tkinter.messagebox as mb
from datetime import datetime
from database_connection import DatabaseManager
from database_queries_moderator import ModeratorQueries

# ---------- Pfade robust ermitteln ----------
BASE_DIR = Path(__file__).resolve().parent
IMG_PATH = BASE_DIR / "images" / "logo.png"
THEME_PATH = BASE_DIR / "style.json"

# ---------- Appearance / Theme ----------
ctk.set_appearance_mode("light")

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
twitch_token = None

# ---------- Hauptfenster ----------
app = ctk.CTk()
app.geometry("1400x800")
app.title("LiveXtrem - Moderator Dashboard")

app.grid_columnconfigure(1, weight=1)
app.grid_rowconfigure(0, weight=1)

# ---------- Twitch Login ----------
def twitch_login():
    """
    Prüft erst auf übergebene Argumente vom Launcher.
    Wenn keine da sind, öffnet es den Browser Login.
    """
    global twitch_token
    
    # Check auf Argumente vom Launcher
    if len(sys.argv) >= 8:
        try:
            arg_atoken = sys.argv[1]
            arg_rtoken = sys.argv[2]
            arg_name = sys.argv[3]
            arg_cid = sys.argv[4]      
            arg_csec = sys.argv[5]     
            arg_uid = sys.argv[6]      
            arg_login = sys.argv[7]    
            
            class LauncherToken:
                def __init__(self, at, rt, dn, cid, csec, uid, ln):
                    self.atoken = at
                    self.rtoken = rt
                    self.displayname = dn
                    self.clientid = cid      
                    self.clientsecret = csec   
                    self.userid = uid          
                    self.loginname = ln        
            
            twitch_token = LauncherToken(arg_atoken, arg_rtoken, arg_name, arg_cid, arg_csec, arg_uid, arg_login)
            print(f"Login erfolgreich vom Launcher übernommen: {twitch_token.displayname}")
            return True
        except Exception as e:
            print(f"Fehler bei Token-Übernahme: {e}")

    # Fallback: Normaler Login via Browser
    try:
        from fremdsys import oauth
        mb.showinfo("Twitch Login", "Keine Sitzung gefunden.\nBrowser öffnet sich für Twitch-Anmeldung.")
        twitch_token = oauth.gen()
        return True
    except Exception as e:
        mb.showerror("Login-Fehler", f"Twitch-Login fehlgeschlagen:\n{e}")
        return False

# ---------- Datenbank initialisieren ----------
def init_database():
    global db, mod_queries
    try:
        db = DatabaseManager()
        db.connection()
        
        if not twitch_login():
            return False
        
        mod_queries = ModeratorQueries(db, twitch_token)
        
        mb.showinfo("Chat laden", "Lade Chat-Nachrichten vom letzten VOD...\nDies kann einen Moment dauern.")
        success = mod_queries.load_vod_chat()
        
        if not success:
            error = mod_queries.get_chat_error()
            mb.showwarning("Chat-Warnung", f"{error}\n\nDas Dashboard funktioniert trotzdem für Moderationsaktionen.")
        else:
            vod = mod_queries.get_vod_info()
            if vod:
                mb.showinfo("Chat geladen", f"Chat erfolgreich geladen!\n\nVOD: {vod.get('title', 'Unbekannt')}")
        
        mod_queries.cleanup_expired_actions()
        return True
    except Exception as e:
        mb.showerror("Datenbankfehler", f"Initialisierung fehlgeschlagen:\n{e}")
        return False

# ---------- Sidebar ----------
sidebar_container = ctk.CTkFrame(app, fg_color="transparent")
sidebar_container.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)

sidebar = ctk.CTkFrame(sidebar_container, width=220, corner_radius=10)
sidebar.pack(fill="both", expand=True, padx=5, pady=5)
sidebar.grid_propagate(False)

# --- Mode Toggle Button ---
def toggle_appearance_mode():
    new_mode = "Dark" if ctk.get_appearance_mode() == "Light" else "Light"
    ctk.set_appearance_mode(new_mode)
    
    if new_mode == "Dark":
        btn_mode.configure(text="☀️ Light Mode")
    else:
        btn_mode.configure(text="🌙 Dark Mode")

# Mode Button: Größer gemacht
btn_mode = ctk.CTkButton(sidebar, 
                        text="🌙 Dark Mode",
                        command=toggle_appearance_mode,
                        width=200, 
                        height=40,
                        font=("Arial", 16, "bold"),
                        fg_color="transparent", 
                        border_width=1,
                        text_color=("gray10", "gray90"))
btn_mode.pack(pady=(15, 5), padx=10)

# Logo
if not IMG_PATH.exists():
    logo = ctk.CTkLabel(sidebar, text="LIVE XTREM", font=("Arial", 25, "bold"))
    logo.pack(pady=(10, 30))
else:
    logo_img = ctk.CTkImage(
        light_image=Image.open(IMG_PATH),
        dark_image=Image.open(IMG_PATH),
        size=(200, 69)
    )
    logo = ctk.CTkLabel(sidebar, image=logo_img, text="")
    logo.pack(pady=(10, 30))

# Moderator Info
mod_info_frame = ctk.CTkFrame(sidebar, fg_color="#CA6931", corner_radius=8)
mod_info_frame.pack(pady=(0, 20), padx=10, fill="x")

mod_info_label = ctk.CTkLabel(mod_info_frame, text="👤 Moderator", font=("Arial", 17, "bold"))
mod_info_label.pack(pady=(8, 2))

mod_name_label = ctk.CTkLabel(mod_info_frame, text="...", font=("Arial", 19))
mod_name_label.pack(pady=(0, 8))

# Buttons
NORMAL_COLOR = "#1f538d"
HOVER_COLOR = "#2a5f9f"

class HoverButton(ctk.CTkButton):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.default_fg = NORMAL_COLOR
        self.hover_fg = HOVER_COLOR
        self.configure(fg_color=self.default_fg, hover_color=self.hover_fg)

# Buttons: Deutlich vergrößert (Höhe 50, Breite 200, Font 18 Bold)
btn_dashboard = HoverButton(sidebar, text="📊  Dashboard", width=200, height=50, font=("Arial", 18, "bold"), corner_radius=8)
btn_chat = HoverButton(sidebar, text="💬  Chat Monitor", width=200, height=50, font=("Arial", 18, "bold"), corner_radius=8)
btn_actions = HoverButton(sidebar, text="⚡  Aktionen", width=200, height=50, font=("Arial", 18, "bold"), corner_radius=8)
btn_refresh = HoverButton(sidebar, text="🔄  Aktualisieren", width=200, height=50, font=("Arial", 18, "bold"), corner_radius=8)

for b in (btn_dashboard, btn_chat, btn_actions, btn_refresh):
    b.pack(pady=8, padx=10, fill="x") # pady leicht erhöht für besseren Abstand

# ---------- Content Area ----------
content = ctk.CTkFrame(app, corner_radius=10)
content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

# ---------- Dashboard View ----------
def show_dashboard():
    clear_content()
    
    header_frame = ctk.CTkFrame(content, fg_color="transparent")
    header_frame.pack(fill="x", pady=20, padx=20)
    
    ctk.CTkLabel(header_frame, text="Moderator Dashboard", 
                font=("Arial", 29, "bold")).pack(side="left")
    
    info_badge = ctk.CTkFrame(header_frame, fg_color="#CA6931", corner_radius=6)
    info_badge.pack(side="right")
    ctk.CTkLabel(info_badge, text="🔗 Twitch API verbunden", 
                font=("Arial", 16)).pack(padx=12, pady=6)
    
    stats_frame = ctk.CTkFrame(content, fg_color="transparent")
    stats_frame.pack(fill="x", padx=20, pady=10)
    stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
    
    stats = mod_queries.get_moderator_stats()
    if stats and "data" in stats and stats["data"]:
        data = stats["data"][0]
        aktive = data[0] if len(data) > 0 else 0
        gebannt = data[1] if len(data) > 1 else 0
        timeouts = data[2] if len(data) > 2 else 0
        total = data[3] if len(data) > 3 else 0
    else:
        aktive = gebannt = timeouts = total = 0
    
    def create_stat_box(parent, col, title, value, icon):
        box = ctk.CTkFrame(parent, fg_color="#CA6931", corner_radius=12)
        box.grid(row=0, column=col, sticky="nsew", padx=8, pady=5)
        ctk.CTkLabel(box, text=f"{icon} {title}", 
                    font=("Arial", 25, "bold")).pack(pady=(12, 5))
        ctk.CTkLabel(box, text=str(value), 
                    font=("Arial", 33, "bold")).pack(pady=(0, 12))
    
    create_stat_box(stats_frame, 0, "Aktive Fälle", aktive, "⚡")
    create_stat_box(stats_frame, 1, "Gebannte User", gebannt, "🚫")
    create_stat_box(stats_frame, 2, "Timeouts", timeouts, "⏸️")
    create_stat_box(stats_frame, 3, "Gesamt", total, "📊")
    
    historie_frame = ctk.CTkFrame(content, fg_color=("gray85", "#1c1c1c"), corner_radius=10)
    historie_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    ctk.CTkLabel(historie_frame, text="📜 Letzte Moderationsaktionen", 
                font=("Arial", 23, "bold")).pack(pady=15)
    
    scroll_frame = ctk.CTkScrollableFrame(historie_frame, fg_color="transparent")
    scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    history = mod_queries.get_moderation_history(limit=15)
    if history and "data" in history and history["data"]:
        for entry in history["data"]:
            aktion_id, typ, grund, dauer, timestamp, ablauf, aktiv, user, mod_name = entry
            
            if typ == "bann":
                bg_color = ("#ffcccc", "#4a1a1a")
                icon = "🚫"
            elif typ == "timeout":
                bg_color = ("#ffebcc", "#4a3a1a")
                icon = "⏸️"
            elif typ == "unban":
                bg_color = ("#ccffcc", "#1a4a1a")
                icon = "✅"
            else:
                bg_color = ("gray90", "#2a2a2a")
                icon = "⚡"
            
            entry_box = ctk.CTkFrame(scroll_frame, fg_color=bg_color, corner_radius=8)
            entry_box.pack(fill="x", pady=4, padx=5)
            
            status_icon = "🟢" if aktiv else "⚫"
            
            time_str = timestamp.strftime("%d.%m. %H:%M") if hasattr(timestamp, 'strftime') else str(timestamp)
            info_text = f"{status_icon} {icon} {typ.upper()} | User: {user} | Moderator: {mod_name} | {time_str}"
            if dauer:
                info_text += f" | Dauer: {dauer}min"
            if grund:
                info_text += f"\n💬 Grund: {grund}"
            
            ctk.CTkLabel(entry_box, text=info_text, font=("Arial", 16), 
                        anchor="w", justify="left", text_color=("black", "white")).pack(pady=8, padx=10, fill="x")
    else:
        ctk.CTkLabel(scroll_frame, text="✅ Noch keine Moderationsaktionen durchgeführt", 
                    font=("Arial", 19), text_color="green").pack(pady=20)

# ---------- Chat Monitor View ----------
def show_chat_monitor():
    clear_content()
    
    header_frame = ctk.CTkFrame(content, fg_color="transparent")
    header_frame.pack(fill="x", pady=20, padx=20)
    
    ctk.CTkLabel(header_frame, text="💬 Chat Monitor (VOD Replay)", 
                font=("Arial", 29, "bold")).pack(side="left")
    
    vod = mod_queries.get_vod_info()
    if vod:
        vod_badge = ctk.CTkFrame(header_frame, fg_color="#CA6931", corner_radius=6)
        vod_badge.pack(side="right")
        vod_title = vod.get('title', 'Unbekannt')[:40] + "..." if len(vod.get('title', '')) > 40 else vod.get('title', 'Unbekannt')
        ctk.CTkLabel(vod_badge, text=f"📺 {vod_title}", 
                    font=("Arial", 16)).pack(padx=12, pady=6)
    
    chat_frame = ctk.CTkFrame(content, fg_color=("gray85", "#1c1c1c"), corner_radius=10)
    chat_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    error = mod_queries.get_chat_error()
    if error:
        error_container = ctk.CTkFrame(chat_frame, fg_color="#4a1a1a", corner_radius=10)
        error_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(error_container, text="⚠️ Chat-Fehler", 
                    font=("Arial", 35, "bold"), text_color="#df92d8").pack(pady=(30, 10))
        ctk.CTkLabel(error_container, text=error, 
                    font=("Arial", 29),text_color="#fcfcfc", wraplength=600).pack(pady=(0, 30))
        return
    
    ctk.CTkLabel(chat_frame, text="📨 Chat-Nachrichten", 
                font=("Arial", 25, "bold")).pack(pady=10)
    
    chat_scroll = ctk.CTkScrollableFrame(chat_frame, fg_color="transparent")
    chat_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    messages = mod_queries.get_all_messages(limit=200)
    if messages and "data" in messages and messages["data"]:
        for msg in reversed(messages["data"]):
            msg_id, username, text, timestamp = msg
            
            msg_box = ctk.CTkFrame(chat_scroll, fg_color=("gray95", "#2a2a2a"), corner_radius=8)
            msg_box.pack(fill="x", pady=3, padx=5)
            
            header_frame = ctk.CTkFrame(msg_box, fg_color="transparent")
            header_frame.pack(fill="x", padx=10, pady=(8, 2))
            
            ctk.CTkLabel(header_frame, text=f"👤 {username}", 
                        font=("Arial", 16, "bold"), anchor="w").pack(side="left")
            
            time_str = timestamp if isinstance(timestamp, str) else timestamp.strftime("%H:%M:%S")
            ctk.CTkLabel(header_frame, text=time_str, 
                        font=("Arial", 14), text_color=("gray40", "gray"), anchor="e").pack(side="right")
            
            ctk.CTkLabel(msg_box, text=text, font=("Arial", 17), 
                        anchor="w", wraplength=800, justify="left").pack(padx=10, pady=(0, 8), fill="x")
    else:
        ctk.CTkLabel(chat_scroll, text="Keine Chat-Nachrichten verfügbar", 
                    font=("Arial", 19)).pack(pady=20)

# ---------- Aktionen View ----------
def show_actions():
    clear_content()
    
    header = ctk.CTkLabel(content, text="⚡ Moderationsaktionen", 
                          font=("Arial", 35, "bold"))
    header.pack(pady=20)
    
    tabview = ctk.CTkTabview(content, corner_radius=10)
    tabview.pack(fill="both", expand=True, padx=20, pady=10)
    
    tabview._segmented_button.configure(font=("Arial", 22, "bold"), height=50)
    
    tab_timeout = tabview.add("⏸️ Timeout")
    tab_ban = tabview.add("🚫 Ban")
    tab_unban = tabview.add("✅ Unban")
    
    # ========== TIMEOUT TAB ==========
    timeout_form = ctk.CTkFrame(tab_timeout, fg_color="transparent")
    timeout_form.pack(pady=30, padx=50)
    
    ctk.CTkLabel(timeout_form, text="User Timeout geben", 
                font=("Arial", 28, "bold")).pack(pady=(0, 20))
    
    ctk.CTkLabel(timeout_form, text="Username:", font=("Arial", 24, "bold")).pack(pady=(10, 5))
    timeout_user_entry = ctk.CTkEntry(timeout_form, width=500, height=50, font=("Arial", 20), placeholder_text="z.B. troll123")
    timeout_user_entry.pack()
    
    ctk.CTkLabel(timeout_form, text="Dauer (Minuten):", font=("Arial", 24, "bold")).pack(pady=(15, 5))
    timeout_duration_entry = ctk.CTkEntry(timeout_form, width=500, height=50, font=("Arial", 20), placeholder_text="z.B. 10")
    timeout_duration_entry.pack()
    timeout_duration_entry.insert(0, "10")
    
    ctk.CTkLabel(timeout_form, text="Grund (optional):", font=("Arial", 24, "bold")).pack(pady=(15, 5))
    timeout_reason_entry = ctk.CTkEntry(timeout_form, width=500, height=50, font=("Arial", 20), placeholder_text="z.B. Spam im Chat")
    timeout_reason_entry.pack()
    
    timeout_status = ctk.CTkLabel(timeout_form, text="", font=("Arial", 20))
    timeout_status.pack(pady=(15, 0))
    
    def execute_timeout():
        username = timeout_user_entry.get().strip()
        duration = timeout_duration_entry.get().strip()
        reason = timeout_reason_entry.get().strip()
        
        if not username:
            timeout_status.configure(text="❌ Bitte Username eingeben", text_color="red")
            return
        
        try:
            dauer = int(duration) if duration else 10
            result = mod_queries.timeout_user(username, dauer, reason)
            
            if result["success"]:
                timeout_status.configure(text=f"✅ {result['message']}", text_color="green")
                timeout_user_entry.delete(0, 'end')
                timeout_reason_entry.delete(0, 'end')
                app.after(3000, lambda: timeout_status.configure(text=""))
            else:
                timeout_status.configure(text=f"❌ {result['message']}", text_color="red")
        except ValueError:
            timeout_status.configure(text="❌ Ungültige Dauer", text_color="red")
    
    ctk.CTkButton(timeout_form, text="⏸️ Timeout ausführen", 
                 font=("Arial", 24, "bold"), height=60, width=350,
                 fg_color="#ffa500", hover_color="#ff8c00",
                 command=execute_timeout).pack(pady=(30, 0))
    
    # ========== BAN TAB ==========
    ban_form = ctk.CTkFrame(tab_ban, fg_color="transparent")
    ban_form.pack(pady=30, padx=50)
    
    ctk.CTkLabel(ban_form, text="User permanent bannen", 
                font=("Arial", 28, "bold")).pack(pady=(0, 20))
    
    ctk.CTkLabel(ban_form, text="Username:", font=("Arial", 24, "bold")).pack(pady=(10, 5))
    ban_user_entry = ctk.CTkEntry(ban_form, width=500, height=50, font=("Arial", 20), placeholder_text="z.B. troll123")
    ban_user_entry.pack()
    
    ctk.CTkLabel(ban_form, text="Grund (optional):", font=("Arial", 24, "bold")).pack(pady=(15, 5))
    ban_reason_entry = ctk.CTkEntry(ban_form, width=500, height=50, font=("Arial", 20), placeholder_text="z.B. Wiederholte Regelverstöße")
    ban_reason_entry.pack()
    
    ban_status = ctk.CTkLabel(ban_form, text="", font=("Arial", 20))
    ban_status.pack(pady=(15, 0))
    
    def execute_ban():
        username = ban_user_entry.get().strip()
        reason = ban_reason_entry.get().strip()
        
        if not username:
            ban_status.configure(text="❌ Bitte Username eingeben", text_color="red")
            return
        
        if not mb.askyesno("Bestätigung", f"User '{username}' wirklich permanent bannen?"):
            return
        
        result = mod_queries.ban_user(username, reason)
        
        if result["success"]:
            ban_status.configure(text=f"✅ {result['message']}", text_color="green")
            ban_user_entry.delete(0, 'end')
            ban_reason_entry.delete(0, 'end')
            app.after(3000, lambda: ban_status.configure(text=""))
        else:
            ban_status.configure(text=f"❌ {result['message']}", text_color="red")
    
    ctk.CTkButton(ban_form, text="🚫 Ban ausführen", 
                 font=("Arial", 24, "bold"), height=60, width=350,
                 fg_color="#dc3545", hover_color="#c82333",
                 command=execute_ban).pack(pady=(30, 0))
    
    # ========== UNBAN TAB ==========
    unban_form = ctk.CTkFrame(tab_unban, fg_color="transparent")
    unban_form.pack(pady=30, padx=50)
    
    ctk.CTkLabel(unban_form, text="User entbannen", 
                font=("Arial", 28, "bold")).pack(pady=(0, 20))
    
    ctk.CTkLabel(unban_form, text="Username:", font=("Arial", 24, "bold")).pack(pady=(10, 5))
    unban_user_entry = ctk.CTkEntry(unban_form, width=500, height=50, font=("Arial", 20), placeholder_text="z.B. troll123")
    unban_user_entry.pack()
    
    unban_status = ctk.CTkLabel(unban_form, text="", font=("Arial", 20))
    unban_status.pack(pady=(15, 0))
    
    def execute_unban():
        username = unban_user_entry.get().strip()
        
        if not username:
            unban_status.configure(text="❌ Bitte Username eingeben", text_color="red")
            return
        
        result = mod_queries.unban_user(username)
        
        if result["success"]:
            unban_status.configure(text=f"✅ {result['message']}", text_color="green")
            unban_user_entry.delete(0, 'end')
            app.after(3000, lambda: unban_status.configure(text=""))
        else:
            unban_status.configure(text=f"❌ {result['message']}", text_color="red")
    
    ctk.CTkButton(unban_form, text="✅ Unban ausführen", 
                 font=("Arial", 24, "bold"), height=60, width=350,
                 fg_color="#28a745", hover_color="#218838",
                 command=execute_unban).pack(pady=(30, 0))

# ---------- Helper Functions ----------
def clear_content():
    for widget in content.winfo_children():
        widget.destroy()

def refresh_data():
    if mod_queries:
        mod_queries.cleanup_expired_actions()
        
        mb.showinfo("Chat neu laden", "Lade Chat-Nachrichten neu...")
        success = mod_queries.load_vod_chat()
        
        if not success:
            error = mod_queries.get_chat_error()
            mb.showwarning("Chat-Warnung", f"{error}")
        else:
            mb.showinfo("Erfolg", "Chat erfolgreich neu geladen!")
        
        show_dashboard()

# ---------- Button Commands ----------
btn_dashboard.configure(command=show_dashboard)
btn_chat.configure(command=show_chat_monitor)
btn_actions.configure(command=show_actions)
btn_refresh.configure(command=refresh_data)

# ---------- Start ----------
if __name__ == "__main__":
    if init_database():
        if twitch_token:
            mod_name_label.configure(text=twitch_token.displayname)
        
        show_dashboard()
        app.mainloop()
        if db:
            db.connClose()
    else:
        app.quit()