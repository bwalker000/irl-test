from shared import *
# Explicitly import shared configuration
from shared import num_dims, numQ, check_session_timeout, reset_session_timer

# Clear the cache when entering this page
st.cache_data.clear()

display_logo()

# Check for session timeout at page entry
check_session_timeout()

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

    # Filter records by support organization, completed assessments only, and blank review dates
    filtered_records = air_data[air_data["Support Organization"] == st.session_state.support_id]
    
    # Only show assessments that are completed (have an Assess_date) and not yet reviewed
    filtered_records = filtered_records[
        (filtered_records["Assess_date"].notna()) &  # Must have completed assessment date
        (filtered_records["Assess_date"] != "") &    # Assessment date must not be empty
        (filtered_records["Assess_date"] != pd.NaT) &  # Assessment date must be valid
        (
            (filtered_records["Review_date"].isnull()) |  # No review date yet
            (filtered_records["Review_date"] == "") |     # Or empty review date
            (filtered_records["Review_date"] == pd.NaT)   # Or invalid review date
        )
    ]

    # Proceed with selection logic
    assessment_names = filtered_records['Name']
    if not assessment_names.empty:
        # Initialize assessment_name if it's not in session_state
        if 'assessment_name' not in st.session_state:
            st.session_state.assessment_name = assessment_names.iloc[0]
        
        selected_name = st.selectbox('Select an assessment for review:', 
                                   options=assessment_names,
                                   key='assessment_select')
        
        # Update session state with the selection
        st.session_state.assessment_name = selected_name

        # This identifies the specific assessment to be reviewed
        air_data_record = air_data.loc[air_data["Name"] == selected_name]
        
        st.session_state.assessment_record_id = air_data_record.iloc[0]["id"]  # Store the record ID for updating
        st.session_state.assessor_id = air_data_record.iloc[0]["ASSESSOR"]
        st.session_state.venture_id = air_data_record.iloc[0]["Venture"]
        st.session_state.project_id = air_data_record.iloc[0]["Project"]
        st.session_state.assess_date = air_data_record.iloc[0]["Assess_date"]  # Store original assessment date
        
        # Load assessor details only if we have a valid assessor_id
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

        # Check for existing review draft for this assessment
        draft_name = f"DRAFT - {st.session_state.venture_name} - {st.session_state.project_name}"
        existing_draft = air_data[
            (air_data['Name'] == draft_name) &
            (air_data['Review_date'].isnull() | (air_data['Review_date'] == ""))
        ]
        
        if not existing_draft.empty:
            st.info("🔄 **Found an in-progress review for this assessment!**")
            if st.button("Resume Review Draft", type="primary"):
                st.session_state.draft_record_id = existing_draft.iloc[0]['id']
        
        # Automatically initialize review data with assessment data by default
        # This eliminates duplication - reviewer starts with assessor's responses
        if 'QR' not in st.session_state or st.session_state.QR is None:
            st.session_state.QR = np.zeros((num_dims, numQ), dtype=bool)
            
            # Copy assessment data as starting point for review
            for dim in range(num_dims):
                for i in range(numQ):
                    field_name = f"QA_{dim:02d}_{i}"
                    if field_name in air_data_record.columns and pd.notna(air_data_record.iloc[0][field_name]):
                        # Start with assessor's response
                        st.session_state.QR[dim, i] = bool(air_data_record.iloc[0][field_name])
            
            # Copy assessment text comments as starting point
            st.session_state.TR = [""] * num_dims
            for dim in range(num_dims):
                field_name = f"TA_{dim:02d}"
                if field_name in air_data_record.columns and pd.notna(air_data_record.iloc[0][field_name]):
                    st.session_state.TR[dim] = air_data_record.iloc[0][field_name]
            
            st.info("✅ **Review initialized with assessment data.** You should modify responses to reflect your professional review.")
        
        # Check for previous reviews (for reference, not for copying)
        completed_reviews = air_data[
            (air_data['Venture'] == st.session_state.venture_id) &
            (air_data['Project'] == st.session_state.project_id) &
            (air_data['Review_date'].notna()) &
            (air_data['Review_date'] != "")
        ]
        
        if not completed_reviews.empty:
            st.info("📋 **Previous reviews available for reference.**")
            
            with st.expander("View previous reviews (for reference)"):
                for idx, row in completed_reviews.iterrows():
                    review_date = row.get('Review_date', 'Unknown')
                    st.write(f"• {row['Name']} (Reviewed: {review_date})")
    else:
        st.warning("No available assessments to review for your Support Organization.")
        # Reset assessment related session state
        for key in ['assessment_name', 'assessor_id', 'venture_id', 'project_id', 'assessor_first_name', 'assessor_last_name', 'venture_name', 'project_name']:
            if key in st.session_state:
                del st.session_state[key]

