import sqlite3

conn = sqlite3.connect("backend/database/buildsensei.db")
cursor = conn.cursor()

cursor.execute("SELECT name, price FROM cpu LIMIT 5")
print(cursor.fetchall())

conn.close()
