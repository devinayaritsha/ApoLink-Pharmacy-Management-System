-- ================================================================
-- Migrasi: tambah tabel `pembelian` (menu Pembelian Barang dari Supplier)
-- Jalankan ini kalau database kamu sudah ada sebelumnya (tidak perlu
-- menjalankan ulang schema.sql yang lama).
-- Contoh: psql -U postgres -d apolink -f migration_pembelian.sql
-- ================================================================

CREATE TABLE IF NOT EXISTS pembelian (
    id SERIAL PRIMARY KEY,
    supplier_nama VARCHAR(150) NOT NULL,
    produk_nama VARCHAR(150) NOT NULL,
    qty INTEGER NOT NULL,
    harga_beli INTEGER NOT NULL DEFAULT 0,
    tanggal DATE NOT NULL DEFAULT CURRENT_DATE,
    catatan VARCHAR(255)
);