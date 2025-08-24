from shared import *

st.title("Create a New Assessment")

#st.write(st.session_state.assessor)

# Debug mode toggle
#debug = st.checkbox("Enable Airtable debug mode", value=False)
debug = False

# Load shared secrets
api_key = st.secrets["general"]["airtable_api_key"]
base_id = st.secrets["general"]["airtable_base_id"]

# load airtable ASSESSORs table
table_name = st.secrets["general"]["airtable_table_assessors"]
air_assessors, debug_details = load_airtable(table_name, base_id, api_key, debug)

# load airtable Ventures table
table_name = st.secrets["general"]["airtable_table_ventures"]
air_ventures, debug_details = load_airtable(table_name, base_id, api_key, debug)

# load airtable Support table
table_name = st.secrets["general"]["airtable_table_support"]
air_support, debug_details = load_airtable(table_name, base_id, api_key, debug)

row = air_assessors.loc[air_assessors["Email"] == st.session_state.assessor_email]

st.session_state.assessor_id = row["id"].tolist()

st.session_state.assessor_first_name = row.iloc[0]["First Name"]
st.session_state.assessor_last_name = row.iloc[0]["Last Name"]

st.session_state.support_id = row.iloc[0]["Organization"]
st.session_state.venture_id = row.iloc[0]["Venture"]

st.session_state.support_name = airtable_value_from_id(air_support, 
        st.session_state.support_id, "Name")
st.session_state.venture_name = airtable_value_from_id(air_ventures, 
        st.session_state.venture_id, "Name")

#
# Display details about the assessment
#
with st.container(border=True):

    col1, col2 = st.columns(2)
    col1.write("__Assessor:__")
    col2.write(f"{st.session_state.assessor_first_name} {st.session_state.assessor_last_name}")

    col1.write("__Support Organization:__")
    col2.write(st.session_state.support_name)

    col1.write("__Venture:__")
    col2.write(st.session_state.venture_name)

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

    records = air_projects[air_projects["Venture"].apply(lambda x: x[0] == st.session_state.venture_id[0])]

    project_names = records['Name']

    # Streamlit selectbox for choosing a Name
    st.session_state.project_name = st.selectbox('__Project:__', options=project_names)

    #st.write("\n")

if st.button("Continue to Assessment"):

    ### Check the following block
    row = records[records["Name"] == st.session_state.project_name]
    st.session_state.project_id = row["id"].tolist()

    st.switch_page("pages/12_Assess_&_Review.py")

if st.button("Home"):
    st.switch_page("streamlit_app.py")