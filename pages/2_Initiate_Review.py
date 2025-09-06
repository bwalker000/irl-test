from shared import *

# Assumptions:
#        A specific ASSESSOR is intrinsically tied to:
#            A specific venture
#        A specific venture is intrinsically tied to:
#            A specific support organization
#        The ASSESSOR can select which project they are interested in assessing.


st.title("Initiate a Review of an existing Assessment")

# Debug mode toggle
#debug = st.checkbox("Enable Airtable debug mode", value=False)
debug = False

# ---------------------------------------------------------------------------------
# Load secrets
api_key = st.secrets["general"]["airtable_api_key"]
base_id = st.secrets["general"]["airtable_base_id"]
table_name = st.secrets["general"]["airtable_table_reviewers"]

#---------------------------------------------------------------------------------
# The only options available should be for the support org associated with the reviewer

# 1. Figure out which ventures are associated with the reviewers support org.
# 2. Reviewer selects which assessment they would like to review
# 3. Then move on to performing the review

#---------------------------------------------------------------------------------
# load airtable Reviewers table
air_reviewers, debug_details = load_airtable(table_name, base_id, api_key, debug)

reviewer_emails = air_reviewers['Email']
row = air_reviewers.loc[air_reviewers["Email"] == st.session_state.reviewer_email]

st.session_state.reviewer_id = row["id"].tolist()
st.session_state.reviewer_first_name = row.iloc[0]["First Name"]
st.session_state.reviewer_last_name = row.iloc[0]["Last Name"]
st.session_state.support_id = row.iloc[0]["Support Organization"]

#---------------------------------------------------------------------------------
# Load Support Organization info
table_name = st.secrets["general"]["airtable_table_support"]
air_support, debug_details = load_airtable(table_name, base_id, api_key, debug)

st.session_state.support_name = airtable_value_from_id(air_support, st.session_state.support_id, "Name")

#---------------------------------------------------------------------------------
# Select between independent review OR review of assessment

option_map = {
    0: "Review Existing Assessment",
    1: "Perform Independent Review",
}

st.session_state.review_mode = st.segmented_control(
    "",
    options=option_map.keys(),
    format_func=lambda option: option_map[option],
    selection_mode="single",
)

#---------------------------------------------------------------------------------
# no review mode selected

if st.session_state.review_mode == None:
    st.write("Select a review mode to continue")

#---------------------------------------------------------------------------------
# Perform a review of an existing assessment

elif st.session_state.review_mode == 0:
    st.write("Select among existing assessments to review")

    table_name = st.secrets["general"]["airtable_table_data"]
    air_data, debug_details = load_airtable(table_name, base_id, api_key, debug)

    st.session_state.support_id

    air_data

    st.write(air_data["Review_date"])

    # find all the assessments that match the reviewer's support organization and are not yet reviewed
    air_data_records = air_data.loc[
        (air_data["Support Organization"] == st.session_state.support_id) &
        (air_data["Review_date"].isnull())
    ]

    assessment_names = air_data_records['Name']

    # Streamlit selectbox for choosing an assessment for review
    st.session_state.assessment_name = st.selectbox('Select an assessment for review:', options = assessment_names)

    air_data_record = air_data.loc[ air_data["Name"] == st.session_state.assessment_name ]

    st.session_state.assessor_id = air_data_record.iloc[0]["ASSESSOR"]
    st.session_state.venture_id = air_data_record.iloc[0]["Venture"]
    st.session_state.project_id = air_data_record.iloc[0]["Project"]

    table_name = st.secrets["general"]["airtable_table_assessors"]
    air_assessors, debug_details = load_airtable(table_name, base_id, api_key, debug)

    row = air_assessors.loc[air_assessors["id"] == st.session_state.assessor_id]

    st.session_state.assessor_first_name = row.iloc[0]["First Name"]
    st.session_state.assessor_last_name = row.iloc[0]["Last Name"]

#---------------------------------------------------------------------------------
# Perform an independent review

elif st.session_state.review_mode == 1:
    st.write("Perform an independent review")

    table_name = st.secrets["general"]["airtable_table_ventures"]
    air_ventures, debug_details = load_airtable(table_name, base_id, api_key, debug)

    ventures = air_ventures.loc[air_ventures["Support Organization"] == st.session_state.support_id]

    venture_names = ventures['Name']
    st.session_state.venture_name = st.selectbox('Select a venture for a new review:', options = venture_names)

    st.session_state.venture_id = air_ventures.loc[air_ventures["Name"] == st.session_state.venture_name]


    table_name = st.secrets["general"]["airtable_table_projects"]
    air_projects, debug_details = load_airtable(table_name, base_id, api_key, debug)

    projects = air_projects.loc[air_projects["Venture"] == st.session_state.venture_id]

    project_names = projects['Name']
    st.session_state.project_name = st.selectbox('Select a project for a new review:', options = project_names)

    st.session_state.project_id = air_projects.loc[ air_projects["Name"] == st.session_state.project_name]

#---------------------------------------------------------------------------------

if st.button("Continue to Review"):
    st.switch_page("pages/12_Assess_&_Review.py")

if st.button("Home"):
    st.switch_page("streamlit_app.py")
