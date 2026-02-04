import streamlit as st
import psycopg2


@st.cache_resource
def get_connection():
    conn = psycopg2.connect(st.secrets["DATABASE_URL"])
    conn.autocommit = True  # IMPORTANT: prevents failed-transaction lock
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Users table
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

    # Incidents table (unchanged)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            incident_id TEXT PRIMARY KEY,
            incident_date TEXT,
            incident_time TEXT,
            category TEXT,
            location TEXT,
            resident_identifier TEXT,
            resident_dob TEXT,
            resident_room TEXT,
            incident_account TEXT,
            immediate_actions_taken TEXT,
            harm_injury_sustained TEXT,
            harm_injury_details TEXT,
            individuals_services_informed TEXT,
            severity TEXT,
            reported_by_name TEXT,
            reported_by_role TEXT,
            immediate_learning_actions TEXT,
            audit_integrity_confirmation TEXT,
            submitted_timestamp TEXT,
            management_review_status TEXT,
            management_reviewer_name TEXT,
            management_reviewer_role TEXT,
            management_review_outcome TEXT,
            signoff_decision TEXT,
            signoff_timestamp TEXT
        );
    """)

    conn.commit()
    cur.close()

