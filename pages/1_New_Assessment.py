from shared import *

st.title("Create a New Assessment")

st.write(st.session_state.name)

# Debug mode toggle
debug = st.checkbox("Enable Airtable debug mode", value=False)

# Load secrets
api_key = st.secrets["general"]["airtable_api_key"]
base_id = st.secrets["general"]["airtable_base_id"]

# load airtable ASSESSORs table
table_name = st.secrets["general"]["airtable_table_assessors"]
air_assessors, debug_details = load_airtable(table_name, base_id, api_key, debug)

# load airtable Ventures table
table_name = st.secrets["general"]["airtable_table_ventures"]
air_ventures, debug_details = load_airtable(table_name, base_id, api_key, debug)

# load airtable Ventures table
table_name = st.secrets["general"]["airtable_table_support"]
air_support, debug_details = load_airtable(table_name, base_id, api_key, debug)

assessor_name = st.session_state.name

row = air_assessors.loc[air_assessors["Name"] == assessor_name]

st.session_state.assessor = st.session_state.name
st.session_state.assessor_first_name = row.iloc["First Name"]
st.session_state.assessor_last_name = row.iloc["Last Name"]
st.session_state.support_org = row["Organization"].values
st.session_state.venture = row["Venture"].values

assessor_first_name = st.session_state.assessor_first_name
assessor_last_name = st.session_state.assessor_last_name
support_org = st.session_state.support_org
venture = st.session_state.venture

st.write(f"Assessor: {assessor_first_name} {assessor_last_name}")
st.write(f"Support Organization: {support_org}")
st.write(f"Venture: {venture}")

if st.button("Home"):
    st.switch_page("streamlit_app.py")