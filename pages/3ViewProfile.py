import streamlit as st
import requests

# Set up the Streamlit page
st.set_page_config(page_title="User Information", page_icon="🔍", layout="wide")

st.title("🔍 User Information Dashboard")
st.subheader("Select a section to view details:")

# Ensure the user is logged in and has a valid user_id in session state
if "user_id" not in st.session_state:
    st.warning("🔒 Please log in first.")
else:
    user_id = st.session_state.user_id

    # Buttons to toggle between Doctor and Patient info
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🩺 View Doctor Information"):
            st.session_state.view_section = "doctor"

    with col2:
        if st.button("🏥 View Patient Information"):
            st.session_state.view_section = "patient"

    st.markdown("---")

    # Display Doctor Information
    if st.session_state.get("view_section") == "doctor":
        st.subheader("🩺 Doctor Information")
        response = requests.get(f"http://localhost:8000/doctor/details/{user_id}")

        if response.status_code == 200:
            data = response.json()
            user_info = data.get("user", {})
            doctor_info = data.get("doctor", {})

            st.subheader("👤 User Information")
            st.write(f"**Username:** {user_info.get('username', 'N/A')}")
            st.write(f"**Name:** {user_info.get('firstName', 'N/A')} {user_info.get('lastName', 'N/A')}")
            st.write(f"**Gender:** {user_info.get('gender', 'N/A')}")
            st.write(f"**Date of Birth:** {user_info.get('dateOfBirth', 'N/A')}")
            st.write(f"**Email:** {user_info.get('email', 'N/A')}")
            st.write(f"**Contact:** {user_info.get('contact', 'N/A')}")

            if doctor_info:
                st.subheader("🩺 Doctor Details")
                st.write(f"**Specialization:** {doctor_info.get('specialization', 'N/A')}")
                st.write(f"**Research Areas:** {', '.join(doctor_info.get('research_area', []))}")

                address = doctor_info.get("address", {})
                st.subheader("📍 Address")
                st.write(f"**Street:** {address.get('street', 'N/A')}")
                st.write(f"**City:** {address.get('city', 'N/A')}")
                st.write(f"**State:** {address.get('state', 'N/A')}")
                st.write(f"**Country:** {address.get('country', 'N/A')}")
                st.write(f"**Postal Code:** {address.get('postal_code', 'N/A')}")
            else:
                st.warning("⚠️ No doctor information found for this user.")
        else:
            st.warning("⚠️ No doctor information found for this user.")

    # Display Patient Information
    elif st.session_state.get("view_section") == "patient":
        st.subheader("🏥 Patient Information")
        response = requests.get(f"http://localhost:8000/patient/details/{user_id}")

        if response.status_code == 200:
            data = response.json()
            user_info = data.get("user", {})
            patient_info = data.get("patient", {})

            st.subheader("👤 User Information")
            st.write(f"**Username:** {user_info.get('username', 'N/A')}")
            st.write(f"**Name:** {user_info.get('firstName', 'N/A')} {user_info.get('lastName', 'N/A')}")
            st.write(f"**Gender:** {user_info.get('gender', 'N/A')}")
            st.write(f"**Date of Birth:** {user_info.get('dateOfBirth', 'N/A')}")
            st.write(f"**Email:** {user_info.get('email', 'N/A')}")
            st.write(f"**Contact:** {user_info.get('contact', 'N/A')}")

            if patient_info:
                st.subheader("🏥 Medical Details")
                st.write(f"**Medical History:** {', '.join(patient_info.get('medical_history', []))}")
                st.write(f"**Symptoms:** {', '.join(patient_info.get('symptoms', []))}")
                st.write(f"**Status:** {patient_info.get('status', 'N/A')}")
                st.write(f"**Drug History:** {', '.join(patient_info.get('drug_history', []))}")

                address = patient_info.get("address", {})
                st.subheader("📍 Address")
                st.write(f"**Street:** {address.get('street', 'N/A')}")
                st.write(f"**City:** {address.get('city', 'N/A')}")
                st.write(f"**State:** {address.get('state', 'N/A')}")
                st.write(f"**Country:** {address.get('country', 'N/A')}")
                st.write(f"**Postal Code:** {address.get('postal_code', 'N/A')}")
            else:
                st.warning("⚠️ No patient information found for this user.")
        else:
            st.warning("⚠️ No doctor information found for this user.")
            