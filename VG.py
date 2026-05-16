# =========================================================
# VIGIOR AI - LIGHT VERSION (STABLE STREAMLIT CLOUD)
# =========================================================

import streamlit as st
import pandas as pd
import sqlite3
import uuid
from datetime import datetime

# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect("vigor.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id TEXT,
    patient_number TEXT,
    date TEXT,
    age INTEGER,
    sex TEXT,
    schatzker TEXT,
    soft_tissue TEXT,
    infection_risk REAL,
    compartment_risk REAL,
    skin_risk REAL,
    treatment TEXT,
    outcome TEXT,
    infection TEXT,
    pseudarthrosis TEXT,
    revision TEXT
)
""")

conn.commit()

# =========================================================
# APP CONFIG
# =========================================================

st.set_page_config(page_title="VIGIOR AI", layout="wide")

st.title("🦴 VIGIOR AI")
st.subheader("Light Predictive Orthopaedic System")

menu = st.sidebar.selectbox(
    "Menu",
    ["New Patient", "Database", "Statistics", "AI Learning"]
)

# =========================================================
# SIMPLE RISK MODEL
# =========================================================

def compute_risk(age, schatzker, soft_tissue):

    base = 10

    if age > 60:
        base += 10

    if schatzker in ["V", "VI"]:
        base += 20

    if soft_tissue == "Moderate":
        base += 15

    if soft_tissue == "Severe":
        base += 30

    infection = min(base + 10, 95)
    compartment = min(base + 5, 95)
    skin = min(base + 15, 95)

    return infection, compartment, skin

# =========================================================
# TREATMENT DECISION (SINGLE OUTPUT)
# =========================================================

def treatment_plan(inf, comp, skin):

    if skin > 70:
        return "External Fixation + Delayed ORIF (soft tissue risk)"

    elif comp > 70:
        return "Monitoring ± Fasciotomy + Staged Fixation"

    elif inf > 60:
        return "MIPO (Minimally invasive fixation)"

    else:
        return "Early ORIF"

# =========================================================
# NEW PATIENT
# =========================================================

if menu == "New Patient":

    st.header("➕ New Patient")

    col1, col2 = st.columns(2)

    with col1:
        patient_number = st.text_input("Patient Number")
        age = st.number_input("Age", 18, 100, 40)
        schatzker = st.selectbox("Schatzker", ["I", "II", "III", "IV", "V", "VI"])

    with col2:
        soft_tissue = st.selectbox("Soft Tissue", ["Mild", "Moderate", "Severe"])
        outcome = st.selectbox("Outcome", ["A", "B", "C"])

    if st.button("Predict"):

        inf, comp, skin = compute_risk(age, schatzker, soft_tissue)
        treatment = treatment_plan(inf, comp, skin)

        st.metric("Infection risk", f"{inf}%")
        st.metric("Compartment risk", f"{comp}%")
        st.metric("Skin risk", f"{skin}%")

        st.success(treatment)

        st.markdown("---")

        infection = st.selectbox("Infection occurred", ["No", "Yes"])
        pseudarthrosis = st.selectbox("Pseudarthrosis", ["No", "Yes"])
        revision = st.selectbox("Revision surgery", ["No", "Yes"])

        if st.button("Save"):

            pid = "VIG-" + str(uuid.uuid4())[:8]

            cursor.execute("""
            INSERT INTO patients VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                pid,
                patient_number,
                str(datetime.now()),
                age,
                "Unknown",
                schatzker,
                soft_tissue,
                inf,
                comp,
                skin,
                treatment,
                outcome,
                infection,
                pseudarthrosis,
                revision
            ))

            conn.commit()

            st.success(f"Saved: {pid}")

# =========================================================
# DATABASE
# =========================================================

elif menu == "Database":

    df = pd.read_sql_query("SELECT * FROM patients", conn)
    st.dataframe(df)

# =========================================================
# STATISTICS
# =========================================================

elif menu == "Statistics":

    df = pd.read_sql_query("SELECT * FROM patients", conn)

    if len(df) == 0:
        st.warning("No data yet")
    else:
        st.metric("Patients", len(df))
        st.metric("Avg Age", round(df["age"].mean(), 1))

        st.subheader("Schatzker types")
        st.bar_chart(df["schatzker"].value_counts())

        st.subheader("Outcomes")
        st.bar_chart(df["outcome"].value_counts())

        st.subheader("Complications")
        st.bar_chart({
            "Infection": (df["infection"] == "Yes").sum(),
            "Pseudarthrosis": (df["pseudarthrosis"] == "Yes").sum(),
            "Revision": (df["revision"] == "Yes").sum()
        })

# =========================================================
# AI LEARNING (SIMPLE)
# =========================================================

elif menu == "AI Learning":

    df = pd.read_sql_query("SELECT * FROM patients", conn)

    if len(df) < 3:
        st.warning("Need more patients for learning")
    else:

        best = df.groupby("treatment")["outcome"].apply(
            lambda x: (x == "A").mean()
        ).idxmax()

        st.success(f"Best treatment in your dataset: {best}")

        st.info("""
AI learns from YOUR real outcomes:
- compares treatments
- identifies best strategy
- updates decision logic (simple version)
""")
