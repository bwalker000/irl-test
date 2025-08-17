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
st.session_state.assessor_first_name = row.iloc[0]["First Name"]
st.session_state.assessor_last_name = row.iloc[0]["Last Name"]

st.session_state.support_org = row.iloc[0]["Organization"][0]
st.session_state.venture = row.iloc[0]["Venture"][0]

assessor_first_name = st.session_state.assessor_first_name
assessor_last_name = st.session_state.assessor_last_name

support_id = st.session_state.support_org
st.write(f"Support id: {support_id}")
st.write("")
venture_id = st.session_state.venture
st.write(f"Venture id: {venture_id}")
st.write("")

st.write("Columns in air_support:", air_support.columns.tolist())
st.write("Columns in air_ventures:", air_ventures.columns.tolist())

support_row = air_support.loc[air_support["id"] == support_id]
support_row
support_name = support_row.iloc[0]["Name"]

venture_row = air_ventures.loc[air_ventures["id"] == venture]
venture_row
venture_name = venture_row.iloc[0]["Name"]


col1, col2 = st.columns(2)
col1.write("Assessor:")
col2.write(f"{assessor_first_name} {assessor_last_name}")

col1.write("Support Organization:")
col2.write(support_name)

col1.write("Venture:")
col2.write(venture_name)

#
#
# Select among projects
#
#

# Load secrets
table_name = st.secrets["general"]["airtable_table_projects"]

# load airtable data
air_projects, debug_details = load_airtable(table_name, base_id, api_key, debug)

records = table.all(formula=f"{{Venture}} = '{venture_id}'")
records 

#project_names = air_projects['Name']

# Streamlit selectbox for choosing a Name
#selected_project = st.selectbox('Select a Project to Assess:', options=names)

#
#
#

if st.button("Continue to Assessment"):
    st.switch_page("pages/12_Assess_&_Review.py")
###    st.session_state.project = 
if st.button("Home"):
    st.switch_page("streamlit_app.py")