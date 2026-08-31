import sys
import os

if sys.platform == "darwin":
    os.environ["NSRequiresAquaSystemAppearance"] = "True"

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
from datetime import datetime, timedelta

import db

def CustomButton(parent, text, command, bg="#34A853", fg="white", font=("Calibri", 10, "bold"), padx=10, pady=5):
    btn_frame = tk.Frame(parent, bg=bg, cursor="hand2")
    lbl = tk.Label(btn_frame, text=text, bg=bg, fg=fg, font=font, padx=padx, pady=pady)
    lbl.pack(fill=tk.BOTH, expand=True)
    
    lbl.bind("<Button-1>", lambda e: command())
    btn_frame.bind("<Button-1>", lambda e: command())
    return btn_frame

# ================= DATA SEKARANG DISIMPAN DI POSTGRESQL (lihat db.py) =================
# cart bersifat sementara per-sesi kasir (belanjaan yang belum di-checkout), jadi tetap
# di memori saja, tidak perlu tabel database.
cart = []

current_user = None

def open_dashboard(user_logged_in, db_users=None):
    global current_user
    current_user = user_logged_in
    main_app()

def main_app():
    root = tk.Tk()
    root.title("ApoLink - Integrated Pharmacy System")
    
    if sys.platform == "darwin":
        root.update_idletasks()
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        root.geometry(f"{screen_w}x{screen_h}+0+0")
    else:
        root.state('zoomed') 
        
    root.configure(bg="#F4F6F9")

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Treeview", background="white", foreground="black", fieldbackground="white", rowheight=25)
    style.configure("Treeview.Heading", background="#E0E0E0", foreground="black", font=("Calibri", 10, "bold"))
    style.configure("TCombobox", fieldbackground="white", background="#E0E0E0", foreground="black")

    def apply_responsive_styles(parent):
        for widget in parent.winfo_children():
            if isinstance(widget, tk.Label) and widget.cget("fg") in ["", "SystemButtonText", "gray"]:
                widget.configure(fg="#333333")
            elif isinstance(widget, tk.Entry):
                widget.configure(fg="black", insertbackground="black")
            if widget.winfo_children():
                apply_responsive_styles(widget)

    # ================= UTAMA LAYOUT SETELAH LOGIN =================
    def show_dashboard_layout():
        for widget in root.winfo_children():
            widget.destroy()

        header = tk.Frame(root, bg="white", height=45, bd=1, relief="solid")
        header.pack(side=tk.TOP, fill=tk.X)

        tk.Label(header, text="ApoLink Pharmacy System", font=("Calibri", 12, "bold"), bg="white", fg="#1E8E3E").pack(side=tk.LEFT, padx=15, pady=8)

        user_info_frame = tk.Frame(header, bg="white")
        user_info_frame.pack(side=tk.RIGHT, padx=15, pady=5)

        lbl_user = tk.Label(user_info_frame, text=f"Welcome, {current_user['nama']}! ({current_user['role']})", font=("Calibri", 11, "bold"), bg="white", fg="#333333")
        lbl_user.pack(side=tk.LEFT, padx=(0, 10))

        def logout():
            # Konfirmasi dialog sebelum logout
            jawaban = msgbox.askyesno("Konfirmasi Logout", "Apakah Anda yakin ingin keluar?")
            if jawaban:
                root.destroy()  # Tutup dashboard, alur otomatis kembali ke main.py (login)

        btn_logout = CustomButton(user_info_frame, text="🚪 Logout", command=logout, bg="#D84315", padx=8, pady=3)
        btn_logout.pack(side=tk.RIGHT)

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

            products = db.get_all_products()
            pasien_list = db.get_all_pasien()

            today = datetime.now().date()
            stok_kritis = sum(1 for p in products if p['stok'] <= 5)

            exp_count = 0
            for p in products:
                if p['tgl_exp'] and p['tgl_exp'] <= today:
                    exp_count += 1

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

            products_cache = db.get_all_products()
            pasien_cache = db.get_all_pasien()
            all_pasien_names = [p["nama"] for p in pasien_cache]

            tk.Label(content, text="Kasir & Pembayaran", font=("Calibri", 18, "bold"), bg="white", fg="#1E8E3E").pack(anchor="w", pady=(0, 10))

            f_in = tk.Frame(content, bg="white")
            f_in.pack(fill=tk.X, pady=5)

            tk.Label(f_in, text="Pilih Produk:", bg="white", fg="#333333").grid(row=0, column=0, sticky="w")
            all_product_names = [p["nama"] for p in products_cache]
            cb_prod = ttk.Combobox(f_in, values=all_product_names, width=20)
            cb_prod.grid(row=0, column=1, padx=5, pady=5)

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

            tk.Label(f_in, text="Qty:", bg="white", fg="#333333").grid(row=0, column=2, padx=(10, 0))
            ent_qty = tk.Entry(f_in, width=5, bg="white", fg="black")
            ent_qty.grid(row=0, column=3, padx=5)
            ent_qty.insert(0, "1")

            tree = ttk.Treeview(content, columns=("Nama", "Harga", "Qty", "Subtotal"), show="headings", height=8)
            for c in ("Nama", "Harga", "Qty", "Subtotal"):
                tree.heading(c, text=c)
                tree.column(c, width=120, anchor="center")
            tree.pack(fill=tk.BOTH, expand=True, pady=10)

            # ---- Data pasien diisi terakhir, setelah daftar obat dipilih ----
            f_pasien = tk.Frame(content, bg="white")
            f_pasien.pack(fill=tk.X, pady=5)

            tk.Label(f_pasien, text="Nama Pasien:", bg="white", fg="#333333").grid(row=0, column=0, sticky="w")
            cb_pasien = ttk.Combobox(f_pasien, values=all_pasien_names, width=21)
            cb_pasien.grid(row=0, column=1, padx=5, pady=5)
            cb_pasien.insert(0, "Umum")

            def on_keyrelease_pasien(event):
                if event.keysym in ("Up", "Down", "Return", "Escape", "Tab"): return
                typed = cb_pasien.get().lower()
                if typed == '':
                    cb_pasien['values'] = all_pasien_names
                else:
                    filtered = [item for item in all_pasien_names if typed in item.lower()]
                    cb_pasien['values'] = filtered
                    # Dropdown hanya dibuka kalau ada nama yang cocok, biar ngetik nama
                    # pasien baru (yang belum terdaftar) gak keganggu popup kosong.
                    if filtered:
                        cb_pasien.event_generate('<Down>')

            cb_pasien.bind('<KeyRelease>', on_keyrelease_pasien)

            tk.Label(f_pasien, text="No. WA:", bg="white", fg="#333333").grid(row=0, column=2, padx=(10, 0))
            ent_wa = tk.Entry(f_pasien, width=18, bg="white", fg="black")
            ent_wa.grid(row=0, column=3, padx=5, pady=5)

            def on_pasien_selected(event=None):
                # Kalau nama yang diketik cocok dengan pasien terdaftar, auto-isi WA-nya
                p = next((x for x in pasien_cache if x["nama"] == cb_pasien.get()), None)
                ent_wa.delete(0, tk.END)
                if p and p["kontak"]:
                    ent_wa.insert(0, p["kontak"])

            cb_pasien.bind('<<ComboboxSelected>>', on_pasien_selected)

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
                item = next((p for p in products_cache if p["nama"] == p_name), None)
                
                if not item:
                    msgbox.showwarning("Peringatan", "Produk tidak ditemukan!")
                    return
                if qty_s.isdigit() and int(qty_s) > 0:
                    q = int(qty_s)
                    if q > item["stok"]:
                        msgbox.showwarning("Stok Kurang", f"Stok tersedia hanya {item['stok']}!")
                        return
                    
                    sub = item["harga"] * q
                    cart.append({"id": item["id"], "nama": p_name, "harga": item["harga"], "qty": q, "subtotal": sub})
                    item["stok"] -= q  # supaya pengecekan stok berikutnya di sesi ini tetap akurat
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
                
                nama_pasien = cb_pasien.get().strip() or "Umum"
                kontak_pasien = ent_wa.get().strip()
                total_bayar = sum(c["subtotal"] for c in cart)

                # Kalau nama pasien belum ada di data Kelola Pasien, otomatis daftarkan
                # (dikecualikan untuk nama generik "Umum" tanpa WA)
                sudah_terdaftar = any(p["nama"] == nama_pasien for p in pasien_cache)
                if nama_pasien.lower() != "umum" and not sudah_terdaftar:
                    try:
                        db.add_pasien(nama_pasien, kontak_pasien)
                    except Exception as e:
                        msgbox.showerror("Database Error", f"Gagal menyimpan data pasien baru:\n{e}")
                        return

                try:
                    waktu_dt = db.process_sale(cart, nama_pasien)
                except Exception as e:
                    msgbox.showerror("Database Error", f"Gagal menyimpan transaksi:\n{e}")
                    return

                waktu = waktu_dt.strftime("%Y-%m-%d %H:%M:%S")

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
                if kontak_pasien:
                    struk_text += f"WA: {kontak_pasien}\n"
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

            CustomButton(f_in, text="+ Tambah", command=tambah, bg="#34A853").grid(row=0, column=4, padx=5)
            
            btn_action_frame = tk.Frame(f_bottom, bg="white")
            btn_action_frame.pack(side=tk.LEFT)
            
            btn_h = CustomButton(btn_action_frame, text="🗑 Hapus Item", command=hapus_item, bg="#D84315")
            btn_h.pack(side=tk.LEFT, padx=2)
            
            btn_c = CustomButton(btn_action_frame, text="🖨 Cetak Struk / Bayar", command=cetak_struk, bg="#1E8E3E")
            btn_c.pack(side=tk.LEFT, padx=5)

        # 3. KELOLA PRODUK
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

            f_search = tk.Frame(content, bg="white")
            f_search.pack(fill=tk.X, pady=(10, 0))
            tk.Label(f_search, text="🔍 Cari:", bg="white", fg="#333333").pack(side=tk.LEFT)
            ent_search = tk.Entry(f_search, width=30, bg="white", fg="black")
            ent_search.pack(side=tk.LEFT, padx=5)

            tree = ttk.Treeview(content, columns=("Nama", "Kategori", "Harga", "Stok", "Tgl Exp"), show="headings", height=8)
            for c in ("Nama", "Kategori", "Harga", "Stok", "Tgl Exp"):
                tree.heading(c, text=c)
                tree.column(c, anchor="center")
            tree.pack(fill=tk.BOTH, expand=True, pady=10)

            def refresh_table():
                keyword = ent_search.get().lower().strip()
                for r in tree.get_children(): tree.delete(r)
                for p in db.get_all_products():
                    tgl_str = p['tgl_exp'].strftime("%Y-%m-%d") if p['tgl_exp'] else "-"
                    haystack = f"{p['nama']} {p['kategori']} {p['harga']} {p['stok']} {tgl_str}".lower()
                    if keyword and keyword not in haystack:
                        continue
                    tree.insert("", tk.END, iid=str(p["id"]), values=(p["nama"], p["kategori"], f"Rp {p['harga']:,}", p["stok"], tgl_str))

            ent_search.bind("<KeyRelease>", lambda e: refresh_table())

            def show_history_popup(event=None):
                selected = tree.selection()
                if not selected:
                    msgbox.showinfo("Info", "Silakan pilih produk terlebih dahulu!")
                    return

                item_values = tree.item(selected[0])['values']
                nama_produk = item_values[0]

                win_hist = tk.Toplevel(root)
                win_hist.title(f"Riwayat Transaksi - {nama_produk}")
                
                w_width, w_height = 550, 380
                scr_w = win_hist.winfo_screenwidth()
                scr_h = win_hist.winfo_screenheight()
                x_c = int((scr_w / 2) - (w_width / 2))
                y_c = int((scr_h / 2) - (w_height / 2))
                win_hist.geometry(f"{w_width}x{w_height}+{x_c}+{y_c}")
                
                win_hist.resizable(False, False)
                win_hist.configure(bg="white")
                win_hist.transient(root)
                win_hist.grab_set()

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

                filtered_history = db.get_transaksi_by_produk(nama_produk)

                if not filtered_history:
                    tree_h.insert("", tk.END, values=("-", "Belum ada transaksi", "-", "-"))
                else:
                    for h in filtered_history:
                        waktu_str = h["waktu"].strftime("%Y-%m-%d %H:%M:%S")
                        tree_h.insert("", tk.END, values=(waktu_str, h["pasien"], h["qty"], f"Rp {h['total']:,}"))

                btn_close = CustomButton(win_hist, text="Tutup / Close", command=win_hist.destroy, bg="#D84315", padx=15, pady=4)
                btn_close.pack(pady=(0, 15))

            tree.bind("<Double-1>", show_history_popup)

            def simpan():
                if e_nama.get() and e_hrg.get().isdigit() and e_stk.get().isdigit():
                    db.add_product(
                        e_nama.get(),
                        cb_k.get(),
                        int(e_hrg.get()),
                        int(e_stk.get()),
                        e_exp.get()
                    )
                    refresh_table()
                    e_nama.delete(0, tk.END); e_hrg.delete(0, tk.END); e_stk.delete(0, tk.END)

            def hapus():
                selected = tree.selection()
                if selected:
                    db.delete_product(int(selected[0]))
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

            f_search = tk.Frame(content, bg="white")
            f_search.pack(fill=tk.X, pady=(10, 0))
            tk.Label(f_search, text="🔍 Cari:", bg="white", fg="#333333").pack(side=tk.LEFT)
            ent_search = tk.Entry(f_search, width=30, bg="white", fg="black")
            ent_search.pack(side=tk.LEFT, padx=5)

            tree = ttk.Treeview(content, columns=("Nama", "Username", "Role"), show="headings", height=8)
            for c in ("Nama", "Username", "Role"):
                tree.heading(c, text=c)
                tree.column(c, anchor="center")
            tree.pack(fill=tk.BOTH, expand=True, pady=10)

            def refresh():
                keyword = ent_search.get().lower().strip()
                for r in tree.get_children(): tree.delete(r)
                for u in db.get_all_users():
                    haystack = f"{u['nama']} {u['username']} {u['role']}".lower()
                    if keyword and keyword not in haystack:
                        continue
                    tree.insert("", tk.END, iid=str(u["id"]), values=(u["nama"], u["username"], u["role"]))

            ent_search.bind("<KeyRelease>", lambda e: refresh())

            def simpan():
                if e_nama.get() and e_user.get() and e_pass.get():
                    try:
                        db.add_user(e_nama.get(), e_user.get(), e_pass.get(), cb_role.get())
                    except Exception as e:
                        msgbox.showerror("Database Error", f"Gagal menambah user (username mungkin sudah dipakai):\n{e}")
                        return
                    refresh()
                    e_nama.delete(0, tk.END); e_user.delete(0, tk.END); e_pass.delete(0, tk.END)
                    msgbox.showinfo("Sukses", "User baru berhasil ditambahkan!")

            def hapus():
                selected = tree.selection()
                if selected:
                    user_id = int(selected[0])
                    if user_id == current_user["id"]:
                        msgbox.showwarning("Peringatan", "Anda tidak bisa menghapus akun Anda sendiri yang sedang aktif!")
                        return
                    db.delete_user(user_id)
                    refresh()

            btn_t = CustomButton(f_form, text="Tambah User", command=simpan, bg="#34A853")
            btn_t.grid(row=1, column=4, padx=5)
            
            btn_h = CustomButton(content, text="🗑 Hapus User Selected", command=hapus, bg="#D84315")
            btn_h.pack(anchor="w")
            
            refresh()

        # 5. LAPORAN KEDALUWARSA
        def show_lap_expired():
            clear_content()

            f_header = tk.Frame(content, bg="white")
            f_header.pack(fill=tk.X, pady=(0, 10))
            tk.Label(f_header, text="⚠️ Laporan Obat / Goods Kedaluwarsa", font=("Calibri", 18, "bold"), bg="white", fg="#1E8E3E").pack(side=tk.LEFT)

            lbl_updated = tk.Label(f_header, text="", font=("Calibri", 9), bg="white", fg="#888888")
            lbl_updated.pack(side=tk.RIGHT, padx=10)

            tree_exp = ttk.Treeview(content, columns=("Nama Barang", "Kategori", "Stok", "Tgl Expired", "Status Expired"), show="headings", height=12)
            tree_exp.heading("Nama Barang", text="Nama Barang"); tree_exp.column("Nama Barang", width=200, anchor="w")
            tree_exp.heading("Kategori", text="Kategori"); tree_exp.column("Kategori", width=100, anchor="center")
            tree_exp.heading("Stok", text="Stok"); tree_exp.column("Stok", width=80, anchor="center")
            tree_exp.heading("Tgl Expired", text="Tgl Expired"); tree_exp.column("Tgl Expired", width=110, anchor="center")
            tree_exp.heading("Status Expired", text="Status Expired"); tree_exp.column("Status Expired", width=180, anchor="center")

            def refresh_laporan():
                for r in tree_exp.get_children(): tree_exp.delete(r)

                now = datetime.now()
                today = now.date()
                warning_limit = today + timedelta(days=30)

                products = db.get_all_products()
                # Urutkan dari tanggal kedaluwarsa terdekat; produk tanpa tanggal ditaruh paling akhir
                products_sorted = sorted(products, key=lambda p: (p["tgl_exp"] is None, p["tgl_exp"]))

                for p in products_sorted:
                    exp_date = p["tgl_exp"]
                    if exp_date is None:
                        status = "❓ Belum diisi"
                        tgl_str = "-"
                    else:
                        tgl_str = exp_date.strftime("%Y-%m-%d")
                        if exp_date <= today:
                            status = "🔴 KEDALUWARSA"
                        elif exp_date <= warning_limit:
                            status = "🟡 SEGERA EXP (≤30 Hari)"
                        else:
                            status = "🟢 Aman"

                    tree_exp.insert("", tk.END, values=(p["nama"], p["kategori"], p["stok"], tgl_str, status))

                lbl_updated.config(text=f"🔄 Data real-time per: {now.strftime('%Y-%m-%d %H:%M:%S')}")

            btn_refresh = CustomButton(content, text="🔄 Refresh Data", command=refresh_laporan, bg="#00838F")
            btn_refresh.pack(anchor="w", pady=(0, 5))

            tree_exp.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

            refresh_laporan()

        # 6. KELOLA PASIEN
        def show_pasien():
            clear_content()
            tk.Label(content, text="Kelola Data Pasien", font=("Calibri", 18, "bold"), bg="white", fg="#1E8E3E").pack(anchor="w", pady=(0, 10))

            f_form = tk.Frame(content, bg="white")
            f_form.pack(fill=tk.X, pady=5)

            tk.Label(f_form, text="Nama Pasien:", bg="white", fg="#333333").grid(row=0, column=0); e_nama = tk.Entry(f_form, bg="white", fg="black"); e_nama.grid(row=0, column=1, padx=5)
            tk.Label(f_form, text="Kontak / WA:", bg="white", fg="#333333").grid(row=0, column=2); e_kontak = tk.Entry(f_form, bg="white", fg="black"); e_kontak.grid(row=0, column=3, padx=5)

            f_search = tk.Frame(content, bg="white")
            f_search.pack(fill=tk.X, pady=(10, 0))
            tk.Label(f_search, text="🔍 Cari:", bg="white", fg="#333333").pack(side=tk.LEFT)
            ent_search = tk.Entry(f_search, width=30, bg="white", fg="black")
            ent_search.pack(side=tk.LEFT, padx=5)

            tree = ttk.Treeview(content, columns=("Nama", "Kontak"), show="headings", height=8)
            for c in ("Nama", "Kontak"):
                tree.heading(c, text=c)
                tree.column(c, anchor="center")
            tree.pack(fill=tk.BOTH, expand=True, pady=10)

            def refresh():
                keyword = ent_search.get().lower().strip()
                for r in tree.get_children(): tree.delete(r)
                for p in db.get_all_pasien():
                    if keyword and keyword not in p["nama"].lower() and keyword not in (p["kontak"] or "").lower():
                        continue
                    tree.insert("", tk.END, iid=str(p["id"]), values=(p["nama"], p["kontak"]))

            ent_search.bind("<KeyRelease>", lambda e: refresh())

            def simpan():
                if e_nama.get():
                    db.add_pasien(e_nama.get(), e_kontak.get())
                    refresh()
                    e_nama.delete(0, tk.END); e_kontak.delete(0, tk.END)

            def hapus():
                selected = tree.selection()
                if selected:
                    db.delete_pasien(int(selected[0]))
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

            f_search = tk.Frame(content, bg="white")
            f_search.pack(fill=tk.X, pady=(10, 0))
            tk.Label(f_search, text="🔍 Cari:", bg="white", fg="#333333").pack(side=tk.LEFT)
            ent_search = tk.Entry(f_search, width=30, bg="white", fg="black")
            ent_search.pack(side=tk.LEFT, padx=5)

            tree = ttk.Treeview(content, columns=("Nama", "Alamat", "Contact"), show="headings", height=8)
            for c in ("Nama", "Alamat", "Contact"):
                tree.heading(c, text=c)
                tree.column(c, anchor="center")
            tree.pack(fill=tk.BOTH, expand=True, pady=10)

            def refresh():
                keyword = ent_search.get().lower().strip()
                for r in tree.get_children(): tree.delete(r)
                for s in db.get_all_suppliers():
                    haystack = f"{s['nama']} {s['alamat'] or ''} {s['kontak'] or ''}".lower()
                    if keyword and keyword not in haystack:
                        continue
                    tree.insert("", tk.END, iid=str(s["id"]), values=(s["nama"], s["alamat"], s["kontak"]))

            ent_search.bind("<KeyRelease>", lambda e: refresh())

            def simpan():
                if e_nama.get():
                    db.add_supplier(e_nama.get(), e_alamat.get(), e_contact.get())
                    refresh()
                    e_nama.delete(0, tk.END); e_alamat.delete(0, tk.END); e_contact.delete(0, tk.END)

            def hapus():
                selected = tree.selection()
                if selected:
                    db.delete_supplier(int(selected[0]))
                    refresh()

            btn_s = CustomButton(f_form, text="Simpan Supplier", command=simpan, bg="#34A853")
            btn_s.grid(row=1, column=4, padx=5)
            
            btn_h = CustomButton(content, text="🗑 Hapus Supplier Selected", command=hapus, bg="#D84315")
            btn_h.pack(anchor="w")
            
            refresh()

        # 7B. PEMBELIAN BARANG (RESTOCK DARI SUPPLIER)
        def show_pembelian():
            clear_content()
            tk.Label(content, text="🛍️ Pembelian Barang (Restock dari Supplier)", font=("Calibri", 18, "bold"), bg="white", fg="#1E8E3E").pack(anchor="w", pady=(0, 10))

            products_cache = db.get_all_products()
            suppliers_cache = db.get_all_suppliers()
            all_product_names = [p["nama"] for p in products_cache]
            all_supplier_names = [s["nama"] for s in suppliers_cache]

            f_form = tk.Frame(content, bg="white")
            f_form.pack(fill=tk.X, pady=5)

            tk.Label(f_form, text="Supplier:", bg="white", fg="#333333").grid(row=0, column=0, sticky="w")
            cb_supplier = ttk.Combobox(f_form, values=all_supplier_names, width=20)
            cb_supplier.grid(row=0, column=1, padx=5, pady=2)

            def on_keyrelease_supplier(event):
                if event.keysym in ("Up", "Down", "Return", "Escape", "Tab"): return
                typed = cb_supplier.get().lower()
                if typed == '':
                    cb_supplier['values'] = all_supplier_names
                else:
                    filtered = [item for item in all_supplier_names if typed in item.lower()]
                    cb_supplier['values'] = filtered
                    if filtered:
                        cb_supplier.event_generate('<Down>')

            cb_supplier.bind('<KeyRelease>', on_keyrelease_supplier)

            tk.Label(f_form, text="Produk:", bg="white", fg="#333333").grid(row=0, column=2, sticky="w", padx=(10, 0))
            cb_produk = ttk.Combobox(f_form, values=all_product_names, width=20)
            cb_produk.grid(row=0, column=3, padx=5, pady=2)

            def on_keyrelease_produk(event):
                if event.keysym in ("Up", "Down", "Return", "Escape", "Tab"): return
                typed = cb_produk.get().lower()
                if typed == '':
                    cb_produk['values'] = all_product_names
                else:
                    filtered = [item for item in all_product_names if typed in item.lower()]
                    cb_produk['values'] = filtered
                    if filtered:
                        cb_produk.event_generate('<Down>')

            cb_produk.bind('<KeyRelease>', on_keyrelease_produk)

            tk.Label(f_form, text="Qty Beli:", bg="white", fg="#333333").grid(row=1, column=0, sticky="w", pady=(8, 2))
            ent_qty = tk.Entry(f_form, width=10, bg="white", fg="black")
            ent_qty.grid(row=1, column=1, padx=5, pady=(8, 2), sticky="w")

            tk.Label(f_form, text="Harga Beli/Satuan:", bg="white", fg="#333333").grid(row=1, column=2, sticky="w", padx=(10, 0), pady=(8, 2))
            ent_harga = tk.Entry(f_form, width=15, bg="white", fg="black")
            ent_harga.grid(row=1, column=3, padx=5, pady=(8, 2))

            tk.Label(f_form, text="Tanggal (YYYY-MM-DD):", bg="white", fg="#333333").grid(row=2, column=0, sticky="w", pady=2)
            ent_tanggal = tk.Entry(f_form, width=15, bg="white", fg="black")
            ent_tanggal.grid(row=2, column=1, padx=5, pady=2, sticky="w")
            ent_tanggal.insert(0, datetime.now().strftime("%Y-%m-%d"))

            tk.Label(f_form, text="Catatan:", bg="white", fg="#333333").grid(row=2, column=2, sticky="w", padx=(10, 0), pady=2)
            ent_catatan = tk.Entry(f_form, width=25, bg="white", fg="black")
            ent_catatan.grid(row=2, column=3, padx=5, pady=2)

            f_search = tk.Frame(content, bg="white")
            f_search.pack(fill=tk.X, pady=(10, 0))
            tk.Label(f_search, text="🔍 Cari Riwayat:", bg="white", fg="#333333").pack(side=tk.LEFT)
            ent_search = tk.Entry(f_search, width=30, bg="white", fg="black")
            ent_search.pack(side=tk.LEFT, padx=5)

            tree = ttk.Treeview(content, columns=("Tanggal", "Supplier", "Produk", "Qty", "Harga Beli", "Total", "Catatan"), show="headings", height=8)
            widths = {"Tanggal": 100, "Supplier": 140, "Produk": 160, "Qty": 60, "Harga Beli": 100, "Total": 110, "Catatan": 150}
            for c in ("Tanggal", "Supplier", "Produk", "Qty", "Harga Beli", "Total", "Catatan"):
                tree.heading(c, text=c)
                tree.column(c, width=widths[c], anchor="center")
            tree.pack(fill=tk.BOTH, expand=True, pady=10)

            def refresh():
                keyword = ent_search.get().lower().strip()
                for r in tree.get_children(): tree.delete(r)
                for pb in db.get_all_pembelian():
                    tgl_str = pb["tanggal"].strftime("%Y-%m-%d") if pb["tanggal"] else "-"
                    total = pb["qty"] * pb["harga_beli"]
                    haystack = f"{pb['supplier_nama']} {pb['produk_nama']} {pb['qty']} {pb['harga_beli']} {tgl_str} {pb['catatan'] or ''}".lower()
                    if keyword and keyword not in haystack:
                        continue
                    tree.insert("", tk.END, iid=str(pb["id"]), values=(
                        tgl_str, pb["supplier_nama"], pb["produk_nama"], pb["qty"],
                        f"Rp {pb['harga_beli']:,}", f"Rp {total:,}", pb["catatan"] or "-"
                    ))

            ent_search.bind("<KeyRelease>", lambda e: refresh())

            def simpan_pembelian():
                supplier_nama = cb_supplier.get().strip()
                produk_nama = cb_produk.get().strip()
                qty_s = ent_qty.get().strip()
                harga_s = ent_harga.get().strip() or "0"
                tanggal = ent_tanggal.get().strip()
                catatan = ent_catatan.get().strip()

                if not supplier_nama or not produk_nama:
                    msgbox.showwarning("Peringatan", "Supplier dan Produk wajib diisi!")
                    return
                if not qty_s.isdigit() or int(qty_s) <= 0:
                    msgbox.showwarning("Peringatan", "Qty Beli harus berupa angka lebih dari 0!")
                    return
                if not harga_s.isdigit():
                    msgbox.showwarning("Peringatan", "Harga Beli harus berupa angka!")
                    return

                prod = db.get_product_by_name(produk_nama)
                if not prod:
                    msgbox.showwarning("Peringatan", "Produk tidak ditemukan di Kelola Produk!")
                    return

                try:
                    db.process_pembelian(
                        prod["id"], produk_nama, supplier_nama,
                        int(qty_s), int(harga_s), tanggal or None, catatan
                    )
                except Exception as e:
                    msgbox.showerror("Database Error", f"Gagal menyimpan pembelian:\n{e}")
                    return

                refresh()
                cb_supplier.set(""); cb_produk.set("")
                ent_qty.delete(0, tk.END); ent_harga.delete(0, tk.END); ent_catatan.delete(0, tk.END)
                ent_tanggal.delete(0, tk.END); ent_tanggal.insert(0, datetime.now().strftime("%Y-%m-%d"))
                msgbox.showinfo("Sukses", f"Pembelian {qty_s} {produk_nama} dari {supplier_nama} berhasil dicatat, stok otomatis bertambah!")

            def hapus_pembelian():
                selected = tree.selection()
                if selected:
                    if msgbox.askyesno("Konfirmasi", "Hapus riwayat pembelian ini? (Stok produk TIDAK otomatis dikurangi kembali)"):
                        db.delete_pembelian(int(selected[0]))
                        refresh()

            btn_p = CustomButton(f_form, text="Catat Pembelian", command=simpan_pembelian, bg="#34A853")
            btn_p.grid(row=1, column=4, rowspan=2, padx=10)

            btn_h = CustomButton(content, text="🗑 Hapus Riwayat Selected", command=hapus_pembelian, bg="#D84315")
            btn_h.pack(anchor="w")

            refresh()

        # 8. STOK OPNAME
        def show_stok_opname():
            clear_content()
            tk.Label(content, text="Stok Opname (Penyesuaian Fisik)", font=("Calibri", 18, "bold"), bg="white", fg="#1E8E3E").pack(anchor="w", pady=(0, 10))

            f_form = tk.Frame(content, bg="white")
            f_form.pack(fill=tk.X, pady=5)

            tk.Label(f_form, text="Pilih Item:", bg="white", fg="#333333").grid(row=0, column=0, sticky="w")
            all_item_names = [p["nama"] for p in db.get_all_products()]
            cb_item = ttk.Combobox(f_form, values=all_item_names, width=20)
            cb_item.grid(row=0, column=1, padx=5, pady=5)

            def on_keyrelease_item(event):
                if event.keysym in ("Up", "Down", "Return", "Escape"): return
                typed = cb_item.get().lower()
                if typed == '':
                    cb_item['values'] = all_item_names
                else:
                    filtered = [item for item in all_item_names if typed in item.lower()]
                    cb_item['values'] = filtered
                    cb_item.event_generate('<Down>')

            cb_item.bind('<KeyRelease>', on_keyrelease_item)

            tk.Label(f_form, text="Stok Sistem:", bg="white", fg="#333333").grid(row=0, column=2, padx=5)
            lbl_sys_stok = tk.Label(f_form, text="0", bg="#E0E0E0", fg="black", width=8, font=("Calibri", 10, "bold"))
            lbl_sys_stok.grid(row=0, column=3, padx=5)

            tk.Label(f_form, text="Stok Fisik:", bg="white", fg="#333333").grid(row=0, column=4, padx=5)
            ent_fisik = tk.Entry(f_form, width=8, bg="white", fg="black")
            ent_fisik.grid(row=0, column=5, padx=5)

            tk.Label(f_form, text="Tgl Opname (YYYY-MM-DD):", bg="white", fg="#333333").grid(row=1, column=0, sticky="w", pady=(8, 0))
            ent_tgl_opname = tk.Entry(f_form, width=15, bg="white", fg="black")
            ent_tgl_opname.grid(row=1, column=1, padx=5, pady=(8, 0), sticky="w")
            ent_tgl_opname.insert(0, datetime.now().strftime("%Y-%m-%d"))

            def auto_load_stok(event=None):
                p = db.get_product_by_name(cb_item.get())
                if p:
                    lbl_sys_stok.config(text=str(p["stok"]))

            cb_item.bind("<<ComboboxSelected>>", auto_load_stok)

            f_search = tk.Frame(content, bg="white")
            f_search.pack(fill=tk.X, pady=(10, 0))
            tk.Label(f_search, text="🔍 Cari Riwayat:", bg="white", fg="#333333").pack(side=tk.LEFT)
            ent_search = tk.Entry(f_search, width=30, bg="white", fg="black")
            ent_search.pack(side=tk.LEFT, padx=5)

            tree = ttk.Treeview(content, columns=("Nama Barang", "Stok Sistem", "Stok Fisik", "Selisih", "Tanggal"), show="headings", height=8)
            for c in ("Nama Barang", "Stok Sistem", "Stok Fisik", "Selisih", "Tanggal"):
                tree.heading(c, text=c)
                tree.column(c, anchor="center")
            tree.pack(fill=tk.BOTH, expand=True, pady=10)

            def refresh():
                keyword = ent_search.get().lower().strip()
                for r in tree.get_children(): tree.delete(r)
                for o in db.get_all_stok_opname():
                    tgl_str = o["waktu"].strftime("%Y-%m-%d") if o["waktu"] else "-"
                    haystack = f"{o['produk_nama']} {o['stok_sistem']} {o['stok_fisik']} {o['selisih']} {tgl_str}".lower()
                    if keyword and keyword not in haystack:
                        continue
                    tree.insert("", tk.END, iid=str(o["id"]), values=(o["produk_nama"], o["stok_sistem"], o["stok_fisik"], o["selisih"], tgl_str))

            ent_search.bind("<KeyRelease>", lambda e: refresh())

            def simpan_opname():
                p_name = cb_item.get()
                fisik_s = ent_fisik.get()
                tgl_opname = ent_tgl_opname.get().strip()
                prod = db.get_product_by_name(p_name)

                if prod and fisik_s.isdigit():
                    fisik = int(fisik_s)
                    stok_sistem = prod["stok"]
                    selisih = fisik - stok_sistem

                    db.update_product_stok(prod["id"], fisik)
                    db.add_stok_opname(p_name, stok_sistem, fisik, selisih, tgl_opname or None)

                    refresh()
                    cb_item.set("")
                    lbl_sys_stok.config(text="0")
                    ent_fisik.delete(0, tk.END)
                    ent_tgl_opname.delete(0, tk.END)
                    ent_tgl_opname.insert(0, datetime.now().strftime("%Y-%m-%d"))
                    msgbox.showinfo("Sukses", f"Stok {p_name} diperbarui menjadi {fisik}!")

            def hapus_opname():
                selected = tree.selection()
                if selected:
                    db.delete_stok_opname(int(selected[0]))
                    refresh()

            btn_p = CustomButton(f_form, text="Proses Opname", command=simpan_opname, bg="#34A853")
            btn_p.grid(row=0, column=6, padx=5)
            
            btn_h = CustomButton(content, text="🗑 Hapus Riwayat Selected", command=hapus_opname, bg="#D84315")
            btn_h.pack(anchor="w")
            
            refresh()

        # NAVIGATION SIDEBAR
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
            btn_nav("🛍️ Pembelian Barang", show_pembelian).pack(fill=tk.X)
            btn_nav("⚖️ Stok Opname", show_stok_opname).pack(fill=tk.X)

        if user_role == "Admin":
            btn_nav("👤 Kelola User", show_kelola_user).pack(fill=tk.X)

        show_dashboard()

    show_dashboard_layout()
    apply_responsive_styles(root)
    root.mainloop()