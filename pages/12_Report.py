from shared import *

st.title("Create a Report")


#-----------------------------------------------------------------------------------------
# Load the assessment data from airtable

# Load secrets
api_key = st.secrets["general"]["airtable_api_key"]
base_id = st.secrets["general"]["airtable_base_id"]
table_name = st.secrets["general"]["airtable_table_data"]

# Debug mode toggle
#debug = st.checkbox("Enable Airtable debug mode", value=False)
debug = False

# load airtable data
air_data, debug_details = load_airtable(table_name, base_id, api_key, debug)

if debug:
    st.subheader("Airtable API Debug Information")
    st.code(f"Request URL: {debug_details['url']}", language="text")
    st.write("Status code:", debug_details["status_code"])
    st.write("Response headers:", debug_details["response_headers"])
    st.write("Raw JSON response:")
    st.json(debug_details["raw_response"])
    st.write("Records returned:", debug_details["records_count"])

if air_data.empty:
    st.warning("No records found in the Airtable table.")

#-----------------------------------------------------------------------------------------
# filter the assessment data based on the user role

# if REVIEWER, then only show assessments associated with the reviewer
if st.session_state.mode == "REVIEWER":
    air_data = air_data.loc[ air_data["REVIEWER"] == st.session_state.reviewer_id[0] ]

# if ASSESSOR, then only show assessments associated with the assessor
if st.session_state.mode == "ASSESSOR":
    air_data = air_data.loc[ air_data["Assessor"] == st.session_state.assessor_id[0] ]    

#-----------------------------------------------------------------------------------------
# Use a pulldown menu to select the assessment to be reported on

# Role-specific assessment selection
if st.session_state.mode == "REVIEWER":
    assessment_names = air_data['Name']
    if assessment_names.empty:
        st.warning("No available assessments to report for you as a REVIEWER.")
        st.stop()
    selected_assessment = st.selectbox('Select an assessment for reporting:', options=assessment_names)

elif st.session_state.mode == "ASSESSOR":
    assessment_names = air_data['Name']
    if assessment_names.empty:
        st.warning("No available assessments to report for you as an ASSESSOR.")
        st.stop()
    selected_assessment = st.selectbox('Select an assessment for reporting:', options=assessment_names)

else:
    st.warning("Unknown mode.")
    st.stop()

# Don't run report immediately after selection!
# Instead, wait for user to click a button

if selected_assessment:
    if st.button("Generate Report"):
        # Filter for chosen assessment
        filtered_data = air_data.loc[air_data["Name"] == selected_assessment]
        if filtered_data.empty:
            st.warning("No data found for the selected assessment.")
            st.stop()

        with st.spinner("Generating your report, please wait..."):
            # ===== Place your report generation code here =====
            # Example:
            # generate_report(filtered_data)
            pass
else:
    st.info("Please select an assessment to enable report generation.")

#-----------------------------------------------------------------------------------------
# Prepare the report


# Load secrets
api_key = st.secrets["general"]["airtable_api_key"]
base_id = st.secrets["general"]["airtable_base_id"]
table_name = st.secrets["general"]["airtable_table_assessment"]

# Debug mode toggle
#debug = st.checkbox("Enable Airtable debug mode", value=False)
debug = False

# load airtable assessment
air_assessment, debug_details = load_airtable(table_name, base_id, api_key, debug)



# Load secrets
api_key = st.secrets["general"]["airtable_api_key"]
base_id = st.secrets["general"]["airtable_base_id"]
table_name = st.secrets["general"]["airtable_table_milestones"]

# Debug mode toggle
#debug = st.checkbox("Enable Airtable debug mode", value=False)
debug = False

# load airtable assessment
air_milestones, debug_details = load_airtable(table_name, base_id, api_key, debug)



# determine the number of rows and columns in the report
num_dims = air_assessment.shape[0]
numQ = 10


# DIMENSION THE REPORT 

# Define letter sheet dimensions and margins (in inches)
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

ax.text(2.0, 9.9, air_data.iloc[0]["Venture"], fontsize=12, ha='left', va='bottom', fontweight='bold')
ax.text(2.0, 9.65, air_data.iloc[0]["ASSESSOR"], fontsize=12, ha='left', va='bottom', fontweight='bold')
ax.text(2.0, 9.4, air_data.iloc[0]["REVIEWER"], fontsize=12, ha='left', va='bottom', fontweight='bold')

ax.text(3.75, 9.9, "Project / Product:", fontsize=12, ha='left', va='bottom', fontweight='bold')
ax.text(3.75, 9.65, "Date:", fontsize=12, ha='left', va='bottom', fontweight='bold')
ax.text(3.75, 9.4, "Date:", fontsize=12, ha='left', va='bottom', fontweight='bold')

ax.text(5.75, 9.9, air_data.iloc[0]["Project"], fontsize=12, ha='left', va='bottom', fontweight='bold')
ax.text(5.75, 9.65, air_data.iloc[0]["Assess_date"], fontsize=12, ha='left', va='bottom', fontweight='bold')
ax.text(5.75, 9.4, air_data.iloc[0]["Review_date"], fontsize=12, ha='left', va='bottom', fontweight='bold')


# MATRIX

n_rows = numQ
n_cols = num_dims

dx =  7 / n_cols
dy = dx

for dim in range(n_rows):

    y0 = (9-n_rows*dy) + dim*dy    
    cy = y0 + dy / 2
    ax.text(0, cy, dim, fontsize=12, ha='left', va='center', fontweight='bold')

    for i in range(n_cols):
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

        # find the milestone associated with this particular question
        milestone = f"Q{i} Milestone"
        milestone_id = air_assessment.iloc[i][milestone]
        color = air_milestones.loc[ air_milestones["id"] == milestone_id ].iloc[0]["Color"]

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
    