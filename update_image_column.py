import sqlite3

conn = sqlite3.connect('database.db')
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE products ADD COLUMN image TEXT")
    conn.commit()
    print("✅ Image column added successfully!")
except Exception as e:
    print("ℹ️", e)

conn.close()