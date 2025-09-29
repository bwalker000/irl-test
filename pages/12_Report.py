from shared import *

st.title("Create a Report")

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

# if REVIEWER, filter for assessments where we are listed as REVIEWER

if air_data.empty:
    st.warning("No records found in the Airtable table.")

#-----------------------------------------------------------------------------------------
# filter the assessment data based on the user role

# if REVIEWER, then only show assessments associated with the reviewer
if st.session_state.mode == "REVIEWER":
    # Debug output
    st.write("Reviewer ID:", st.session_state.reviewer_id)
    
    # Get reviewer ID (might be in a tuple)
    reviewer_id = st.session_state.reviewer_id[0] if isinstance(st.session_state.reviewer_id, (list, tuple)) else st.session_state.reviewer_id
    st.write("Processed Reviewer ID:", reviewer_id)
    
    # Show what's in the REVIEWER column
    st.write("REVIEWER column in data:")
    st.write(air_data["REVIEWER"].head())
    
    # Filter records where reviewer is in the REVIEWER field
    air_data = air_data[air_data["REVIEWER"].apply(
        lambda x: reviewer_id in x if isinstance(x, (list, tuple)) else x == reviewer_id
    )]
    
    st.write("Records after filtering:", len(air_data))

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
    def get_name_from_id(table_df, record_id, name_field='Name'):
        if isinstance(record_id, (list, tuple)):
            record_id = record_id[0]
        st.write(f"Looking up ID: {record_id}")
        st.write(f"Available columns: {table_df.columns.tolist()}")
        matches = table_df[table_df['id'] == record_id]
        if matches.empty:
            st.write(f"No matches found for ID {record_id}")
            return record_id
        st.write(f"Found match: {matches.iloc[0].to_dict()}")
        if name_field not in matches.columns:
            st.write(f"'{name_field}' column not found in table")
            return record_id
        return matches.iloc[0][name_field]

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

    # Diagnostic information
    st.write("### Debug Information")
    st.write("Assessment Table Structure:")
    st.write(f"- Number of rows: {air_assessment.shape[0]}")
    st.write(f"- Columns: {air_assessment.columns.tolist()}")

    st.write("\nMilestones Table Structure:")
    st.write(f"- Number of rows: {air_milestones.shape[0]}")
    st.write(f"- Columns: {air_milestones.columns.tolist()}")
    
    # Show first milestone reference and lookup
    if not air_assessment.empty:
        first_milestone = air_assessment.iloc[0]["Q0 Milestone"]
        st.write("\nExample Milestone Lookup:")
        st.write(f"- First milestone ID from assessment: {first_milestone}")
        matching = air_milestones.loc[air_milestones["id"] == first_milestone]
        st.write(f"- Found in milestones table: {not matching.empty}")
        if not matching.empty:
            st.write(f"- Color value: {matching.iloc[0]['Color']}")

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

ax.text(0.00, 9.9, "Venture:", fontsize=12, ha='left', va='bottom', fontweight='bold')
ax.text(0.00, 9.65, "ASSESSOR:", fontsize=12, ha='left', va='bottom', fontweight='bold')
ax.text(0.00, 9.4, "REVIEWER:", fontsize=12, ha='left', va='bottom', fontweight='bold')

ax.text(2.0, 9.9, get_name_from_id(air_ventures, air_data.iloc[0]["Venture"], 'Venture Name'), fontsize=12, ha='left', va='bottom', fontweight='bold')
ax.text(2.0, 9.65, get_name_from_id(air_assessors, air_data.iloc[0]["ASSESSOR"], 'Full Name'), fontsize=12, ha='left', va='bottom', fontweight='bold')
ax.text(2.0, 9.4, get_name_from_id(air_reviewers, air_data.iloc[0]["REVIEWER"], 'Full Name'), fontsize=12, ha='left', va='bottom', fontweight='bold')

ax.text(3.75, 9.9, "Project / Product:", fontsize=12, ha='left', va='bottom', fontweight='bold')
ax.text(3.75, 9.65, "Date:", fontsize=12, ha='left', va='bottom', fontweight='bold')
ax.text(3.75, 9.4, "Date:", fontsize=12, ha='left', va='bottom', fontweight='bold')

ax.text(5.75, 9.9, air_data.iloc[0]["Project"], fontsize=12, ha='left', va='bottom', fontweight='bold')

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

dx =  7 / n_cols
dy = dx

for dim in range(n_rows):

    y0 = (9-n_rows*dy) + dim*dy    
    cy = y0 + dy / 2
    ax.text(0, cy, dim, fontsize=12, ha='left', va='center', fontweight='bold')

    for i in range(numQ):  # Use numQ instead of n_cols to ensure we only go 0-9
        x0 = 0.3 + i*dx   

        # look into the assessment table to determine what milestone is associated

        # load the ASSESSOR response
        field_name = f"QA_{dim:02d}_{i}"
        if field_name in air_data.columns:
            st.session_state.QA[dim, i] = bool(air_data.iloc[0][field_name])
        else:
            st.session_state.QA[dim, i] = False

        # load the REVIEWER response
        field_name = f"QR_{dim:02d}_{i}"
        if field_name in air_data.columns:
            st.session_state.QR[dim, i] = bool(air_data.iloc[0][field_name])
        else:
            st.session_state.QR[dim, i] = False

        # DRAW THE SQUARE

        # Add code to accumulate each milestone

        try:
            # find the milestone associated with this particular question
            milestone = f"Q{i} Milestone"
            milestone_id = air_assessment.iloc[i][milestone]
            matching_milestones = air_milestones.loc[air_milestones["id"] == milestone_id]
            
            if matching_milestones.empty:
                color = '#FFFFFF'  # Default to white if milestone not found
            else:
                color = matching_milestones.iloc[0]["Color"]
        except Exception as e:
            st.error(f"Error processing milestone {i}: {str(e)}")
            color = '#FFFFFF'  # Default to white on error

        rect = patches.Rectangle((x0, y0), dx, dy, facecolor=color, edgecolor='black', lw=1)
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


st.pyplot(fig)

#plt.show()

# Save as PDF
# plt.savefig('letter_figure.pdf', bbox_inches='tight')
# plt.close()



# consider saving the report to airtable


# display the pdf



# allow the user to print or save the report

# UI to allow creation of another report, return to home, other TBD




if st.button("Home"):
    st.switch_page("streamlit_app.py")
    