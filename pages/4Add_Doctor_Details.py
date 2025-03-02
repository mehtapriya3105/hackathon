import streamlit as st
import requests
from pydantic import BaseModel
from typing import List

# Define the Doctor class with the new address structure
class Doctor(BaseModel):
    user_id: str  # Foreign key to User
    Specialization: str
    ResearchArea: List[str]
    Address: dict  # Address will be a dictionary with multiple fields

# Set up the Streamlit page
st.set_page_config(page_title="Add Doctor Information", page_icon="🩺", layout="wide")

st.title("🩺 Add Doctor Information")
st.subheader("Please fill out the details below:")

# Ensure the user is logged in and has a valid user_id in session state
if "user_id" not in st.session_state:
    st.warning("🔒 Please log in first.")
else:
    user_id = st.session_state.user_id
    print(user_id)
    # Input fields for the doctor information
    specialization = st.text_input("Specialization")
    research_area = st.text_area("Research Area (comma-separated)").split(",")
    
    # Address fields
    street = st.text_input("Street Address")
    city = st.text_input("City")
    state = st.text_input("State")
    country = st.text_input("Country")
    postal_code = st.text_input("Postal Code")

    # Button to submit the information
    submit_button = st.button("Submit Information")

    # Handle the form submission
    if submit_button:
        # Ensure that all fields are filled out
        if specialization and research_area and street and city and state and country and postal_code:
            # Create the address dictionary
            address = {
                "street": street,
                "city": city,
                "state": state,
                "country": country,
                "postal_code": postal_code
            }

            # Create a doctor object from the input data
            doctor_info = Doctor(
                user_id=user_id,
                Specialization=specialization,
                ResearchArea=[item.strip() for item in research_area],
                Address=address
            )
            
            # Send the doctor data to your backend API for storage (using POST)
            response = requests.post(
                "http://localhost:8000/doctor/add?id=" + user_id, 
                json=doctor_info.dict()
            )
            
            if response.status_code == 200:
                st.success("Doctor information successfully added!")
            else:
                st.error(f"Error: {response.text}")
        else:
            st.warning("⚠️ Please fill out all fields before submitting.")

# Optional: Navigation buttons or other features
st.markdown("---")
st.subheader("🔄 Navigate to Other Sections")

col1, col2 = st.columns(2)

with col1:
    if st.button("👩‍⚕️ View Doctor Information", key="view_doctor"):
        st.switch_page("pages/3ViewProfile.py")  # Change the path to your actual page if needed

# with col2:
#     if st.button("👤 User Dashboard", key="user_dashboard"):
#         st.switch_page("pages/user_dashboard.py")  # Change the path to your actual page if needed
