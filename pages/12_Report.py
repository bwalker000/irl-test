from shared import *
import io
from draw import *

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

# Show all UI controls in one section
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    generate_report = st.button("Generate Report", disabled=(not selected_assessment))

with col2:
    # We'll populate this with the PDF button after generating the report
    pdf_placeholder = st.empty()

with col3:
    if st.button("Return to Home", key="main_home_button"):
        st.switch_page("streamlit_app.py")

if not selected_assessment or not generate_report:
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


#-----------------------------------------------------------------------------------------
# DIMENSION THE REPORT
letter_width = 8.5
letter_height = 11
margin = 0.5

font_size = 11

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

ax.text(7.5/2, 10.25, "Impact Readiness Level\u2122", fontsize=font_size, ha='center', va='bottom', fontweight='bold')

ax.text(0.00, 9.9, "Venture:", fontsize=font_size, ha='left', va='bottom', fontweight='normal')
ax.text(0.18, 9.65, "ASSESSOR:", fontsize=font_size, ha='left', va='bottom', fontweight='normal')
ax.text(0.18, 9.4, "REVIEWER:", fontsize=font_size, ha='left', va='bottom', fontweight='normal')

ax.text(1.0, 9.9, get_name_from_id(air_ventures, air_data.iloc[0]["Venture"], 'single'), fontsize=font_size, ha='left', va='bottom', fontweight='bold')

# Add ASSESSOR name and symbol
assessor_name = get_name_from_id(air_assessors, air_data.iloc[0]["ASSESSOR"], 'full')
ax.text(1.16, 9.65, assessor_name, fontsize=font_size, ha='left', va='bottom', fontweight='bold')
# Add circle symbol before ASSESSOR
circle = patches.Circle((0.08, 9.75), radius=0.06, facecolor='black', edgecolor='black', lw=1)
ax.add_patch(circle)

# Add REVIEWER name and symbol
reviewer_id = air_data.iloc[0]["REVIEWER"]
reviewer_available = False  # Track if reviewer is available for later use

if pd.notna(reviewer_id) and reviewer_id:  # Check if reviewer exists
    reviewer_name = get_name_from_id(air_reviewers, reviewer_id, 'full')
    if reviewer_name and reviewer_name != reviewer_id:  # Valid reviewer found
        ax.text(1.16, 9.4, reviewer_name, fontsize=font_size, ha='left', va='bottom', fontweight='bold')
        reviewer_available = True
    else:
        # Reviewer ID exists but no matching record found
        ax.text(1.16, 9.4, "[Pending]", fontsize=font_size, ha='left', va='bottom', fontweight='bold')
else:
    # No reviewer assigned yet
    ax.text(1.16, 9.4, "[Pending]", fontsize=font_size, ha='left', va='bottom', fontweight='bold')

# Always add diamond symbol for reviewer
diamond = draw_diamond(0.08, 9.5, 0.12, filled=True)
ax.add_patch(diamond)

ax.text(3.75, 9.9, "Project / Product:", fontsize=font_size, ha='left', va='bottom', fontweight='normal')
ax.text(3.75, 9.65, "Date:", fontsize=font_size, ha='left', va='bottom', fontweight='normal')
ax.text(3.75, 9.4, "Date:", fontsize=font_size, ha='left', va='bottom', fontweight='normal')

# Load projects table for project name lookup
table_name = st.secrets["general"]["airtable_table_projects"]
air_projects, _ = load_airtable(table_name, base_id, api_key, False)
project_name = get_name_from_id(air_projects, air_data.iloc[0]["Project"], 'single')
ax.text(5.25, 9.9, project_name, fontsize=font_size, ha='left', va='bottom', fontweight='bold')

# Convert dates to abbreviated month format
def format_date(date_str):
    try:
        if pd.isna(date_str) or not date_str:  # Handle missing dates
            return "[Pending]"
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d-%b-%Y')  # This will show like "29-SEP-2025"
    except:
        return "[Pending]"

ax.text(5.25, 9.65, format_date(air_data.iloc[0]["Assess_date"]), fontsize=font_size, ha='left', va='bottom', fontweight='bold')

# Handle review date - might be missing if no reviewer assigned yet
review_date = air_data.iloc[0].get("Review_date")
ax.text(5.25, 9.4, format_date(review_date), fontsize=font_size, ha='left', va='bottom', fontweight='bold')


