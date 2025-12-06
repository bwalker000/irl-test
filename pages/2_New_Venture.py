from shared import *
from shared import check_session_timeout, reset_session_timer
from pyairtable import Api

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

# Project creation section
st.subheader("Create New Project")
st.info("A new project will be created for this venture.")

project_name = st.text_input(
    "Project Name*",
    placeholder="Enter the project name",
    help="Required field"
)

project_description = st.text_area(
    "Project Description",
    placeholder="Enter a description of the project (optional)",
    help="Optional field"
)

# Assessor creation section
st.subheader("Assessor Assignment")

assessor_choice = st.radio(
    "Choose assessor option:",
    ["Create new assessor", "Reviewer-only venture (no assessor)"],
    help="Select whether this venture will have an assessor or be reviewer-only"
)

new_assessor_first = ""
new_assessor_last = ""
new_assessor_email = ""
new_assessor_phone = ""

if assessor_choice == "Create new assessor":
    st.info("A new assessor will be created for this venture. You will be automatically assigned as the reviewer.")
    
    # New assessor form
    st.write("**New Assessor Information**")
    col1, col2 = st.columns(2)
    with col1:
        new_assessor_first = st.text_input("First Name*", placeholder="Enter first name")
        new_assessor_email = st.text_input("Email*", placeholder="Enter email address")
    with col2:
        new_assessor_last = st.text_input("Last Name*", placeholder="Enter last name")
        new_assessor_phone = st.text_input("Phone", placeholder="Enter phone number (optional)")
else:
    st.info("This venture will be reviewer-only. No assessor will be assigned. You will perform independent reviews for this venture.")

# Navigation buttons
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("← Cancel"):
        reset_session_timer()
        st.switch_page("pages/2_Reviewer_Home.py")

with col3:
    # Check if all required fields are filled
    submit_disabled = (not venture_name or not venture_name.strip() or
                      not project_name or not project_name.strip())
    
    if assessor_choice == "Create new assessor":
        submit_disabled = submit_disabled or (
            not new_assessor_first or not new_assessor_first.strip() or
            not new_assessor_last or not new_assessor_last.strip() or
            not new_assessor_email or not new_assessor_email.strip()
        )
    
    if st.button("Submit →", type="primary", disabled=submit_disabled):
        reset_session_timer()
        
        # Validate venture name
        if not venture_name.strip():
            st.error("Venture name is required.")
            st.stop()
            
        # Validate project name
        if not project_name.strip():
            st.error("Project name is required.")
            st.stop()
        
        # Validate assessor fields if creating assessor
        if assessor_choice == "Create new assessor":
            if not new_assessor_first.strip() or not new_assessor_last.strip() or not new_assessor_email.strip():
                st.error("Assessor First Name, Last Name, and Email are required.")
                st.stop()
        
        # Check for duplicate venture names within the support organization
        duplicate_check = support_org_ventures[support_org_ventures['Name'].str.lower() == venture_name.strip().lower()]
        if not duplicate_check.empty:
            st.error(f"A venture named '{venture_name.strip()}' already exists for this support organization. Please use a different name.")
            st.stop()
        
        try:
            assessor_id = None
            
            # Initialize Airtable API
            api = Api(api_key)
            base = api.base(base_id)
            
            # Handle assessor creation if needed
            if assessor_choice == "Create new assessor":
                # Load assessors table to check for duplicate email
                table_name = st.secrets["general"]["airtable_table_assessors"]
                air_assessors, _ = load_airtable(table_name, base_id, api_key, False)
                
                # Check for duplicate assessor email
                email_check = air_assessors[air_assessors['Email'].str.lower() == new_assessor_email.strip().lower()]
                if not email_check.empty:
                    st.error(f"An assessor with email '{new_assessor_email.strip()}' already exists. Please use a different email.")
                    st.stop()
                
                # Create new assessor record
                new_assessor_data = {
                    "First Name": new_assessor_first.strip(),
                    "Last Name": new_assessor_last.strip(),
                    "Email": new_assessor_email.strip(),
                    "Organization": [support_org_id]
                }
                
                if new_assessor_phone and new_assessor_phone.strip():
                    new_assessor_data["Phone"] = new_assessor_phone.strip()
                
                assessors_table = base.table(st.secrets["general"]["airtable_table_assessors"])
                created_assessor = assessors_table.create(new_assessor_data)
                assessor_id = created_assessor['id']
                
                st.success(f"✅ New assessor '{new_assessor_first} {new_assessor_last}' created successfully!")
            
            # Create new project record (without Support Organization field)
            new_project_data = {
                "Name": project_name.strip()
            }
            
            if project_description and project_description.strip():
                new_project_data["Description"] = project_description.strip()
            
            projects_table = base.table(st.secrets["general"]["airtable_table_projects"])
            created_project = projects_table.create(new_project_data)
            project_id = created_project['id']
            
            st.success(f"✅ Project '{project_name.strip()}' created successfully!")
            
            # Prepare the venture record for Airtable
            new_venture = {
                "Name": venture_name.strip(),
                "Support Organization": [support_org_id],
                "REVIEWER": [reviewer_id],  # Current reviewer
                "Projects": [project_id]    # Link to newly created project
            }
            
            # Only add assessor if one was created
            if assessor_id:
                new_venture["ASSESSOR"] = [assessor_id]  # Use correct field name "ASSESSOR"
            
            # Create the venture record in Airtable
            ventures_table = base.table(st.secrets["general"]["airtable_table_ventures"])
            created_record = ventures_table.create(new_venture)
            
            # Update project to link back to venture
            projects_table.update(project_id, {"Venture": [created_record['id']]})
            
            st.success(f"✅ Venture '{venture_name.strip()}' created successfully!")
            st.success(f"✅ You have been assigned as the reviewer for this venture.")
            
            if assessor_choice == "Reviewer-only venture (no assessor)":
                st.info("ℹ️ This venture is set up for independent reviews only (no assessor assigned).")
            
            # Set a flag to indicate successful creation
            st.session_state.venture_created = True
            st.rerun()  # Rerun to show the success state
            
        except Exception as e:
            st.error(f"Failed to create venture: {str(e)}")
            st.error("Please try again or contact support if the problem persists.")

# Show success message and return button if venture was created
if st.session_state.get('venture_created', False):
    st.success("🎉 **Venture created successfully!**")
    st.info("Your new venture and project are now ready for assessments and reviews.")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Return to Reviewer Home", type="primary"):
            # Clear the creation flag
            if 'venture_created' in st.session_state:
                del st.session_state.venture_created
            reset_session_timer()
            st.switch_page("pages/2_Reviewer_Home.py")

# Add help text at bottom
st.divider()
st.caption("* Required fields")
