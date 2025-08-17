from shared import *

st.title("Create a New Assessment")

st.write(st.session_state.name)

# Debug mode toggle
debug = st.checkbox("Enable Airtable debug mode", value=False)

# Load shared secrets
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

support_id = st.session_state.support
venture_id = st.session_state.venture

support_name = airtable_value_from_id(air_support, support_id, "Name")
venture_name = airtable_value_from_id(air_ventures, venture_id, "Name")

st.session_state.support_name = support_name
st.session_state.venture_name = venture_name

#
# Display details about the assessment
#
col1, col2 = st.columns(2)
col1.write("__Assessor:__")
col2.write(f"{assessor_first_name} {assessor_last_name}")

col1.write("__Support Organization:__")
col2.write(support_name)

col1.write("__Venture:__")
col2.write(venture_name)

#
# Select among projects
#

# Load secrets
table_name = st.secrets["general"]["airtable_table_projects"]

# load airtable data
air_projects, debug_details = load_airtable(table_name, base_id, api_key, debug)

#air_projects
#venture_id
#air_projects.iloc[0]["Venture"][0]

records = air_projects[air_projects["Venture"].apply(lambda x: x[0] == venture_id)]
#records

project_names = records['Name']

# Streamlit selectbox for choosing a Name
selected_project = st.selectbox('Project:', options=project_names)

if st.button("Continue to Assessment"):
    row = records[records["Name"] == selected_project]
    st.session_state.project = row["id"].iloc[0]
    project_id = st.session_state.project
    st.session_state.project_name = airtable_value_from_id(air_projects, project_id, "Name")
    st.switch_page("pages/12_Assess_&_Review.py")

if st.button("Home"):
    st.switch_page("streamlit_app.py")