# Calculate delta (sum of absolute differences between ASSESSOR and REVIEWER responses)
delta = 0
for i in range(numQ):
    for dim in range(num_dims):
        qa_field = f"QA_{i:02d}_{dim}"
        qr_field = f"QR_{i:02d}_{dim}"
        qa_value = bool(air_data.iloc[0][qa_field]) if qa_field in air_data.columns else False
        qr_value = bool(air_data.iloc[0][qr_field]) if qr_field in air_data.columns else False
        delta += abs(int(qa_value) - int(qr_value))

# MATRIX

n_rows = numQ
n_cols = num_dims

dy =  0.9 * 7.15 / n_cols       # 0.9 to reduces the size of the table
dx = dy

# Calculate total matrix width and center it on the page
page_width = letter_width - 2*margin  # Available width within margins
question_num_width = 0.3  # Width for question numbers column
matrix_width = question_num_width + n_cols * dx  # Total width of matrix
start_x = (page_width - matrix_width) / 2  # Center the matrix

# Iterate over rows (questions 0 to numQ-1)
for i in range(n_rows):
    y0 = (9.3-n_rows*dy) + i*dy    
    cy = y0 + dy / 2
    ax.text(start_x, cy, i, fontsize=font_size, ha='left', va='center', fontweight='bold')

    # Iterate over columns (dimensions 0 to num_dims-1)
    for dim in range(n_cols): 
        x0 = start_x + question_num_width + dim*dx   

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
        if st.session_state.QR[dim, i] == True:
            diamond = draw_diamond(cx, cy+radius*1.2, 2*radius, filled=True)
            ax.add_patch(diamond)
        else:
            diamond = draw_diamond(cx, cy+radius*1.2, 2*radius, filled=False)
            ax.add_patch(diamond)

# After all squares, circles, and diamonds are drawn, add labels in a separate loop
if i == n_rows - 1 and dim == n_cols - 1:  # After completing all rows and columns
    # Calculate the y position for labels (based on bottom row position)
    bottom_y = (9.3-n_rows*dy)  # y position of top row
#    bottom_y = bottom_y + (numQ-1)*dy  # Move to last row
    label_y = bottom_y - 0.1  # Position below the last row
    
    # Add labels for all columns
    for label_dim in range(n_cols):
        # Calculate x position for this dimension (center of square)
        x0 = start_x + question_num_width + label_dim*dx
        x_text = x0 + 0.625*dx  # Center of the rectangle (same as cx calculation above)
        
        # Get abbreviation from assessment table
        dimension_label = air_assessment.iloc[label_dim]["Abbreviation"]
        
        # Add rotated text, aligned to end at center of rectangle
        ax.text(x_text, label_y, dimension_label, 
                rotation=60,  # 45-degree angle
                ha='right',   # Right-align text
                va='top',     # Align to top of text box
                fontsize=10)   # Smaller font for long labels

# --------------------------------------------------------------------------------------
    # Define key table variables first (needed for delta box positioning)
    key_text_width = 1.9
    key_num_width = 0.3
    dx = key_text_width + key_num_width
    key_x0 = 0.4
    dy = 0.2

    # Now add delta box below the labels (aligned with TECHNOLOGY focus box)
    delta_box_width = 1.2
    delta_box_x = key_x0  # Align with left edge of key table (same as TECHNOLOGY focus)
    delta_box_y = label_y - 1.2  # Position below the labels
    delta_box_height = dy  # Use same height as key table boxes
    
    # Draw main box
    rect = patches.Rectangle((delta_box_x, delta_box_y), delta_box_width, delta_box_height, 
                           facecolor='none', edgecolor='black', lw=1)
    ax.add_patch(rect)
    
    # Draw shaded value box
    delta_value_box_width = 0.4
    delta_value_box = patches.Rectangle((delta_box_x + delta_box_width - delta_value_box_width, delta_box_y), 
                                delta_value_box_width, delta_box_height,
                                facecolor='#F0F0F0', edgecolor='black', lw=1)
    ax.add_patch(delta_value_box)
    
    # Add text
    ax.text(delta_box_x + 0.1, delta_box_y + delta_box_height/2, "Delta:", 
            fontsize=font_size, ha='left', va='center')
    
    # Show X if no reviewer available, otherwise show delta value
    delta_display = "X" if not reviewer_available else str(delta)
    ax.text(delta_box_x + delta_box_width - delta_value_box_width/2, delta_box_y + delta_box_height/2, delta_display, 
            fontsize=font_size, ha='center', va='center')

