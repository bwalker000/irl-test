from shared import *

st.title("Assessor Home")

if 'mode' not in st.session_state:
    st.session_state.mode = 'ASSESSOR'

# Load secrets for Assessors Table
api_key = st.secrets["general"]["airtable_api_key"]
base_id = st.secrets["general"]["airtable_base_id"]
table_name = st.secrets["general"]["airtable_table_assessors"]

# Debug mode toggle
#debug = st.checkbox("Enable Airtable debug mode", value=False)
debug = False

# load airtable data
air_assessors, debug_details = load_airtable(table_name, base_id, api_key, debug)

assessor_emails = air_assessors['Email']

# Streamlit selectbox for choosing a the Assessor
### *** In the future this will happen automatically at login.
st.session_state.assessor_email = st.selectbox('Select an Assessor:', options=assessor_emails)

if st.button("Assess"):
    st.switch_page("pages/1_New_Assessment.py")
if st.button("Home"):
    st.switch_page("streamlit_app.py")
