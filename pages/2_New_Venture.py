from shared import *
from shared import check_session_timeout, reset_session_timer
from pyairtable import Table

display_logo()

# Check for session timeout at page entry
check_session_timeout()

st.title("Add New Venture")

# Initialize session state
if 'mode' not in st.session_state or st.session_state.mode != 'REVIEWER':
    st.error("This page is only accessible to reviewers.")
    st.switch_page("streamlit_app.py")

if 'reviewer_id' not in st.session_state:
    st.error("Reviewer information not found. Please return to home.")
    if st.button("Return to Home"):
        st.switch_page("streamlit_app.py")
    st.stop()

# Load secrets
api_key = st.secrets["general"]["airtable_api_key"]
base_id = st.secrets["general"]["airtable_base_id"]

# Get reviewer's support organization
table_name = st.secrets["general"]["airtable_table_reviewers"]
air_reviewers, _ = load_airtable(table_name, base_id, api_key, False)

reviewer_id = st.session_state.reviewer_id[0] if isinstance(st.session_state.reviewer_id, (list, tuple)) else st.session_state.reviewer_id
reviewer_record = air_reviewers[air_reviewers['id'] == reviewer_id]

if reviewer_record.empty:
    st.error("Reviewer record not found.")
    if st.button("Return to Home"):
        st.switch_page("streamlit_app.py")
    st.stop()

# Get support organization ID and name
support_org_id = reviewer_record.iloc[0].get('Support Organization')
if isinstance(support_org_id, (list, tuple)):
    support_org_id = support_org_id[0]

# Load support organization information
table_name = st.secrets["general"]["airtable_table_support"]
air_support_orgs, _ = load_airtable(table_name, base_id, api_key, False)
support_org_record = air_support_orgs[air_support_orgs['id'] == support_org_id]

if support_org_record.empty:
    st.error("Support Organization not found.")
    if st.button("Return to Home"):
        st.switch_page("streamlit_app.py")
    st.stop()

support_org_name = support_org_record.iloc[0]['Name']

# Display support organization name
st.info(f"**Support Organization:** {support_org_name}")

# Load existing ventures for this support organization
table_name = st.secrets["general"]["airtable_table_ventures"]
air_ventures, _ = load_airtable(table_name, base_id, api_key, False)

# Filter ventures by support organization
support_org_ventures = air_ventures[air_ventures['Support Organization'].apply(
    lambda x: support_org_id in x if isinstance(x, (list, tuple)) else x == support_org_id
)]

# Display existing ventures
if not support_org_ventures.empty:
    st.subheader("Existing Ventures")
    for idx, venture in support_org_ventures.iterrows():
        st.write(f"• **{venture['Name']}**")
    st.divider()

# Form for new venture
st.subheader("Create New Venture")

venture_name = st.text_input(
    "Venture Name*",
    placeholder="Enter the venture name",
    help="Required field"
)

st.subheader("Select or Create Reviewer")

# Load all reviewers for selection
all_reviewers = air_reviewers.copy()

# Create a display name for each reviewer
reviewer_options = []
reviewer_lookup = {}
for idx, reviewer in all_reviewers.iterrows():
    first_name = reviewer.get('First Name', '')
    last_name = reviewer.get('Last Name', '')
    email = reviewer.get('Email', '')
    display_name = f"{first_name} {last_name} ({email})"
    reviewer_options.append(display_name)
    reviewer_lookup[display_name] = reviewer['id']

# Option to select existing or create new
reviewer_choice = st.radio(
    "Choose an option:",
    ["Select existing reviewer", "Create new reviewer"],
    horizontal=True
)

selected_reviewer_id = None

if reviewer_choice == "Select existing reviewer":
    selected_reviewer_display = st.selectbox(
        "Select Reviewer*",
        options=reviewer_options,
        help="Required field"
    )
    if selected_reviewer_display:
        selected_reviewer_id = reviewer_lookup[selected_reviewer_display]