#------------------------------------------------------------------------------------------
# Draw the "Key" Table

    # Calculate total key table width and center it
    key_table_total_width = 3 * dx  # Three columns of boxes
    key_x0 = (page_width - key_table_total_width) / 2  # Center the key table
    
    # Use the key table position for delta box
    key_y0 = delta_box_y
    
    # ************************************************************************************
    # draw the "VENTURE Focus" box
    x = key_x0 + 2*dx
    y = key_y0
    rect = patches.Rectangle((x, y), dx, dy, facecolor='none', edgecolor='black', lw=1)
    ax.add_patch(rect)
    ax.text(x + dx/2, y + dy/2, "VENTURE focus", fontsize=font_size, ha='center', va='center', fontweight='bold')

    # draw the boxes for dimensions 6 to 15
    for dim in range(6, 16):
        x = key_x0 + 2*dx
        y = key_y0 - (dim-5)*dy
        rect = patches.Rectangle((x, y), key_text_width, dy, facecolor='none', edgecolor='black', lw=1)
        ax.add_patch(rect)
        # Get the dimension name from assessment table and add it to the rectangle
        dimension_name = air_assessment.iloc[dim]["Dimension"]
        ax.text(x + 0.1, y + dy/2, dimension_name, fontsize=font_size, ha='left', va='center')
        rect = patches.Rectangle((x + key_text_width, y), key_num_width, dy, facecolor='#F0F0F0', edgecolor='black', lw=1)
        ax.add_patch(rect)

        # Find the highest question number with a positive reviewer response for this dimension
        max_positive_q = -1  # Initialize to -1 to handle case where no positives found
        if reviewer_available:  # Only calculate if reviewer is available
            for q in range(numQ):
                qr_field = f"QR_{q:02d}_{dim}"
                qr_value = bool(air_data.iloc[0][qr_field]) if qr_field in air_data.columns else False
                if qr_value:
                    max_positive_q = q

        # Show X if no reviewer, otherwise show max question number if positive responses found
        if not reviewer_available:
            ax.text(x + key_text_width + key_num_width/2, y + dy/2, 
                   "X", fontsize=font_size, ha='center', va='center')
        elif max_positive_q >= 0:
            ax.text(x + key_text_width + key_num_width/2, y + dy/2, 
                   str(max_positive_q), fontsize=font_size, ha='center', va='center')

    # ************************************************************************************
    # draw the "PRODUCT Focus" box
    x = key_x0 + dx
    y = key_y0 - 3*dy
    rect = patches.Rectangle((x, y), dx, dy, facecolor='none', edgecolor='black', lw=1)
    ax.add_patch(rect)
    ax.text(x + dx/2, y + dy/2, "PRODUCT focus", fontsize=font_size, ha='center', va='center', fontweight='bold')

    # draw the boxes for dimensions 2 to 5
    for dim in range(2, 6):
        x = key_x0 + dx
        y = key_y0 - (dim+2)*dy
        rect = patches.Rectangle((x, y), key_text_width, dy, facecolor='none', edgecolor='black', lw=1)
        ax.add_patch(rect)
        # Get the dimension name from assessment table and add it to the rectangle
        dimension_name = air_assessment.iloc[dim]["Dimension"]
        ax.text(x + 0.1, y + dy/2, dimension_name, fontsize=font_size, ha='left', va='center')
        rect = patches.Rectangle((x + key_text_width, y), key_num_width, dy, facecolor='#F0F0F0', edgecolor='black', lw=1)
        ax.add_patch(rect)

        # Find the highest question number with a positive reviewer response for this dimension
        max_positive_q = -1  # Initialize to -1 to handle case where no positives found
        if reviewer_available:  # Only calculate if reviewer is available
            for q in range(numQ):
                qr_field = f"QR_{q:02d}_{dim}"
                qr_value = bool(air_data.iloc[0][qr_field]) if qr_field in air_data.columns else False
                if qr_value:
                    max_positive_q = q

        # Show X if no reviewer, otherwise show max question number if positive responses found
        if not reviewer_available:
            ax.text(x + key_text_width + key_num_width/2, y + dy/2, 
                   "X", fontsize=font_size, ha='center', va='center')
        elif max_positive_q >= 0:
            ax.text(x + key_text_width + key_num_width/2, y + dy/2, 
                   str(max_positive_q), fontsize=font_size, ha='center', va='center')

    # ************************************************************************************
    # draw the "TECHNOLOGY Focus" box
    x = key_x0
    y = key_y0 - 3*dy
    rect = patches.Rectangle((x, y), dx, dy, facecolor='none', edgecolor='black', lw=1)
    ax.add_patch(rect)
    ax.text(x + dx/2, y + dy/2, "TECHNOLOGY focus", fontsize=font_size, ha='center', va='center', fontweight='bold')

    # draw the boxes for dimension 0
    for dim in range(0, 1):
        x = key_x0
        y = key_y0 - (dim+4)*dy
        rect = patches.Rectangle((x, y), key_text_width, dy, facecolor='none', edgecolor='black', lw=1)
        ax.add_patch(rect)
        # Get the dimension name from assessment table and add it to the rectangle
        dimension_name = air_assessment.iloc[dim]["Dimension"]
        ax.text(x + 0.1, y + dy/2, dimension_name, fontsize=font_size, ha='left', va='center')
        rect = patches.Rectangle((x + key_text_width, y), key_num_width, dy, facecolor='#F0F0F0', edgecolor='black', lw=1)
        ax.add_patch(rect)

        # Find the highest question number with a positive reviewer response for this dimension
        max_positive_q = -1  # Initialize to -1 to handle case where no positives found
        if reviewer_available:  # Only calculate if reviewer is available
            for q in range(numQ):
                qr_field = f"QR_{q:02d}_{dim}"
                qr_value = bool(air_data.iloc[0][qr_field]) if qr_field in air_data.columns else False
                if qr_value:
                    max_positive_q = q

        # Show X if no reviewer, otherwise show max question number if positive responses found
        if not reviewer_available:
            ax.text(x + key_text_width + key_num_width/2, y + dy/2, 
                   "X", fontsize=font_size, ha='center', va='center')
        elif max_positive_q >= 0:
            ax.text(x + key_text_width + key_num_width/2, y + dy/2, 
                   str(max_positive_q), fontsize=font_size, ha='center', va='center')

    # ************************************************************************************
    # draw the "NEED Focus" box
    x = key_x0
    y = key_y0 - 6*dy
    rect = patches.Rectangle((x, y), dx, dy, facecolor='none', edgecolor='black', lw=1)
    ax.add_patch(rect)
    ax.text(x + dx/2, y + dy/2, "NEED focus", fontsize=font_size, ha='center', va='center', fontweight='bold')

    # draw the boxes for dimension 1
    for dim in range(1, 2):
        x = key_x0
        y = key_y0 - (dim+6)*dy
        rect = patches.Rectangle((x, y), key_text_width, dy, facecolor='none', edgecolor='black', lw=1)
        ax.add_patch(rect)
        # Get the dimension name from assessment table and add it to the rectangle
        dimension_name = air_assessment.iloc[dim]["Dimension"]
        ax.text(x + 0.1, y + dy/2, dimension_name, fontsize=font_size, ha='left', va='center')
        rect = patches.Rectangle((x + key_text_width, y), key_num_width, dy, facecolor='#F0F0F0', edgecolor='black', lw=1)
        ax.add_patch(rect)

        # Find the highest question number with a positive reviewer response for this dimension
        max_positive_q = -1  # Initialize to -1 to handle case where no positives found
        if reviewer_available:  # Only calculate if reviewer is available
            for q in range(numQ):
                qr_field = f"QR_{q:02d}_{dim}"
                qr_value = bool(air_data.iloc[0][qr_field]) if qr_field in air_data.columns else False
                if qr_value:
                    max_positive_q = q

        # Show X if no reviewer, otherwise show max question number if positive responses found
        if not reviewer_available:
            ax.text(x + key_text_width + key_num_width/2, y + dy/2, 
                   "X", fontsize=font_size, ha='center', va='center')
        elif max_positive_q >= 0:
            ax.text(x + key_text_width + key_num_width/2, y + dy/2, 
                   str(max_positive_q), fontsize=font_size, ha='center', va='center')

