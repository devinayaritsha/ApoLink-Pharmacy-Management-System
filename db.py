"""
db.py - Lapisan akses database PostgreSQL untuk ApoLink.

Semua kredensial diambil dari environment variable (lihat .env.example).
Jangan hardcode username/password database di sini.
"""

import os
from datetime import datetime

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "apolink"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}


def get_connection():
    """Buka koneksi baru ke PostgreSQL. Baris dikembalikan sebagai dict (RealDictRow)."""
    return psycopg2.connect(cursor_factory=psycopg2.extras.RealDictCursor, **DB_CONFIG)


# ================= USERS =================

def get_all_users():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, nama, username, password, role FROM users ORDER BY id")
        return cur.fetchall()


def authenticate_user(username, password):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, nama, username, password, role FROM users WHERE username=%s AND password=%s",
            (username, password),
        )
        return cur.fetchone()


def add_user(nama, username, password, role):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (nama, username, password, role) VALUES (%s, %s, %s, %s)",
            (nama, username, password, role),
        )
        conn.commit()


def delete_user(user_id):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
        conn.commit()

def update_user_password(user_id, new_password):
    """Memperbarui kata sandi user berdasarkan user_id."""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE users SET password = %s WHERE id = %s",
            (new_password, user_id),
        )
        conn.commit()


# ================= PRODUCTS =================

def get_all_products():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, nama, kategori, harga, stok, tgl_exp FROM products ORDER BY id")
        return cur.fetchall()


def get_product_by_name(nama):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, nama, kategori, harga, stok, tgl_exp FROM products WHERE nama=%s", (nama,))
        return cur.fetchone()


def add_product(nama, kategori, harga, stok, tgl_exp):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO products (nama, kategori, harga, stok, tgl_exp) VALUES (%s, %s, %s, %s, %s)",
            (nama, kategori, harga, stok, tgl_exp),
        )
        conn.commit()


def update_product_stok(product_id, stok_baru):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("UPDATE products SET stok=%s WHERE id=%s", (stok_baru, product_id))
        conn.commit()


def delete_product(product_id):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM products WHERE id=%s", (product_id,))
        conn.commit()


# ================= PASIEN =================

def get_all_pasien():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, nama, kontak FROM pasien ORDER BY id")
        return cur.fetchall()


def add_pasien(nama, kontak):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO pasien (nama, kontak) VALUES (%s, %s)", (nama, kontak))
        conn.commit()


def delete_pasien(pasien_id):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM pasien WHERE id=%s", (pasien_id,))
        conn.commit()


# ================= SUPPLIERS =================

def get_all_suppliers():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, nama, alamat, kontak FROM suppliers ORDER BY id")
        return cur.fetchall()


def add_supplier(nama, alamat, kontak):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO suppliers (nama, alamat, kontak) VALUES (%s, %s, %s)",
            (nama, alamat, kontak),
        )
        conn.commit()


def delete_supplier(supplier_id):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM suppliers WHERE id=%s", (supplier_id,))
        conn.commit()


# ================= STOK OPNAME =================

def get_all_stok_opname():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, produk_nama, stok_sistem, stok_fisik, selisih, waktu "
            "FROM stok_opname ORDER BY waktu DESC, id DESC"
        )
        return cur.fetchall()


def add_stok_opname(produk_nama, stok_sistem, stok_fisik, selisih, tanggal_opname=None):
    """Menyimpan record pencatatan stok opname beserta tanggal penyesuaiannya."""
    waktu_input = tanggal_opname if tanggal_opname else datetime.now()
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO stok_opname (produk_nama, stok_sistem, stok_fisik, selisih, waktu) "
            "VALUES (%s, %s, %s, %s, %s)",
            (produk_nama, stok_sistem, stok_fisik, selisih, waktu_input),
        )
        conn.commit()


