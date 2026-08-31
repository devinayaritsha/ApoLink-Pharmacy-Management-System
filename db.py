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
            "FROM stok_opname ORDER BY id DESC"
        )
        return cur.fetchall()


def add_stok_opname(produk_nama, stok_sistem, stok_fisik, selisih, tanggal=None):
    with get_connection() as conn, conn.cursor() as cur:
        if tanggal:
            cur.execute(
                "INSERT INTO stok_opname (produk_nama, stok_sistem, stok_fisik, selisih, waktu) "
                "VALUES (%s, %s, %s, %s, %s)",
                (produk_nama, stok_sistem, stok_fisik, selisih, tanggal),
            )
        else:
            cur.execute(
                "INSERT INTO stok_opname (produk_nama, stok_sistem, stok_fisik, selisih) "
                "VALUES (%s, %s, %s, %s)",
                (produk_nama, stok_sistem, stok_fisik, selisih),
            )
        conn.commit()


def delete_stok_opname(opname_id):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM stok_opname WHERE id=%s", (opname_id,))
        conn.commit()


# ================= TRANSAKSI =================

def get_transaksi_by_produk(nama_produk):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT waktu, pasien, produk, qty, total FROM transaksi "
            "WHERE produk=%s ORDER BY waktu DESC",
            (nama_produk,),
        )
        return cur.fetchall()


def process_sale(cart_items, nama_pasien):
    """
    Proses satu transaksi kasir: kurangi stok tiap produk & catat riwayat transaksi
    dalam satu database transaction (all-or-nothing).

    cart_items: list of dict, tiap item minimal punya keys:
        id (product id), nama, qty, subtotal
    """
    waktu = datetime.now()
    with get_connection() as conn, conn.cursor() as cur:
        for item in cart_items:
            cur.execute(
                "UPDATE products SET stok = stok - %s WHERE id=%s",
                (item["qty"], item["id"]),
            )
            cur.execute(
                "INSERT INTO transaksi (waktu, pasien, produk, qty, total) "
                "VALUES (%s, %s, %s, %s, %s)",
                (waktu, nama_pasien, item["nama"], item["qty"], item["subtotal"]),
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


def process_pembelian(product_id, produk_nama, supplier_nama, qty, harga_beli, tanggal, catatan):
    """
    Catat satu pembelian/restock dari supplier & otomatis tambahkan stok produk terkait,
    dalam satu database transaction (all-or-nothing).
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("UPDATE products SET stok = stok + %s WHERE id=%s", (qty, product_id))
        cur.execute(
            "INSERT INTO pembelian (supplier_nama, produk_nama, qty, harga_beli, tanggal, catatan) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (supplier_nama, produk_nama, qty, harga_beli, tanggal, catatan),
        )
        conn.commit()


def delete_pembelian(pembelian_id):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM pembelian WHERE id=%s", (pembelian_id,))
        conn.commit()