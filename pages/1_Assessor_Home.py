from shared import *

st.title("Assessor Home")

if 'mode' not in st.session_state:
    st.session_state.mode = 'ASSESSOR'

# Load secrets
api_key = st.secrets["general"]["airtable_api_key"]
base_id = st.secrets["general"]["airtable_base_id"]
table_name = st.secrets["general"]["airtable_table_assessors"]

# Debug mode toggle
debug = st.checkbox("Enable Airtable debug mode", value=False)

# load airtable data
df, debug_details = load_airtable(table_name, base_id, api_key, debug)

names = df['Name']

# Streamlit selectbox for choosing a Name
selected_name = st.selectbox('Select a Name:', options=names)

if st.button("Assess"):
    st.session_state.name = selected_name
    st.switch_page("pages/1_New_Assessment.py")
if st.button("Home"):
    st.switch_page("streamlit_app.py")
