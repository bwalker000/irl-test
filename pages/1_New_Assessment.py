from shared import *
from pyairtable.formulas import match

st.title("Create a New Assessment")

st.write(st.session_state.name)

# Debug mode toggle
debug = st.checkbox("Enable Airtable debug mode", value=False)

# Load secrets
api_key = st.secrets["general"]["airtable_api_key"]
base_id = st.secrets["general"]["airtable_base_id"]
table_name = st.secrets["general"]["airtable_table_assessors"]

# load airtable ASSESSORs table
at_assessors, debug_details = load_airtable(table_name, base_id, api_key, debug)

assessor_name = st.session_state.name
formula = match({"Name": assessor_name})
records = at_assessors.all(filterByFormula=formula)

if records:
    assessor_record = records[0]  # Should only be one, as Name is unique
    fields = assessor_record['fields']
    first_name = fields.get("First Name", "")
    last_name = fields.get("Last Name", "")
    organization = fields.get("Organization", [])  # Usually a list of linked record IDs
    venture = fields.get("Venture", [])            # Usually a list of linked record IDs
else:
    st.error("No record found for the given Name.")


first_name
last_name
organization
venture


if st.button("Home"):
    st.switch_page("streamlit_app.py")