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
    waktu_input = tanggal_opname if tanggal_opname else datetime.now()
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO stok_opname (produk_nama, stok_sistem, stok_fisik, selisih, waktu) "
            "VALUES (%s, %s, %s, %s, %s)",
            (produk_nama, stok_sistem, stok_fisik, selisih, waktu_input),
        )
        conn.commit()


def process_stok_opname(product_id, produk_nama, stok_fisik, keterangan_opname="Penyesuaian Stok Opname", tanggal_opname=None):
    waktu_sekarang = tanggal_opname if tanggal_opname else datetime.now()
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT stok FROM products WHERE id=%s FOR UPDATE", (product_id,))
        prod = cur.fetchone()
        stok_awal = prod["stok"] if prod else 0
        
        selisih = stok_fisik - stok_awal
        qty_masuk = selisih if selisih > 0 else 0
        qty_keluar = abs(selisih) if selisih < 0 else 0

        if selisih == 0:
            return False

        cur.execute("UPDATE products SET stok = %s WHERE id=%s", (stok_fisik, product_id))

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
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT waktu, tipe_transaksi, keterangan, stok_awal, qty_masuk, qty_keluar, stok_akhir "
            "FROM riwayat_stok WHERE LOWER(produk_nama) = LOWER(%s) ORDER BY waktu DESC, id DESC",
            (nama_produk,),
        )
        return cur.fetchall()


# ================= TRANSAKSI (PENJUALAN KASIR) =================

def process_sale(cart_items, nama_pasien, resep_id=None):
    waktu = datetime.now()
    with get_connection() as conn, conn.cursor() as cur:
        for item in cart_items:
            cur.execute("SELECT stok FROM products WHERE id=%s FOR UPDATE", (item["id"],))
            prod = cur.fetchone()
            stok_awal = prod["stok"] if prod else 0
            stok_akhir = stok_awal - item["qty"]

            cur.execute(
                "UPDATE products SET stok = %s WHERE id=%s",
                (stok_akhir, item["id"]),
            )

            cur.execute(
                "INSERT INTO transaksi (waktu, pasien, produk, qty, total) "
                "VALUES (%s, %s, %s, %s, %s)",
                (waktu, nama_pasien, item["nama"], item["qty"], item["subtotal"]),
            )

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

        if resep_id:
            cur.execute("UPDATE resep SET status = 'COMPLETED' WHERE id = %s", (resep_id,))

        conn.commit()
    return waktu


# ================= PEMBELIAN =================

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
            "WHERE LOWER(pasien)=LOWER(%s) ORDER BY waktu DESC",
            (nama_pasien,),
        )
        return cur.fetchall()


def get_laporan_penjualan(tgl_mulai, tgl_selesai):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, waktu, pasien, produk, qty, total "
            "FROM transaksi WHERE DATE(waktu) >= %s AND DATE(waktu) <= %s "
            "ORDER BY waktu DESC",
            (tgl_mulai, tgl_selesai),
        )
        transaksi = cur.fetchall()

        total_omzet = sum(t["total"] for t in transaksi)
        total_item = sum(t["qty"] for t in transaksi)

        cur.execute(
            "SELECT produk, SUM(qty) as total_qty, SUM(total) as total_penjualan "
            "FROM transaksi WHERE DATE(waktu) >= %s AND DATE(waktu) <= %s "
            "GROUP BY produk ORDER BY total_qty DESC LIMIT 5",
            (tgl_mulai, tgl_selesai),
        )
        top_products = cur.fetchall()

        return {
            "transaksi": transaksi,
            "total_omzet": total_omzet,
            "total_item": total_item,
            "top_products": top_products,
        }


# ================= RESEP PASIEN (BARU) =================

def create_resep_step1(nama_pasien, dokter_penulis, tanggal_resep, item_list):
    now = datetime.now()
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM resep")
        cnt = cur.fetchone()["count"] + 1
        nomor_resep = f"RXP-{cnt:03d}"

        cur.execute(
            "INSERT INTO resep (nomor_resep, nama_pasien, dokter_penulis, tanggal_resep, status, preparation_start_time, hasil_telaah) "
            "VALUES (%s, %s, %s, %s, 'DRAFT', %s, 'Belum Telaah') RETURNING id",
            (nomor_resep, nama_pasien, dokter_penulis, tanggal_resep, now),
        )
        resep_id = cur.fetchone()["id"]

        for item in item_list:
            cur.execute(
                "INSERT INTO resep_detail (resep_id, produk_id, produk_nama, dosis_aturan, jumlah, harga_satuan, subtotal) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    resep_id,
                    item["produk_id"],
                    item["produk_nama"],
                    item["dosis_aturan"],
                    item["jumlah"],
                    item["harga_satuan"],
                    item["subtotal"],
                ),
            )
        conn.commit()
        return resep_id, nomor_resep


def update_resep_telaah(resep_id, hasil_telaah="Lengkap (Pass)"):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE resep SET status = 'REVIEWED', hasil_telaah = %s WHERE id = %s",
            (hasil_telaah, resep_id),
        )
        conn.commit()


def complete_resep_validation(resep_id):
    now = datetime.now()
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT preparation_start_time FROM resep WHERE id = %s", (resep_id,))
        rsp = cur.fetchone()
        start_time = rsp["preparation_start_time"] if rsp else now
        
        duration_sec = int((now - start_time).total_seconds())

        cur.execute(
            "UPDATE resep SET status = 'READY_TO_BILL', preparation_end_time = %s, duration_seconds = %s WHERE id = %s",
            (now, duration_sec, resep_id),
        )
        cur.execute("UPDATE resep_detail SET is_validated = TRUE WHERE resep_id = %s", (resep_id,))
        conn.commit()


def get_all_resep():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, nomor_resep, nama_pasien, dokter_penulis, tanggal_resep, status, "
            "preparation_start_time, preparation_end_time, duration_seconds, hasil_telaah "
            "FROM resep ORDER BY id DESC"
        )
        return cur.fetchall()


def get_resep_by_id(resep_id):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM resep WHERE id = %s", (resep_id,))
        rsp = cur.fetchone()
        if rsp:
            cur.execute("SELECT * FROM resep_detail WHERE resep_id = %s ORDER BY id", (resep_id,))
            rsp["items"] = cur.fetchall()
        return rsp


def get_resep_ready_to_bill():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM resep WHERE status = 'READY_TO_BILL' ORDER BY id DESC")
        reseps = cur.fetchall()
        for r in reseps:
            cur.execute("SELECT * FROM resep_detail WHERE resep_id = %s", (r["id"],))
            r["items"] = cur.fetchall()
        return reseps