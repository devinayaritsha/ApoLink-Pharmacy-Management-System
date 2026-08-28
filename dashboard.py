import sys
import os

if sys.platform == "darwin":
    os.environ["NSRequiresAquaSystemAppearance"] = "True"

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
from datetime import datetime, timedelta

# Helper CustomButton agar warna tombol responsive & tidak tertimpa macOS Aqua engine
def CustomButton(parent, text, command, bg="#34A853", fg="white", font=("Calibri", 10, "bold"), padx=10, pady=5):
    btn_frame = tk.Frame(parent, bg=bg, cursor="hand2")
    lbl = tk.Label(btn_frame, text=text, bg=bg, fg=fg, font=font, padx=padx, pady=pady)
    lbl.pack(fill=tk.BOTH, expand=True)
    
    lbl.bind("<Button-1>", lambda e: command())
    btn_frame.bind("<Button-1>", lambda e: command())
    return btn_frame

# ================= DATABASE IN-MEMORY =================
users_db = [
    {"nama": "Administrator", "username": "admin", "password": "123", "role": "Admin"},
    {"nama": "Budi Kasir", "username": "budi", "password": "123", "role": "Kasir"},
    {"nama": "Siti Apoteker", "username": "siti", "password": "123", "role": "Apoteker"}
]

products = [
    {"nama": "Paracetamol 500mg", "kategori": "Obat", "harga": 5000, "stok": 50, "tgl_exp": "2026-12-31"},
    {"nama": "Alkohol 70%", "kategori": "Alkes", "harga": 12000, "stok": 4, "tgl_exp": "2026-09-15"},
    {"nama": "Kasa Steril", "kategori": "BHP", "harga": 15000, "stok": 2, "tgl_exp": "2026-08-01"},
    {"nama": "Amoxicillin 500mg", "kategori": "Obat", "harga": 8000, "stok": 20, "tgl_exp": "2027-05-20"},
    {"nama": "Vitamin C 1000mg", "kategori": "Obat", "harga": 10000, "stok": 30, "tgl_exp": "2026-09-01"}
]

pasien_list = [
    {"nama": "Budi Santoso", "kontak": "08123456789"},
    {"nama": "Siti Aminah", "kontak": "08567890123"}
]

suppliers = [
    {"nama": "PT Kimia Farma", "alamat": "Jl. Veteran No. 10", "kontak": "021-5551234"}
]

stok_opname_list = []
transaksi_history = []
cart = []

current_user = None

def open_dashboard():
    main_app()

