import streamlit as st
import requests


def logout():
    st.warning("User session over.")


sp1, sp2, sp3 = st.columns(3)
placeholder = sp3.empty()

try:
    response = requests.get("http://localhost:8000/system/viewUser")

    if response.status_code != 200:
        st.warning("User is unauthorized")
    else:
        full_data = response.json()

        if st.button('Logout', on_click=logout):
            requests.post("http://127.0.0.1:8000/system/logout")

        placeholder.write(f"Hello {full_data[1]} {full_data[2]}!")

except Exception:
    st.warning("User unauthorized")
