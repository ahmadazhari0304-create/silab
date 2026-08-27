import sqlite3

conn = sqlite3.connect('database_lab.db')
c = conn.cursor()
try:
    c.execute("ALTER TABLE labs ADD COLUMN status TEXT DEFAULT 'Tersedia'")
    conn.commit()
    print('Column status added.')
except Exception as e:
    print('Error:', e)
finally:
    conn.close()