def process_stok_opname(product_id, produk_nama, stok_fisik, keterangan_opname="Penyesuaian Stok Opname", tanggal_opname=None):
    """
    Menyesuaikan stok produk berdasarkan hasil opname fisik 
    dan mencatat selisihnya ke dalam tabel `riwayat_stok`.
    """
    waktu_sekarang = tanggal_opname if tanggal_opname else datetime.now()
    with get_connection() as conn, conn.cursor() as cur:
        # 1. Ambil stok awal dari sistem
        cur.execute("SELECT stok FROM products WHERE id=%s FOR UPDATE", (product_id,))
        prod = cur.fetchone()
        stok_awal = prod["stok"] if prod else 0
        
        # 2. Hitung selisih masuk/keluar
        selisih = stok_fisik - stok_awal
        qty_masuk = selisih if selisih > 0 else 0
        qty_keluar = abs(selisih) if selisih < 0 else 0

        if selisih == 0:
            return False

        # 3. Update master produk dengan stok hasil opname
        cur.execute("UPDATE products SET stok = %s WHERE id=%s", (stok_fisik, product_id))

        # 4. Catat mutasi stok opname ke riwayat_stok
        cur.execute(
            "INSERT INTO riwayat_stok (produk_id, produk_nama, waktu, tipe_transaksi, keterangan, stok_awal, qty_masuk, qty_keluar, stok_akhir) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                product_id,
                produk_nama,
                waktu_sekarang,
                "Stok Opname",
                f"{keterangan_opname} (Selisih: {selisih:+d})",
                stok_awal,
                qty_masuk,
                qty_keluar,
                stok_fisik,
            ),
        )
        conn.commit()
    return True


def delete_stok_opname(opname_id):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM stok_opname WHERE id=%s", (opname_id,))
        conn.commit()


# ================= RIWAYAT STOK =================

def get_riwayat_stok_by_produk(nama_produk):
    """Mengambil log mutasi riwayat stok berdasarkan nama produk."""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT waktu, tipe_transaksi, keterangan, stok_awal, qty_masuk, qty_keluar, stok_akhir "
            "FROM riwayat_stok WHERE LOWER(produk_nama) = LOWER(%s) ORDER BY waktu DESC, id DESC",
            (nama_produk,),
        )
        return cur.fetchall()

# ================= TRANSAKSI (PENJUALAN KASIR) =================

def process_sale(cart_items, nama_pasien):
    """
    Proses transaksi kasir: kurangi stok produk & catat ke tabel `transaksi` 
    serta log mutasi stok ke tabel `riwayat_stok` (All-in-one Transaction).
    """
    waktu = datetime.now()
    with get_connection() as conn, conn.cursor() as cur:
        for item in cart_items:
            # 1. Ambil stok saat ini (stok_awal)
            cur.execute("SELECT stok FROM products WHERE id=%s FOR UPDATE", (item["id"],))
            prod = cur.fetchone()
            stok_awal = prod["stok"] if prod else 0
            stok_akhir = stok_awal - item["qty"]

            # 2. Update stok di tabel master produk
            cur.execute(
                "UPDATE products SET stok = %s WHERE id=%s",
                (stok_akhir, item["id"]),
            )

            # 3. Catat transaksi penjualan
            cur.execute(
                "INSERT INTO transaksi (waktu, pasien, produk, qty, total) "
                "VALUES (%s, %s, %s, %s, %s)",
                (waktu, nama_pasien, item["nama"], item["qty"], item["subtotal"]),
            )

            # 4. Catat log mutasi ke riwayat_stok
            cur.execute(
                "INSERT INTO riwayat_stok (produk_id, produk_nama, waktu, tipe_transaksi, keterangan, stok_awal, qty_masuk, qty_keluar, stok_akhir) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    item["id"],
                    item["nama"],
                    waktu,
                    "Penjualan (Keluar)",
                    f"Penjualan Kasir - Pasien: {nama_pasien}",
                    stok_awal,
                    0,
                    item["qty"],
                    stok_akhir,
                ),
            )
        conn.commit()
    return waktu

# ================= PEMBELIAN (RESTOCK DARI SUPPLIER) =================

def get_all_pembelian():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, supplier_nama, produk_nama, qty, harga_beli, tanggal, catatan "
            "FROM pembelian ORDER BY tanggal DESC, id DESC"
        )
        return cur.fetchall()


def delete_pembelian(pembelian_id):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM pembelian WHERE id=%s", (pembelian_id,))
        conn.commit()


# ================= RIWAYAT & LAPORAN TRANSAKSI =================

