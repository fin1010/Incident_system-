import streamlit as st
import psycopg2


# =================================================
# DATABASE CONNECTION
# =================================================
@st.cache_resource
def get_connection():
    """
    Returns a cached Postgres connection using Streamlit secrets.
    Autocommit is enabled to avoid failed-transaction issues.
    """
    conn = psycopg2.connect(st.secrets["DATABASE_URL"])
    conn.autocommit = True
    return conn


# =================================================
# INITIALISE DATABASE SCHEMA
# =================================================
def init_db():
    """
    Creates required tables and columns if they do not already exist.
    Safe to run on every app start.
    """
    conn = get_connection()
    cur = conn.cursor()

    # -----------------------------
    # USERS TABLE (AUTHENTICATION)
    # -----------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            care_home_id INTEGER NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('staff', 'manager')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # -----------------------------
    # INCIDENTS TABLE (CORE DATA)
    # -----------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id SERIAL PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            care_home_id INTEGER NOT NULL,
            incident_type TEXT,
            description TEXT,
            completed_by_name TEXT,
            completed_by_role TEXT
        );
    """)

    # -----------------------------
    # MANAGEMENT REVIEW FIELDS
    # (added safely via ALTER)
    # -----------------------------
    cur.execute("""
        ALTER TABLE incidents
        ADD COLUMN IF NOT EXISTS reviewed_by TEXT;
    """)

    cur.execute("""
        ALTER TABLE incidents
        ADD COLUMN IF NOT EXISTS review_outcome TEXT;
    """)

    cur.execute("""
        ALTER TABLE incidents
        ADD COLUMN IF NOT EXISTS signoff_decision TEXT;
    """)

    cur.execute("""
        ALTER TABLE incidents
        ADD COLUMN IF NOT EXISTS signed_off_at TIMESTAMP;
    """)

    cur.execute("""
        ALTER TABLE incidents
        ADD COLUMN IF NOT EXISTS locked BOOLEAN DEFAULT FALSE;
    """)

    cur.close()

