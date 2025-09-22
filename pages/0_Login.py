from shared import *

st.title("Login")

if st.button("Home"):
    st.switch_page("streamlit_app.py")

if st.button("Log in"):
    st.login()
if st.user.is_logged_in:
    if st.button("Log out"):
        st.logout()
#st.write(f"Hello, {st.user.name}!")
             

#if st.button("Login as Assessor"):
#    st.switch_page("pages/1_Assessor_Home.py")
#if st.button("Login as Reviewer"):
#    st.switch_page("pages/2_Reviewer_Home.py")
