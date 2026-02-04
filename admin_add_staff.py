import sqlite3
import bcrypt
from datetime import datetime

DB_PATH = "incident_system.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=== Add Staff User ===")

care_home_id = input("Care home ID to attach staff to: ").strip()
username = input("Staff username: ").strip()
password = input("Staff password: ").strip()

if not care_home_id.isdigit():
    raise SystemExit("Care home ID must be a number.")
if not username or not password:
    raise SystemExit("Username and password are required.")

# Ensure users table has care_home_id
cursor.execute("PRAGMA table_info(users)")
columns = [row[1] for row in cursor.fetchall()]
if "care_home_id" not in columns:
    cursor.execute("ALTER TABLE users ADD COLUMN care_home_id INTEGER")

password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

try:
    cursor.execute(
        """
        INSERT INTO users (username, password_hash, role, care_home_id, created_at)
        VALUES (?, ?, 'staff', ?, ?)
        """,
        (username, password_hash, int(care_home_id), datetime.utcnow().isoformat()),
    )
    conn.commit()
    print("\n✅ Staff user added successfully")
    print("Username:", username)
    print("Care home ID:", care_home_id)
except sqlite3.IntegrityError:
    print("\n❌ Username already exists. Choose a different username.")
finally:
    conn.close()
