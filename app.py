# app.py
import streamlit as st
import pandas as pd
from datetime import date, time, datetime

st.set_page_config(
    page_title="Care Home Incident Management",
    page_icon="🧾",
    layout="wide",
)

# ---------------------------
# State
# ---------------------------
if "incidents" not in st.session_state:
    st.session_state.incidents = []

# ---------------------------
# Utilities
# ---------------------------
def generate_incident_id() -> str:
    return datetime.now().strftime("CSI-%Y%m%d-%H%M%S")  # Clinical / Safety Incident ID

def incidents_df() -> pd.DataFrame:
    if not st.session_state.incidents:
        return pd.DataFrame()
    return pd.DataFrame(st.session_state.incidents)

def require_text(value: str) -> bool:
    return bool(value and value.strip())

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

            st.session_state.incidents.append(record)
            st.success("Clinical / safety incident submitted. Management review and sign-off can now be completed.")

            with st.expander("View submitted incident (for verification)"):
                st.json(record)

# ============================================================
# Page: Inspection evidence & audit integrity
# ============================================================
elif page == "Inspection evidence & audit integrity":
    st.title("🧾 Inspection evidence & audit integrity")

    df = incidents_df()

    if df.empty:
        st.info("No clinical / safety incidents have been submitted.")
    else:
        # Keep language: avoid "logs", use "inspection evidence"
        st.markdown(
            "This section supports **inspection evidence**, **audit integrity**, and **management review and sign-off**. "
            "Use the filters below to find incidents requiring review."
        )

        # Filters
        f1, f2, f3 = st.columns([1, 1, 2])
        with f1:
            status_filter = st.selectbox(
                "Management review status",
                ["All", "Pending", "Completed"],
                index=0,
            )
        with f2:
            severity_filter = st.selectbox(
                "Severity",
                ["All", "Low", "Moderate", "High", "Critical"],
                index=0,
            )
        with f3:
            search_text = st.text_input("Search (resident, location, category, ID)")

        view_df = df.copy()

        if status_filter != "All" and "Management review status" in view_df.columns:
            view_df = view_df[view_df["Management review status"] == status_filter]

        if severity_filter != "All" and "Severity" in view_df.columns:
            view_df = view_df[view_df["Severity"] == severity_filter]

        if search_text.strip():
            q = search_text.strip().lower()
            cols_to_search = [
                "Incident ID",
                "Resident identifier",
                "Location",
                "Category",
            ]
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

        # Pick an incident to review
        incident_ids = view_df["Incident ID"].tolist() if "Incident ID" in view_df.columns else []
        if not incident_ids:
            st.info("No incidents match the current filters.")
        else:
            selected_id = st.selectbox("Select incident for management review", incident_ids)

            # Find in session list
            idx = next(
                (i for i, rec in enumerate(st.session_state.incidents) if rec.get("Incident ID") == selected_id),
                None,
            )

            if idx is None:
                st.error("Selected incident could not be found.")
            else:
                current = st.session_state.incidents[idx]

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
                        st.session_state.incidents[idx]["Management reviewer (name)"] = reviewer_name.strip()
                        st.session_state.incidents[idx]["Management reviewer (role)"] = reviewer_role.strip()
                        st.session_state.incidents[idx]["Management review outcome"] = review_outcome.strip()
                        st.session_state.incidents[idx]["Sign-off decision"] = signoff_decision
                        st.session_state.incidents[idx]["Sign-off timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state.incidents[idx]["Management review status"] = "Completed" if evidence_ready else "Completed"

                        st.success("Management review and sign-off completed.")

        st.markdown("---")
        st.subheader("Export for inspection evidence")
        export_df = incidents_df()
        csv = export_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download incident dataset (CSV)",
            data=csv,
            file_name=f"clinical_safety_incidents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )
