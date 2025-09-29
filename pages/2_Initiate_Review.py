from shared import *
# Explicitly import shared configuration
from shared import num_dims, numQ

# Assumptions:
#        A specific ASSESSOR is intrinsically tied to:
#            A specific venture
#        A specific venture is intrinsically tied to:
#            A specific support organization
#        The ASSESSOR can select which project they are interested in assessing.


st.title("Initiate a Review")

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
    0: "Review an Existing Assessment",
    1: "Perform an Independent Review",
}

st.session_state.review_mode = st.segmented_control(
    "Review Mode",
    options=list(option_map.keys()),  # Convert to list to ensure hashable type
    format_func=lambda option: option_map[option],
    selection_mode="single",
    label_visibility="collapsed"  # Hide the label but maintain accessibility
)

#---------------------------------------------------------------------------------
# no review mode selected

if st.session_state.review_mode == None:
    st.write("Select a review mode to continue")

#---------------------------------------------------------------------------------
# Perform a review of an existing assessment

elif st.session_state.review_mode == 0:
    table_name = st.secrets["general"]["airtable_table_data"]
    air_data, debug_details = load_airtable(table_name, base_id, api_key, debug)

    # Filter records by support organization and blank review dates
    filtered_records = air_data[air_data["Support Organization"] == st.session_state.support_id]
    filtered_records = filtered_records[
        (filtered_records["Review_date"].isnull()) |
        (filtered_records["Review_date"] == "") |
        (filtered_records["Review_date"] == pd.NaT)
    ]

    # Proceed with selection logic
    assessment_names = filtered_records['Name']
    if not assessment_names.empty:
        # Initialize assessment_name if it's not in session state
        if 'assessment_name' not in st.session_state:
            st.session_state.assessment_name = assessment_names.iloc[0]
        
        selected_name = st.selectbox('Select an assessment for review:', 
                                   options=assessment_names,
                                   key='assessment_select')
        
        # Update session state with the selection
        st.session_state.assessment_name = selected_name

        # This identifies the specific assessment to be reviewed
        air_data_record = air_data.loc[air_data["Name"] == selected_name]
        
        st.session_state.assessor_id = air_data_record.iloc[0]["ASSESSOR"]
        st.session_state.venture_id = air_data_record.iloc[0]["Venture"]
        st.session_state.project_id = air_data_record.iloc[0]["Project"]
    else:
        st.warning("No available assessments to review for your Support Organization.")
        # Reset assessment related session state
        for key in ['assessment_name', 'assessor_id', 'venture_id', 'project_id']:
            if key in st.session_state:
                del st.session_state[key]

    table_name = st.secrets["general"]["airtable_table_assessors"]
    air_assessors, debug_details = load_airtable(table_name, base_id, api_key, debug)

    st.session_state.assessor_first_name = airtable_value_from_id(air_assessors, st.session_state.assessor_id, "First Name")
    st.session_state.assessor_last_name = airtable_value_from_id(air_assessors, st.session_state.assessor_id, "Last Name")

    table_name = st.secrets["general"]["airtable_table_ventures"]
    air_ventures, debug_details = load_airtable(table_name, base_id, api_key, debug)
    st.session_state.venture_name = airtable_value_from_id(air_ventures, st.session_state.venture_id, "Name")

    table_name = st.secrets["general"]["airtable_table_projects"]
    air_projects, debug_details = load_airtable(table_name, base_id, api_key, debug)
    st.session_state.project_name = airtable_value_from_id(air_projects, st.session_state.project_id, "Name")

#---------------------------------------------------------------------------------
# Perform an independent review

elif st.session_state.review_mode == 1:
    st.write("Perform an independent review")

    # Set default values for assessor-related session state fields since there is no assessment being reviewed.
    # This ensures the review process can proceed independently of any existing assessment.
    
    # Set assessor info to default values since this is an independent review
    st.session_state.assessor_first_name = "N/A"
    st.session_state.assessor_last_name = ""
    st.session_state.assessor_id = []
    st.session_state.assessment_name = None  # No associated assessment
    st.session_state.assessment_date = None  # No assessment date
    
    # Initialize assessment matrices using shared configuration
    if ('dim' not in st.session_state):
        st.session_state.dim = 0  # start with the first dimension

    if 'QA' not in st.session_state:
        st.session_state.QA = np.zeros((num_dims, numQ), dtype=bool)
    if 'QR' not in st.session_state:
        st.session_state.QR = np.zeros((num_dims, numQ), dtype=bool)
    if 'TA' not in st.session_state:
        st.session_state.TA = [""] * num_dims
    if 'TR' not in st.session_state:
        st.session_state.TR = [""] * num_dims

    # load the table of all ventures
    table_name = st.secrets["general"]["airtable_table_ventures"]
    air_ventures, debug_details = load_airtable(table_name, base_id, api_key, debug)

    # Extract your support_id string
    support_id = st.session_state.support_id[0]

    # Build the boolean mask for support org match
    support_match = air_ventures["Support Organization"].apply(
        lambda x: support_id in x if isinstance(x, (list, tuple)) else x == support_id
    )

    # Filter the ventures that are managed by the current support org
    filtered_records = air_ventures[support_match]

    # Proceed with selection logic for the ventures
    venture_names = filtered_records['Name']
    if not venture_names.empty:

# After venture selection
        st.session_state.venture_name = st.selectbox('Select a venture for review:', options=venture_names)
        
        air_ventures_record = air_ventures.loc[ air_ventures["Name"] == st.session_state.venture_name ]
        st.session_state.venture_id = air_ventures_record["id"]

        # Get the row for the selected venture
        selected_venture_row = filtered_records.loc[filtered_records["Name"] == st.session_state.venture_name]
        if not selected_venture_row.empty:
            # Get associated project IDs
            project_ids = selected_venture_row.iloc[0]['Projects']
            # Load all projects
            table_name = st.secrets["general"]["airtable_table_projects"]
            air_projects, debug_details = load_airtable(table_name, base_id, api_key, debug)
            if isinstance(project_ids, (list, tuple)):
                project_ids_list = list(project_ids)  # Convert tuple to list if needed
                filtered_projects = air_projects[air_projects["id"].isin(project_ids_list)]
                project_names = filtered_projects['Name']
                if not project_names.empty:
                    st.session_state.project_name = st.selectbox('Select a project for review:', options=project_names)

                    air_projects_record = air_projects.loc[ air_projects["Name"] == st.session_state.project_name ]
                    st.session_state.project_id = air_projects_record["id"]
                else:
                    st.warning("No available projects for the selected Venture.")
            else:
                st.warning("No available projects for the selected Venture.")
        else:
            st.warning("Selected Venture not found.")
    else:
        st.warning("No available ventures to review for your Support Organization.")


#---------------------------------------------------------------------------------

if st.button("Continue to Review"):
    st.switch_page("pages/12_Assess_&_Review.py")

if st.button("Home"):
    st.switch_page("streamlit_app.py")
