import sqlite3

conn = sqlite3.connect("tasks.db")
cursor = conn.cursor()

with open("schema_tasks.sql") as f:
    cursor.executescript(f.read())

conn.commit()
conn.close()

print("Base tasks.db créée")
