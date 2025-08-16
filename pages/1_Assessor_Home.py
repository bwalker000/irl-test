from shared import *

st.title("Assessor Home")

st_session_state.mode = 'ASSESSOR'

if st.button("Assess"):
    st.switch_page("pages/12_Assess_&_Review.py")
if st.button("Home"):
    st.switch_page("streamlit_app.py")