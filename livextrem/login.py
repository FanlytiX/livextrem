import customtkinter as ctk
from tkinter import messagebox
import threading
from PIL import Image
import os
import mariadb

from config import Config
from fremdsys import oauth
from security import hash_password, verify_password
from session_user import SessionUser, TwitchIdentity
from router import open_dashboard


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Wird bei erfolgreichem Login gesetzt, damit danach (nach mainloop)
        # sauber das passende Dashboard im MAIN-Thread gestartet werden kann.
        # Wichtig: Tkinter ist nicht thread-safe.
        self._login_session: SessionUser | None = None

        self.title("LiveXtrem Login")
        self.geometry("500x600")
        self.resizable(False, False)
        self.configure(fg_color="white")

        # Logo
        logo_path = os.path.join(os.path.dirname(__file__), "images", "logo.png")
        try:
            logo_img = ctk.CTkImage(light_image=Image.open(logo_path), size=(220, 80))
            ctk.CTkLabel(self, image=logo_img, text="").pack(pady=(30, 10))
        except Exception:
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
        Config.validate()
        return mariadb.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASS,
            database=Config.DB_NAME
        )

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

        ctk.CTkButton(self.container, text="Mit Twitch verbinden & registrieren",
                      fg_color="#1c31ba",
                      hover_color="#14375e",
                      command=self.start_twitch_registration).pack(pady=(20, 10))

        ctk.CTkButton(self.container, text="Zurück",
                      fg_color="gray70",
                      hover_color="gray80",
                      command=self.build_login_view).pack(pady=5)

    # ====================
    #   REGISTER FLOW
    # ====================
    def start_twitch_registration(self):
        username = self.reg_username.get().strip()
        email = self.reg_email.get().strip()
        pw = self.reg_password.get().strip()

        if not username or not pw or not email:
            messagebox.showerror("Fehler", "Bitte alle Felder ausfüllen.")
            return

        def worker():
            try:
                token = oauth.gen()  # Token nur im RAM (oauth Modul)
                self._register_streamer(username, email, pw, token)
                self.after(0, lambda: messagebox.showinfo("Erfolg", "Streamer erfolgreich registriert!"))
                self.after(0, self.build_login_view)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Fehler", f"Registrierung fehlgeschlagen: {e}"))

        threading.Thread(target=worker, daemon=True).start()
        messagebox.showinfo("Weiter", "Twitch Login öffnet sich im Browser.")

    def _register_streamer(self, username: str, email: str, pw: str, token):
        db = self._db()
        cur = db.cursor()

        # Username/Email uniqueness
        cur.execute("SELECT user_id FROM users WHERE username=? OR email=? LIMIT 1", (username, email))
        if cur.fetchone():
            db.close()
            raise RuntimeError("Benutzername oder E-Mail existiert bereits.")

        pw_hash = hash_password(pw)

        # user
        cur.execute("INSERT INTO users (email, username, password_hash, created_at) VALUES (?,?,?, NOW())",
                    (email, username, pw_hash))
        user_id = cur.lastrowid

        # role STREAMER (role_id = 1)
        cur.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?,1)", (user_id,))

        # streamer table
        cur.execute("INSERT INTO streamer (name, plattform, email, user_id, status) VALUES (?,'Twitch',?,?, 'Aktiv')",
                    (token.displayname, email, user_id))

        # twitch identity row (NO TOKENS STORED)
        # ensure row exists
        cur.execute("SELECT id FROM twitch_tokens WHERE user_id=? LIMIT 1", (user_id,))
        row = cur.fetchone()
        if row:
            cur.execute("""UPDATE twitch_tokens
                           SET twitch_userid=?, twitch_login=?, twitch_displayname=?,
                               access_token=NULL, refresh_token=NULL, expires_in=NULL
                           WHERE user_id=?""",
                        (str(token.userid), token.loginname, token.displayname, user_id))
        else:
            cur.execute("""INSERT INTO twitch_tokens
                           (user_id, twitch_userid, twitch_login, twitch_displayname, access_token, refresh_token, expires_in)
                           VALUES (?,?,?,?, NULL, NULL, NULL)""",
                        (user_id, str(token.userid), token.loginname, token.displayname))

        db.commit()
        db.close()

    # ====================
    #   LOGIN FLOW
    # ====================
    def handle_login(self):
        username = self.username.get().strip()
        pw = self.password.get().strip()

        if not username or not pw:
            messagebox.showerror("Fehler", "Felder dürfen nicht leer sein.")
            return

        def worker():
            try:
                session = self._login_and_build_session(username, pw)
                # Dashboard NICHT im Worker-Thread starten (Tkinter ist nicht thread-safe).
                # Stattdessen Session merken und mainloop sauber beenden.
                self.after(0, lambda s=session: self._on_login_success(s))
            except Exception as e:
                msg = str(e)
                self.after(0, lambda msg=msg: messagebox.showerror("Login fehlgeschlagen", msg))

        threading.Thread(target=worker, daemon=True).start()

    def _on_login_success(self, session: SessionUser):
        """Wird im MAIN-Thread aufgerufen."""
        self._login_session = session
        # Login-Fenster verstecken, dann mainloop beenden.
        # (Destroy kommt danach, wenn das Dashboard startet.)
        try:
            self.withdraw()
        except Exception:
            pass
        self.after(0, self.quit)

    def _login_and_build_session(self, username: str, pw: str) -> SessionUser:
        db = self._db()
        cur = db.cursor(dictionary=True)

        cur.execute("SELECT * FROM users WHERE username=? LIMIT 1", (username,))
        user = cur.fetchone()
        if not user:
            db.close()
            raise RuntimeError("Benutzerdaten falsch.")

        ok, upgraded = verify_password(pw, user["password_hash"])
        if not ok:
            db.close()
            raise RuntimeError("Benutzerdaten falsch.")

        # migrate hash if needed
        if upgraded:
            cur.execute("UPDATE users SET password_hash=? WHERE user_id=?", (upgraded, user["user_id"]))
            db.commit()

        # role id (1/2/3)
        cur.execute("SELECT role_id FROM user_roles WHERE user_id=? LIMIT 1", (user["user_id"],))
        role_row = cur.fetchone()
        if not role_row:
            db.close()
            raise RuntimeError("Dem Benutzer ist keine Rolle zugewiesen.")
        role_id = int(role_row["role_id"])

        # streamer row (optional)
        cur.execute("SELECT * FROM streamer WHERE user_id=? LIMIT 1", (user["user_id"],))
        streamer_row = cur.fetchone()

        # Für Moderator/Manager: Streamer-Zuordnung über Mapping-Tabellen (falls kein eigener Streamer-Account)
        if streamer_row is None and role_id in (2, 3):
            if role_id == 2:
                cur.execute(
                    """SELECT s.*
                       FROM streamer s
                       JOIN streamer_moderator sm ON sm.streamer_id = s.streamer_id
                       JOIN moderator m ON m.moderator_id = sm.moderator_id
                       WHERE m.user_id = ?
                       LIMIT 1""",
                    (user["user_id"],)
                )
                streamer_row = cur.fetchone()
            elif role_id == 3:
                # Manager -> streamer_manager
                cur.execute(
                    """SELECT s.*
                       FROM streamer s
                       JOIN streamer_manager smg ON smg.streamer_id = s.streamer_id
                       WHERE smg.user_id = ?
                       LIMIT 1""",
                    (user["user_id"],)
                )
                streamer_row = cur.fetchone()

        
        # Ergänzung: Streamer-Twitch-ID (broadcaster_id) für Moderator/Manager-Aktionen
        # Falls dem Streamer ein User-Account zugeordnet ist, holen wir dessen Twitch-Identity
        if streamer_row is not None and streamer_row.get("user_id"):
            cur.execute(
                "SELECT twitch_userid, twitch_login, twitch_displayname FROM twitch_tokens WHERE user_id=? LIMIT 1",
                (streamer_row["user_id"],)
            )
            s_trow = cur.fetchone()
            if s_trow:
                streamer_row["twitch_userid"] = s_trow.get("twitch_userid")
                streamer_row["twitch_login"] = s_trow.get("twitch_login")
                streamer_row["twitch_displayname"] = s_trow.get("twitch_displayname")
            else:
                streamer_row["twitch_userid"] = None
                streamer_row["twitch_login"] = None
                streamer_row["twitch_displayname"] = None

