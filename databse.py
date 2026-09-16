import sqlite3
connection=sqlite3.connect("link.db")
cursor=connection.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    centre TEXT,
    date TEXT,
    time TEXT,
    crop TEXT,
    quantity INTEGER,
    token INTEGER)
""")
connection.commit()
connection.close()

