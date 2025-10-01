from shared import *
import io

st.title("Create a Report")

# Provide immediate option to return home
col1, col2, col3 = st.columns([1, 4, 1])
with col3:
    if st.button("Return to Home", key="top_home_button"):
        st.switch_page("streamlit_app.py")
        st.stop()

# Clear the cache when entering this page
st.cache_data.clear()

#-----------------------------------------------------------------------------------------
# Load the assessment data from airtable

# Load secrets
api_key = st.secrets["general"]["airtable_api_key"]
base_id = st.secrets["general"]["airtable_base_id"]
table_name = st.secrets["general"]["airtable_table_data"]

# load airtable data
air_data, _ = load_airtable(table_name, base_id, api_key, False)

# Initialize session state if needed
if "mode" not in st.session_state:
    st.warning("Please start from the home page to set your user role.")
    st.stop()

if air_data.empty:
    st.warning("No records found in the Airtable table.")

#-----------------------------------------------------------------------------------------
# filter the assessment data based on the user role

# if REVIEWER, then only show assessments associated with the reviewer
if st.session_state.mode == "REVIEWER":
    # Get reviewer ID (might be in a tuple)
    reviewer_id = st.session_state.reviewer_id[0] if isinstance(st.session_state.reviewer_id, (list, tuple)) else st.session_state.reviewer_id
    # Filter records where reviewer is in the REVIEWER field
    air_data = air_data[air_data["REVIEWER"].apply(
        lambda x: reviewer_id in x if isinstance(x, (list, tuple)) else x == reviewer_id
    )]

# if ASSESSOR, then only show assessments associated with the assessor
if st.session_state.mode == "ASSESSOR":
    # Get assessor ID (might be in a tuple)
    assessor_id = st.session_state.assessor_id[0] if isinstance(st.session_state.assessor_id, (list, tuple)) else st.session_state.assessor_id
    # Filter records where assessor is in the ASSESSOR field
    air_data = air_data[air_data["ASSESSOR"].apply(
        lambda x: assessor_id in x if isinstance(x, (list, tuple)) else x == assessor_id
    )]

#-----------------------------------------------------------------------------------------
# Use a pulldown menu to select the assessment to be reported on

# Role-specific assessment selection
if st.session_state.mode == "REVIEWER":
    assessment_names = air_data['Name']
    if assessment_names.empty:
        st.warning("No available assessments to report for you as a REVIEWER.")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Return to Home"):
                st.switch_page("streamlit_app.py")
        st.stop()
    selected_assessment = st.selectbox('Select an assessment for reporting:', options=assessment_names)

elif st.session_state.mode == "ASSESSOR":
    assessment_names = air_data['Name']
    if assessment_names.empty:
        st.warning("No available assessments to report for you as an ASSESSOR.")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Return to Home"):
                st.switch_page("streamlit_app.py")
        st.stop()
    selected_assessment = st.selectbox('Select an assessment for reporting:', options=assessment_names)

else:
    st.warning("Unknown mode.")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Return to Home"):
            st.switch_page("streamlit_app.py")
    st.stop()

# Don't run report immediately after selection!
# Instead, wait for user to click a button

if not selected_assessment:
    st.info("Please select an assessment to enable report generation.")
    st.stop()

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Generate Report"):
        pass  # Continue with report generation
    else:
        st.stop()
        
with col2:
    if st.button("Return to Home"):
        st.switch_page("streamlit_app.py")
        st.stop()

# Filter for chosen assessment
filtered_data = air_data.loc[air_data["Name"] == selected_assessment]
if filtered_data.empty:
    st.warning("No data found for the selected assessment.")
    st.stop()

with st.spinner("Generating your report, please wait..."):
    #-----------------------------------------------------------------------------------------
    # Prepare the report

    # Helper function to get name from ID
    def get_name_from_id(table_df, record_id, name_type='single'):
        if isinstance(record_id, (list, tuple)):
            record_id = record_id[0]
        matches = table_df[table_df['id'] == record_id]
        if matches.empty:
            return record_id
            
        row = matches.iloc[0]
        if name_type == 'single':
            return row['Name']
        elif name_type == 'full':
            return f"{row['First Name']} {row['Last Name']}"
        return record_id

    # Load ventures table for name lookups
    table_name = st.secrets["general"]["airtable_table_ventures"]
    air_ventures, _ = load_airtable(table_name, base_id, api_key, False)
    
    # Load assessors and reviewers tables
    table_name = st.secrets["general"]["airtable_table_assessors"]
    air_assessors, _ = load_airtable(table_name, base_id, api_key, False)
    table_name = st.secrets["general"]["airtable_table_reviewers"]
    air_reviewers, _ = load_airtable(table_name, base_id, api_key, False)

    # Load secrets
    
    #-----------------------------------------------------------------------------------------
    # Prepare the report

    # Load secrets
    api_key = st.secrets["general"]["airtable_api_key"]
    base_id = st.secrets["general"]["airtable_base_id"]
    table_name = st.secrets["general"]["airtable_table_assessment"]

    # load airtable assessment
    air_assessment, _ = load_airtable(table_name, base_id, api_key, False)

    # Load secrets for milestones
    api_key = st.secrets["general"]["airtable_api_key"]
    base_id = st.secrets["general"]["airtable_base_id"]
    table_name = st.secrets["general"]["airtable_table_milestones"]

    # load airtable milestones
    air_milestones, _ = load_airtable(table_name, base_id, api_key, False)

    # Initialize arrays with correct dimensions from shared configuration
    st.session_state.QA = np.zeros((num_dims, numQ), dtype=bool)
    st.session_state.QR = np.zeros((num_dims, numQ), dtype=bool)

    # DIMENSION THE REPORT
