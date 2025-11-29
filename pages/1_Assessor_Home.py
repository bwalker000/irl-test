from shared import *
from shared import check_session_timeout, reset_session_timer

display_logo()

# Check for session timeout at page entry
check_session_timeout()

st.title("Assessor Home")

if 'mode' not in st.session_state:
    st.session_state.mode = 'ASSESSOR'

# ---------------------------------------------------------------------------------
# Verify assessor session state is set
if 'assessor_email' not in st.session_state or 'assessor_id' not in st.session_state:
    st.error("Assessor information not found. Please log in again.")
    if st.button("Return to Login"):
        st.switch_page("streamlit_app.py")
    st.stop()

# Display current assessor
st.info(f"**Logged in as:** {st.session_state.assessor_email}")

# ---------------------------------------------------------------------------------
# Navigate

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Assess"):
        reset_session_timer()
        st.switch_page("pages/1_New_Assessment.py")
with col2:
    if st.button("Add New Project"):
        reset_session_timer()
        st.switch_page("pages/1_New_Project.py")
with col3:
    if st.button("Report"):
        reset_session_timer()
        st.switch_page("pages/12_Report.py")
with col4:
    if st.button("Log out"):
        # Clear EULA acceptance and login attempt on logout
        st.session_state.eula_accepted = False
        st.session_state.login_attempted = False
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        try:
            st.logout()
        except:
            st.rerun()