# twitch identity row (optional)
        cur.execute("SELECT twitch_userid, twitch_login, twitch_displayname FROM twitch_tokens WHERE user_id=? LIMIT 1", (user["user_id"],))
        trow = cur.fetchone()
        twitch_identity = TwitchIdentity(
            userid=(trow["twitch_userid"] if trow else None),
            login=(trow["twitch_login"] if trow else None),
            displayname=(trow["twitch_displayname"] if trow else None),
        )

        # Twitch login for Streamer & Moderator
        twitch_token = None
        if role_id in (1, 2):
            twitch_token = oauth.gen()  # caches in oauth module; no DB storage
            # identity binding / verification
            incoming_uid = str(twitch_token.userid)

            if twitch_identity.userid and twitch_identity.userid != incoming_uid:
                db.close()
                raise RuntimeError("Twitch-Account stimmt nicht mit dem zugewiesenen Benutzer überein.")

            # upsert identity without tokens
            if trow:
                cur.execute("""UPDATE twitch_tokens
                               SET twitch_userid=?, twitch_login=?, twitch_displayname=?,
                                   access_token=NULL, refresh_token=NULL, expires_in=NULL
                               WHERE user_id=?""",
                            (incoming_uid, twitch_token.loginname, twitch_token.displayname, user["user_id"]))
            else:
                cur.execute("""INSERT INTO twitch_tokens
                               (user_id, twitch_userid, twitch_login, twitch_displayname, access_token, refresh_token, expires_in)
                               VALUES (?,?,?,?, NULL, NULL, NULL)""",
                            (user["user_id"], incoming_uid, twitch_token.loginname, twitch_token.displayname))
            db.commit()
            twitch_identity = TwitchIdentity(userid=incoming_uid, login=twitch_token.loginname, displayname=twitch_token.displayname)

        db.close()

        return SessionUser(
            user_row=user,
            role_id=role_id,
            streamer_row=streamer_row,
            twitch_identity=twitch_identity,
            twitch_token=twitch_token
        )


if __name__ == "__main__":
    # Wichtig: Dashboards erst NACH dem Login-mainloop starten,
    # sonst gibt es Probleme (mehrere mainloops / Threads / mehrere Tk-Roots).
    app = LoginWindow()
    app.mainloop()

    session = getattr(app, "_login_session", None)
    try:
        app.destroy()
    except Exception:
        pass

    if session is not None:
        started = open_dashboard(session)

        # Falls das Dashboard nicht starten konnte (Fehler/fehlende Abhängigkeiten/etc.),
        # nicht einfach beenden, sondern wieder ins Login zurück.
        if not started:
            app2 = LoginWindow()
            app2.mainloop()
            session2 = getattr(app2, "_login_session", None)
            try:
                app2.destroy()
            except Exception:
                pass
            if session2 is not None:
                open_dashboard(session2)