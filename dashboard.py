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

class DateSelector(tk.Frame):
    """Komponen alternatif pengganti tkcalendar yang 100% stabil dan anti-freeze"""
    def __init__(self, parent, default_date=None, bg="white"):
        super().__init__(parent, bg=bg)
        if default_date is None:
            default_date = datetime.now()
            
        days = [f"{i:02d}" for i in range(1, 32)]
        months = [f"{i:02d}" for i in range(1, 13)]
        years = [str(i) for i in range(2020, 2035)]
        
        self.cb_day = ttk.Combobox(self, values=days, width=3, state="readonly")
        self.cb_month = ttk.Combobox(self, values=months, width=3, state="readonly")
        self.cb_year = ttk.Combobox(self, values=years, width=5, state="readonly")
        
        self.cb_day.pack(side=tk.LEFT, padx=1)
        self.cb_month.pack(side=tk.LEFT, padx=1)
        self.cb_year.pack(side=tk.LEFT, padx=1)
        
        self.set_date(default_date)

    def set_date(self, dt):
        self.cb_day.set(f"{dt.day:02d}")
        self.cb_month.set(f"{dt.month:02d}")
        self.cb_year.set(str(dt.year))

    def get_date_str(self):
        return f"{self.cb_year.get()}-{self.cb_month.get()}-{self.cb_day.get()}"

    def get_date(self):
        try:
            return datetime.strptime(self.get_date_str(), "%Y-%m-%d").date()
        except ValueError:
            return datetime.now().date()

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
            if msgbox.askyesno("Konfirmasi Logout", "Apakah Anda yakin ingin keluar?"):
                root.destroy()

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

            exp_count = sum(1 for p in products if p['tgl_exp'] and p['tgl_exp'] <= today)

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
            f_top_kasir = tk.Frame(content, bg="white")
            f_top_kasir.pack(fill=tk.X, pady=(0, 10))

            tk.Label(f_top_kasir, text="🛒 Menu Transaksi Kasir", font=("Calibri", 18, "bold"), bg="white", fg="#1E8E3E").pack(side=tk.LEFT)

            lbl_clock = tk.Label(f_top_kasir, text="", font=("Calibri", 13, "bold"), bg="#1E8E3E", fg="white", padx=12, pady=4)
            lbl_clock.pack(side=tk.RIGHT)

            def update_clock():
                now_str = datetime.now().strftime("%A, %d %b %Y - %H:%M:%S")
                lbl_clock.config(text=f"🕒 {now_str}")
                lbl_clock.after(1000, update_clock)

            update_clock()
            cart.clear()

            products_cache = db.get_all_products()
            pasien_cache = db.get_all_pasien()
            all_pasien_names = [p["nama"] for p in pasien_cache]

            f_in = tk.Frame(content, bg="white")
            f_in.pack(fill=tk.X, pady=5)

            tk.Label(f_in, text="Pilih Produk:", bg="white", fg="#333333").grid(row=0, column=0, sticky="w")
            all_product_names = [p["nama"] for p in products_cache]
            cb_prod = ttk.Combobox(f_in, values=all_product_names, width=20)
            cb_prod.grid(row=0, column=1, padx=5, pady=5)

            def on_keyrelease(event):
                if event.keysym in ("Up", "Down", "Return", "Escape", "Tab"): return
                typed = cb_prod.get().lower()
                cb_prod['values'] = all_product_names if typed == '' else [item for item in all_product_names if typed in item.lower()]

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

            f_pasien = tk.Frame(content, bg="white")
            f_pasien.pack(fill=tk.X, pady=5)

            tk.Label(f_pasien, text="Nama Pasien:", bg="white", fg="#333333").grid(row=0, column=0, sticky="w")
            cb_pasien = ttk.Combobox(f_pasien, values=all_pasien_names, width=21)
            cb_pasien.grid(row=0, column=1, padx=5, pady=5)
            cb_pasien.insert(0, "Umum")

            def on_keyrelease_pasien(event):
                if event.keysym in ("Up", "Down", "Return", "Escape", "Tab"): return
                typed = cb_pasien.get().lower()
                cb_pasien['values'] = all_pasien_names if typed == '' else [item for item in all_pasien_names if typed in item.lower()]

            cb_pasien.bind('<KeyRelease>', on_keyrelease_pasien)

            tk.Label(f_pasien, text="No. WA:", bg="white", fg="#333333").grid(row=0, column=2, padx=(10, 0))
            ent_wa = tk.Entry(f_pasien, width=18, bg="white", fg="black")
            ent_wa.grid(row=0, column=3, padx=5, pady=5)

            def on_pasien_selected(event=None):
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
                    item["stok"] -= q
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
            
            CustomButton(btn_action_frame, text="🗑 Hapus Item", command=hapus_item, bg="#D84315").pack(side=tk.LEFT, padx=2)
            CustomButton(btn_action_frame, text="🖨 Cetak Struk / Bayar", command=cetak_struk, bg="#1E8E3E").pack(side=tk.LEFT, padx=5)

        # 3. KELOLA PRODUK
        def show_produk():
            clear_content()
            tk.Label(content, text="Kelola Data Produk (Obat/Alkes/BHP)", font=("Calibri", 18, "bold"), bg="white", fg="#1E8E3E").pack(anchor="w", pady=(0, 10))

            f_form = tk.Frame(content, bg="white")
            f_form.pack(fill=tk.X, pady=5)

            tk.Label(f_form, text="Nama:", bg="white", fg="#333333").grid(row=0, column=0, sticky="w")
            e_nama = tk.Entry(f_form, bg="white", fg="black")
            e_nama.grid(row=0, column=1, padx=5, pady=2)

            tk.Label(f_form, text="Kategori:", bg="white", fg="#333333").grid(row=0, column=2, sticky="w")
            cb_k = ttk.Combobox(f_form, values=["", "Obat", "Alkes", "BHP"], width=17)
            cb_k.grid(row=0, column=3, padx=5, pady=2)
            cb_k.set("")

            tk.Label(f_form, text="Harga:", bg="white", fg="#333333").grid(row=1, column=0, sticky="w")
            e_hrg = tk.Entry(f_form, bg="white", fg="black")
            e_hrg.grid(row=1, column=1, padx=5, pady=2)

            tk.Label(f_form, text="Stok:", bg="white", fg="#333333").grid(row=1, column=2, sticky="w")
            e_stk = tk.Entry(f_form, bg="white", fg="black")
            e_stk.grid(row=1, column=3, padx=5, pady=2)
            
            tk.Label(f_form, text="Tgl Expired:", bg="white", fg="#333333").grid(row=0, column=6, padx=5)
            
            f_date = tk.Frame(f_form, bg="white")
            f_date.grid(row=0, column=7, padx=5)

            cb_day = ttk.Combobox(f_date, values=[""] + [f"{i:02d}" for i in range(1, 32)], width=3)
            cb_day.pack(side=tk.LEFT, padx=1)
            cb_day.set("")

            cb_month = ttk.Combobox(f_date, values=[""] + [f"{i:02d}" for i in range(1, 13)], width=3)
            cb_month.pack(side=tk.LEFT, padx=1)
            cb_month.set("")

            cb_year = ttk.Combobox(f_date, values=[""] + [str(i) for i in range(2024, 2035)], width=5)
            cb_year.pack(side=tk.LEFT, padx=1)
            cb_year.set("")

            tree = ttk.Treeview(content, columns=("Nama", "Kategori", "Harga", "Stok", "Tgl Exp"), show="headings", height=8)
            for c in ("Nama", "Kategori", "Harga", "Stok", "Tgl Exp"):
                tree.heading(c, text=c)
                tree.column(c, anchor="center")
            tree.pack(fill=tk.BOTH, expand=True, pady=10)

            def refresh_table(f_nama="", f_kat="", f_hrg="", f_stk="", f_d="", f_m="", f_y=""):
                for r in tree.get_children(): 
                    tree.delete(r)
                
                count = 0
                for p in db.get_all_products():
                    tgl_dt = p['tgl_exp']
                    tgl_str = tgl_dt.strftime("%Y-%m-%d") if tgl_dt else "-"
                    
                    p_day = tgl_dt.strftime("%d") if tgl_dt else ""
                    p_month = tgl_dt.strftime("%m") if tgl_dt else ""
                    p_year = tgl_dt.strftime("%Y") if tgl_dt else ""

                    match_nama = not f_nama or f_nama in p['nama'].lower()
                    match_kat = not f_kat or f_kat == p['kategori'].lower()
                    match_hrg = not f_hrg or f_hrg == str(p['harga'])
                    match_stk = not f_stk or f_stk == str(p['stok'])
                    
                    match_d = not f_d or f_d == p_day
                    match_m = not f_m or f_m == p_month
                    match_y = not f_y or f_y == p_year

                    if match_nama and match_kat and match_hrg and match_stk and match_d and match_m and match_y:
                        tree.insert("", tk.END, iid=str(p["id"]), values=(p["nama"], p["kategori"], f"Rp {p['harga']:,}", p["stok"], tgl_str))
                        count += 1

                return count

            def cari_produk():
                f_nama = e_nama.get().strip().lower()
                f_kat = cb_k.get().strip().lower()
                f_hrg = e_hrg.get().strip()
                f_stk = e_stk.get().strip()
                f_d = cb_day.get().strip()
                f_m = cb_month.get().strip()
                f_y = cb_year.get().strip()

                has_filter = any([f_nama, f_kat, f_hrg, f_stk, f_d, f_m, f_y])
                count = refresh_table(f_nama, f_kat, f_hrg, f_stk, f_d, f_m, f_y)
                
                if has_filter and count == 0:
                    msgbox.showinfo("Informasi", "produk yang anda cari tidak ada")

            def simpan():
                nama = e_nama.get().strip()
                kategori = cb_k.get().strip()
                harga = e_hrg.get().strip()
                stok = e_stk.get().strip()
                
                d, m, y = cb_day.get().strip(), cb_month.get().strip(), cb_year.get().strip()

                if not nama or not kategori or not harga.isdigit() or not stok.isdigit() or not (d and m and y):
                    msgbox.showwarning("Peringatan", "Mohon isi Nama, Kategori, Harga, Stok, dan Tanggal Expired (Lengkap DD-MM-YYYY) saat menyimpan!")
                    return

                existing_products = db.get_all_products()
                is_exist = any(p['nama'].lower() == nama.lower() for p in existing_products)

                if is_exist:
                    msgbox.showwarning("Peringatan", "produk yang anda cari sudah ada")
                else:
                    tgl_exp_str = f"{y}-{m}-{d}"
                    db.add_product(nama, kategori, int(harga), int(stok), tgl_exp_str)
                    
                    refresh_table()
                    e_nama.delete(0, tk.END); e_hrg.delete(0, tk.END); e_stk.delete(0, tk.END)
                    cb_k.set("")
                    cb_day.set(""); cb_month.set(""); cb_year.set("")
                    msgbox.showinfo("Sukses", "Produk baru berhasil ditambahkan!")

            def show_riwayat_stok_popup():
                selected = tree.selection()
                if not selected:
                    msgbox.showinfo("Info", "Silakan pilih produk terlebih dahulu!")
                    return

                item_values = tree.item(selected[0])['values']
                nama_produk = item_values[0]

                win_hist = tk.Toplevel(root)
                win_hist.title(f"Riwayat Stok - {nama_produk}")
                win_hist.geometry("780x420")
                win_hist.configure(bg="white")
                win_hist.transient(root)
                win_hist.grab_set()

                tk.Label(win_hist, text=f"Riwayat Mutasi Stok: {nama_produk}", font=("Calibri", 13, "bold"), bg="white", fg="#1E8E3E").pack(pady=(15, 5))
                tk.Label(win_hist, text="Mencakup penjualan, restock dari supplier, dan penyesuaian stok opname", font=("Calibri", 9), bg="white", fg="#888888").pack(pady=(0, 5))

                cols = ("Waktu", "Tipe", "Keterangan", "Stok Awal", "Masuk", "Keluar", "Stok Akhir")
                tree_h = ttk.Treeview(win_hist, columns=cols, show="headings", height=10)
                widths = {"Waktu": 130, "Tipe": 110, "Keterangan": 200, "Stok Awal": 70, "Masuk": 60, "Keluar": 60, "Stok Akhir": 70}
                for c in cols:
                    tree_h.heading(c, text=c)
                    tree_h.column(c, width=widths[c], anchor="center" if c != "Keterangan" else "w")

                tree_h.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

                riwayat = db.get_riwayat_stok_by_produk(nama_produk)
                if not riwayat:
                    tree_h.insert("", tk.END, values=("-", "-", "Belum ada mutasi stok", "-", "-", "-", "-"))
                else:
                    for r in riwayat:
                        waktu_str = r["waktu"].strftime("%Y-%m-%d %H:%M:%S")
                        tree_h.insert("", tk.END, values=(
                            waktu_str, r["tipe_transaksi"], r["keterangan"] or "-",
                            r["stok_awal"], r["qty_masuk"], r["qty_keluar"], r["stok_akhir"]
                        ))

                CustomButton(win_hist, text="Tutup / Close", command=win_hist.destroy, bg="#D84315", padx=15, pady=4).pack(pady=(0, 15))

            def hapus():
                selected = tree.selection()
                if selected:
                    db.delete_product(int(selected[0]))
                    refresh_table()

            btn_action_frame = tk.Frame(f_form, bg="white")
            btn_action_frame.grid(row=2, column=4, columnspan=2, padx=5, pady=5, sticky="w")

            CustomButton(btn_action_frame, text="Simpan", command=simpan, bg="#34A853").pack(side=tk.LEFT, padx=(0, 5))
            CustomButton(btn_action_frame, text="Cari", command=cari_produk, bg="#00838F").pack(side=tk.LEFT)

            f_btn = tk.Frame(content, bg="white")
            f_btn.pack(fill=tk.X)
            CustomButton(f_btn, text="🗑 Hapus Produk Selected", command=hapus, bg="#D84315").pack(side=tk.LEFT)
            CustomButton(f_btn, text="📜 Lihat Riwayat Stok", command=show_riwayat_stok_popup, bg="#00838F").pack(side=tk.LEFT, padx=5)
            
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
                        msgbox.showerror("Database Error", f"Gagal menambah user:\n{e}")
                        return
                    refresh()
                    e_nama.delete(0, tk.END); e_user.delete(0, tk.END); e_pass.delete(0, tk.END)
                    msgbox.showinfo("Sukses", "User baru berhasil ditambahkan!")

            def hapus():
                selected = tree.selection()
                if selected:
                    user_id = int(selected[0])
                    if user_id == current_user["id"]:
                        msgbox.showwarning("Peringatan", "Anda tidak bisa menghapus akun Anda sendiri!")
                        return
                    db.delete_user(user_id)
                    refresh()

            CustomButton(f_form, text="Tambah User", command=simpan, bg="#34A853").grid(row=1, column=4, padx=5)
            CustomButton(content, text="🗑 Hapus User Selected", command=hapus, bg="#D84315").pack(anchor="w")
            
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

            CustomButton(content, text="🔄 Refresh Data", command=refresh_laporan, bg="#00838F").pack(anchor="w", pady=(0, 5))
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

            def show_history_pasien_popup(event=None):
                selected = tree.selection()
                if not selected:
                    msgbox.showinfo("Info", "Silakan pilih pasien terlebih dahulu!")
                    return

                item_values = tree.item(selected[0])['values']
                nama_pasien = item_values[0]

                win_hist = tk.Toplevel(root)
                win_hist.title(f"Riwayat Obat / Pembelian - {nama_pasien}")
                win_hist.geometry("600x400")
                win_hist.configure(bg="white")
                win_hist.transient(root)
                win_hist.grab_set()

                tk.Label(win_hist, text=f"Riwayat Rekam Obat: {nama_pasien}", font=("Calibri", 13, "bold"), bg="white", fg="#1E8E3E").pack(pady=(15, 5))

                tree_h = ttk.Treeview(win_hist, columns=("Waktu", "Produk / Obat", "Qty", "Total Harga"), show="headings", height=9)
                tree_h.heading("Waktu", text="Waktu Transaksi")
                tree_h.heading("Produk / Obat", text="Produk / Obat")
                tree_h.heading("Qty", text="Qty")
                tree_h.heading("Total Harga", text="Total Harga")

                tree_h.column("Waktu", width=150, anchor="center")
                tree_h.column("Produk / Obat", width=180, anchor="w")
                tree_h.column("Qty", width=60, anchor="center")
                tree_h.column("Total Harga", width=120, anchor="e")

                tree_h.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

                filtered_history = db.get_transaksi_by_pasien(nama_pasien)
                if not filtered_history:
                    tree_h.insert("", tk.END, values=("-", "Belum ada riwayat transaksi", "-", "-"))
                else:
                    for h in filtered_history:
                        waktu_str = h["waktu"].strftime("%Y-%m-%d %H:%M:%S")
                        tree_h.insert("", tk.END, values=(waktu_str, h["produk"], h["qty"], f"Rp {h['total']:,}"))

                CustomButton(win_hist, text="Tutup / Close", command=win_hist.destroy, bg="#D84315", padx=15, pady=4).pack(pady=(0, 15))

            tree.bind("<Double-1>", show_history_pasien_popup)

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

            CustomButton(f_form, text="Tambah Pasien", command=simpan, bg="#34A853").grid(row=0, column=4, padx=5)
            
            f_btn_action = tk.Frame(content, bg="white")
            f_btn_action.pack(fill=tk.X)

            CustomButton(f_btn_action, text="🗑 Hapus Pasien Selected", command=hapus, bg="#D84315").pack(side=tk.LEFT)
            CustomButton(f_btn_action, text="📜 Lihat Riwayat Obat Pasien", command=show_history_pasien_popup, bg="#00838F").pack(side=tk.LEFT, padx=5)
            
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

            CustomButton(f_form, text="Simpan Supplier", command=simpan, bg="#34A853").grid(row=1, column=4, padx=5)
            CustomButton(content, text="🗑 Hapus Supplier Selected", command=hapus, bg="#D84315").pack(anchor="w")
            
            refresh()

        # 8. PEMBELIAN BARANG (RESTOCK DARI SUPPLIER)
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
                cb_supplier['values'] = all_supplier_names if typed == '' else [item for item in all_supplier_names if typed in item.lower()]

            cb_supplier.bind('<KeyRelease>', on_keyrelease_supplier)

            tk.Label(f_form, text="Produk:", bg="white", fg="#333333").grid(row=0, column=2, sticky="w", padx=(10, 0))
            cb_produk = ttk.Combobox(f_form, values=all_product_names, width=20)
            cb_produk.grid(row=0, column=3, padx=5, pady=2)

            # --- Disesuaikan presisi & kondisinya persis seperti Combobox Supplier ---
            def on_keyrelease_produk(event):
                if event.keysym in ("Up", "Down", "Return", "Escape", "Tab"): return
                typed = cb_produk.get().lower()
                cb_produk['values'] = all_product_names if typed == '' else [item for item in all_product_names if typed in item.lower()]

            cb_produk.bind('<KeyRelease>', on_keyrelease_produk)

            tk.Label(f_form, text="Qty Beli:", bg="white", fg="#333333").grid(row=1, column=0, sticky="w", pady=(8, 2))
            ent_qty = tk.Entry(f_form, width=10, bg="white", fg="black")
            ent_qty.grid(row=1, column=1, padx=5, pady=(8, 2), sticky="w")

            tk.Label(f_form, text="Harga Beli/Satuan:", bg="white", fg="#333333").grid(row=1, column=2, sticky="w", padx=(10, 0), pady=(8, 2))
            ent_harga = tk.Entry(f_form, width=15, bg="white", fg="black")
            ent_harga.grid(row=1, column=3, padx=5, pady=(8, 2))

            tk.Label(f_form, text="Tgl Pembelian:", bg="white", fg="#333333").grid(row=0, column=4, padx=5)
            ent_beli = DateSelector(f_form)
            ent_beli.grid(row=0, column=5, padx=5)

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

            def prompt_supplier_baru(nama_awal):
                """Popup isi data supplier baru (Nama/Alamat/Kontak), sama seperti form di Kelola Supplier.
                Return True kalau berhasil disimpan, False kalau dibatalkan."""
                result = {"success": False}

                win = tk.Toplevel(root)
                win.title("Tambah Supplier Baru")
                win.geometry("400x260")
                win.configure(bg="white")
                win.transient(root)
                win.grab_set()

                tk.Label(win, text="Supplier belum terdaftar", font=("Calibri", 13, "bold"), bg="white", fg="#1E8E3E").pack(pady=(15, 2))
                tk.Label(win, text="Lengkapi data supplier baru berikut:", font=("Calibri", 9), bg="white", fg="#888888").pack(pady=(0, 10))

                f = tk.Frame(win, bg="white")
                f.pack(padx=20, fill=tk.X)

                tk.Label(f, text="Nama Supplier:", bg="white", fg="#333333").grid(row=0, column=0, sticky="w", pady=4)
                e_nama = tk.Entry(f, bg="white", fg="black", width=25)
                e_nama.grid(row=0, column=1, pady=4)
                e_nama.insert(0, nama_awal)

                tk.Label(f, text="Alamat:", bg="white", fg="#333333").grid(row=1, column=0, sticky="w", pady=4)
                e_alamat = tk.Entry(f, bg="white", fg="black", width=25)
                e_alamat.grid(row=1, column=1, pady=4)

                tk.Label(f, text="Kontak:", bg="white", fg="#333333").grid(row=2, column=0, sticky="w", pady=4)
                e_kontak = tk.Entry(f, bg="white", fg="black", width=25)
                e_kontak.grid(row=2, column=1, pady=4)

                def simpan_popup():
                    nama = e_nama.get().strip()
                    if not nama:
                        msgbox.showwarning("Peringatan", "Nama supplier wajib diisi!")
                        return
                    try:
                        db.add_supplier(nama, e_alamat.get().strip(), e_kontak.get().strip())
                    except Exception as e:
                        msgbox.showerror("Database Error", f"Gagal menyimpan supplier:\n{e}")
                        return
                    result["success"] = True
                    result["nama"] = nama
                    win.destroy()

                f_btn = tk.Frame(win, bg="white")
                f_btn.pack(pady=15)
                CustomButton(f_btn, text="Simpan Supplier", command=simpan_popup, bg="#34A853").pack(side=tk.LEFT, padx=5)
                CustomButton(f_btn, text="Batal", command=win.destroy, bg="#D84315").pack(side=tk.LEFT, padx=5)

                win.wait_window()
                return result

            def prompt_produk_baru(nama_awal, harga_awal=""):
                """Popup isi data produk baru (Nama/Kategori/Harga/Tgl Exp), sama seperti form di Kelola Produk.
                Return True kalau berhasil disimpan, False kalau dibatalkan."""
                result = {"success": False}

                win = tk.Toplevel(root)
                win.title("Tambah Produk Baru")
                win.geometry("400x320")
                win.configure(bg="white")
                win.transient(root)
                win.grab_set()

                tk.Label(win, text="Produk belum terdaftar", font=("Calibri", 13, "bold"), bg="white", fg="#1E8E3E").pack(pady=(15, 2))
                tk.Label(win, text="Lengkapi data produk baru berikut:", font=("Calibri", 9), bg="white", fg="#888888").pack(pady=(0, 10))

                f = tk.Frame(win, bg="white")
                f.pack(padx=20, fill=tk.X)

                tk.Label(f, text="Nama Produk:", bg="white", fg="#333333").grid(row=0, column=0, sticky="w", pady=4)
                e_nama = tk.Entry(f, bg="white", fg="black", width=25)
                e_nama.grid(row=0, column=1, pady=4)
                e_nama.insert(0, nama_awal)

                tk.Label(f, text="Kategori:", bg="white", fg="#333333").grid(row=1, column=0, sticky="w", pady=4)
                cb_kategori = ttk.Combobox(f, values=["Obat", "Alkes", "BHP"], width=22)
                cb_kategori.grid(row=1, column=1, pady=4)
                cb_kategori.set("Obat")

                tk.Label(f, text="Harga Jual:", bg="white", fg="#333333").grid(row=2, column=0, sticky="w", pady=4)
                e_harga = tk.Entry(f, bg="white", fg="black", width=25)
                e_harga.grid(row=2, column=1, pady=4)
                e_harga.insert(0, harga_awal)

                tk.Label(f, text="Tgl Exp (YYYY-MM-DD):", bg="white", fg="#333333").grid(row=3, column=0, sticky="w", pady=4)
                e_exp = tk.Entry(f, bg="white", fg="black", width=25)
                e_exp.grid(row=3, column=1, pady=4)

                def simpan_popup():
                    nama = e_nama.get().strip()
                    harga_s = e_harga.get().strip()
                    if not nama:
                        msgbox.showwarning("Peringatan", "Nama produk wajib diisi!")
                        return
                    if not harga_s.isdigit():
                        msgbox.showwarning("Peringatan", "Harga jual harus berupa angka!")
                        return
                    try:
                        db.add_product(nama, cb_kategori.get(), int(harga_s), 0, e_exp.get().strip() or None)
                    except Exception as e:
                        msgbox.showerror("Database Error", f"Gagal menyimpan produk:\n{e}")
                        return
                    result["success"] = True
                    result["nama"] = nama
                    win.destroy()

                f_btn = tk.Frame(win, bg="white")
                f_btn.pack(pady=15)
                CustomButton(f_btn, text="Simpan Produk", command=simpan_popup, bg="#34A853").pack(side=tk.LEFT, padx=5)
                CustomButton(f_btn, text="Batal", command=win.destroy, bg="#D84315").pack(side=tk.LEFT, padx=5)

                win.wait_window()
                return result

            def simpan_pembelian():
                supplier_nama = cb_supplier.get().strip()
                produk_nama = cb_produk.get().strip()
                qty_s = ent_qty.get().strip()
                harga_s = ent_harga.get().strip() or "0"
                tanggal = ent_beli.get_date_str()
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

                # Kalau supplier belum terdaftar, minta lengkapi datanya dulu lewat popup
                supplier_exists = any(s.lower() == supplier_nama.lower() for s in all_supplier_names)
                if not supplier_exists:
                    hasil = prompt_supplier_baru(supplier_nama)
                    if not hasil["success"]:
                        return  # dibatalkan
                    supplier_nama = hasil["nama"]
                    suppliers_cache[:] = db.get_all_suppliers()
                    all_supplier_names[:] = [s["nama"] for s in suppliers_cache]
                    cb_supplier['values'] = all_supplier_names

                # Kalau produk belum terdaftar, minta lengkapi datanya dulu lewat popup
                prod = db.get_product_by_name(produk_nama)
                if not prod:
                    hasil = prompt_produk_baru(produk_nama, harga_s)
                    if not hasil["success"]:
                        return  # dibatalkan
                    produk_nama = hasil["nama"]
                    prod = db.get_product_by_name(produk_nama)
                    products_cache[:] = db.get_all_products()
                    all_product_names[:] = [p["nama"] for p in products_cache]
                    cb_produk['values'] = all_product_names

                if not prod:
                    msgbox.showerror("Error", "Produk gagal ditemukan setelah didaftarkan.")
                    return

                try:
                    db.process_pembelian(
                        prod["id"], produk_nama, supplier_nama,
                        int(qty_s), int(harga_s), tanggal, catatan
                    )
                except Exception as e:
                    msgbox.showerror("Database Error", f"Gagal menyimpan pembelian:\n{e}")
                    return

                refresh()
                cb_supplier.set(""); cb_produk.set("")
                ent_qty.delete(0, tk.END); ent_harga.delete(0, tk.END); ent_catatan.delete(0, tk.END)
                ent_beli.set_date(datetime.now())
                msgbox.showinfo("Sukses", f"Pembelian {qty_s} {produk_nama} dari {supplier_nama} berhasil dicatat, stok otomatis bertambah!")

            def hapus_pembelian():
                selected = tree.selection()
                if selected:
                    if msgbox.askyesno("Konfirmasi", "Hapus riwayat pembelian ini?"):
                        db.delete_pembelian(int(selected[0]))
                        refresh()

            CustomButton(f_form, text="Catat Pembelian", command=simpan_pembelian, bg="#34A853").grid(row=1, column=4, rowspan=2, padx=10)
            CustomButton(content, text="🗑 Hapus Riwayat Selected", command=hapus_pembelian, bg="#D84315").pack(anchor="w")

            refresh()

        # 9. STOK OPNAME
        def show_stok_opname():
            clear_content()
            tk.Label(content, text="Stok Opname (Penyesuaian Fisik)", font=("Calibri", 18, "bold"), bg="white", fg="#1E8E3E").pack(anchor="w", pady=(0, 10))

            f_form = tk.Frame(content, bg="white")
            f_form.pack(fill=tk.X, pady=5)

            tk.Label(f_form, text="Pilih Item:", bg="white", fg="#333333").grid(row=0, column=0, sticky="w", pady=2)
            all_item_names = [p["nama"] for p in db.get_all_products()]
            cb_item = ttk.Combobox(f_form, values=all_item_names, width=18)
            cb_item.grid(row=0, column=1, padx=(5, 15), pady=2, sticky="w")

            def on_keyrelease_item(event):
                if event.keysym in ("Up", "Down", "Return", "Escape", "Tab"): return
                typed = cb_item.get().lower()
                cb_item['values'] = all_item_names if typed == '' else [item for item in all_item_names if typed in item.lower()]

            cb_item.bind('<KeyRelease>', on_keyrelease_item)

            tk.Label(f_form, text="Stok Sistem:", bg="white", fg="#333333").grid(row=0, column=2, sticky="w", pady=2)
            lbl_sys_stok = tk.Label(f_form, text="0", bg="#E0E0E0", fg="black", width=6, font=("Calibri", 10, "bold"))
            lbl_sys_stok.grid(row=0, column=3, padx=(5, 15), pady=2, sticky="w")

            tk.Label(f_form, text="Stok Fisik:", bg="white", fg="#333333").grid(row=0, column=4, sticky="w", pady=2)
            ent_fisik = tk.Entry(f_form, width=6, bg="white", fg="black")
            ent_fisik.grid(row=0, column=5, padx=(5, 15), pady=2, sticky="w")

            tk.Label(f_form, text="Tgl Stok Opname:", bg="white", fg="#333333").grid(row=0, column=6, sticky="w", pady=2)
            ent_tgl_opname = DateSelector(f_form)
            ent_tgl_opname.grid(row=0, column=7, padx=5, pady=2, sticky="w")

            btn_container = tk.Frame(f_form, bg="white")
            btn_container.grid(row=1, column=0, columnspan=8, sticky="w", pady=(10, 5))

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
                p_name = cb_item.get().strip()
                fisik_s = ent_fisik.get().strip()
                tgl_opname = ent_tgl_opname.get_date_str()
                prod = db.get_product_by_name(p_name)

                if not prod:
                    msgbox.showwarning("Peringatan", "Pilih atau masukkan barang yang valid!")
                    return

                if not fisik_s.isdigit():
                    msgbox.showwarning("Peringatan", "Stok fisik harus berupa angka positif!")
                    return

                fisik = int(fisik_s)
                stok_sistem = prod["stok"]
                selisih = fisik - stok_sistem

                try:
                    # 1. Catat riwayat opname beserta tanggal pilihan UI
                    db.add_stok_opname(p_name, stok_sistem, fisik, selisih, tgl_opname)
                    
                    # 2. Update stok & log mutasi riwayat_stok sesuai tanggal pilihan UI
                    db.process_stok_opname(prod["id"], p_name, fisik, f"Opname Tanggal {tgl_opname}", tgl_opname)

                    refresh()
                    cb_item.set("")
                    lbl_sys_stok.config(text="0")
                    ent_fisik.delete(0, tk.END)
                    ent_tgl_opname.set_date(datetime.now())

                    status_selisih = f"Selisih Lebih: +{selisih}" if selisih > 0 else (f"Selisih Kurang: {selisih}" if selisih < 0 else "Stok Sesuai (0)")
                    msgbox.showinfo("Sukses", f"Stok Opname Berhasil!\nStok {p_name} diperbarui menjadi {fisik}.\nStatus: {status_selisih}")
                except Exception as e:
                    msgbox.showerror("Database Error", f"Gagal memproses Stok Opname:\n{e}")

                    
            def hapus_opname():
                selected = tree.selection()
                if selected:
                    db.delete_stok_opname(int(selected[0]))
                    refresh()

            CustomButton(btn_container, text="Proses Opname", command=simpan_opname, bg="#34A853").pack(side=tk.LEFT)
            CustomButton(content, text="🗑 Hapus Riwayat Selected", command=hapus_opname, bg="#D84315").pack(anchor="w")
            
            refresh()

        # 10. LAPORAN PENJUALAN
        def show_laporan_penjualan():
            clear_content()
            tk.Label(content, text="📈 Laporan Penjualan & Analisis Omzet", font=("Calibri", 18, "bold"), bg="white", fg="#1E8E3E").pack(anchor="w", pady=(0, 10))

            f_filter = tk.Frame(content, bg="white")
            f_filter.pack(fill=tk.X, pady=5)

            tgl_hari_ini = datetime.now()
            tgl_awal_bulan = datetime.now() - timedelta(days=30)

            tk.Label(f_filter, text="Dari Tanggal:", bg="white", fg="#333333").grid(row=0, column=0, sticky="w")
            ent_tgl_mulai = DateSelector(f_filter, default_date=tgl_awal_bulan)
            ent_tgl_mulai.grid(row=0, column=1, padx=5)

            tk.Label(f_filter, text="Sampai Tanggal:", bg="white", fg="#333333").grid(row=0, column=2, padx=(10, 0), sticky="w")
            ent_tgl_selesai = DateSelector(f_filter, default_date=tgl_hari_ini)
            ent_tgl_selesai.grid(row=0, column=3, padx=5)

            f_cards = tk.Frame(content, bg="white")
            f_cards.pack(fill=tk.X, pady=10)

            lbl_omzet_val = tk.Label(f_cards, text="Total Omzet: Rp 0", font=("Calibri", 16, "bold"), bg="#1E8E3E", fg="white", padx=15, pady=10)
            lbl_omzet_val.pack(side=tk.LEFT, padx=(0, 10))

            lbl_qty_val = tk.Label(f_cards, text="Total Terjual: 0 Item", font=("Calibri", 16, "bold"), bg="#00838F", fg="white", padx=15, pady=10)
            lbl_qty_val.pack(side=tk.LEFT)

            f_grid = tk.Frame(content, bg="white")
            f_grid.pack(fill=tk.BOTH, expand=True, pady=10)

            f_top = tk.LabelFrame(f_grid, text="🏆 Top 5 Produk Terlaris", font=("Calibri", 11, "bold"), bg="white", fg="#1E8E3E", padx=10, pady=10)
            f_top.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

            tree_top = ttk.Treeview(f_top, columns=("Produk", "Terjual", "Omzet"), show="headings", height=8)
            tree_top.heading("Produk", text="Produk"); tree_top.column("Produk", width=130, anchor="w")
            tree_top.heading("Terjual", text="Qty"); tree_top.column("Terjual", width=50, anchor="center")
            tree_top.heading("Omzet", text="Omzet"); tree_top.column("Omzet", width=100, anchor="e")
            tree_top.pack(fill=tk.BOTH, expand=True)

            f_trans = tk.LabelFrame(f_grid, text="📋 Riwayat Transaksi Lengkap", font=("Calibri", 11, "bold"), bg="white", fg="#1E8E3E", padx=10, pady=10)
            f_trans.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

            tree_trans = ttk.Treeview(f_trans, columns=("Waktu", "Pasien", "Produk", "Qty", "Total"), show="headings", height=8)
            tree_trans.heading("Waktu", text="Waktu"); tree_trans.column("Waktu", width=130, anchor="center")
            tree_trans.heading("Pasien", text="Pasien"); tree_trans.column("Pasien", width=100, anchor="w")
            tree_trans.heading("Produk", text="Produk"); tree_trans.column("Produk", width=120, anchor="w")
            tree_trans.heading("Qty", text="Qty"); tree_trans.column("Qty", width=45, anchor="center")
            tree_trans.heading("Total", text="Total"); tree_trans.column("Total", width=90, anchor="e")
            tree_trans.pack(fill=tk.BOTH, expand=True)

            def filter_laporan():
                tgl_m = ent_tgl_mulai.get_date_str()
                tgl_s = ent_tgl_selesai.get_date_str()

                try:
                    data = db.get_laporan_penjualan(tgl_m, tgl_s)
                except Exception as e:
                    msgbox.showerror("Error", f"Gagal memuat laporan penjualan:\n{e}")
                    return

                lbl_omzet_val.config(text=f"Total Omzet: Rp {data['total_omzet']:,}")
                lbl_qty_val.config(text=f"Total Terjual: {data['total_item']:,} Item")

                for r in tree_top.get_children(): tree_top.delete(r)
                for tp in data["top_products"]:
                    tree_top.insert("", tk.END, values=(tp["produk"], tp["total_qty"], f"Rp {tp['total_penjualan']:,}"))

                for r in tree_trans.get_children(): tree_trans.delete(r)
                for tr in data["transaksi"]:
                    waktu_str = tr["waktu"].strftime("%Y-%m-%d %H:%M")
                    tree_trans.insert("", tk.END, values=(waktu_str, tr["pasien"], tr["produk"], tr["qty"], f"Rp {tr['total']:,}"))

            CustomButton(f_filter, text="🔍 Tampilkan Laporan", command=filter_laporan, bg="#34A853").grid(row=0, column=4, padx=10)
            filter_laporan()

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

        if user_role in ["Admin", "Kasir", "Apoteker"]:
            btn_nav("📈 Laporan Penjualan", show_laporan_penjualan).pack(fill=tk.X)

        if user_role == "Admin":
            btn_nav("👤 Kelola User", show_kelola_user).pack(fill=tk.X)

        show_dashboard()

    show_dashboard_layout()
    apply_responsive_styles(root)

    def on_closing():
        root.quit()
        root.destroy()
        sys.exit(0)

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()