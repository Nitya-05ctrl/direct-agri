import sqlite3

conn = sqlite3.connect('database.db')
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE products ADD COLUMN user_id INTEGER")
    conn.commit()
    print("✅ user_id column added")
except Exception as e:
    print(e)

conn.close()