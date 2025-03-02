import streamlit as st
import requests
from pydantic import BaseModel
from typing import List, Dict

# Define the Patient class with the correct address structure
class Patient(BaseModel):
    user_id: str  # Foreign key to User
    medical_history: List[str]
    symptoms: List[str]
    address: Dict[str, str]  # Ensure proper dictionary format
    status: str
    drug_history: List[str]

# Set up the Streamlit page
st.set_page_config(page_title="Add Patient Information", page_icon="🏥", layout="wide")

st.title("🏥 Add Patient Information")
st.subheader("Please fill out the details below:")

# Ensure the user is logged in and has a valid user_id in session state
if "user_id" not in st.session_state:
    st.warning("🔒 Please log in first.")
else:
    user_id = st.session_state.user_id
    
    # Input fields for the patient information
    medical_history = [item.strip() for item in st.text_area("Medical History (comma-separated)").split(",") if item.strip()]
    symptoms = [item.strip() for item in st.text_area("Symptoms (comma-separated)").split(",") if item.strip()]
    status = st.selectbox("Current Status", ["Stable", "Critical", "Under Treatment"])
    drug_history = [item.strip() for item in st.text_area("Drug History (comma-separated)").split(",") if item.strip()]
    
    # Address fields
    street = st.text_input("Street Address").strip()
    city = st.text_input("City").strip()
    state = st.text_input("State").strip()
    country = st.text_input("Country").strip()
    postal_code = st.text_input("Postal Code").strip()

    # Button to submit the information
    submit_button = st.button("Submit Information")

    # Handle the form submission
    if submit_button:
        # Ensure that all fields are filled out
        if all([user_id, medical_history, symptoms, status, drug_history, street, city, state, country, postal_code]):
            # Create the address dictionary with correctly formatted keys
            address = {
                "street": street,
                "city": city,
                "state": state,
                "country": country,
                "postal_code": postal_code
            }

            # Create a patient object from the input data
            patient_info = Patient(
                user_id=user_id,
                medical_history=medical_history,
                symptoms=symptoms,
                address=address,
                status=status,
                drug_history=drug_history
            )
            
            # Send the patient data to your backend API for storage (using POST)
            response = requests.post(
                f"http://localhost:8000/patient/add/{user_id}",
                json=patient_info.dict()
            )
            
            if response.status_code == 200:
                st.success("✅ Patient information successfully added!")
            else:
                st.error(f"❌ Error: {response.text}")
        else:
            st.warning("⚠️ Please fill out all fields before submitting.")

# Optional: Navigation buttons or other features
st.markdown("---")
st.subheader("🔄 Navigate to Other Sections")

col1, col2 = st.columns(2)

with col1:
    if st.button("👩‍⚕️ View Patient Information", key="view_patient"):
        st.switch_page("pages/3ViewProfile.py")  # Change the path if needed

# with col2:
#     if st.button("👤 User Dashboard", key="user_dashboard"):
#         st.switch_page("pages/user_dashboard.py")  # Change the path if needed
