import os
from pathlib import Path
import customtkinter as ctk
from PIL import Image
import tkinter.messagebox as mb

# ---------- Pfade robust ermitteln ----------
BASE_DIR = Path(__file__).resolve().parent
IMG_PATH = BASE_DIR / "images" / "logo.png"
THEME_PATH = BASE_DIR / "style.json"

# ---------- Appearance / Theme ----------
ctk.set_appearance_mode("dark")  # "light" | "dark" | "system"

# Versuche Theme zu laden, sonst Fallback
if THEME_PATH.exists():
    try:
        ctk.set_default_color_theme(str(THEME_PATH))
    except Exception as e:
        mb.showwarning("Theme-Fehler", f"style.json konnte nicht geladen werden:\n{e}\n=> Fallback auf 'blue'")
        ctk.set_default_color_theme("blue")
else:
    ctk.set_default_color_theme("blue")

# ---------- Window ----------
menu = ctk.CTk()
menu.geometry("1000x600")
menu.title("LiveXtrem - Hauptmenü")

menu.grid_columnconfigure(1, weight=1)
menu.grid_rowconfigure(0, weight=1)

# ---------- Sidebar (mit Abstand & modernem Look) ----------
sidebar_container = ctk.CTkFrame(menu, fg_color="transparent")
sidebar_container.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)

sidebar = ctk.CTkFrame(sidebar_container, width=200, corner_radius=10)
sidebar.pack(fill="both", expand=True, padx=5, pady=5)
sidebar.grid_propagate(False)

# Logo – Seitenverhältnis 882x306 beibehalten (300x104)
if not IMG_PATH.exists():
    mb.showerror("Bild fehlt", f"Logo nicht gefunden unter:\n{IMG_PATH}\nArbeitsverzeichnis:\n{Path.cwd()}")
    logo = ctk.CTkLabel(sidebar, text="LIVE XTREM", font=("Arial", 20, "bold"))
    logo.pack(pady=(20, 30))
else:
    logo_img = ctk.CTkImage(
        light_image=Image.open(IMG_PATH),
        dark_image=Image.open(IMG_PATH),
        size=(300, 104)
    )
    logo = ctk.CTkLabel(sidebar, image=logo_img, text="")
    logo.pack(pady=(20, 30))

# ---------- Soft-Hover Button Style ----------
NORMAL_COLOR = "#1f538d"
HOVER_COLOR = "#2a5f9f"

class HoverButton(ctk.CTkButton):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.default_fg = NORMAL_COLOR
        self.hover_fg = HOVER_COLOR
        self.configure(fg_color=self.default_fg, hover_color=self.hover_fg)

# Sidebar Buttons
btn_home = HoverButton(sidebar, text="🏠  Startseite", width=160, corner_radius=6)
btn_donate = HoverButton(sidebar, text="💜  Spende", width=160, corner_radius=6)
btn_stats = HoverButton(sidebar, text="📊  Statistik", width=160, corner_radius=6)
btn_reco = HoverButton(sidebar, text="✅  Empfehlungen", width=160, corner_radius=6)
btn_settings = HoverButton(sidebar, text="⚙️  Einstellungen", width=160, corner_radius=6)

for b in (btn_home, btn_donate, btn_stats, btn_reco, btn_settings):
    b.pack(pady=6, padx=10, fill="x")

# ---------- Dashboard ----------
content = ctk.CTkFrame(menu, corner_radius=10)
content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
content.grid_columnconfigure((0, 1), weight=1)

def info_box(parent, title, body):
    box = ctk.CTkFrame(parent, fg_color="#CA6931", corner_radius=12)
    ctk.CTkLabel(box, text=title, font=("Arial", 18, "bold")).pack(pady=(8, 4))
    ctk.CTkLabel(box, text=body, font=("Arial", 14)).pack(pady=(0, 10))
    return box

# Boxen
box1 = info_box(content, "📊 Zuschauerstatistik",
                "Aktuell: 234 Zuschauer\nDurchschnitt: 180 Zuschauer\nSpitze: 300 Zuschauer")
box1.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

box2 = info_box(content, "💸 Spendenübersicht",
                "Heute: 25 €\nMonat: 320 €\nLetzte Spende von: „LisaS“")
box2.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

box3 = info_box(content, "🎬 Letzter Stream",
                "Spiel: Midnight Club L.A.\nDauer: 2 h 34 min\nDatum: 07.10.2025")
box3.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

box4 = info_box(content, "📅 Geplante Streams",
                "Samstag: 20:00 – Drift Event")
box4.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

menu.mainloop()
