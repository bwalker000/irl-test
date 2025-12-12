from shared import *
from shared import check_session_timeout, reset_session_timer

display_logo()

# Check for session timeout at page entry
check_session_timeout()

st.title("Create a New Assessment")

# Add back button at the top
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    if st.button("← Back", key="back_top"):
        reset_session_timer()
        st.switch_page("streamlit_app.py")

# Clear any existing assessment/review data from previous sessions
# This ensures a clean slate for the new assessment
if 'dim' in st.session_state:
    del st.session_state.dim
if 'QA' in st.session_state:
    del st.session_state.QA
if 'QR' in st.session_state:
    del st.session_state.QR
if 'TA' in st.session_state:
    del st.session_state.TA
if 'TR' in st.session_state:
    del st.session_state.TR
if 'submitted' in st.session_state:
    del st.session_state.submitted
if 'assessment_name' in st.session_state:
    del st.session_state.assessment_name
if 'assessment_record_id' in st.session_state:
    del st.session_state.assessment_record_id

#st.write(st.session_state.assessor)

st.session_state.mode = "ASSESSOR"

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

    # Streamlit selectbox for choosing the Project
    st.session_state.project_name = st.selectbox('__Project:__', options=project_names)

    # Set project_id immediately after project selection
    row = records[records["Name"] == st.session_state.project_name]
    st.session_state.project_id = row["id"].tolist()

    #st.write("\n")

#
# Check for existing draft
#
table_name = st.secrets["general"]["airtable_table_data"]
air_data_drafts, _ = load_airtable(table_name, base_id, api_key, False)

# Look for drafts by this assessor for this venture/project
draft_name_pattern = f"A-DRAFT - {st.session_state.venture_name}"
existing_drafts = air_data_drafts[
    (air_data_drafts['Name'].str.startswith(draft_name_pattern, na=False)) &
    (air_data_drafts['Assess_date'].isnull() | (air_data_drafts['Assess_date'] == ""))
]

if not existing_drafts.empty:
    st.warning("🔄 **Found an in-progress assessment!**")
    st.write("You have a saved draft for this venture. Would you like to continue where you left off?")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Resume Draft", type="primary"):
            # Load the draft
            draft_record = existing_drafts.iloc[0]
            st.session_state.draft_record_id = draft_record['id']
            st.switch_page("pages/12_Assess_&_Review.py")
    with col2:
        if st.button("Start Fresh"):
            # Delete old draft
            try:
                table = Table(api_key, base_id, st.secrets["general"]["airtable_table_data"])
                table.delete(existing_drafts.iloc[0]['id'])
            except:
                pass
            st.rerun()
    with col3:
        if st.button("Cancel"):
            reset_session_timer()
            st.switch_page("streamlit_app.py")
    st.stop()

# Check for completed assessments for this venture/project
completed_assessments = air_data_drafts[
    (air_data_drafts['Venture'] == st.session_state.venture_id) &
    (air_data_drafts['Project'] == st.session_state.project_id) &
    (air_data_drafts['Assess_date'].notna()) &
    (air_data_drafts['Assess_date'] != "")
]

if not completed_assessments.empty:
    st.info("📋 **Previous assessments found for this project.**")
    
    with st.expander("View previous assessments"):
        for idx, row in completed_assessments.iterrows():
            assess_date = row.get('Assess_date', 'Unknown')
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"• {row['Name']} (Assessed: {assess_date})")
            with col2:
                if st.button("Copy Data", key=f"copy_{idx}"):
                    # Load data from this assessment
                    st.session_state.copy_from_assessment_id = row['id']
                    st.rerun()
    
    # If user clicked to copy data from an assessment
    if 'copy_from_assessment_id' in st.session_state:
        source_record = air_data_drafts[air_data_drafts['id'] == st.session_state.copy_from_assessment_id].iloc[0]
        
        # Initialize arrays with data from source assessment
        from shared import num_dims, numQ
        st.session_state.QA = np.zeros((num_dims, numQ), dtype=bool)
        
        for dim in range(num_dims):
            for i in range(numQ):
                field_name = f"QA_{dim:02d}_{i}"
                if field_name in source_record and pd.notna(source_record[field_name]):
                    st.session_state.QA[dim, i] = bool(source_record[field_name])
        
        # Copy text responses
        st.session_state.TA = [""] * num_dims
        for dim in range(num_dims):
            field_name = f"TA_{dim:02d}"
            if field_name in source_record and pd.notna(source_record[field_name]):
                st.session_state.TA[dim] = source_record[field_name]
        
        # Clear the copy flag and show success
        del st.session_state.copy_from_assessment_id
        st.success(f"✓ Copied data from previous assessment. Starting new assessment with this data as a baseline.")
        st.info("Click 'Continue to Assessment' to begin your new assessment.")

# Navigation buttons at bottom
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("← Back to Home", key="back_bottom"):
        reset_session_timer()
        st.switch_page("streamlit_app.py")
with col3:
    if st.button("Continue to Assessment →", type="primary"):
        reset_session_timer()
        st.switch_page("pages/12_Assess_&_Review.py")