-- ================================================================
-- ApoLink Pharmacy Management System - PostgreSQL Schema
-- Jalankan file ini sekali di database kamu untuk membuat tabel.
-- Contoh: psql -U postgres -d apolink -f schema.sql
-- ================================================================

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('Admin', 'Kasir', 'Apoteker'))
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    nama VARCHAR(150) NOT NULL,
    kategori VARCHAR(20) NOT NULL,
    harga INTEGER NOT NULL,
    stok INTEGER NOT NULL DEFAULT 0,
    tgl_exp DATE
);

CREATE TABLE IF NOT EXISTS pasien (
    id SERIAL PRIMARY KEY,
    nama VARCHAR(150) NOT NULL,
    kontak VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS suppliers (
    id SERIAL PRIMARY KEY,
    nama VARCHAR(150) NOT NULL,
    alamat VARCHAR(255),
    kontak VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS stok_opname (
    id SERIAL PRIMARY KEY,
    produk_nama VARCHAR(150) NOT NULL,
    stok_sistem INTEGER NOT NULL,
    stok_fisik INTEGER NOT NULL,
    selisih INTEGER NOT NULL,
    waktu TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS transaksi (
    id SERIAL PRIMARY KEY,
    waktu TIMESTAMP NOT NULL DEFAULT NOW(),
    pasien VARCHAR(150),
    produk VARCHAR(150) NOT NULL,
    qty INTEGER NOT NULL,
    total INTEGER NOT NULL
);

-- ================================================================
-- Seed data awal (sama seperti data dummy yang ada di kode lama)
-- ================================================================

INSERT INTO users (nama, username, password, role) VALUES
    ('Administrator', 'admin', '123', 'Admin'),
    ('Budi Setiawan', 'budi', '123', 'Kasir'),
    ('Siti Aminah', 'siti', '123', 'Apoteker')
ON CONFLICT (username) DO NOTHING;

INSERT INTO products (nama, kategori, harga, stok, tgl_exp) VALUES
    ('Paracetamol 500mg', 'Obat', 5000, 50, '2026-12-31'),
    ('Alkohol 70%', 'Alkes', 12000, 4, '2026-09-15'),
    ('Kasa Steril', 'BHP', 15000, 2, '2026-08-01'),
    ('Amoxicillin 500mg', 'Obat', 8000, 20, '2027-05-20'),
    ('Vitamin C 1000mg', 'Obat', 10000, 30, '2026-09-01');

INSERT INTO pasien (nama, kontak) VALUES
    ('Budi Santoso', '08123456789'),
    ('Siti Aminah', '08567890123');

INSERT INTO suppliers (nama, alamat, kontak) VALUES
    ('PT Kimia Farma', 'Jl. Veteran No. 10', '021-5551234');
