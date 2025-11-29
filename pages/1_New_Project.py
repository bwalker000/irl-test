from shared import *
from shared import check_session_timeout, reset_session_timer
from pyairtable import Table

display_logo()

# Check for session timeout at page entry
check_session_timeout()

st.title("Add New Project")

# Initialize session state
if 'mode' not in st.session_state or st.session_state.mode != 'ASSESSOR':
    st.error("This page is only accessible to assessors.")
    st.switch_page("streamlit_app.py")

if 'assessor_id' not in st.session_state:
    st.error("Assessor information not found. Please return to home.")
    if st.button("Return to Home"):
        st.switch_page("streamlit_app.py")
    st.stop()

# Load secrets
api_key = st.secrets["general"]["airtable_api_key"]
base_id = st.secrets["general"]["airtable_base_id"]

# Get assessor's venture
table_name = st.secrets["general"]["airtable_table_assessors"]
air_assessors, _ = load_airtable(table_name, base_id, api_key, False)

assessor_id = st.session_state.assessor_id[0] if isinstance(st.session_state.assessor_id, (list, tuple)) else st.session_state.assessor_id
assessor_record = air_assessors[air_assessors['id'] == assessor_id]

if assessor_record.empty:
    st.error("Assessor record not found.")
    if st.button("Return to Home"):
        st.switch_page("streamlit_app.py")
    st.stop()

# Get venture ID and name
venture_id = assessor_record.iloc[0].get('Venture')
if isinstance(venture_id, (list, tuple)):
    venture_id = venture_id[0]

# Load venture information
table_name = st.secrets["general"]["airtable_table_ventures"]
air_ventures, _ = load_airtable(table_name, base_id, api_key, False)
venture_record = air_ventures[air_ventures['id'] == venture_id]

if venture_record.empty:
    st.error("Venture not found.")
    if st.button("Return to Home"):
        st.switch_page("streamlit_app.py")
    st.stop()

venture_name = venture_record.iloc[0]['Name']

# Display venture name
st.info(f"**Venture:** {venture_name}")

# Load existing projects for this venture
table_name = st.secrets["general"]["airtable_table_projects"]
air_projects, _ = load_airtable(table_name, base_id, api_key, False)

# Filter projects by venture
venture_projects = air_projects[air_projects['Venture'].apply(
    lambda x: venture_id in x if isinstance(x, (list, tuple)) else x == venture_id
)]

# Display existing projects
if not venture_projects.empty:
    st.subheader("Existing Projects")
    for idx, project in venture_projects.iterrows():
        st.write(f"• **{project['Name']}**")
        if 'Description' in project and pd.notna(project['Description']):
            st.write(f"  _{project['Description']}_")
    st.divider()

# Form for new project
st.subheader("Create New Project")

project_name = st.text_input(
    "Project Name*",
    placeholder="Enter the project name",
    help="Required field"
)

project_description = st.text_area(
    "Project Description",
    placeholder="Enter a description for this project (optional)",
    height=150
)

# Navigation buttons
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("← Cancel"):
        reset_session_timer()
        st.switch_page("pages/1_Assessor_Home.py")

with col3:
    submit_disabled = not project_name or not project_name.strip()
    if st.button("Submit →", type="primary", disabled=submit_disabled):
        reset_session_timer()
        
        # Validate project name
        if not project_name.strip():
            st.error("Project name is required.")
            st.stop()
        
        # Check for duplicate project names within the venture
        duplicate_check = venture_projects[venture_projects['Name'].str.lower() == project_name.strip().lower()]
        if not duplicate_check.empty:
            st.error(f"A project named '{project_name.strip()}' already exists for this venture. Please use a different name.")
            st.stop()
        
        try:
            # Prepare the record for Airtable
            new_project = {
                "Name": project_name.strip(),
                "Venture": [venture_id]  # Link to venture table
            }
            
            # Add description if provided
            if project_description and project_description.strip():
                new_project["Description"] = project_description.strip()
            
            # Create the record in Airtable
            projects_table = Table(api_key, base_id, st.secrets["general"]["airtable_table_projects"])
            created_record = projects_table.create(new_project)
            
            st.success(f"✅ Project '{project_name.strip()}' created successfully!")
            
            # Add a button to return to assessor home
            if st.button("Return to Assessor Home"):
                reset_session_timer()
                st.switch_page("pages/1_Assessor_Home.py")
            
        except Exception as e:
            st.error(f"Failed to create project: {str(e)}")
            st.error("Please try again or contact support if the problem persists.")

# Add help text at bottom
st.divider()
st.caption("* Required fields")
