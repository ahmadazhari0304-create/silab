import sqlite3

conn = sqlite3.connect('database_lab.db')
c = conn.cursor()

# Enable WAL Mode
c.execute('PRAGMA journal_mode=WAL;')
print('Journal mode:', c.fetchone())

# Add indexes to bookings
c.execute('CREATE INDEX IF NOT EXISTS idx_bookings_tanggal ON bookings(tanggal);')
c.execute('CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);')
c.execute('CREATE INDEX IF NOT EXISTS idx_bookings_lab ON bookings(nama_lab);')

# Add indexes to labs
c.execute('CREATE INDEX IF NOT EXISTS idx_labs_nama ON labs(nama_lab);')

# Add indexes to users
c.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);')

conn.commit()
print('Indexes created successfully!')
conn.close()
