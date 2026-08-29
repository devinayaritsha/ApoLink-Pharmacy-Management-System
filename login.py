import sys
import os

if sys.platform == "darwin":
    os.environ["NSRequiresAquaSystemAppearance"] = "True"

import tkinter as tk
import tkinter.messagebox as msgbox

# ================= DATABASE USER DIPINDAHKAN KE SINI =================
users_db = [
    {"nama": "Administrator", "username": "admin", "password": "123", "role": "Admin"},
    {"nama": "Budi Setiawan", "username": "budi", "password": "123", "role": "Kasir"},
    {"nama": "Siti Aminah", "username": "siti", "password": "123", "role": "Apoteker"}
]

BG_MAIN = "#E6F4EA"
BG_ACCENT = "#34A853"
FG_TEXT = "#1E8E3E"

def CustomButton(parent, text, command, bg=BG_ACCENT, fg="white", font=('Calibri', 13, 'bold'), pady=8):
    btn_frame = tk.Frame(parent, bg=bg, cursor="hand2")
    lbl = tk.Label(btn_frame, text=text, bg=bg, fg=fg, font=font, pady=pady)
    lbl.pack(fill=tk.BOTH, expand=True)
    
    lbl.bind("<Button-1>", lambda e: command())
    btn_frame.bind("<Button-1>", lambda e: command())
    return btn_frame

def show_login(on_login_success):
    login_win = tk.Tk()
    login_win.title("ApoLink - System Login")
    
    if sys.platform == "darwin":
        login_win.attributes('-fullscreen', True)
    else:
        login_win.state('zoomed')
        
    login_win.configure(bg=BG_MAIN)

    frame_header = tk.Frame(login_win, bg=BG_MAIN)
    frame_header.pack(pady=(80, 20))

    lbl_title = tk.Label(frame_header, text="ApoLink Pharmacy System", bg=BG_MAIN, fg=FG_TEXT, font=('Calibri', 34, 'bold'))
    lbl_title.pack()
    
    lbl_subtitle = tk.Label(frame_header, text="Please enter your credentials to access the system", bg=BG_MAIN, fg="#555555", font=('Calibri', 14))
    lbl_subtitle.pack(pady=5)

    card_login = tk.Frame(login_win, bg="white", bd=1, relief="solid", padx=40, pady=30)
    card_login.pack(pady=20)

    lbl_card_title = tk.Label(card_login, text="User Login", bg="white", fg=FG_TEXT, font=('Calibri', 18, 'bold'))
    lbl_card_title.grid(row=0, column=0, columnspan=2, pady=(0, 20))

    tk.Label(card_login, text="Username", bg="white", fg="#333333", font=('Calibri', 12, 'bold')).grid(row=1, column=0, sticky="w", pady=(5, 2))
    input_username = tk.Entry(card_login, font=('Calibri', 14), width=28, bg="#F9F9F9", fg="black", insertbackground="black", relief="solid", bd=1)
    input_username.grid(row=2, column=0, columnspan=2, pady=(0, 15), ipady=5)

    tk.Label(card_login, text="Password", bg="white", fg="#333333", font=('Calibri', 12, 'bold')).grid(row=3, column=0, sticky="w", pady=(5, 2))
    input_password = tk.Entry(card_login, show="*", font=('Calibri', 14), width=28, bg="#F9F9F9", fg="black", insertbackground="black", relief="solid", bd=1)
    input_password.grid(row=4, column=0, columnspan=2, pady=(0, 20), ipady=5)

    def authenticate():
        username = input_username.get()
        password = input_password.get()

        user_found = next((u for u in users_db if u["username"] == username and u["password"] == password), None)

        if user_found:
            msgbox.showinfo("Success", f"Login Successful! Welcome, {user_found['nama']}.")
            login_win.destroy()  
            on_login_success(user_found, users_db)   
        else:
            msgbox.showerror("Error", "Invalid Username or Password!")

    button_login = CustomButton(card_login, text="LOGIN TO SYSTEM", command=authenticate, bg=BG_ACCENT)
    button_login.grid(row=5, column=0, columnspan=2, sticky="we")

    lbl_footer = tk.Label(login_win, text="© ApoLink Management System v1.0", bg=BG_MAIN, fg="#666666", font=('Calibri', 10))
    lbl_footer.pack(side="bottom", pady=20)

    login_win.mainloop()