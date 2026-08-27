-- Buat tabel users
CREATE TABLE public.users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0
);

-- Buat tabel labs
CREATE TABLE public.labs (
    id SERIAL PRIMARY KEY,
    nama_lab TEXT NOT NULL,
    status TEXT DEFAULT 'Tersedia'
);

-- Buat tabel items
CREATE TABLE public.items (
    id SERIAL PRIMARY KEY,
    nama_barang TEXT NOT NULL,
    value TEXT NOT NULL
);

-- Buat tabel bookings
CREATE TABLE public.bookings (
    id SERIAL PRIMARY KEY,
    nama_lab TEXT NOT NULL,
    tanggal DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    kelas TEXT NOT NULL,
    prodi TEXT NOT NULL,
    tujuan TEXT NOT NULL,
    user_id INTEGER REFERENCES public.users(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'pending'
);

-- Buat tabel bhp
CREATE TABLE public.bhp (
    id SERIAL PRIMARY KEY,
    nama_barang TEXT NOT NULL,
    praktikum TEXT NOT NULL,
    jumlah INTEGER NOT NULL CHECK (jumlah > 0),
    tanggal DATE NOT NULL,
    prodi TEXT NOT NULL DEFAULT 'D3',
    user_id INTEGER REFERENCES public.users(id) ON DELETE CASCADE
);

-- Buat tabel sops
CREATE TABLE public.sops (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    filename TEXT NOT NULL,
    user_id INTEGER REFERENCES public.users(id) ON DELETE CASCADE
);

-- Buat tabel maintenance
CREATE TABLE public.maintenance (
    id SERIAL PRIMARY KEY,
    nama_lab TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    keterangan TEXT NOT NULL,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE
);

-- Insert Data Awal
INSERT INTO public.users (username, password_hash, is_admin) VALUES
('admin', 'scrypt:32768:8:1$KqF24fB2bKhyk9a1$e876c164d1f27404f69165d3ec6ccb1916328328c704da8a2d18388ab7d98305041ff2544bd06b3a2723c34eb46ecff1c8ec78fdbf83c66f91f158525e9dd3d6', 1);

INSERT INTO public.labs (nama_lab) VALUES 
('Lab Ward'), ('Lab Emergency'), ('Lab Keluarga'), ('Lab Gerontik'), 
('Lab Mikrobiologi Gd.G'), ('Lab Histologi Gd.G'), ('Lab Anatomi'), ('Lab Promkes');

INSERT INTO public.items (nama_barang, value) VALUES
('Masker Sensi (Box)', 'Masker'),
('Handscoon Steril (Pasang)', 'Handscoon'),
('Spuit 3cc (Pcs)', 'Spuit 3cc'),
('Infusion Set (Set)', 'Infusion Set'),
('Kassa Steril (Pack)', 'Kassa Steril'),
('Cairan NaCl 0.9% (Botol)', 'Cairan NaCl 0.9%');
