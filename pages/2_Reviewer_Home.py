from shared import *
from airtable_utils import load_airtable
from shared import check_session_timeout, reset_session_timer

display_logo()

# Check for session timeout at page entry
check_session_timeout()

st.title("Reviewer Home")

if 'mode' not in st.session_state:
    st.session_state.mode = 'REVIEWER'

# Load secrets
api_key = st.secrets["general"]["airtable_api_key"]
base_id = st.secrets["general"]["airtable_base_id"]
table_name = st.secrets["general"]["airtable_table_reviewers"]

# Debug mode toggle
#debug = st.checkbox("Enable Airtable debug mode", value=False)
debug = False

# load airtable data
air_reviewers, debug_details = load_airtable(table_name, base_id, api_key, debug)

reviewer_emails = air_reviewers['Email']

# Streamlit selectbox for choosing a Reviewer by email
### *** This will go away in the future and be part of login
st.session_state.reviewer_email = st.selectbox('Select a REVIEWER:', options=reviewer_emails)

# Verify reviewer session state is set
if 'reviewer_email' not in st.session_state or 'reviewer_id' not in st.session_state:
    st.error("Reviewer information not found. Please log in again.")
    if st.button("Return to Login"):
        st.switch_page("streamlit_app.py")
    st.stop()

# Display current reviewer
st.info(f"**Logged in as:** {st.session_state.reviewer_email}")

# Navigate
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Review"):
        reset_session_timer()
        st.switch_page("pages/2_Initiate_Review.py")
with col2:
    if st.button("Add New Venture"):
        reset_session_timer()
        st.switch_page("pages/2_New_Venture.py")
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

