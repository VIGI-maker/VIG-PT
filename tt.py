import streamlit as st
import pandas as pd

st.set_page_config(page_title="VIGIOR AI", layout="wide")

st.title("🦴 VIGIOR AI")
st.subheader("Simple working version (test deployment)")

menu = st.sidebar.selectbox("Menu", ["New Patient", "Database"])

# -------------------------
# SESSION STORAGE (no DB)
# -------------------------
if "patients" not in st.session_state:
    st.session_state.patients = []

# -------------------------
# NEW PATIENT
# -------------------------
if menu == "New Patient":

    st.header("➕ New Patient")

    patient_number = st.text_input("Patient Number")
    age = st.number_input("Age", 18, 100, 40)

    schatzker = st.selectbox("Schatzker", ["I", "II", "III", "IV", "V", "VI"])
    soft_tissue = st.selectbox("Soft Tissue", ["Mild", "Moderate", "Severe"])

    if st.button("Predict"):

        # simple risk model
        risk = age / 2

        if schatzker in ["V", "VI"]:
            risk += 20

        if soft_tissue == "Moderate":
            risk += 10
        elif soft_tissue == "Severe":
            risk += 25

        risk = min(risk, 95)

        st.metric("Estimated Risk (%)", f"{risk:.1f}%")

        if risk > 70:
            st.warning("External Fixation + Delayed ORIF")
        elif risk > 50:
            st.info("MIPO recommended")
        else:
            st.success("Early ORIF possible")

        st.session_state.patients.append({
            "patient": patient_number,
            "age": age,
            "schatzker": schatzker,
            "soft_tissue": soft_tissue,
            "risk": risk
        })

# -------------------------
# DATABASE
# -------------------------
if menu == "Database":

    st.header("📊 Patients")

    df = pd.DataFrame(st.session_state.patients)

    st.dataframe(df)

    if len(df) > 0:
        st.bar_chart(df["schatzker"].value_counts())
