import sqlite3
import bcrypt
from datetime import datetime

DB_PATH = "incident_system.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=== Care Home Onboarding ===")

home_name = input("Care home name: ").strip()
manager_username = input("Manager username: ").strip()
manager_password = input("Manager password: ").strip()

if not home_name or not manager_username or not manager_password:
    raise SystemExit("All fields are required.")

# Ensure care_homes table exists
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS care_homes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """
)

# Ensure users table has care_home_id
cursor.execute("PRAGMA table_info(users)")
columns = [row[1] for row in cursor.fetchall()]
if "care_home_id" not in columns:
    cursor.execute("ALTER TABLE users ADD COLUMN care_home_id INTEGER")

# Create care home
cursor.execute(
    "INSERT INTO care_homes (name, created_at) VALUES (?, ?)",
    (home_name, datetime.utcnow().isoformat())
)
care_home_id = cursor.lastrowid

# Hash password
password_hash = bcrypt.hashpw(
    manager_password.encode("utf-8"),
    bcrypt.gensalt()
)

# Create manager user linked to care home
cursor.execute(
    """
    INSERT INTO users (username, password_hash, role, care_home_id, created_at)
    VALUES (?, ?, 'manager', ?, ?)
    """,
    (manager_username, password_hash, care_home_id, datetime.utcnow().isoformat())
)

conn.commit()
conn.close()

print("\n✅ Care home created successfully")
print(f"Care home ID: {care_home_id}")
print(f"Manager username: {manager_username}")
