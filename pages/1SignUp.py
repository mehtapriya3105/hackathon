import uuid
import streamlit as st
import requests
import uuid
with st.form("my_form"):
    st.title("Sign up")

    fname, lname = st.columns(2)
    fname_s = fname.text_input("First name*")
    lname_s = lname.text_input("Last name*")
    userName = fname_s + " " + lname_s
    date, gender = st.columns(2)
    date_s = date.date_input("Date Of Birth")
    gender_s = gender.radio(
        "Gender",
        ["Male", "Female", "Other"],
        horizontal=True
    )

    num_s = st.text_input("Phone number*")
    email_s = st.text_input("Email*")

    pw, repw = st.columns(2)
    pw_s = pw.text_input("Password*", type="password")
    repw_s = repw.text_input("Confirm Password*", type="password")

    st.text("By clicking on I agree, you agree to User agreement, Privacy policy, and Cookie policy.")
    agree_s = st.checkbox("I agree.*")

    signup_s = st.form_submit_button("Sign up")
col1, col2 = st.columns([3, 1])
# ✅ Move the "Login" button OUTSIDE the form
with col1:
    st.write("Already have an account? :man:")

with col2:
    if st.button("Login"):
        st.switch_page("pages/2Login.py")

if signup_s:
    if not all([fname_s.strip(), lname_s.strip(), num_s.strip(), email_s.strip(), pw_s.strip(), repw_s.strip(), agree_s]):
        st.error("Mandatory fields cannot be empty.")
    elif pw_s.strip() != repw_s.strip():
        st.error("Passwords MUST match!")
    else:
        date_str = date_s.isoformat()
        # Fix the typo and missing fields
        data = {
            "firstName": fname_s, 
            "lastName": lname_s, 
            "dateOfBirth": date_str, 
            "gender": gender_s,  # Changed from gender_s to gender
            "contact": num_s, 
            "email": email_s, 
            "password": pw_s, 
            "user_id" : uuid.uuid4().hex,
            "username": userName  # Fixed the key from userName to username
        }
        response = requests.post("http://127.0.0.1:8000/user/signup", json=data)

        if response.status_code == 200:
            st.success(f"User created successfully: {response.json()}")
            st.switch_page("pages/2Login.py")
            
        else:
            st.error(f"Error creating user: {response.text}")
