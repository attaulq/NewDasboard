import sqlite3

conn = sqlite3.connect("database.db")

with open("schema_sqlite.sql", "r") as f:
    conn.executescript(f.read())

conn.close()

print("✅ database.db berhasil dibuat!")