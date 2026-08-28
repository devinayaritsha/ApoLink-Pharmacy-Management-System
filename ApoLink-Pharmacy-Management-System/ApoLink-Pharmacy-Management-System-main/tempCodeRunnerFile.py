import sys
import os

# Memaksa macOS agar tetap merender aplikasi dalam tampilan Light Mode
if sys.platform == "darwin":
    os.environ["NSRequiresAquaSystemAppearance"] = "True"

from login import show_login
from dashboard import open_dashboard

if __name__ == "__main__":
    # Jalankan form login -> Jika sukses, panggil open_dashboard
    show_login(open_dashboard)