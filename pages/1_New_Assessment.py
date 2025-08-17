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

# If "Organization" and "Venture" columns contain record IDs:
org_id = row.iloc["Organization"] if row.iloc["Organization"] else None
venture_id = row.iloc["Venture"] if row.iloc["Venture"] else None

# Map IDs to names using reference DataFrames (example: org_df and venture_df)
org_map = dict(zip(org_df["id"], org_df["Name"]))
venture_map = dict(zip(venture_df["id"], venture_df["Name"]))

st.session_state.support_org = org_map.get(org_id, "Unknown")
st.session_state.venture = venture_map.get(venture_id, "Unknown")

assessor_first_name = st.session_state.assessor_first_name
assessor_last_name = st.session_state.assessor_last_name
support_org = st.session_state.support_org
venture = st.session_state.venture

st.write(f"Assessor: {assessor_first_name} {assessor_last_name}")
st.write(f"Support Organization: {support_org}")
st.write(f"Venture: {venture}")

if st.button("Home"):
    st.switch_page("streamlit_app.py")
