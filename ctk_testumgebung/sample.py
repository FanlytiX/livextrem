import customtkinter as ctk

# Dies ist nur ein Dummy Testprogramm um zu sehen, wie das Style aussieht

# Globale Einstellungen
ctk.set_appearance_mode("teststyle")  # "dark", "light", oder "system"
#ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"
ctk.set_default_color_theme("C:\\Users\\stmar\\Documents\\RDFSemester1\\Semester_3_4\\Projektarbeit\\fanlytix\\ctk_testumgebung\\teststyle.json")  # "blue", "green", "dark-blue"

# Hauptfenster
root = ctk.CTk()
root.title("CustomTkinter Demo")
root.geometry("500x400")

# Label
label = ctk.CTkLabel(root, text="Willkommen in der CTk-Demo!", font=("Arial", 18))
label.pack(pady=20)

# Buttons
btn1 = ctk.CTkButton(root, text="Standard Button")
btn1.pack(pady=10)

btn2 = ctk.CTkButton(root, text="Grüner Button", fg_color="green", hover_color="darkgreen")
btn2.pack(pady=10)

btn3 = ctk.CTkButton(root, text="Outline Button", fg_color="transparent", border_width=2, border_color="blue")
btn3.pack(pady=10)

# Checkboxen
checkbox1 = ctk.CTkCheckBox(root, text="Option A")
checkbox1.pack(pady=5)

checkbox2 = ctk.CTkCheckBox(root, text="Option B")
checkbox2.pack(pady=5)

# Radiobuttons
radio_var = ctk.IntVar(value=0)
radio1 = ctk.CTkRadioButton(root, text="Auswahl 1", variable=radio_var, value=1)
radio2 = ctk.CTkRadioButton(root, text="Auswahl 2", variable=radio_var, value=2)
radio1.pack(pady=5)
radio2.pack(pady=5)

# Eingabefeld
entry = ctk.CTkEntry(root, placeholder_text="Hier etwas eingeben...")
entry.pack(pady=20)

# Schieberegler
slider = ctk.CTkSlider(root, from_=0, to=100, number_of_steps=10)
slider.pack(pady=10)

# Switch (Toggle)
switch = ctk.CTkSwitch(root, text="Dark Mode?")
switch.pack(pady=10)

# Start der Anwendung
root.mainloop()
