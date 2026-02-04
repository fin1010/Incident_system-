# app.py
import streamlit as st
import pandas as pd
from datetime import date, time, datetime

# IMPORTANT:
# Your database.py must expose BOTH:
#   - get_connection()
#   - init_db()
# and init_db() must CREATE the incidents table (schema below assumes Postgres).
from database import get_connection, init_db

# =================================================
# DB: create tables on app start
# =================================================
init_db()

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="Care Home Incident Management",
    page_icon="🧾",
    layout="wide",
)

# ---------------------------
# Utilities
# ---------------------------
def generate_incident_id() -> str:
    return datetime.now().strftime("CSI-%Y%m%d-%H%M%S")  # Clinical / Safety Incident ID

def require_text(value: str) -> bool:
    return bool(value and str(value).strip())

def insert_incident_to_db(record: dict) -> None:
    """Postgres INSERT."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO incidents (
            incident_id,
            incident_date,
            incident_time,
            category,
            location,
            resident_identifier,
            resident_dob,
            resident_room,
            incident_account,
            immediate_actions_taken,
            harm_injury_sustained,
            harm_injury_details,
            individuals_services_informed,
            severity,
            reported_by_name,
            reported_by_role,
            immediate_learning_actions,
            audit_integrity_confirmation,
            submitted_timestamp,
            management_review_status,
            management_reviewer_name,
            management_reviewer_role,
            management_review_outcome,
            signoff_decision,
            signoff_timestamp
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
        """,
        (
            record["Incident ID"],
            record["Incident date"],
            record["Incident time"],
            record["Category"],
            record["Location"],
            record["Resident identifier"],
            record["Date of birth"],
            record["Room"],
            record["Incident account"],
            record["Immediate actions taken"],
            record["Harm / injury sustained"],
            record["Harm / injury details"],
            record["Individuals / services informed"],
            record["Severity"],
            record["Reported by (name)"],
            record["Reported by (role)"],
            record["Immediate learning / actions"],
            record["Audit integrity confirmation"],
            record["Submitted timestamp"],
            record["Management review status"],
            record["Management reviewer (name)"],
            record["Management reviewer (role)"],
            record["Management review outcome"],
            record["Sign-off decision"],
            record["Sign-off timestamp"],
        ),
    )
    conn.commit()
    cur.close()

def fetch_incidents_df() -> pd.DataFrame:
    """Load incidents from Postgres into a DataFrame."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            incident_id AS "Incident ID",
            incident_date AS "Incident date",
            incident_time AS "Incident time",
            category AS "Category",
            location AS "Location",
            resident_identifier AS "Resident identifier",
            resident_dob AS "Date of birth",
            resident_room AS "Room",
            incident_account AS "Incident account",
            immediate_actions_taken AS "Immediate actions taken",
            harm_injury_sustained AS "Harm / injury sustained",
            harm_injury_details AS "Harm / injury details",
            individuals_services_informed AS "Individuals / services informed",
            severity AS "Severity",
            reported_by_name AS "Reported by (name)",
            reported_by_role AS "Reported by (role)",
            immediate_learning_actions AS "Immediate learning / actions",
            audit_integrity_confirmation AS "Audit integrity confirmation",
            submitted_timestamp AS "Submitted timestamp",
            management_review_status AS "Management review status",
            management_reviewer_name AS "Management reviewer (name)",
            management_reviewer_role AS "Management reviewer (role)",
            management_review_outcome AS "Management review outcome",
            signoff_decision AS "Sign-off decision",
            signoff_timestamp AS "Sign-off timestamp"
        FROM incidents
        ORDER BY submitted_timestamp DESC
        """
    )
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    cur.close()

    if not rows:
        return pd.DataFrame(columns=cols)

    df = pd.DataFrame(rows, columns=cols)
    return df

