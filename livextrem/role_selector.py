import customtkinter as ctk

class RoleSelectorWindow(ctk.CTk):

    def __init__(self, session):
        super().__init__()

        self.session = session
        self.title("Rollen auswählen")
        self.geometry("400x400")
        self.configure(fg_color="white")

        ctk.CTkLabel(self, text=f"Angemeldet als: {self.session.display_name}",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 10))

        ctk.CTkLabel(self, text="Wähle ein Dashboard:",
                     font=ctk.CTkFont(size=14)).pack(pady=(0, 20))

        # STREAMER sieht ALLES
        if self.session.is_streamer:
            self._add_streamer_button()
            self._add_manager_button()
            self._add_moderator_button()
            return

        # Manager sieht NUR Manager
        if self.session.is_manager:
            self._add_manager_button()
            return

        # Moderator sieht nur Mod
        if self.session.is_moderator:
            self._add_moderator_button()
            return

        ctk.CTkLabel(self, text="Keine Rolle vorhanden.", text_color="red").pack(pady=20)


    # ====== BUTTON BUILDER ======
    def _add_streamer_button(self):
        ctk.CTkButton(self, text="Streamer Dashboard",
                      fg_color="#1c31ba", hover_color="#14375e",
                      command=self.open_streamer_dashboard).pack(pady=10, fill="x", padx=40)

    def _add_manager_button(self):
        ctk.CTkButton(self, text="Manager Dashboard",
                      fg_color="#1c31ba", hover_color="#14375e",
                      command=self.open_manager_dashboard).pack(pady=10, fill="x", padx=40)

    def _add_moderator_button(self):
        ctk.CTkButton(self, text="Moderator Dashboard",
                      fg_color="#1c31ba", hover_color="#14375e",
                      command=self.open_moderator_dashboard).pack(pady=10, fill="x", padx=40)

    # ====== OPEN DASHBOARDS (WICHTIG: OHNE mainloop!) ======

    def open_streamer_dashboard(self):
        #from streamer_dashboard import StreamerDashboard
        self.destroy()
        #StreamerDashboard()

    def open_manager_dashboard(self):
        from manager_gui import ManagerDashboard
        self.withdraw()
        ManagerDashboard()

    def open_moderator_dashboard(self):
        print("MD")
        #from moderator_dashboard import ModeratorDashboard
        #self.withdraw()
        #ModeratorDashboard()