letter_width = 8.5
letter_height = 11
margin = 0.5

# Set figure size to letter dimensions
fig = plt.figure(figsize=(letter_width, letter_height))

# Axes covering the area within margins, using inches as coordinates
ax = fig.add_axes([
    margin / letter_width,         # left as fraction
    margin / letter_height,        # bottom as fraction
    (letter_width-2*margin) / letter_width,   # width as fraction
    (letter_height-2*margin) / letter_height  # height as fraction
])

# Set axis limits so (0,0) is the lower left inside margin
ax.set_xlim(0, letter_width-2*margin)
ax.set_ylim(0, letter_height-2*margin)

# Hide axes and labels
ax.set_axis_off()


# HEADER 

ax.text(7.5/2, 10.25, "Impact Readiness Level\u2122", fontsize=12, ha='center', va='bottom', fontweight='bold')

ax.text(0.00, 9.9, "Venture:", fontsize=12, ha='left', va='bottom', fontweight='normal')
ax.text(0.00, 9.65, "ASSESSOR:", fontsize=12, ha='left', va='bottom', fontweight='normal')
ax.text(0.00, 9.4, "REVIEWER:", fontsize=12, ha='left', va='bottom', fontweight='normal')

ax.text(1.0, 9.9, get_name_from_id(air_ventures, air_data.iloc[0]["Venture"], 'single'), fontsize=12, ha='left', va='bottom', fontweight='bold')

# Add ASSESSOR name and symbol
assessor_name = get_name_from_id(air_assessors, air_data.iloc[0]["ASSESSOR"], 'full')
ax.text(1.0, 9.65, assessor_name, fontsize=12, ha='left', va='bottom', fontweight='bold')
# Add circle symbol after name
name_width = len(assessor_name) * 0.07  # Approximate width of text
circle = patches.Circle((1.0 + name_width + 0.1, 9.63), radius=0.06, facecolor='black', edgecolor='black', lw=1)
ax.add_patch(circle)

# Add REVIEWER name and symbol
reviewer_name = get_name_from_id(air_reviewers, air_data.iloc[0]["REVIEWER"], 'full')
ax.text(1.0, 9.4, reviewer_name, fontsize=12, ha='left', va='bottom', fontweight='bold')
# Add diamond symbol after name
name_width = len(reviewer_name) * 0.07  # Approximate width of text
diamond_half = 0.06 * 1.2  # Same size as in matrix
diamond = patches.Polygon([
    (1.0 + name_width + 0.1, 9.4 + diamond_half),          # top
    (1.0 + name_width + 0.1 + diamond_half, 9.4),          # right
    (1.0 + name_width + 0.1, 9.4 - diamond_half),          # bottom
    (1.0 + name_width + 0.1 - diamond_half, 9.4),          # left
], closed=True, facecolor='black', edgecolor='black', lw=1)
ax.add_patch(diamond)

ax.text(3.75, 9.9, "Project / Product:", fontsize=12, ha='left', va='bottom', fontweight='normal')
ax.text(3.75, 9.65, "Date:", fontsize=12, ha='left', va='bottom', fontweight='normal')
ax.text(3.75, 9.4, "Date:", fontsize=12, ha='left', va='bottom', fontweight='normal')

# Load projects table for project name lookup
table_name = st.secrets["general"]["airtable_table_projects"]
air_projects, _ = load_airtable(table_name, base_id, api_key, False)
project_name = get_name_from_id(air_projects, air_data.iloc[0]["Project"], 'single')
ax.text(5.75, 9.9, project_name, fontsize=12, ha='left', va='bottom', fontweight='bold')

# Convert dates to abbreviated month format
def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d-%b-%Y')  # This will show like "29-SEP-2025"
    except:
        return date_str

ax.text(5.75, 9.65, format_date(air_data.iloc[0]["Assess_date"]), fontsize=12, ha='left', va='bottom', fontweight='bold')
ax.text(5.75, 9.4, format_date(air_data.iloc[0]["Review_date"]), fontsize=12, ha='left', va='bottom', fontweight='bold')


# MATRIX

n_rows = numQ
n_cols = num_dims

dy =  7.15 / n_cols
dx = dy

