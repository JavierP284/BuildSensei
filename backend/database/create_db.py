import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "buildsensei.db")

SQL_PATH = os.path.join(BASE_DIR, "scripts_sql", "create_tables.sql")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

with open(SQL_PATH, "r", encoding="utf-8") as f:
    sql_script = f.read()

cursor.executescript(sql_script)
conn.commit()
conn.close()

print("✔ Database created and tables initialized.")
