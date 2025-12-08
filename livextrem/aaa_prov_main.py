from fremdsys import oauth, tapi_data, tapi_mod
import customtkinter as ctk
import moderator_dashboard
import os
import subprocess
import sys
import manager_gui

global token
token = None

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.geometry("200x200")
root.title("Starthilfe")

def on_close():
    print("Beende Anwendung…")
    root.destroy()
    exit()

def f_twlogon():
    global token
    token = oauth.gen()
    lb_status.configure(text=f"Angemeldet: {token.displayname}", text_color="green")

def f_twrefresh():
    oauth.refresh(token)
    if token == None:
        lb_status.configure(text="Bitte anmelden!", text_color="red")
        return
    print(token.atoken, token.rtoken)

def f_moddshb():
    print("Mod Dashboard geklickt")
    def starte_dashboard():
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # ZIEL: moderator_dashboard1.py
        script_path = os.path.join(current_dir, "moderator_dashboard1.py")
        
        # Basis-Befehl
        cmd = [sys.executable, script_path]
        
        # ÄNDERUNG: Token-Daten anhängen, falls vorhanden
        if token:
            print(f"Übergebe Login an Dashboard: {token.displayname}")
            # Reihenfolge: [script, atoken, rtoken, displayname, clientid, clientsecret, userid, loginname]
            cmd.append(str(token.atoken))
            cmd.append(str(token.rtoken))
            cmd.append(str(token.displayname))
            cmd.append(str(token.clientid))
            cmd.append(str(token.clientsecret))
            cmd.append(str(token.userid))
            cmd.append(str(token.loginname))
            
        subprocess.Popen(cmd)
    starte_dashboard()

def f_mangdshb():
    def starte_dashboard():
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(current_dir, "manager_gui.py")
        subprocess.Popen([sys.executable, script_path])
    starte_dashboard()
    


lb_status = ctk.CTkLabel(root, text="")
lb_status.pack(pady=5)
bn_twlogon = ctk.CTkButton(root, text="Twitch Anmelden", command=f_twlogon).pack(pady=2)
bn_twrefresh = ctk.CTkButton(root, text="Twitch Refresh", command=f_twrefresh).pack(pady=2)
ctk.CTkLabel(root, text="").pack()
bn_moddshb = ctk.CTkButton(root, text="Mod Dashboard", command=f_moddshb).pack(pady=2)
bn_mangdshb = ctk.CTkButton(root, text="Manager Dashboard", command=f_mangdshb).pack(pady=2)


root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()