#---------------------------------------------------------------------------------
# Perform an independent review

elif st.session_state.review_mode == 1:
    st.write("Perform an independent review")

    # Clear any existing assessment data from previous reviews/reports
    # This ensures a clean slate for the independent review
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
        st.session_state.venture_id = air_ventures_record["id"].tolist()

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
                    st.session_state.project_id = air_projects_record["id"].tolist()
                else:
                    st.warning("No available projects for the selected Venture.")
            else:
                st.warning("No available projects for the selected Venture.")
        else:
            st.warning("Selected Venture not found.")
    else:
        st.warning("No available ventures to review for your Support Organization.")

    # After project selection, check for drafts and previous reviews
    if 'project_name' in st.session_state:
        # Check for existing independent review draft
        draft_name = f"DRAFT - {st.session_state.venture_name} - {st.session_state.project_name}"
        
        table_name = st.secrets["general"]["airtable_table_data"]
        air_data_check, _ = load_airtable(table_name, base_id, api_key, False)
        
        existing_draft = air_data_check[
            (air_data_check['Name'] == draft_name) &
            (air_data_check['Review_date'].isnull() | (air_data_check['Review_date'] == ""))
        ]
        
        if not existing_draft.empty:
            st.info("🔄 **Found an in-progress independent review!**")
            if st.button("Resume Independent Review Draft", type="primary"):
                st.session_state.draft_record_id = existing_draft.iloc[0]['id']
        
        # Check for previous independent reviews
        venture_id_to_check = st.session_state.venture_id[0] if isinstance(st.session_state.venture_id, (list, tuple)) else st.session_state.venture_id
        project_id_to_check = st.session_state.project_id[0] if isinstance(st.session_state.project_id, (list, tuple)) else st.session_state.project_id
        
        # Filter for true independent reviews only - must have valid data and be truly independent
        completed_independent_reviews = air_data_check[
            (air_data_check['Venture'].apply(lambda x: (x[0] if isinstance(x, (list, tuple)) else x) == venture_id_to_check)) &
            (air_data_check['Project'].apply(lambda x: (x[0] if isinstance(x, (list, tuple)) else x) == project_id_to_check)) &
            (air_data_check['Review_date'].notna()) &
            (air_data_check['Review_date'] != "") &
            (air_data_check['Review_date'] != pd.NaT) &
            (air_data_check['Name'].notna()) &  # Must have a valid name
            (air_data_check['Name'] != "") &    # Name cannot be empty
            (~air_data_check['Name'].str.startswith('DRAFT', na=False)) &  # Exclude DRAFT records
            (
                (air_data_check['Assess_date'].isna()) |  # No assessment date (independent)
                (air_data_check['Assess_date'] == "") |   # Or empty assessment date
                (air_data_check['Assess_date'] == pd.NaT)  # Or invalid assessment date
            ) &
            (
                (air_data_check['ASSESSOR'].isna()) |  # No assessor (independent)
                (air_data_check['ASSESSOR'] == "") |   # Or empty assessor
                (air_data_check['ASSESSOR'].apply(lambda x: len(x) == 0 if isinstance(x, (list, tuple)) and pd.notna(x) else pd.isna(x)))  # Or empty assessor list
            )
        ]
        
        # Aggressive filter: Remove records with nan/null values in critical fields
        completed_independent_reviews = completed_independent_reviews[
            (~completed_independent_reviews['Name'].isin(['nan', 'NaN', 'null', 'None'])) &
            (~completed_independent_reviews['Name'].astype(str).str.lower().isin(['nan', 'none', 'null'])) &
            (completed_independent_reviews['Name'].astype(str) != 'nan') &
            (completed_independent_reviews['Review_date'].astype(str) != 'nan') &
            (completed_independent_reviews['Review_date'] != 'NaT')
        ]
        
        # Final sanity check: only keep records where Name is actually a meaningful string
        completed_independent_reviews = completed_independent_reviews[
            completed_independent_reviews['Name'].astype(str).str.len() >= 1  # Name must be at least 1 character
        ]

        if not completed_independent_reviews.empty:
            st.info("📋 **Previous independent reviews found for this project.**")
            
            with st.expander("View previous independent reviews"):
                for idx, row in completed_independent_reviews.iterrows():
                    review_date = row.get('Review_date', 'Unknown')
                    reviewer_name = row.get('Name', 'Unknown Review')
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"• {reviewer_name} (Reviewed: {review_date})")
                    with col2:
                        if st.button("Copy Data", key=f"copy_indep_{idx}"):
                            st.session_state.copy_from_independent_id = row['id']
                            st.rerun()

            # If user clicked to copy data
            if 'copy_from_independent_id' in st.session_state:
                source_record = air_data_check[air_data_check['id'] == st.session_state.copy_from_independent_id].iloc[0]
                
                # Initialize with source data
                st.session_state.QR = np.zeros((num_dims, numQ), dtype=bool)
                
                for dim in range(num_dims):
                    for i in range(numQ):
                        field_name = f"QR_{dim:02d}_{i}"
                        if field_name in source_record.index and pd.notna(source_record[field_name]):
                            st.session_state.QR[dim, i] = bool(source_record[field_name])
                
                st.session_state.TR = [""] * num_dims
                for dim in range(num_dims):
                    field_name = f"TR_{dim:02d}"
                    if field_name in source_record.index and pd.notna(source_record[field_name]):
                        st.session_state.TR[dim] = source_record[field_name]
                
                del st.session_state.copy_from_independent_id
                st.success(f"✓ Copied data from previous independent review. Starting new review with this data as a baseline.")
                st.info("Click 'Continue to Review' to begin your new independent review.")


