from shared import *
from airtable_utils import load_airtable

display_logo()

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
    st.switch_page("pages/2_Initiate_Review.py")
if st.button("Report"):
    st.switch_page("pages/12_Report.py")
if st.button("Home"):
    st.switch_page("streamlit_app.py")