def get_transaksi_by_produk(nama_produk):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT waktu, pasien, produk, qty, total FROM transaksi "
            "WHERE produk=%s ORDER BY waktu DESC",
            (nama_produk,),
        )
        return cur.fetchall()


def get_transaksi_by_pasien(nama_pasien):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT waktu, produk, qty, total FROM transaksi "
            "WHERE pasien=%s ORDER BY waktu DESC",
            (nama_pasien,),
        )
        return cur.fetchall()


def get_laporan_penjualan(tgl_mulai, tgl_selesai):
    """
    Mengembalikan ringkasan laporan penjualan dalam rentang tanggal tertentu:
    total omzet, total item terjual, top 5 produk terlaris, dan daftar transaksi lengkap.
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT waktu, pasien, produk, qty, total FROM transaksi "
            "WHERE waktu::date BETWEEN %s AND %s ORDER BY waktu DESC",
            (tgl_mulai, tgl_selesai),
        )
        rows = cur.fetchall()

    total_omzet = sum(r["total"] for r in rows)
    total_item = sum(r["qty"] for r in rows)

    agregat = {}
    for r in rows:
        key = r["produk"]
        if key not in agregat:
            agregat[key] = {"produk": key, "total_qty": 0, "total_penjualan": 0}
        agregat[key]["total_qty"] += r["qty"]
        agregat[key]["total_penjualan"] += r["total"]

    top_products = sorted(agregat.values(), key=lambda x: x["total_qty"], reverse=True)[:5]

    return {
        "total_omzet": total_omzet,
        "total_item": total_item,
        "top_products": top_products,
        "transaksi": rows,
    }


# ================= PROSES PEMBELIAN (UPDATE STOK + LOG) =================

def process_pembelian(product_id, produk_nama, supplier_nama, qty, harga_beli, tanggal, catatan):
    """
    Catat pembelian dari supplier, tambahkan stok produk, 
    dan log mutasi ke tabel `riwayat_stok`.
    """
    waktu_sekarang = datetime.now()
    with get_connection() as conn, conn.cursor() as cur:
        # 1. Ambil stok saat ini
        cur.execute("SELECT stok FROM products WHERE id=%s FOR UPDATE", (product_id,))
        prod = cur.fetchone()
        stok_awal = prod["stok"] if prod else 0
        stok_akhir = stok_awal + qty

        # 2. Update master produk
        cur.execute("UPDATE products SET stok = %s WHERE id=%s", (stok_akhir, product_id))

        # 3. Catat pembelian
        cur.execute(
            "INSERT INTO pembelian (supplier_nama, produk_nama, qty, harga_beli, tanggal, catatan) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (supplier_nama, produk_nama, qty, harga_beli, tanggal, catatan),
        )

        # 4. Catat log mutasi ke riwayat_stok
        cur.execute(
            "INSERT INTO riwayat_stok (produk_id, produk_nama, waktu, tipe_transaksi, keterangan, stok_awal, qty_masuk, qty_keluar, stok_akhir) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                product_id,
                produk_nama,
                waktu_sekarang,
                "Restock (Masuk)",
                f"Pembelian - Supplier: {supplier_nama}",
                stok_awal,
                qty,
                0,
                stok_akhir,
            ),
        )
        conn.commit()

# function buat dashboard
def get_dashboard_metrics(self):
    cursor = self.conn.cursor()
    
    # Total varian produk & produk stok menipis (<= 5)
    cursor.execute("SELECT COUNT(*), SUM(CASE WHEN stok <= 5 THEN 1 ELSE 0 END) FROM products")
    row_prod = cursor.fetchone()
    total_produk = row_prod[0] or 0
    stok_menipis = row_prod[1] or 0

    # Total Penjualan & Transaksi Hari Ini
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT COUNT(DISTINCT id), SUM(total_harga) 
        FROM penjualan 
        WHERE DATE(tanggal) = ?
    """, (today,))
    row_penjualan = cursor.fetchone()
    total_tx_today = row_penjualan[0] or 0
    omset_today = row_penjualan[1] or 0

    return {
        "total_produk": total_produk,
        "stok_menipis": stok_menipis,
        "tx_today": total_tx_today,
        "omset_today": omset_today
    }