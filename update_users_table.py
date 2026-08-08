import sqlite3

conn = sqlite3.connect('database.db')
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE users ADD COLUMN address TEXT")
except:
    print("address column already exists")

try:
    cur.execute("ALTER TABLE users ADD COLUMN phone TEXT")
except:
    print("phone column already exists")

conn.commit()
conn.close()

print("Users table updated successfully!")