def main_app():
    root = tk.Tk()
    root.title("ApoLink - Integrated Pharmacy System")
    
    if sys.platform == "darwin":
        root.attributes('-fullscreen', True)
    else:
        root.state('zoomed') 
        
    root.configure(bg="#F4F6F9")

    # Styling TTK khusus macOS agar Treeview (Tabel) & Combobox tidak terpengaruh Dark Mode
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Treeview", 
                    background="white", 
                    foreground="black", 
                    fieldbackground="white", 
                    rowheight=25)
    style.configure("Treeview.Heading", 
                    background="#E0E0E0", 
                    foreground="black", 
                    font=("Calibri", 10, "bold"))
    style.configure("TCombobox", fieldbackground="white", background="#E0E0E0", foreground="black")

    # Pemindai otomatis agar SEMUA tk.Label & tk.Entry berwarna tegas hitam
    def apply_responsive_styles(parent):
        for widget in parent.winfo_children():
            if isinstance(widget, tk.Label) and widget.cget("fg") in ["", "SystemButtonText", "gray"]:
                widget.configure(fg="#333333")
            elif isinstance(widget, tk.Entry):
                widget.configure(fg="black", insertbackground="black")
            if widget.winfo_children():
                apply_responsive_styles(widget)

    # ================= 0. SYSTEM LOGIN SCREEN =================
    def show_login():
        for widget in root.winfo_children():
            widget.destroy()

        login_frame = tk.Frame(root, bg="white", padx=35, pady=35, bd=1, relief="solid")
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(login_frame, text="ApoLink System", font=("Calibri", 22, "bold"), bg="white", fg="#1E8E3E").pack(pady=(0, 20))

        tk.Label(login_frame, text="Username:", bg="white", fg="#333333", font=("Calibri", 11, "bold")).pack(anchor="w")
        ent_user = tk.Entry(login_frame, font=("Calibri", 11), width=25, bg="#F9F9F9", fg="black", relief="solid", bd=1)
        ent_user.pack(pady=(0, 10), ipady=3)

        tk.Label(login_frame, text="Password:", bg="white", fg="#333333", font=("Calibri", 11, "bold")).pack(anchor="w")
        ent_pass = tk.Entry(login_frame, font=("Calibri", 11), width=25, show="*", bg="#F9F9F9", fg="black", relief="solid", bd=1)
        ent_pass.pack(pady=(0, 20), ipady=3)

        def process_login():
            global current_user
            u_in = ent_user.get()
            p_in = ent_pass.get()

            user_found = next((u for u in users_db if u["username"] == u_in and u["password"] == p_in), None)

            if user_found:
                current_user = user_found
                show_dashboard_layout()
            else:
                msgbox.showerror("Login Gagal", "Username atau Password salah!")

        btn_login = CustomButton(login_frame, text="LOGIN", command=process_login, bg="#1E8E3E", pady=6)
        btn_login.pack(fill=tk.X)

    # ================= UTAMA LAYOUT SETELAH LOGIN =================
    def show_dashboard_layout():
        for widget in root.winfo_children():
            widget.destroy()

        # Top Header Bar
        header = tk.Frame(root, bg="white", height=45, bd=1, relief="solid")
        header.pack(side=tk.TOP, fill=tk.X)

        tk.Label(header, text="ApoLink Pharmacy System", font=("Calibri", 12, "bold"), bg="white", fg="#1E8E3E").pack(side=tk.LEFT, padx=15, pady=8)

        # User Greeting & Logout
        user_info_frame = tk.Frame(header, bg="white")
        user_info_frame.pack(side=tk.RIGHT, padx=15, pady=5)

        lbl_user = tk.Label(user_info_frame, text=f"Welcome, {current_user['nama']}! ({current_user['role']})", font=("Calibri", 11, "bold"), bg="white", fg="#333333")
        lbl_user.pack(side=tk.LEFT, padx=(0, 10))

        def logout():
            global current_user
            if msgbox.askyesno("Logout", "Apakah Anda yakin ingin keluar?"):
                current_user = None
                show_login()

        btn_logout = CustomButton(user_info_frame, text="🚪 Logout", command=logout, bg="#D84315", padx=8, pady=3)
        btn_logout.pack(side=tk.RIGHT)

        # Main Body
        body = tk.Frame(root, bg="#F4F6F9")
        body.pack(fill=tk.BOTH, expand=True)

        sidebar = tk.Frame(body, bg="#1E8E3E", width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        content = tk.Frame(body, bg="white", padx=20, pady=20)
        content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        def clear_content():
            for widget in content.winfo_children():
                widget.destroy()

        # 1. DASHBOARD
        def show_dashboard():
            clear_content()
            tk.Label(content, text="Dashboard Ringkasan", font=("Calibri", 18, "bold"), bg="white", fg="#1E8E3E").pack(anchor="w", pady=(0, 15))

            cards_frame = tk.Frame(content, bg="white")
            cards_frame.pack(fill=tk.X, pady=10)

            today = datetime.now().date()
            stok_kritis = sum(1 for p in products if p['stok'] <= 5)
            
            exp_count = 0
            for p in products:
                try:
                    exp_date = datetime.strptime(p['tgl_exp'], "%Y-%m-%d").date()
                    if exp_date <= today:
                        exp_count += 1
                except ValueError:
                    pass

            def make_card(parent, title, val, color):
                box = tk.Frame(parent, bg=color, padx=15, pady=15, width=150)
                box.pack(side=tk.LEFT, padx=5)
                tk.Label(box, text=title, bg=color, fg="white", font=("Calibri", 10)).pack()
                tk.Label(box, text=str(val), bg=color, fg="white", font=("Calibri", 20, "bold")).pack()

            make_card(cards_frame, "Total Produk", len(products), "#2E7D32")
            make_card(cards_frame, "Stok Kritis (≤5)", stok_kritis, "#00838F")
            make_card(cards_frame, "Expired / Lewat", exp_count, "#D84315")
            make_card(cards_frame, "Total Pasien", len(pasien_list), "#6A1B9A")

        # 2. KASIR
        def show_kasir():
            clear_content()
            cart.clear()

            tk.Label(content, text="Kasir & Pembayaran", font=("Calibri", 18, "bold"), bg="white", fg="#1E8E3E").pack(anchor="w", pady=(0, 10))

            f_in = tk.Frame(content, bg="white")
            f_in.pack(fill=tk.X, pady=5)

            tk.Label(f_in, text="Pasien:", bg="white", fg="#333333").grid(row=0, column=0, sticky="w")
            ent_pasien = tk.Entry(f_in, width=23, bg="white", fg="black")
            ent_pasien.grid(row=0, column=1, padx=5, pady=5)
            ent_pasien.insert(0, "Umum")

            tk.Label(f_in, text="Pilih Produk:", bg="white", fg="#333333").grid(row=1, column=0, sticky="w")
            all_product_names = [p["nama"] for p in products]
            cb_prod = ttk.Combobox(f_in, values=all_product_names, width=20)
            cb_prod.grid(row=1, column=1, padx=5, pady=5)

            def on_keyrelease(event):
                if event.keysym in ("Up", "Down", "Return", "Escape"): return
                typed = cb_prod.get().lower()
                if typed == '':
                    cb_prod['values'] = all_product_names
                else:
                    filtered = [item for item in all_product_names if typed in item.lower()]
                    cb_prod['values'] = filtered
                    cb_prod.event_generate('<Down>')

            cb_prod.bind('<KeyRelease>', on_keyrelease)

            tk.Label(f_in, text="Qty:", bg="white", fg="#333333").grid(row=1, column=2, padx=(10, 0))
            ent_qty = tk.Entry(f_in, width=5, bg="white", fg="black")
            ent_qty.grid(row=1, column=3, padx=5)
            ent_qty.insert(0, "1")

            tree = ttk.Treeview(content, columns=("Nama", "Harga", "Qty", "Subtotal"), show="headings", height=8)
            for c in ("Nama", "Harga", "Qty", "Subtotal"):
                tree.heading(c, text=c)
                tree.column(c, width=120, anchor="center")
            tree.pack(fill=tk.BOTH, expand=True, pady=10)

            f_bottom = tk.Frame(content, bg="white")
            f_bottom.pack(fill=tk.X, pady=5)

            lbl_total = tk.Label(f_bottom, text="Total: Rp 0", font=("Calibri", 14, "bold"), bg="white", fg="#1E8E3E")
            lbl_total.pack(side=tk.RIGHT)

            def update_total():
                tot = sum(c["subtotal"] for c in cart)
                lbl_total.config(text=f"Total: Rp {tot:,}")

            def tambah():
                p_name = cb_prod.get()
                qty_s = ent_qty.get()
                item = next((p for p in products if p["nama"] == p_name), None)
                
                if not item:
                    msgbox.showwarning("Peringatan", "Produk tidak ditemukan!")
                    return
                if qty_s.isdigit() and int(qty_s) > 0:
                    q = int(qty_s)
                    if q > item["stok"]:
                        msgbox.showwarning("Stok Kurang", f"Stok tersedia hanya {item['stok']}!")
                        return
                    
                    sub = item["harga"] * q
                    cart.append({"nama": p_name, "harga": item["harga"], "qty": q, "subtotal": sub, "ref": item})
                    tree.insert("", tk.END, values=(p_name, f"Rp {item['harga']:,}", q, f"Rp {sub:,}"))
                    update_total()
                    cb_prod.set("")
                    cb_prod['values'] = all_product_names

            def hapus_item():
                selected = tree.selection()
                if selected:
                    idx = tree.index(selected[0])
                    del cart[idx]
                    tree.delete(selected[0])
                    update_total()

            def cetak_struk():
                if not cart:
                    msgbox.showwarning("Peringatan", "Keranjang belanjaan masih kosong!")
                    return
                
                nama_pasien = ent_pasien.get() or "Umum"
                total_bayar = sum(c["subtotal"] for c in cart)
                waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                for item in cart:
                    item["ref"]["stok"] -= item["qty"]
                    transaksi_history.append({
                        "waktu": waktu,
                        "pasien": nama_pasien,
                        "produk": item["nama"],
                        "qty": item["qty"],
                        "total": item["subtotal"]
                    })

                win_struk = tk.Toplevel(root)
                win_struk.title("Struk Transaksi - ApoLink")
                win_struk.geometry("350x450")
                win_struk.configure(bg="white")

                txt = tk.Text(win_struk, font=("Courier", 10), bg="white", fg="black", bd=0, padx=10, pady=10)
                txt.pack(fill=tk.BOTH, expand=True)

                struk_text = f"{'APOLINK PHARMACY':^32}\n"
                struk_text += f"{'Jl. Kesehatan No. 123':^32}\n"
                struk_text += "="*32 + "\n"
                struk_text += f"Kasir: {current_user['nama']}\n"
                struk_text += f"Tgl: {waktu}\n"
                struk_text += f"Pasien: {nama_pasien}\n"
                struk_text += "-"*32 + "\n"
                
                for c in cart:
                    struk_text += f"{c['nama'][:20]:<20}\n"
                    struk_text += f"  {c['qty']} x {c['harga']:,} = Rp{c['subtotal']:,}\n"
                
                struk_text += "="*32 + "\n"
                struk_text += f"TOTAL      : Rp {total_bayar:,}\n"
                struk_text += "="*32 + "\n"
                struk_text += f"{'Terima Kasih Semoga Lekas Sembuh':^32}\n"

                txt.insert(tk.END, struk_text)
                txt.config(state=tk.DISABLED)

                msgbox.showinfo("Sukses", "Transaksi berhasil dan stok telah diperbarui!")
                cart.clear()
                show_kasir()

            CustomButton(f_in, text="+ Tambah", command=tambah, bg="#34A853").grid(row=1, column=4, padx=5)
            
            btn_action_frame = tk.Frame(f_bottom, bg="white")
            btn_action_frame.pack(side=tk.LEFT)
            
            btn_h = CustomButton(btn_action_frame, text="🗑 Hapus Item", command=hapus_item, bg="#D84315")
            btn_h.pack(side=tk.LEFT, padx=2)
            
            btn_c = CustomButton(btn_action_frame, text="🖨 Cetak Struk / Bayar", command=cetak_struk, bg="#1E8E3E")
            btn_c.pack(side=tk.LEFT, padx=5)

        # 3. KELOLA PRODUK
        # 3. KELOLA PRODUK (Diperbarui dengan Pop-up Riwayat UX Friendly)
        def show_produk():
            clear_content()
            tk.Label(content, text="Kelola Data Produk (Obat/Alkes/BHP)", font=("Calibri", 18, "bold"), bg="white", fg="#1E8E3E").pack(anchor="w", pady=(0, 10))

            f_form = tk.Frame(content, bg="white")
            f_form.pack(fill=tk.X, pady=5)

            tk.Label(f_form, text="Nama:", bg="white", fg="#333333").grid(row=0, column=0, sticky="w"); e_nama = tk.Entry(f_form, bg="white", fg="black"); e_nama.grid(row=0, column=1, padx=5, pady=2)
            tk.Label(f_form, text="Kategori:", bg="white", fg="#333333").grid(row=0, column=2, sticky="w"); cb_k = ttk.Combobox(f_form, values=["Obat", "Alkes", "BHP"], width=17); cb_k.grid(row=0, column=3, padx=5, pady=2)
            tk.Label(f_form, text="Harga:", bg="white", fg="#333333").grid(row=1, column=0, sticky="w"); e_hrg = tk.Entry(f_form, bg="white", fg="black"); e_hrg.grid(row=1, column=1, padx=5, pady=2)
            tk.Label(f_form, text="Stok:", bg="white", fg="#333333").grid(row=1, column=2, sticky="w"); e_stk = tk.Entry(f_form, bg="white", fg="black"); e_stk.grid(row=1, column=3, padx=5, pady=2)
            
            tk.Label(f_form, text="Tgl Exp (YYYY-MM-DD):", bg="white", fg="#333333").grid(row=2, column=0, sticky="w"); e_exp = tk.Entry(f_form, bg="white", fg="black"); e_exp.grid(row=2, column=1, padx=5, pady=2)
            e_exp.insert(0, datetime.now().strftime("%Y-%m-%d"))

            tree = ttk.Treeview(content, columns=("Nama", "Kategori", "Harga", "Stok", "Tgl Exp"), show="headings", height=8)
            for c in ("Nama", "Kategori", "Harga", "Stok", "Tgl Exp"):
                tree.heading(c, text=c)
                tree.column(c, anchor="center")
            tree.pack(fill=tk.BOTH, expand=True, pady=10)

            def refresh_table():
                for r in tree.get_children(): tree.delete(r)
                for p in products: tree.insert("", tk.END, values=(p["nama"], p["kategori"], f"Rp {p['harga']:,}", p["stok"], p.get("tgl_exp", "-")))

            # Pop-up Riwayat Stok yang Compact & UX Friendly
            def show_history_popup(event=None):
                selected = tree.selection()
                if not selected:
                    msgbox.showinfo("Info", "Silakan pilih produk terlebih dahulu!")
                    return

                item_values = tree.item(selected[0])['values']
                nama_produk = item_values[0]

                # Toplevel Modal khusus
                win_hist = tk.Toplevel(root)
                win_hist.title(f"Riwayat Transaksi - {nama_produk}")
                
                # Mengatur Ukuran Pop-up & Posisikan Tepat di Tengah Layar
                w_width, w_height = 550, 380
                scr_w = win_hist.winfo_screenwidth()
                scr_h = win_hist.winfo_screenheight()
                x_c = int((scr_w / 2) - (w_width / 2))
                y_c = int((scr_h / 2) - (w_height / 2))
                win_hist.geometry(f"{w_width}x{w_height}+{x_c}+{y_c}")
                
                win_hist.resizable(False, False)
                win_hist.configure(bg="white")
                win_hist.transient(root) # Tetap melayang di atas jendela utama
                win_hist.grab_set()    # Fokus ke modal saja

                tk.Label(win_hist, text=f"Riwayat Transaksi: {nama_produk}", font=("Calibri", 13, "bold"), bg="white", fg="#1E8E3E").pack(pady=(15, 5))

                tree_h = ttk.Treeview(win_hist, columns=("Waktu", "Pasien", "Qty", "Total Harga"), show="headings", height=8)
                tree_h.heading("Waktu", text="Waktu")
                tree_h.heading("Pasien", text="Pasien")
                tree_h.heading("Qty", text="Qty")
                tree_h.heading("Total Harga", text="Total Harga")

                tree_h.column("Waktu", width=140, anchor="center")
                tree_h.column("Pasien", width=130, anchor="w")
                tree_h.column("Qty", width=60, anchor="center")
                tree_h.column("Total Harga", width=120, anchor="e")

                tree_h.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

                filtered_history = [t for t in transaksi_history if t["produk"] == nama_produk]

                if not filtered_history:
                    tree_h.insert("", tk.END, values=("-", "Belum ada transaksi", "-", "-"))
                else:
                    for h in filtered_history:
                        tree_h.insert("", tk.END, values=(h["waktu"], h["pasien"], h["qty"], f"Rp {h['total']:,}"))

                # Tombol Tutup UX Friendly
                btn_close = CustomButton(win_hist, text="Tutup / Close", command=win_hist.destroy, bg="#D84315", padx=15, pady=4)
                btn_close.pack(pady=(0, 15))

            tree.bind("<Double-1>", show_history_popup)

            def simpan():
                if e_nama.get() and e_hrg.get().isdigit() and e_stk.get().isdigit():
                    products.append({
                        "nama": e_nama.get(), 
                        "kategori": cb_k.get(), 
                        "harga": int(e_hrg.get()), 
                        "stok": int(e_stk.get()),
                        "tgl_exp": e_exp.get()
                    })
                    refresh_table()
                    e_nama.delete(0, tk.END); e_hrg.delete(0, tk.END); e_stk.delete(0, tk.END)

            def hapus():
                selected = tree.selection()
                if selected:
                    idx = tree.index(selected[0])
                    del products[idx]
                    refresh_table()

            f_btn = tk.Frame(content, bg="white")
            f_btn.pack(fill=tk.X)
            
            btn_s = CustomButton(f_form, text="Simpan", command=simpan, bg="#34A853")
            btn_s.grid(row=2, column=4, padx=5)
            
            btn_h = CustomButton(f_btn, text="🗑 Hapus Produk Selected", command=hapus, bg="#D84315")
            btn_h.pack(side=tk.LEFT)
            
            btn_r = CustomButton(f_btn, text="📜 Lihat Riwayat Stok", command=show_history_popup, bg="#00838F")
            btn_r.pack(side=tk.LEFT, padx=5)
            
            refresh_table()

        # 4. KELOLA USER
        def show_kelola_user():
            clear_content()
            tk.Label(content, text="Kelola Akun Pengguna / User System", font=("Calibri", 18, "bold"), bg="white", fg="#1E8E3E").pack(anchor="w", pady=(0, 10))

            f_form = tk.Frame(content, bg="white")
            f_form.pack(fill=tk.X, pady=5)

            tk.Label(f_form, text="Nama Lengkap:", bg="white", fg="#333333").grid(row=0, column=0, sticky="w"); e_nama = tk.Entry(f_form, bg="white", fg="black"); e_nama.grid(row=0, column=1, padx=5, pady=2)
            tk.Label(f_form, text="Username:", bg="white", fg="#333333").grid(row=0, column=2, sticky="w"); e_user = tk.Entry(f_form, bg="white", fg="black"); e_user.grid(row=0, column=3, padx=5, pady=2)
            tk.Label(f_form, text="Password:", bg="white", fg="#333333").grid(row=1, column=0, sticky="w"); e_pass = tk.Entry(f_form, bg="white", fg="black"); e_pass.grid(row=1, column=1, padx=5, pady=2)
            tk.Label(f_form, text="Role:", bg="white", fg="#333333").grid(row=1, column=2, sticky="w"); cb_role = ttk.Combobox(f_form, values=["Admin", "Kasir", "Apoteker"], width=17); cb_role.grid(row=1, column=3, padx=5, pady=2); cb_role.set("Kasir")

            tree = ttk.Treeview(content, columns=("Nama", "Username", "Role"), show="headings", height=8)
            for c in ("Nama", "Username", "Role"):
                tree.heading(c, text=c)
                tree.column(c, anchor="center")
            tree.pack(fill=tk.BOTH, expand=True, pady=10)

            def refresh():
                for r in tree.get_children(): tree.delete(r)
                for u in users_db: tree.insert("", tk.END, values=(u["nama"], u["username"], u["role"]))

            def simpan():
                if e_nama.get() and e_user.get() and e_pass.get():
                    users_db.append({
                        "nama": e_nama.get(),
                        "username": e_user.get(),
                        "password": e_pass.get(),
                        "role": cb_role.get()
                    })
                    refresh()
                    e_nama.delete(0, tk.END); e_user.delete(0, tk.END); e_pass.delete(0, tk.END)
                    msgbox.showinfo("Sukses", "User baru berhasil ditambahkan!")

            def hapus():
                selected = tree.selection()
                if selected:
                    idx = tree.index(selected[0])
                    if users_db[idx]["username"] == current_user["username"]:
                        msgbox.showwarning("Peringatan", "Anda tidak bisa menghapus akun Anda sendiri yang sedang aktif!")
                        return
                    del users_db[idx]
                    refresh()

            btn_t = CustomButton(f_form, text="Tambah User", command=simpan, bg="#34A853")
            btn_t.grid(row=1, column=4, padx=5)
            
            btn_h = CustomButton(content, text="🗑 Hapus User Selected", command=hapus, bg="#D84315")
            btn_h.pack(anchor="w")
            
            refresh()

        # 5. LAPORAN KEDALUWARSA
        def show_lap_expired():
            clear_content()
            tk.Label(content, text="⚠️ Laporan Obat / Goods Kedaluwarsa", font=("Calibri", 18, "bold"), bg="white", fg="#1E8E3E").pack(anchor="w", pady=(0, 10))

            tree_exp = ttk.Treeview(content, columns=("Nama Barang", "Kategori", "Stok", "Tgl Expired", "Status Expired"), show="headings", height=12)
            for c in ("Nama Barang", "Kategori", "Stok", "Tgl Expired", "Status Expired"):
                tree_exp.heading(c, text=c)
                tree_exp.column(c, anchor="center")
            tree_exp.pack(fill=tk.BOTH, expand=True, pady=10)

            today = datetime.now().date()
            warning_limit = today + timedelta(days=30)

            for p in products:
                tgl_str = p.get("tgl_exp", "")
                status = "🟢 Aman"
                try:
                    exp_date = datetime.strptime(tgl_str, "%Y-%m-%d").date()
                    if exp_date <= today:
                        status = "🔴 KEDALUWARSA"
                    elif exp_date <= warning_limit:
                        status = "🟡 SEGERA EXP (≤30 Hari)"
                except ValueError:
                    status = "❓ Format Tgl Salah"

                tree_exp.insert("", tk.END, values=(p["nama"], p["kategori"], p["stok"], tgl_str, status))

        # 6. KELOLA PASIEN
        def show_pasien():
            clear_content()
            tk.Label(content, text="Kelola Data Pasien", font=("Calibri", 18, "bold"), bg="white", fg="#1E8E3E").pack(anchor="w", pady=(0, 10))

            f_form = tk.Frame(content, bg="white")
            f_form.pack(fill=tk.X, pady=5)

            tk.Label(f_form, text="Nama Pasien:", bg="white", fg="#333333").grid(row=0, column=0); e_nama = tk.Entry(f_form, bg="white", fg="black"); e_nama.grid(row=0, column=1, padx=5)
            tk.Label(f_form, text="Kontak / WA:", bg="white", fg="#333333").grid(row=0, column=2); e_kontak = tk.Entry(f_form, bg="white", fg="black"); e_kontak.grid(row=0, column=3, padx=5)

            tree = ttk.Treeview(content, columns=("Nama", "Kontak"), show="headings", height=8)
            for c in ("Nama", "Kontak"):
                tree.heading(c, text=c)
                tree.column(c, anchor="center")
            tree.pack(fill=tk.BOTH, expand=True, pady=10)

            def refresh():
                for r in tree.get_children(): tree.delete(r)
                for p in pasien_list: tree.insert("", tk.END, values=(p["nama"], p["kontak"]))

            def simpan():
                if e_nama.get():
                    pasien_list.append({"nama": e_nama.get(), "kontak": e_kontak.get()})
                    refresh()
                    e_nama.delete(0, tk.END); e_kontak.delete(0, tk.END)

            def hapus():
                selected = tree.selection()
                if selected:
                    idx = tree.index(selected[0])
                    del pasien_list[idx]
                    refresh()

            btn_t = CustomButton(f_form, text="Tambah Pasien", command=simpan, bg="#34A853")
            btn_t.grid(row=0, column=4, padx=5)
            
            btn_h = CustomButton(content, text="🗑 Hapus Pasien Selected", command=hapus, bg="#D84315")
            btn_h.pack(anchor="w")
            
            refresh()

        # 7. KELOLA SUPPLIER
        def show_supplier():
            clear_content()
            tk.Label(content, text="Kelola Data Supplier", font=("Calibri", 18, "bold"), bg="white", fg="#1E8E3E").pack(anchor="w", pady=(0, 10))

            f_form = tk.Frame(content, bg="white")
            f_form.pack(fill=tk.X, pady=5)

            tk.Label(f_form, text="Nama Supplier:", bg="white", fg="#333333").grid(row=0, column=0, sticky="w"); e_nama = tk.Entry(f_form, bg="white", fg="black"); e_nama.grid(row=0, column=1, padx=5, pady=2)
            tk.Label(f_form, text="Alamat:", bg="white", fg="#333333").grid(row=0, column=2, sticky="w"); e_alamat = tk.Entry(f_form, bg="white", fg="black"); e_alamat.grid(row=0, column=3, padx=5, pady=2)
            tk.Label(f_form, text="Contact:", bg="white", fg="#333333").grid(row=1, column=0, sticky="w"); e_contact = tk.Entry(f_form, bg="white", fg="black"); e_contact.grid(row=1, column=1, padx=5, pady=2)

            tree = ttk.Treeview(content, columns=("Nama", "Alamat", "Contact"), show="headings", height=8)
            for c in ("Nama", "Alamat", "Contact"):
                tree.heading(c, text=c)
                tree.column(c, anchor="center")
            tree.pack(fill=tk.BOTH, expand=True, pady=10)

            def refresh():
                for r in tree.get_children(): tree.delete(r)
                for s in suppliers: tree.insert("", tk.END, values=(s["nama"], s["alamat"], s["kontak"]))

            def simpan():
                if e_nama.get():
                    suppliers.append({"nama": e_nama.get(), "alamat": e_alamat.get(), "kontak": e_contact.get()})
                    refresh()
                    e_nama.delete(0, tk.END); e_alamat.delete(0, tk.END); e_contact.delete(0, tk.END)

            def hapus():
                selected = tree.selection()
                if selected:
                    idx = tree.index(selected[0])
                    del suppliers[idx]
                    refresh()

            btn_s = CustomButton(f_form, text="Simpan Supplier", command=simpan, bg="#34A853")
            btn_s.grid(row=1, column=4, padx=5)
            
            btn_h = CustomButton(content, text="🗑 Hapus Supplier Selected", command=hapus, bg="#D84315")
            btn_h.pack(anchor="w")
            
            refresh()

        # 8. STOK OPNAME
        def show_stok_opname():
            clear_content()
            tk.Label(content, text="Stok Opname (Penyesuaian Fisik)", font=("Calibri", 18, "bold"), bg="white", fg="#1E8E3E").pack(anchor="w", pady=(0, 10))

            f_form = tk.Frame(content, bg="white")
            f_form.pack(fill=tk.X, pady=5)

            tk.Label(f_form, text="Pilih Item:", bg="white", fg="#333333").grid(row=0, column=0, sticky="w")
            cb_item = ttk.Combobox(f_form, values=[p["nama"] for p in products], width=20)
            cb_item.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(f_form, text="Stok Sistem:", bg="white", fg="#333333").grid(row=0, column=2, padx=5)
            lbl_sys_stok = tk.Label(f_form, text="0", bg="#E0E0E0", fg="black", width=8, font=("Calibri", 10, "bold"))
            lbl_sys_stok.grid(row=0, column=3, padx=5)

            tk.Label(f_form, text="Stok Fisik:", bg="white", fg="#333333").grid(row=0, column=4, padx=5)
            ent_fisik = tk.Entry(f_form, width=8, bg="white", fg="black")
            ent_fisik.grid(row=0, column=5, padx=5)

            def auto_load_stok(event=None):
                p = next((x for x in products if x["nama"] == cb_item.get()), None)
                if p:
                    lbl_sys_stok.config(text=str(p["stok"]))

            cb_item.bind("<<ComboboxSelected>>", auto_load_stok)

            tree = ttk.Treeview(content, columns=("Nama Barang", "Stok Sistem", "Stok Fisik", "Selisih"), show="headings", height=8)
            for c in ("Nama Barang", "Stok Sistem", "Stok Fisik", "Selisih"):
                tree.heading(c, text=c)
                tree.column(c, anchor="center")
            tree.pack(fill=tk.BOTH, expand=True, pady=10)

            def refresh():
                for r in tree.get_children(): tree.delete(r)
                for o in stok_opname_list:
                    tree.insert("", tk.END, values=(o["nama"], o["sistem"], o["fisik"], o["selisih"]))

            def simpan_opname():
                p_name = cb_item.get()
                fisik_s = ent_fisik.get()
                prod = next((x for x in products if x["nama"] == p_name), None)

                if prod and fisik_s.isdigit():
                    fisik = int(fisik_s)
                    selisih = fisik - prod["stok"]
                    prod["stok"] = fisik
                    
                    stok_opname_list.append({"nama": p_name, "sistem": prod["stok"], "fisik": fisik, "selisih": selisih})
                    refresh()
                    cb_item.set("")
                    lbl_sys_stok.config(text="0")
                    ent_fisik.delete(0, tk.END)
                    msgbox.showinfo("Sukses", f"Stok {p_name} diperbarui menjadi {fisik}!")

            def hapus_opname():
                selected = tree.selection()
                if selected:
                    idx = tree.index(selected[0])
                    del stok_opname_list[idx]
                    refresh()

            btn_p = CustomButton(f_form, text="Proses Opname", command=simpan_opname, bg="#34A853")
            btn_p.grid(row=0, column=6, padx=5)
            
            btn_h = CustomButton(content, text="🗑 Hapus Riwayat Selected", command=hapus_opname, bg="#D84315")
            btn_h.pack(anchor="w")
            
            refresh()

        # NAVIGATION SIDEBAR (DINAMIS)
        def btn_nav(txt, cmd):
            return tk.Button(sidebar, text=txt, command=cmd, bg="#1E8E3E", fg="white", font=("Calibri", 11, "bold"), bd=0, activebackground="#34A853", activeforeground="white", pady=10, anchor="w", padx=20)

        user_role = current_user["role"]

        btn_nav("📊 Dashboard", show_dashboard).pack(fill=tk.X)

        if user_role in ["Admin", "Kasir"]:
            btn_nav("🛒 Kasir", show_kasir).pack(fill=tk.X)
            btn_nav("👥 Kelola Pasien", show_pasien).pack(fill=tk.X)

        if user_role in ["Admin", "Apoteker"]:
            btn_nav("📦 Kelola Produk", show_produk).pack(fill=tk.X)
            btn_nav("⚠️ Lap. Kedaluwarsa", show_lap_expired).pack(fill=tk.X)
            btn_nav("🚚 Kelola Supplier", show_supplier).pack(fill=tk.X)
            btn_nav("⚖️ Stok Opname", show_stok_opname).pack(fill=tk.X)

        if user_role == "Admin":
            btn_nav("👤 Kelola User", show_kelola_user).pack(fill=tk.X)

        show_dashboard()

    show_login()
    
    # Memastikan warna teks terpoles hitam sepenuhnya sebelum aplikasi dirender
    apply_responsive_styles(root)
    root.mainloop()

if __name__ == "__main__":
    main_app()