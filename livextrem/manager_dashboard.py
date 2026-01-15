import os
import datetime
import calendar

import customtkinter as ctk
from PIL import Image

# ✅ kommt aus Modul 1
from data_manager import DataManager, Config, STREAMER_COLOR_CHOICES


from manager_gui import ManagerDashboard

if __name__ == "__main__":
    app = ManagerDashboard()
    app.mainloop()