#------------------------------------------------------------------------------------------
# Draw the milestones table

    # Helper function to render text with **bold** markup
    def render_formatted_text(ax, x, y, text, fontsize, ha='left', va='center'):
        """
        Render text with **bold** markup using LaTeX formatting
        """
        import re
        
        # Convert **text** to LaTeX bold format
        latex_text = re.sub(r'\*\*(.*?)\*\*', r'$\\mathbf{\1}$', text)
        
        # Remove any remaining ** markers
        latex_text = latex_text.replace('**', '')
        
        # Render the text with LaTeX formatting
        ax.text(x, y, latex_text, fontsize=fontsize, ha=ha, va=va)
        
        return len(text) * fontsize * 0.6 / 72  # Rough width estimate

    # Calculate starting position for milestones table (below the key table)
    milestone_table_y_start = key_y0 - 12*dy  # Start below the lowest key table entry
    milestone_row_height = 0.2
    milestone_col_widths = [1.1, 5.0, 0.8]  # Width for each column
    milestone_table_width = sum(milestone_col_widths)
    
    # Center the milestones table
    milestone_x_start = (page_width - milestone_table_width) / 2
    
    # Get number of milestones
    num_milestones = len(air_milestones)
    
    # Draw table header
    header_y = milestone_table_y_start
    col_x = milestone_x_start
    
    # Header for column 1
    rect = patches.Rectangle((col_x, header_y), milestone_col_widths[0], milestone_row_height, 
                           facecolor='#E0E0E0', edgecolor='black', lw=1)
    ax.add_patch(rect)
    ax.text(col_x + milestone_col_widths[0]/2, header_y + milestone_row_height/2, "Milestone", 
            fontsize=font_size, ha='center', va='center', fontweight='bold')
    
    # Header for column 2
    col_x += milestone_col_widths[0]
    rect = patches.Rectangle((col_x, header_y), milestone_col_widths[1], milestone_row_height, 
                           facecolor='#E0E0E0', edgecolor='black', lw=1)
    ax.add_patch(rect)
    ax.text(col_x + milestone_col_widths[1]/2, header_y + milestone_row_height/2, "Label", 
            fontsize=font_size, ha='center', va='center', fontweight='bold')
    
    # Header for column 3
    col_x += milestone_col_widths[1]
    rect = patches.Rectangle((col_x, header_y), milestone_col_widths[2], milestone_row_height, 
                           facecolor='#E0E0E0', edgecolor='black', lw=1)
    ax.add_patch(rect)
    ax.text(col_x + milestone_col_widths[2]/2, header_y + milestone_row_height/2, "Progress", 
            fontsize=font_size, ha='center', va='center', fontweight='bold')
    
    # Draw data rows
    for milestone_idx in range(num_milestones):
        row_y = header_y - (milestone_idx + 1) * milestone_row_height
        milestone_row = air_milestones.iloc[milestone_idx]
        milestone_id = milestone_row['id']
        milestone_name = milestone_row['Name']
        milestone_label = milestone_row['Label']
        milestone_color = milestone_row['Color']
        milestone_text_color = milestone_row.get('Text Color', '#000000')  # Default to black if not specified
        
        # Ensure colors have # prefix
        if pd.notna(milestone_color) and not milestone_color.startswith('#'):
            milestone_color = f"#{milestone_color}"
        if pd.isna(milestone_color):
            milestone_color = '#FFFFFF'
            
        if pd.notna(milestone_text_color) and not milestone_text_color.startswith('#'):
            milestone_text_color = f"#{milestone_text_color}"
        if pd.isna(milestone_text_color):
            milestone_text_color = '#000000'
        
        # Calculate AA and BB values for this milestone
        aa_count = 0  # Number of true QR responses for this milestone
        bb_count = 0  # Total possible responses for this milestone
        
        # Always calculate bb_count (total possible) regardless of reviewer availability
        for i in range(numQ):
            for dim in range(num_dims):
                try:
                    milestone_field = f"Q{i} Milestone"
                    assessed_milestone_id = air_assessment.iloc[dim][milestone_field]
                    
                    if isinstance(assessed_milestone_id, (list, tuple)):
                        assessed_milestone_id = assessed_milestone_id[0]
                    
                    if assessed_milestone_id == milestone_id:
                        bb_count += 1  # This position uses this milestone
                        
                        # Only calculate aa_count if reviewer is available
                        if reviewer_available:
                            # Check if reviewer answered positively
                            qr_field = f"QR_{i:02d}_{dim}"
                            if qr_field in air_data.columns:
                                qr_value = bool(air_data.iloc[0][qr_field])
                                if qr_value:
                                    aa_count += 1
                except:
                    continue
        
        # Column 1: Milestone name with mixed formatting
        col_x = milestone_x_start
        rect = patches.Rectangle((col_x, row_y), milestone_col_widths[0], milestone_row_height, 
                               facecolor='white', edgecolor='black', lw=1)
        ax.add_patch(rect)
        
        # Use the helper function for mixed formatting
        milestone_text = f"Milestone **{milestone_name}**"
        render_formatted_text(ax, col_x + 0.05, row_y + milestone_row_height/2, 
                             milestone_text, font_size-1, ha='left', va='center')
        
        # Column 2: Label (could also have formatting if needed)
        col_x += milestone_col_widths[0]
        rect = patches.Rectangle((col_x, row_y), milestone_col_widths[1], milestone_row_height, 
                               facecolor='white', edgecolor='black', lw=1)
        ax.add_patch(rect)
        
        # Check if label has formatting markup
        if '**' in milestone_label:
            render_formatted_text(ax, col_x + 0.05, row_y + milestone_row_height/2, 
                                 milestone_label, font_size-1, ha='left', va='center')
        else:
            ax.text(col_x + 0.05, row_y + milestone_row_height/2, milestone_label, 
                    fontsize=font_size-1, ha='left', va='center')
        
        # Column 3: Progress with milestone color background
        col_x += milestone_col_widths[1]
        rect = patches.Rectangle((col_x, row_y), milestone_col_widths[2], milestone_row_height, 
                               facecolor=milestone_color, edgecolor='black', lw=1)
        ax.add_patch(rect)
        
        # Show X/total if no reviewer, otherwise show actual progress
        if not reviewer_available:
            progress_text = f"X/{bb_count}" if bb_count > 0 else "X/0"
        else:
            progress_text = f"{aa_count}/{bb_count}" if bb_count > 0 else "0/0"
            
        ax.text(col_x + milestone_col_widths[2]/2, row_y + milestone_row_height/2, progress_text, 
                fontsize=font_size-1, ha='center', va='center', color=milestone_text_color, fontweight='bold')

