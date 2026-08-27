import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_FILE = 'database_lab.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS labs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_lab TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_barang TEXT NOT NULL,
        value TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        nama_lab TEXT NOT NULL,
        tanggal TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        kelas TEXT NOT NULL,
        prodi TEXT NOT NULL,
        tujuan TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bhp (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        nama_barang TEXT NOT NULL,
        praktikum TEXT NOT NULL,
        jumlah INTEGER NOT NULL,
        tanggal TEXT NOT NULL,
        prodi TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        filename TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS maintenance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_lab TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        keterangan TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')

    # Add a default admin user
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                       ('admin', generate_password_hash('admin123')))

    cursor.execute('SELECT COUNT(*) FROM labs')
    if cursor.fetchone()[0] == 0:
        default_labs = [
            ('Lab Ward',), ('Lab Emergency',), ('Lab Keluarga',), ('Lab Gerontik',), 
            ('Lab Mikrobiologi Gd.G',), ('Lab Histologi Gd.G',), ('Lab Anatomi',), ('Lab Promkes',)
        ]
        cursor.executemany('INSERT INTO labs (nama_lab) VALUES (?)', default_labs)

    cursor.execute('SELECT COUNT(*) FROM items')
    if cursor.fetchone()[0] == 0:
        default_items = [
            ('Masker Sensi (Box)', 'Masker'),
            ('Handscoon Steril (Pasang)', 'Handscoon'),
            ('Spuit 3cc (Pcs)', 'Spuit 3cc'),
            ('Infusion Set (Set)', 'Infusion Set'),
            ('Kassa Steril (Pack)', 'Kassa Steril'),
            ('Cairan NaCl 0.9% (Botol)', 'Cairan NaCl 0.9%')
        ]
        cursor.executemany('INSERT INTO items (nama_barang, value) VALUES (?, ?)', default_items)

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
