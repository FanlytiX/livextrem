def open_dashboard(session):
    """Öffnet direkt das passende Dashboard – kein Rollen-Auswahlfenster mehr."""
    if session.is_streamer:
        from streamer_dashboard import StreamerDashboard
        app = StreamerDashboard(session=session)
        app.mainloop()
        return

    if session.is_moderator:
        import moderator_dashboard as md
        md.session = session  # Session für Streamer-Zuordnung (broadcaster_id)
        # Moderator-Dashboard ist als Skript gebaut – wir starten es kontrolliert.
        if md.init_database():
            # Twitch Login wird übersprungen, wenn bereits per oauth.gen() eingeloggt.
            md.twitch_login()
            md.show_dashboard()
            md.app.mainloop()
            if getattr(md, "db", None):
                try:
                    md.db.connClose()
                except Exception:
                    pass
        return

    if session.is_manager:
        from manager_gui import ManagerDashboard
        app = ManagerDashboard(session=session)
        app.mainloop()
        return

    # Fallback
    from tkinter import messagebox
    messagebox.showerror("Keine Rolle", "Dem Benutzer ist keine gültige Rolle zugewiesen.")