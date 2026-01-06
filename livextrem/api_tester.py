from fremdsys import oauth, tapi_data, tapi_mod
import customtkinter as ctk
import moderator_dashboard
import os
import subprocess
import sys
import manager_gui

def on_close():
    print("Beende Anwendung…")
    root.destroy()
    exit()

def ausgabe(gesamtliste, neueliste):
    def auflisten(liste):
        _liste = ""
        j = 0
        for i in liste:
            if j <= 3:
                _liste += f"{i}, "
                j += 1
            else:
                _liste += f"{i} \n"
                j=0
        return _liste
    
    liste1 = auflisten(gesamtliste)
    liste1 = liste1 + "\n\nNeu:"
    liste2 = auflisten(neueliste)
    _liste = liste1 + liste2
    lb_ausgabe.configure(text=_liste)

def f_twlogon():
    global token
    token = oauth.gen()
    lb_status.configure(text=f"Angemeldet: {token.displayname}", text_color="green")
    bn_flwr.configure(state="enabled")
    bn_sub.configure(state="enabled")
    bn_twlogon.configure(state="disabled")

def f_twrefresh():
    oauth.refresh(token)
    if token == None:
        lb_status.configure(text="Bitte anmelden!", text_color="red")
        return
    print(token.atoken, token.rtoken)

def f_flwr():
    flwrlist, new_flwr = tapi_data.followlist(token)
    print(f"\n\nNeu:{new_flwr}")
    ausgabe(flwrlist, new_flwr)

def f_sub():
    sublist, newsub = tapi_data.sublist(token)
    #print(f"\n\nNeu:{newsub}")
    ausgabe(sublist, newsub)
    

global token
token = None

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.geometry("500x500")
root.title("API tester")

lb_status = ctk.CTkLabel(root, text="")
lb_status.pack(pady=5)
bn_twlogon = ctk.CTkButton(root, text="Twitch Anmelden", command=f_twlogon)
bn_twlogon.pack(pady=2)
bn_twrefresh = ctk.CTkButton(root, text="Twitch Refresh", command=f_twrefresh).pack(pady=2)
ctk.CTkLabel(root, text="").pack()
bn_flwr = ctk.CTkButton(root, text="Follower", command=f_flwr, state="disabled")
bn_flwr.pack(pady=2)
bn_sub = ctk.CTkButton(root, text="Subs", command=f_sub, state="disabled")
bn_sub.pack(pady=2)
lb_ausgabe = ctk.CTkLabel(root, text="")
lb_ausgabe.pack(pady=2)

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()