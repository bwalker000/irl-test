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

if st.button("Initiate Review"):
    reset_session_timer()  # User is active
    st.switch_page("pages/2_Initiate_Review.py")
if st.button("Report"):
    reset_session_timer()  # User is active
    st.switch_page("pages/12_Report.py")
if st.button("Home"):
    reset_session_timer()  # User is active
    st.switch_page("streamlit_app.py")

