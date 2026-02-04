import sqlite3

# Connect to database
conn = sqlite3.connect("incidents.db", check_same_thread=False)
cursor = conn.cursor()

# Care homes table
cursor.execute("""
CREATE TABLE IF NOT EXISTS care_homes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)
""")

# Users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    care_home_id INTEGER,
    username TEXT UNIQUE,
    password_hash TEXT,
    role TEXT
)
""")

# Incidents table
cursor.execute("""
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    care_home_id INTEGER,
    incident_datetime TEXT,
    category TEXT,
    location TEXT,
    description TEXT,
    action_taken TEXT,
    medical_advice TEXT,
    family_informed TEXT,
    outcome TEXT,
    reviewed INTEGER DEFAULT 0
)
""")

conn.commit()
