import customtkinter as ctk
from tkinter import messagebox
import hashlib
import threading
from PIL import Image
import os
import mysql.connector

from fremdsys import oauth
from session_user import SessionUser
from role_selector import RoleSelectorWindow   # <-- Neues Zwischenfenster


class LoginWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("LiveXtrem Login")
        self.geometry("500x600")
        self.resizable(False, False)
        self.configure(fg_color="white")

        # Logo
        logo_path = os.path.join(os.path.dirname(__file__), "images", "logo.png")
        try:
            logo_img = ctk.CTkImage(light_image=Image.open(logo_path), size=(220, 80))
            ctk.CTkLabel(self, image=logo_img, text="").pack(pady=(30, 10))
        except:
            ctk.CTkLabel(self, text="LIVE XTREM",
                         font=ctk.CTkFont(size=32, weight="bold"),
                         text_color="#1c31ba").pack(pady=(40, 20))

        self.container = ctk.CTkFrame(self, fg_color="#f2f2f2", corner_radius=12)
        self.container.pack(pady=20, padx=20, fill="both", expand=True)

        self.build_login_view()

    # ======================
    #  🔧 DATENBANK
    # ======================
    def _db(self):
        return mysql.connector.connect(
            host="88.218.227.14",
            user="livextrem",
            password="leckmeineeier",
            database="livextrem"
        )

    # ======================
    #   🔐 HASH
    # ======================
    def hash_password(self, pw: str):
        return hashlib.sha256(pw.encode()).hexdigest()

    # ======================
    #   LOGIN UI
    # ======================
    def build_login_view(self):
        for w in self.container.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.container, text="Anmelden",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="#1c31ba").pack(pady=(20, 10))

        self.username = ctk.CTkEntry(self.container, placeholder_text="Benutzername")
        self.username.pack(pady=10, padx=40, fill="x")

        self.password = ctk.CTkEntry(self.container, placeholder_text="Passwort", show="*")
        self.password.pack(pady=10, padx=40, fill="x")

        ctk.CTkButton(self.container, text="Login",
                      fg_color="#1c31ba",
                      hover_color="#14375e",
                      command=self.handle_login).pack(pady=(20, 10))

        ctk.CTkButton(self.container, text="Registrieren",
                      fg_color="gray70",
                      hover_color="gray80",
                      command=self.build_register_view).pack(pady=5)

    # ======================
    #   REGISTER UI
    # ======================
    def build_register_view(self):
        for w in self.container.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.container, text="Streamer registrieren",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="#1c31ba").pack(pady=(20, 10))

        self.reg_username = ctk.CTkEntry(self.container, placeholder_text="Benutzername")
        self.reg_username.pack(pady=10, padx=40, fill="x")

        self.reg_email = ctk.CTkEntry(self.container, placeholder_text="E-Mail")
        self.reg_email.pack(pady=10, padx=40, fill="x")

        self.reg_password = ctk.CTkEntry(self.container, placeholder_text="Passwort", show="*")
        self.reg_password.pack(pady=10, padx=40, fill="x")

        ctk.CTkButton(self.container, text="Mit Twitch verbinden",
                      fg_color="#1c31ba",
                      hover_color="#14375e",
                      command=self.start_twitch_registration).pack(pady=(20, 10))

        ctk.CTkButton(self.container, text="Zurück",
                      fg_color="gray70",
                      hover_color="gray80",
                      command=self.build_login_view).pack(pady=5)

    # ===================================================
    #   TWITCH LOGIN STARTEN
    # ===================================================
    def start_twitch_registration(self):
        username = self.reg_username.get().strip()
        email = self.reg_email.get().strip()
        pw = self.reg_password.get().strip()

        if not username or not pw or not email:
            messagebox.showerror("Fehler", "Bitte alle Felder ausfüllen.")
            return

        hashed = self.hash_password(pw)

        def twitch_flow():
            token = oauth.gen_direct()
            self.save_streamer_user(username, email, hashed, token)

        threading.Thread(target=twitch_flow, daemon=True).start()

        messagebox.showinfo("Weiter", "Twitch Login geöffnet.")

    # ===================================================
    #   STREAMER + ROLE + TOKEN SPEICHERN
    # ===================================================
    def save_streamer_user(self, username, email, hashed_pw, token):
        db = self._db()
        cursor = db.cursor(dictionary=True)

        # Tokens Tabelle erstellen wenn nötig
        cursor.execute("""
            SELECT COUNT(*) AS cnt FROM information_schema.tables
            WHERE table_schema='livextrem' AND table_name='twitch_tokens'
        """)
        if cursor.fetchone()["cnt"] == 0:
            cursor.execute("""CREATE TABLE twitch_tokens (
                id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT UNSIGNED NOT NULL,
                twitch_userid VARCHAR(50),
                twitch_login VARCHAR(50),
                twitch_displayname VARCHAR(50),
                access_token TEXT,
                refresh_token TEXT,
                expires_in INT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )""")
            db.commit()

        # User anlegen
        cursor.execute("""
            INSERT INTO users (email, username, password_hash, created_at)
            VALUES (%s,%s,%s, NOW())
        """, (email, username, hashed_pw))
        user_id = cursor.lastrowid

        # Rolle Streamer zuweisen
        cursor.execute("SELECT role_id FROM roles WHERE name='STREAMER'")
        role = cursor.fetchone()
        cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (%s,%s)",
                       (user_id, role["role_id"]))

        # Streamer erstellen
        cursor.execute("""
            INSERT INTO streamer (name, plattform, email, user_id, status)
            VALUES (%s,'Twitch',%s,%s,'Aktiv')
        """, (token.displayname, email, user_id))

        # Token speichern
        cursor.execute("""
            INSERT INTO twitch_tokens (
                user_id, twitch_userid, twitch_login, twitch_displayname,
                access_token, refresh_token, expires_in)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            user_id,
            token.userid,
            token.loginname,
            token.displayname,
            token.atoken,
            token.rtoken,
            token.expire
        ))

        db.commit()
        db.close()

        messagebox.showinfo("Erfolg", "Streamer erfolgreich registriert!")
        self.build_login_view()

    # ===================================================
    #   LOGIN VERARBEITEN
    # ===================================================
    def handle_login(self):
        username = self.username.get().strip()
        pw = self.password.get().strip()

        if not username or not pw:
            messagebox.showerror("Fehler", "Felder dürfen nicht leer sein.")
            return

        hashed_pw = self.hash_password(pw)

        db = self._db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM users WHERE username=%s AND password_hash=%s
        """, (username, hashed_pw))

        user = cursor.fetchone()

        if not user:
            messagebox.showerror("Fehler", "Benutzerdaten falsch.")
            return

        session = self.load_session_user(user["user_id"])

        db.close()

        # → ZWISCHENFENSTER ÖFFNEN
        self.destroy()
        RoleSelectorWindow(session).mainloop()


    # ===================================================
    #   SESSION USER BAUEN
    # ===================================================
    def load_session_user(self, user_id):
        db = self._db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
        user_row = cursor.fetchone()

        cursor.execute("""
            SELECT r.name
            FROM roles r
            JOIN user_roles ur ON ur.role_id = r.role_id
            WHERE ur.user_id=%s
        """, (user_id,))
        roles = [r["name"] for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM streamer WHERE user_id=%s", (user_id,))
        streamer_row = cursor.fetchone()

        cursor.execute("SELECT * FROM twitch_tokens WHERE user_id=%s", (user_id,))
        tokens_row = cursor.fetchone()

        db.close()

        return SessionUser(
            user_row=user_row,
            roles=roles,
            streamer_row=streamer_row,
            tokens_row=tokens_row
        )


if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()
