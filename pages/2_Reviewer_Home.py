from shared import *

st.title("Reviewer Home")

st_session_state.mode = 'REVIEWER'

if st.button("Assess"):
    st.switch_page("pages/12_Assess_&_Review.py")
if st.button("Home"):
    st.switch_page("streamlit_app.py")
