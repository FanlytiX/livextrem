from tkinter import messagebox


def _open_streamer_dashboard(session):
    from streamer_dashboard import StreamerDashboard
    app = StreamerDashboard(session=session)
    app.mainloop()
    return True


def _open_moderator_dashboard(session):
    if not getattr(session, "can_access_moderator_dashboard", False):
        messagebox.showerror("Kein Zugriff", "Dieses Dashboard ist für diesen Benutzer nicht freigegeben.")
        return False

    import moderator_dashboard as md
    md.session = session
    if md.init_database():
        md.show_dashboard()
        md.app.mainloop()
        if getattr(md, "db", None):
            try:
                md.db.connClose()
            except Exception:
                pass
        return True
    return False


def _open_manager_dashboard(session):
    if not getattr(session, "can_access_manager_dashboard", False):
        messagebox.showerror("Kein Zugriff", "Dieses Dashboard ist für diesen Benutzer nicht freigegeben.")
        return False

    from manager_gui import ManagerDashboard
    app = ManagerDashboard(session=session)
    app.mainloop()
    return True


def open_dashboard(session, target=None):
    """Öffnet das passende Dashboard.

    target=None nutzt die Primärrolle.
    target kann außerdem 'streamer', 'moderator' oder 'manager' sein.
    """
    target = (target or "").strip().lower()

    if target == "streamer":
        return _open_streamer_dashboard(session)
    if target == "moderator":
        return _open_moderator_dashboard(session)
    if target == "manager":
        return _open_manager_dashboard(session)

    if session.is_streamer:
        return _open_streamer_dashboard(session)

    if session.is_moderator:
        return _open_moderator_dashboard(session)

    if session.is_manager:
        return _open_manager_dashboard(session)

    messagebox.showerror("Keine Rolle", "Dem Benutzer ist keine gültige Rolle zugewiesen.")
    return False