else:
    st.write("**New Reviewer Information**")
    col1, col2 = st.columns(2)
    with col1:
        new_reviewer_first = st.text_input("First Name*", placeholder="Enter first name")
        new_reviewer_email = st.text_input("Email*", placeholder="Enter email address")
    with col2:
        new_reviewer_last = st.text_input("Last Name*", placeholder="Enter last name")
        new_reviewer_phone = st.text_input("Phone", placeholder="Enter phone number (optional)")

# Navigation buttons
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("← Cancel"):
        reset_session_timer()
        st.switch_page("pages/2_Reviewer_Home.py")

with col3:
    # Determine if submit should be disabled
    submit_disabled = not venture_name or not venture_name.strip()
    
    if reviewer_choice == "Create new reviewer":
        submit_disabled = submit_disabled or not new_reviewer_first or not new_reviewer_first.strip() or \
                         not new_reviewer_last or not new_reviewer_last.strip() or \
                         not new_reviewer_email or not new_reviewer_email.strip()
    else:
        submit_disabled = submit_disabled or selected_reviewer_id is None
    
    if st.button("Submit →", type="primary", disabled=submit_disabled):
        reset_session_timer()
        
        # Validate venture name
        if not venture_name.strip():
            st.error("Venture name is required.")
            st.stop()
        
        # Check for duplicate venture names within the support organization
        duplicate_check = support_org_ventures[support_org_ventures['Name'].str.lower() == venture_name.strip().lower()]
        if not duplicate_check.empty:
            st.error(f"A venture named '{venture_name.strip()}' already exists for this support organization. Please use a different name.")
            st.stop()
        
        try:
            # Handle reviewer creation if needed
            final_reviewer_id = selected_reviewer_id
            
            if reviewer_choice == "Create new reviewer":
                # Validate new reviewer fields
                if not new_reviewer_first.strip() or not new_reviewer_last.strip() or not new_reviewer_email.strip():
                    st.error("First Name, Last Name, and Email are required for creating a new reviewer.")
                    st.stop()
                
                # Check for duplicate email
                email_check = air_reviewers[air_reviewers['Email'].str.lower() == new_reviewer_email.strip().lower()]
                if not email_check.empty:
                    st.error(f"A reviewer with email '{new_reviewer_email.strip()}' already exists. Please select the existing reviewer or use a different email.")
                    st.stop()
                
                # Create new reviewer record
                new_reviewer_data = {
                    "First Name": new_reviewer_first.strip(),
                    "Last Name": new_reviewer_last.strip(),
                    "Email": new_reviewer_email.strip(),
                    "Support Organization": [support_org_id]
                }
                
                if new_reviewer_phone and new_reviewer_phone.strip():
                    new_reviewer_data["Phone"] = new_reviewer_phone.strip()
                
                reviewers_table = Table(api_key, base_id, st.secrets["general"]["airtable_table_reviewers"])
                created_reviewer = reviewers_table.create(new_reviewer_data)
                final_reviewer_id = created_reviewer['id']
                
                st.success(f"✅ New reviewer '{new_reviewer_first} {new_reviewer_last}' created successfully!")
            
            # Prepare the venture record for Airtable
            new_venture = {
                "Name": venture_name.strip(),
                "Support Organization": [support_org_id],
                "REVIEWER": [final_reviewer_id]
            }
            
            # Create the venture record in Airtable
            ventures_table = Table(api_key, base_id, st.secrets["general"]["airtable_table_ventures"])
            created_record = ventures_table.create(new_venture)
            
            st.success(f"✅ Venture '{venture_name.strip()}' created successfully!")
            
            # Add a button to return to reviewer home
            if st.button("Return to Reviewer Home"):
                reset_session_timer()
                st.switch_page("pages/2_Reviewer_Home.py")
            
        except Exception as e:
            st.error(f"Failed to create venture: {str(e)}")
            st.error("Please try again or contact support if the problem persists.")

# Add help text at bottom
st.divider()
st.caption("* Required fields")
