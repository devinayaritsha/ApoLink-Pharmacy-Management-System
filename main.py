import sys
import os

if sys.platform == "darwin":
    os.environ["NSRequiresAquaSystemAppearance"] = "True"

from login import show_login
from dashboard import open_dashboard

session = {
    "user": None,
    "db": None
}

def on_login_success(user, db):
    session["user"] = user
    session["db"] = db

if __name__ == "__main__":
    while True:
        session["user"] = None  # Reset sesi user setiap iterasi
        
        # 1. Tampilkan Halaman Login
        show_login(on_login_success)
        
        # 2. Jika user menutup window login (klik X) tanpa login, keluar dari program
        if not session["user"]:
            break
            
        # 3. Buka Halaman Dashboard (Menahan alur program sampai user klik Logout)
        open_dashboard(session["user"], session["db"])