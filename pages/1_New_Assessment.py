from shared import *

st.title("Create a New Assessment")

st.write(st.session_state.name)

# Debug mode toggle
debug = st.checkbox("Enable Airtable debug mode", value=False)

# Load secrets
api_key = st.secrets["general"]["airtable_api_key"]
base_id = st.secrets["general"]["airtable_base_id"]
table_name = st.secrets["general"]["airtable_table_assessors"]

# load airtable ASSESSORs table
air_assessors, debug_details = load_airtable(table_name, base_id, api_key, debug)

assessor_name = st.session_state.name

row = air_assessors.loc[air_assessors["Name"] == assessor_name]

first_name = row["First Name"].values
last_name = row["Last Name"].values
organization = row["Organization"].values
venture = row["Venture"].values

first_name
last_name
organization
venture

if st.button("Home"):
    st.switch_page("streamlit_app.py")