from shared import *
from shared import check_session_timeout, reset_session_timer

display_logo()

# Check for session timeout at page entry
check_session_timeout()

st.title("Reviewer Home")

if 'mode' not in st.session_state:
    st.session_state.mode = 'REVIEWER'

# Verify reviewer session state is set
if 'reviewer_email' not in st.session_state or 'reviewer_id' not in st.session_state:
    st.error("Reviewer information not found. Please log in again.")
    if st.button("Return to Login"):
        st.switch_page("streamlit_app.py")
    st.stop()

# Load reviewer details from Airtable
api_key = st.secrets["general"]["airtable_api_key"]
base_id = st.secrets["general"]["airtable_base_id"]

# Load reviewers table
table_name = st.secrets["general"]["airtable_table_reviewers"]
air_reviewers, _ = load_airtable(table_name, base_id, api_key, False)

# Get reviewer record
reviewer_id = st.session_state.reviewer_id[0] if isinstance(st.session_state.reviewer_id, (list, tuple)) else st.session_state.reviewer_id
reviewer_record = air_reviewers[air_reviewers['id'] == reviewer_id]

if reviewer_record.empty:
    st.error("Reviewer record not found.")
    if st.button("Return to Login"):
        st.switch_page("streamlit_app.py")
    st.stop()

# Extract reviewer details
reviewer_first_name = reviewer_record.iloc[0].get('First Name', '')
reviewer_last_name = reviewer_record.iloc[0].get('Last Name', '')
support_org_id = reviewer_record.iloc[0].get('Support Organization')

# Load support organization name
table_name = st.secrets["general"]["airtable_table_support"]
air_support, _ = load_airtable(table_name, base_id, api_key, False)

if isinstance(support_org_id, (list, tuple)):
    support_org_id = support_org_id[0]

support_org_record = air_support[air_support['id'] == support_org_id]
support_org_name = support_org_record.iloc[0]['Name'] if not support_org_record.empty else "Unknown"

# Display current reviewer info
st.info(f"**Logged in as:** {reviewer_first_name} {reviewer_last_name}")
st.info(f"**Support Organization:** {support_org_name}")

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