def update_management_review(
    incident_id: str,
    reviewer_name: str,
    reviewer_role: str,
    review_outcome: str,
    signoff_decision: str,
    signoff_timestamp: str,
    management_review_status: str,
) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE incidents
        SET
            management_reviewer_name = %s,
            management_reviewer_role = %s,
            management_review_outcome = %s,
            signoff_decision = %s,
            signoff_timestamp = %s,
            management_review_status = %s
        WHERE incident_id = %s
        """,
        (
            reviewer_name,
            reviewer_role,
            review_outcome,
            signoff_decision,
            signoff_timestamp,
            management_review_status,
            incident_id,
        ),
    )
    conn.commit()
    cur.close()

def get_incident_record(incident_id: str) -> dict | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            incident_id,
            incident_date,
            incident_time,
            category,
            location,
            resident_identifier,
            resident_dob,
            resident_room,
            incident_account,
            immediate_actions_taken,
            harm_injury_sustained,
            harm_injury_details,
            individuals_services_informed,
            severity,
            reported_by_name,
            reported_by_role,
            immediate_learning_actions,
            audit_integrity_confirmation,
            submitted_timestamp,
            management_review_status,
            management_reviewer_name,
            management_reviewer_role,
            management_review_outcome,
            signoff_decision,
            signoff_timestamp
        FROM incidents
        WHERE incident_id = %s
        """,
        (incident_id,),
    )
    row = cur.fetchone()
    cur.close()

    if not row:
        return None

    keys = [
        "Incident ID",
        "Incident date",
        "Incident time",
        "Category",
        "Location",
        "Resident identifier",
        "Date of birth",
        "Room",
        "Incident account",
        "Immediate actions taken",
        "Harm / injury sustained",
        "Harm / injury details",
        "Individuals / services informed",
        "Severity",
        "Reported by (name)",
        "Reported by (role)",
        "Immediate learning / actions",
        "Audit integrity confirmation",
        "Submitted timestamp",
        "Management review status",
        "Management reviewer (name)",
        "Management reviewer (role)",
        "Management review outcome",
        "Sign-off decision",
        "Sign-off timestamp",
    ]
    return dict(zip(keys, row))

# ---------------------------
# Sidebar navigation
# ---------------------------
st.sidebar.title("Care Home System")
page = st.sidebar.radio(
    "Navigation",
    ["Report a clinical / safety incident", "Inspection evidence & audit integrity"],
)

