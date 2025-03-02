import streamlit as st
import requests

st.title("Login")

# Create a form for login
with st.form("login_form"):
    email_l = st.text_input("Email*")
    pass_l = st.text_input("Password*", type="password")

    submit_l = st.form_submit_button("Login")

    # Forgot Password Link
    st.write('<a href="https://login.microsoftonline.com" target="_blank">Forgot password?</a>', unsafe_allow_html=True)

    # Handling login logic
    if submit_l:
        if email_l.strip() == '' or pass_l.strip() == '':
            st.error("Mandatory fields cannot be empty.")
        else:
            try:
                data = {"email": email_l, "password": pass_l}
                response = requests.post("http://127.0.0.1:8000/user/login", json=data)

                if response.status_code == 200:
                    # Assuming the response contains the user_id (or token)
                    user_data = response.json()
                    user_id = user_data.get("user_id")  # Or token if that's what the API sends

                    # Store the user_id in session state
                    st.session_state.user_id = user_id

                    # Print response and display success
                    print(type( st.session_state.user_id))
                    st.success(f"Hi user: {user_data}")
                    st.switch_page("pages/3ViewProfile.py")

                else:
                    st.error(f"Login failed: {response.text}")

            except requests.exceptions.RequestException:
                st.error("Server error or incorrect username/password.")

# Sign Up Section (Outside Form)
col1, col2 = st.columns([3, 1])

with col1:
    st.write("Don't have an account? :woman:")

with col2:
    if st.button("Sign up"):
        st.switch_page("pages/1SignUp.py")