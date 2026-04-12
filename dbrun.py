import os
from sqlite3 import connect

# Same file as Flask uses: p1_heartdiseaseprediction/mohithheart.db next to app.py
_ROOT = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(_ROOT, "p1_heartdiseaseprediction", "mohithheart.db")

with connect(db_path) as con:

    # ---------------- USER TABLE ----------------
    con.execute("""
        CREATE TABLE IF NOT EXISTS user (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            email    TEXT NOT NULL
        )
    """)

    # ---------------- HISTORY TABLE ----------------
    con.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,

            age REAL,
            cp INTEGER,
            bp REAL,
            chol REAL,
            maxhr REAL,
            std REAL,
            fluro REAL,
            th REAL,

            prediction INTEGER,
            probability REAL,

            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    con.commit()

    # ---------------- VERIFY ----------------
    cursor = con.cursor()

    print("\n--- USERS ---")
    cursor.execute("SELECT * FROM user")
    for row in cursor.fetchall():
        print(row)

    print("\n--- HISTORY ---")
    cursor.execute("SELECT * FROM history")
    for row in cursor.fetchall():
        print(row)

print("\nDatabase setup complete.")
print(f"Database file: {db_path}")
