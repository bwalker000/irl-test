from shared import *

st.title("Create New Reviewer")

st.write("New reviewers can currently only be created by the administrator. Please request via email.")

if st.button("Back"):
    st.switch_page("pages/Reviewer_Home.py")
