from shared import *

st.title("Reviewer Home")

if 'mode' not in st.session_state:
    st.session_state.mode = 'REVIEWER'

if st.button("Review"):
    st.switch_page("pages/12_Assess_&_Review.py")
if st.button("Home"):
    st.switch_page("streamlit_app.py")