# ============================================================
# Page: Report a clinical / safety incident
# ============================================================
if page == "Report a clinical / safety incident":
    st.title("🧾 Clinical / Safety Incident Reporting")

    st.markdown(
        "Use this form to report a **clinical / safety incident** in a clear, factual manner. "
        "The aim is **resident safety**, **audit integrity**, and appropriate **management review and sign-off**."
    )

    with st.form("incident_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            incident_date = st.date_input("Date of incident", value=date.today())
        with c2:
            incident_time = st.time_input("Time of incident", value=time(12, 0))
        with c3:
            incident_category = st.selectbox(
                "Incident category",
                [
                    "Fall",
                    "Medication incident",
                    "Safeguarding concern",
                    "Aggression / violence",
                    "Pressure injury",
                    "Infection prevention / control",
                    "Equipment / environment safety",
                    "Other",
                ],
            )

        location = st.text_input("Location (e.g. Room 12, Lounge)")

        st.markdown("### Resident details")
        r1, r2, r3 = st.columns([2, 1, 1])
        with r1:
            resident_identifier = st.text_input("Resident name / identifier")
        with r2:
            resident_dob = st.date_input("Date of birth")
        with r3:
            resident_room = st.text_input("Room number (if applicable)")

        st.markdown("### Incident account (factual)")
        incident_account = st.text_area(
            "What happened?",
            height=160,
            placeholder="Provide a clear, factual account of events in chronological order.",
        )

        immediate_actions = st.text_area(
            "Immediate actions taken",
            height=120,
            placeholder="First aid, observations, escalation, medical review requested, environment made safe, etc.",
        )

        st.markdown("### Harm / injury")
        harm_occurred = st.radio("Was harm or injury sustained?", ["No", "Yes"], horizontal=True)
        if harm_occurred == "Yes":
            harm_details = st.text_area(
                "Harm / injury details and care provided",
                height=110,
                placeholder="Describe injuries, observations, treatment, and any onward referral.",
            )
        else:
            harm_details = "No harm or injury sustained"

        st.markdown("### Escalation and notifications")
        informed = st.multiselect(
            "Individuals / services informed",
            [
                "Nurse in charge",
                "Registered manager",
                "GP",
                "Family / next of kin",
                "Safeguarding team",
                "Emergency services",
                "Other professional (specify in free text)",
            ],
        )

        severity = st.selectbox("Severity classification", ["Low", "Moderate", "High", "Critical"])

        st.markdown("---")
        st.subheader("✍️ Incident reported by")
        reported_by_name = st.text_input("Name", placeholder="Full name")
        reported_by_role = st.text_input("Role", placeholder="Job title / role")

        st.markdown("### Immediate learning / actions to reduce recurrence (optional)")
        learning_actions = st.text_area(
            "Learning / actions",
            height=100,
            placeholder="If known: contributing factors, immediate learning, and practical actions taken.",
        )

        st.markdown("---")
        st.subheader("🧾 Audit integrity confirmation")
        audit_statement = st.checkbox(
            "I confirm this incident account is accurate to the best of my knowledge and recorded in good faith.",
            value=False,
        )

        submitted = st.form_submit_button("Submit clinical / safety incident")

    if submitted:
        errors = []
        if not require_text(resident_identifier):
            errors.append("Resident name / identifier is required.")
        if not require_text(location):
            errors.append("Location is required.")
        if not require_text(incident_account):
            errors.append("A factual incident account is required.")
        if not require_text(reported_by_name):
            errors.append("Reporter name is required.")
        if not require_text(reported_by_role):
            errors.append("Reporter role is required.")
        if not audit_statement:
            errors.append("Audit integrity confirmation must be completed before submission.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            record = {
                "Incident ID": generate_incident_id(),
                "Incident date": str(incident_date),
                "Incident time": str(incident_time),
                "Category": incident_category,
                "Location": location.strip(),
                "Resident identifier": resident_identifier.strip(),
                "Date of birth": str(resident_dob),
                "Room": resident_room.strip(),
                "Incident account": incident_account.strip(),
                "Immediate actions taken": immediate_actions.strip(),
                "Harm / injury sustained": harm_occurred,
                "Harm / injury details": harm_details.strip() if isinstance(harm_details, str) else str(harm_details),
                "Individuals / services informed": ", ".join(informed),
                "Severity": severity,
                "Reported by (name)": reported_by_name.strip(),
                "Reported by (role)": reported_by_role.strip(),
                "Immediate learning / actions": learning_actions.strip(),
                "Audit integrity confirmation": "Confirmed",
                "Submitted timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                # Management fields start blank until sign-off:
                "Management review status": "Pending",
                "Management reviewer (name)": "",
                "Management reviewer (role)": "",
                "Management review outcome": "",
                "Sign-off decision": "",
                "Sign-off timestamp": "",
            }

            # ✅ SAVE TO POSTGRES (INSERT)
            insert_incident_to_db(record)

            st.success("Clinical / safety incident submitted. Management review and sign-off can now be completed.")
            with st.expander("View submitted incident (for verification)"):
                st.json(record)

# ============================================================
# Page: Inspection evidence & audit integrity
# ============================================================
elif page == "Inspection evidence & audit integrity":
    st.title("🧾 Inspection evidence & audit integrity")

    df = fetch_incidents_df()

    if df.empty:
        st.info("No clinical / safety incidents have been submitted.")
    else:
        st.markdown(
            "This section supports **inspection evidence**, **audit integrity**, and **management review and sign-off**. "
            "Use the filters below to find incidents requiring review."
        )

        # Filters
        f1, f2, f3 = st.columns([1, 1, 2])
        with f1:
            status_filter = st.selectbox("Management review status", ["All", "Pending", "Completed"], index=0)
        with f2:
            severity_filter = st.selectbox("Severity", ["All", "Low", "Moderate", "High", "Critical"], index=0)
        with f3:
            search_text = st.text_input("Search (resident, location, category, ID)")

        view_df = df.copy()

        if status_filter != "All" and "Management review status" in view_df.columns:
            view_df = view_df[view_df["Management review status"] == status_filter]

        if severity_filter != "All" and "Severity" in view_df.columns:
            view_df = view_df[view_df["Severity"] == severity_filter]

        if search_text.strip():
            q = search_text.strip().lower()
            cols_to_search = ["Incident ID", "Resident identifier", "Location", "Category"]
            existing_cols = [c for c in cols_to_search if c in view_df.columns]
            if existing_cols:
                mask = False
                for c in existing_cols:
                    mask = mask | view_df[c].astype(str).str.lower().str.contains(q, na=False)
                view_df = view_df[mask]

        st.markdown("### Clinical / safety incidents")
        st.dataframe(view_df, use_container_width=True)

        st.markdown("---")
        st.subheader("✅ Management review and sign-off")

        incident_ids = view_df["Incident ID"].tolist() if "Incident ID" in view_df.columns else []
        if not incident_ids:
            st.info("No incidents match the current filters.")
        else:
            selected_id = st.selectbox("Select incident for management review", incident_ids)

            current = get_incident_record(selected_id)
            if not current:
                st.error("Selected incident could not be found.")
            else:
                with st.expander("View incident details"):
                    st.json(current)

                with st.form("management_review_form"):
                    mr1, mr2 = st.columns(2)
                    with mr1:
                        reviewer_name = st.text_input("Reviewer name", value=current.get("Management reviewer (name)", ""))
                    with mr2:
                        reviewer_role = st.text_input("Reviewer role", value=current.get("Management reviewer (role)", ""))

                    review_outcome = st.text_area(
                        "Management review outcome",
                        value=current.get("Management review outcome", ""),
                        height=120,
                        placeholder="Summary of review, findings, contributing factors, and required actions.",
                    )

                    signoff_decision = st.selectbox(
                        "Sign-off decision",
                        ["", "Accepted", "Further action required", "Re-opened for clarification"],
                        index=0,
                    )

                    evidence_ready = st.checkbox(
                        "Mark as suitable for inspection evidence (complete, reviewed, and signed off where appropriate).",
                        value=False,
                    )

                    complete_review = st.form_submit_button("Complete management review and sign-off")

                if complete_review:
                    review_errors = []
                    if not require_text(reviewer_name):
                        review_errors.append("Reviewer name is required.")
                    if not require_text(reviewer_role):
                        review_errors.append("Reviewer role is required.")
                    if not require_text(review_outcome):
                        review_errors.append("Management review outcome is required.")
                    if not require_text(signoff_decision):
                        review_errors.append("A sign-off decision is required.")

                    if review_errors:
                        for e in review_errors:
                            st.error(e)
                    else:
                        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        status = "Completed"  # evidence_ready currently just a checkbox, status remains Completed either way

                        # ✅ UPDATE IN POSTGRES
                        update_management_review(
                            incident_id=selected_id,
                            reviewer_name=reviewer_name.strip(),
                            reviewer_role=reviewer_role.strip(),
                            review_outcome=review_outcome.strip(),
                            signoff_decision=signoff_decision,
                            signoff_timestamp=ts,
                            management_review_status=status,
                        )

                        st.success("Management review and sign-off completed.")
                        st.rerun()

        st.markdown("---")
        st.subheader("Export for inspection evidence")

        export_df = fetch_incidents_df()
        csv = export_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download incident dataset (CSV)",
            data=csv,
            file_name=f"clinical_safety_incidents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

