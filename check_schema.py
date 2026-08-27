import sqlite3
conn = sqlite3.connect('database_lab.db')
c = conn.cursor()
print(c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='labs'").fetchone()[0])
print(c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='bookings'").fetchone()[0])
