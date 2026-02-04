import streamlit as st
import psycopg2

@st.cache_resource
def get_connection():
    return psycopg2.connect(
        st.secrets["DATABASE_URL"],
        sslmode="require"
    )

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id SERIAL PRIMARY KEY,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            care_home_id INTEGER NOT NULL,
            incident_type TEXT,
            description TEXT,
            completed_by_name TEXT,
            completed_by_role TEXT
        );
    """)
    conn.commit()
    cur.close()