# Iterate over rows (questions 0 to numQ-1)
for i in range(n_rows):
    y0 = (9.2-n_rows*dy) + i*dy    
    cy = y0 + dy / 2
    ax.text(0, cy, i, fontsize=12, ha='left', va='center', fontweight='bold')

    # Iterate over columns (dimensions 0 to num_dims-1)
    for dim in range(n_cols): 
        x0 = 0.3 + dim*dx   

        # look into the assessment table to determine what milestone is associated

        # load the ASSESSOR response
        field_name = f"QA_{i:02d}_{dim}"
        if field_name in air_data.columns:
            st.session_state.QA[dim, i] = bool(air_data.iloc[0][field_name])
        else:
            st.session_state.QA[dim, i] = False

        # load the REVIEWER response
        field_name = f"QR_{i:02d}_{dim}"
        if field_name in air_data.columns:
            st.session_state.QR[dim, i] = bool(air_data.iloc[0][field_name])
        else:
            st.session_state.QR[dim, i] = False

        # DRAW THE SQUARE
        
        try:
            # For matrix position (i,dim):
            # - i is the question number (0-9)
            # - dim is the dimension (0-15)
            # - Use row 'dim' in assessment table (because rows are dimensions)
            # - Use column 'Qi Milestone' (because columns are questions)
            milestone_field = f"Q{i} Milestone"  # Column for this question number
            milestone_id = air_assessment.iloc[dim][milestone_field]  # Get from dimension's row
            
            if isinstance(milestone_id, (list, tuple)):
                milestone_id = milestone_id[0]
            
            # Look up the milestone color
            matching_milestones = air_milestones.loc[air_milestones["id"] == milestone_id]
            
            if matching_milestones.empty:
                color = '#FFFFFF'
            else:
                raw_color = matching_milestones.iloc[0]["Color"]
                color = '#FFFFFF' if pd.isna(raw_color) or not raw_color else (raw_color if raw_color.startswith('#') else f"#{raw_color}")
        except Exception as e:
            color = '#FFFFFF'

        rect = patches.Rectangle((x0, y0), dx, dy, facecolor=color, edgecolor='none', lw=1)
        ax.add_patch(rect)

        # Center of the square
        cx = x0 + dx / 2

        # Draw centered circle
        radius = 0.06  # scales circle relative to square size
        if st.session_state.QA[dim, i] == True:
            circle = patches.Circle((cx, cy-radius), radius, facecolor='black', edgecolor='black', lw=1)
        else:
            circle = patches.Circle((cx, cy-radius), radius, facecolor='white', edgecolor='black', lw=1)
        ax.add_patch(circle)

        # Draw centered diamond
        diamond_half = radius*1.2  # scales diamond relative to circle size
        if st.session_state.QR[dim, i] == True:
            diamond = patches.Polygon([
                (cx, cy + diamond_half+diamond_half),   # top
                (cx + diamond_half, cy+diamond_half),   # right
                (cx, cy - diamond_half+diamond_half),   # bottom
                (cx - diamond_half, cy+diamond_half),   # left
            ], closed=True, facecolor='black', edgecolor='black', lw=1)
        else:
            diamond = patches.Polygon([
                (cx, cy + diamond_half+diamond_half),   # top
                (cx + diamond_half, cy+diamond_half),   # right
                (cx, cy - diamond_half+diamond_half),   # bottom
                (cx - diamond_half, cy+diamond_half),   # left
            ], closed=True, facecolor='white', edgecolor='black', lw=1)
        ax.add_patch(diamond)

# After all squares, circles, and diamonds are drawn, add labels in a separate loop
if i == n_rows - 1 and dim == n_cols - 1:  # After completing all rows and columns
    # Calculate the y position for labels (based on bottom row position)
    bottom_y = (9.2-n_rows*dy)  # y position of top row
#    bottom_y = bottom_y + (numQ-1)*dy  # Move to last row
    label_y = bottom_y - 0.1  # Position below the last row
    
    # Add labels for all columns
    for label_dim in range(n_cols):
        # Calculate x position for this dimension (center of square)
        x0 = 0.3 + label_dim*dx
        x_text = x0 + 0.625*dx  # Center of the rectangle (same as cx calculation above)
        
        # Get abbreviation from assessment table
        dimension_label = air_assessment.iloc[label_dim]["Abbreviation"]
        
        # Add rotated text, aligned to end at center of rectangle
        ax.text(x_text, label_y, dimension_label, 
                rotation=60,  # 45-degree angle
                ha='right',   # Right-align text
                va='top',     # Align to top of text box
                fontsize=11)   # Smaller font for long labels


st.pyplot(fig)

# Create columns for the action buttons
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    # Create PDF in memory
    pdf_buffer = io.BytesIO()
    plt.savefig(pdf_buffer, format='pdf', bbox_inches='tight')
    pdf_buffer.seek(0)
    
    # Create download button
    if st.download_button(
        label="Save as PDF",
        data=pdf_buffer,
        file_name=f"IRL_Report_{selected_assessment}.pdf",
        mime="application/pdf",
        key="pdf_download"
    ):
        plt.close()

with col3:
    if st.button("Return to Home", key="bottom_home_button"):
        st.switch_page("streamlit_app.py")

# Add some spacing before the next element
st.write("")
    