-- ================================================================
-- Migrasi: tambah tabel `riwayat_stok` (log audit trail setiap mutasi stok:
-- penjualan kasir, restock dari supplier, dan penyesuaian stok opname).
-- Jalankan ini kalau database kamu sudah ada sebelumnya.
-- Contoh: psql -U postgres -d apolink -f migration_riwayat_stok.sql
-- ================================================================

CREATE TABLE IF NOT EXISTS riwayat_stok (
    id SERIAL PRIMARY KEY,
    produk_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    produk_nama VARCHAR(150) NOT NULL,
    waktu TIMESTAMP NOT NULL DEFAULT NOW(),
    tipe_transaksi VARCHAR(20) NOT NULL CHECK (tipe_transaksi IN ('Restock (Masuk)', 'Penjualan (Keluar)', 'Stok Opname')),
    keterangan VARCHAR(255),
    stok_awal INTEGER NOT NULL,
    qty_masuk INTEGER NOT NULL DEFAULT 0,
    qty_keluar INTEGER NOT NULL DEFAULT 0,
    stok_akhir INTEGER NOT NULL
);