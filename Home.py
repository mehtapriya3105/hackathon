import streamlit as st

# Page Background (Optional)
# page_bg_img = """
# <style>
# [class="main st-emotion-cache-uf99v8 ea3mdgi3"]{
# background-image: url("https://img.freepik.com/free-vector/watercolor-blue-background_23-2149323831.jpg");
# background-size: 2000px 1000px;
# background-repeat:no-repeat
# }
# [data-testid="stSidebarNavItems"]{
# visibility:hidden
# }
# </style>
# """
# st.markdown(page_bg_img, unsafe_allow_html=True)

end_text = """Hi user!  
Welcome to the Rare Disease Support Map!  

This project is named as **Global Rare Disease Network**.  
Create your account to connect with patient groups, caregivers, and researchers worldwide.  
This project helps you discover and engage with rare disease communities, providing support, resources, and collaboration opportunities.
"""

# **Image Display**
sp1, sp2, sp3, sp4 = st.columns(4)
sp2.image("Rare_Disease.jpeg", caption="Powered by Hack4Health", width=250)

# **Static Text Display**
st.markdown(f"{end_text}")

# **Login/Signup Sections**
s1, s2 = st.columns(2)
s1.markdown(":blue[***Already have an account?***]")
s2.markdown(":violet[***Don't have an account?***]")

s1, s2 = st.columns(2)
if s1.button("Login"):
    st.switch_page("pages/2Login.py")
elif s2.button("Signup"):
    st.switch_page("pages/1SignUp.py")