#------------------------------------------------------------------------------------------
# Add footnote at bottom of page
footnote_y = 0.1  # Position near bottom of page
footnote_fontsize = 8
footnote_color = '#808080'  # Gray color

# Left: "DO NOT DUPLICATE - DO NOT DISTRIBUTE"
ax.text(0, footnote_y, "DO NOT DUPLICATE - DO NOT DISTRIBUTE", 
        fontsize=footnote_fontsize, ha='left', va='bottom', color=footnote_color)

# Center: "v. 0.31"
ax.text(page_width/2, footnote_y, "v. 0.31", 
        fontsize=footnote_fontsize, ha='center', va='bottom', color=footnote_color)

# Right: "© Impact Readiness Ltd. 2024-5"
ax.text(page_width, footnote_y, "© Impact Readiness Ltd. 2024-5", 
        fontsize=footnote_fontsize, ha='right', va='bottom', color=footnote_color)

#------------------------------------------------------------------------------------------
# Add diagonal "CONFIDENTIAL" watermark across the entire page
watermark_text = "CONFIDENTIAL"
watermark_fontsize = 72
watermark_color = '#B0B0B0'  # Slightly darker gray color
watermark_alpha = 0.3  # Transparency

# Position watermark in center of page
watermark_x = page_width / 2
watermark_y = (letter_height - 2*margin) / 2

# Add the watermark text with rotation
ax.text(watermark_x, watermark_y, watermark_text, 
        fontsize=watermark_fontsize, ha='center', va='center', 
        color=watermark_color, alpha=watermark_alpha, 
        rotation=45, fontweight='bold')

#------------------------------------------------------------------------------------------
st.pyplot(fig)

# Now that the figure is generated, create the PDF download button
pdf_buffer = io.BytesIO()
plt.savefig(pdf_buffer, format='pdf', dpi=300)
pdf_buffer.seek(0)

# Display the download button in the placeholder we created earlier
pdf_placeholder.download_button(
    label="Save as PDF",
    data=pdf_buffer,
    file_name=f"IRL_Report_{selected_assessment}.pdf",
    mime="application/pdf",
    key="pdf_download"
)

# End of report