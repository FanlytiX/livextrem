from fremdsys import oauth, tapi_data, tapi_mod
import tkinter as tk
import moderator_dashboard
import os
import customtkinter as ctk
import subprocess
import sys

root = tk.Tk()
root.geometry("200x150")
root.title("Starthilfe")

def f_bn1():
    print("Anmeldung geklickt")
    global token
    token = oauth.gen()
    if token != []:
        tk.Label(root, text="Angemeldet", fg="green").pack()

def f_bn2():
    print("Mod Dashboard geklickt")
    def starte_dashboard():
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(current_dir, "moderator_dashboard.py")
        subprocess.Popen([sys.executable, script_path])
    starte_dashboard()

def f_bn3():
    print("Manager Dashboard geklickt")

tk.Label(root, text="").pack()
bn1 = tk.Button(root, text="Twitch Anmelden", command=f_bn1).pack()
bn2 = tk.Button(root, text="Mod Dashboard", command=f_bn2).pack()
bd3 = tk.Button(root, text="Manager Dashboard", command=f_bn3).pack()

root.mainloop()