#---------------------------------------------------------------------------------

# Check for existing draft or completed assessment for this venture/project combination
# Only check if venture_id and project_id are available in session state
if hasattr(st.session_state, 'venture_id') and hasattr(st.session_state, 'project_id'):
    # Load air_data_check if not already loaded
    if 'air_data_check' not in locals():
        table_name = st.secrets["general"]["airtable_table_data"]
        air_data_check, _ = load_airtable(table_name, base_id, api_key, False)
    
    # Extract single ID from list if needed
    venture_id_to_check = st.session_state.venture_id[0] if isinstance(st.session_state.venture_id, (list, tuple)) else st.session_state.venture_id
    project_id_to_check = st.session_state.project_id[0] if isinstance(st.session_state.project_id, (list, tuple)) else st.session_state.project_id

    existing_draft_or_assessment = air_data_check[
        (air_data_check['Venture'].apply(lambda x: (x[0] if isinstance(x, (list, tuple)) else x) == venture_id_to_check)) &
        (air_data_check['Project'].apply(lambda x: (x[0] if isinstance(x, (list, tuple)) else x) == project_id_to_check))
    ]


# Determine if "Continue to Review" should be enabled
can_continue = False
if st.session_state.review_mode == 0:
    # For existing assessment review, need a valid assessment selection
    can_continue = (
        'assessment_name' in st.session_state and 
        st.session_state.assessment_name is not None and
        'project_name' in st.session_state
    )
elif st.session_state.review_mode == 1:
    # For independent review, need venture and project selected
    can_continue = (
        'venture_name' in st.session_state and 
        'project_name' in st.session_state
    )

# Navigation buttons in columns for consistency with other pages
col1, col2 = st.columns(2)
with col1:
    if st.button("Continue to Review", disabled=not can_continue):
        reset_session_timer()  # User is active
        st.switch_page("pages/12_Assess_&_Review.py")
with col2:
    if st.button("Home"):
        reset_session_timer()  # User is active
        st.switch_page("streamlit_app.py")
