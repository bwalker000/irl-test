from shared import *
# Explicitly import shared configuration
from shared import num_dims, numQ, check_session_timeout, reset_session_timer
from airtable_utils import auto_save_progress

display_logo()

# Check for session timeout at page entry
check_session_timeout()

st.title("Assessment & Review")

# Initialize session state for submission tracking if not already set
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# Load secrets
api_key = st.secrets["general"]["airtable_api_key"]
base_id = st.secrets["general"]["airtable_base_id"]
table_name = st.secrets["general"]["airtable_table_assessment"]

# Debug mode toggle
#debug = st.checkbox("Enable Airtable debug mode", value=False)
debug = False

# load airtable data
df, debug_details = load_airtable(table_name, base_id, api_key, debug)

if debug:
    st.subheader("Airtable API Debug Information")
    st.code(f"Request URL: {debug_details['url']}", language="text")
    st.write("Status code:", debug_details["status_code"])
    st.write("Response headers:", debug_details["response_headers"])
    st.write("Raw JSON response:")
    st.json(debug_details["raw_response"])
    st.write("Records returned:", debug_details["records_count"])

if df.empty:
    st.warning("No records found in the Airtable table.")
#else:
    #st.dataframe(df)

#
#-----------------------------------------------------------------------------------------
# Initialize
# 
### fix the following to recognize that things are different for ASSESSOR and REVIEWER
if ('dim' not in st.session_state):
    st.session_state.dim = 0        # start with the first dimension

    # initiate all the variables as empty
    # ASSESSOR Question answers
    st.session_state.QA = np.zeros((num_dims, numQ), dtype=bool)

    # REVIEWER Question answers
    st.session_state.QR = np.zeros((num_dims, numQ), dtype=bool)

    # ASSESSOR Text responses
    st.session_state.TA = [""]*num_dims

    # REVIEWER Text responses
    st.session_state.TR = [""]*num_dims
    
    # Initialize submitted flag
    st.session_state.submitted = False
    
    # Initialize auto-save timer
    st.session_state.last_autosave = time.time()
    
    # Load draft data if resuming a draft assessment
    if 'draft_record_id' in st.session_state:
        table_name = st.secrets["general"]["airtable_table_data"]
        air_data, debug_details = load_airtable(table_name, base_id, api_key, debug)
        
        draft_record = air_data[air_data['id'] == st.session_state.draft_record_id]
        if not draft_record.empty:
            draft_record = draft_record.iloc[0]
            
            # Load question responses
            for dim in range(num_dims):
                for i in range(numQ):
                    field_name = f"QA_{dim:02d}_{i}"
                    if field_name in draft_record and pd.notna(draft_record[field_name]):
                        st.session_state.QA[dim, i] = bool(draft_record[field_name])
            
            # Load text responses
            for dim in range(num_dims):
                field_name = f"TA_{dim:02d}"
                if field_name in draft_record and pd.notna(draft_record[field_name]):
                    st.session_state.TA[dim] = draft_record[field_name]
    
    # if this is a reivew, then load the assessment data
    elif st.session_state.mode == "REVIEWER":

        # load the data for the specific assessment
        table_name = st.secrets["general"]["airtable_table_data"]
        air_data, debug_details = load_airtable(table_name, base_id, api_key, debug)
        
        # Only load existing assessment data if reviewing an existing assessment (not independent review)
        if "assessment_name" in st.session_state and st.session_state.assessment_name is not None:
            # Convert list columns to strings to avoid hashing issues
            list_cols = air_data.select_dtypes(include=['object']).columns
            for col in list_cols:
                air_data[col] = air_data[col].apply(lambda x: str(x) if isinstance(x, list) else x)
            air_data_record = air_data.loc[air_data["Name"] == st.session_state.assessment_name]

            # load the assessment question responses
            for dim in range(num_dims):
                for i in range(numQ):
                    field_name = f"QA_{dim:02d}_{i}"
                    # Set the value based on whether the field exists
                    if field_name in air_data_record.columns:
                        st.session_state.QA[dim, i] = bool(air_data_record.iloc[0][field_name])
                    else:
                        st.session_state.QA[dim, i] = False

            # load the assessment text responses
            for dim in range(num_dims):
                field_name = f"TA_{dim:02d}"
                if field_name in air_data_record.columns:
                    st.session_state.TA[dim] = air_data_record.iloc[0][field_name]
                else:
                    st.session_state.TA[dim] = ""
        # else: for independent reviews, QA and TA remain as initialized (all zeros/empty strings)

#
#-----------------------------------------------------------------------------------------
# Present the page
# 

# create a list of all the dimensions
dims = (
    df["Dimension"]
    .tolist()              # convert to list
)
dim = dims[st.session_state.dim]


if (st.session_state.mode == "ASSESSOR"):
    live_col = 1
    mode = "ASSESSOR"
elif (st.session_state.mode == "REVIEWER"):
    live_col = 2
    mode = "REVIEWER" 
else:
    live_col = None

# Page title
if mode == "ASSESSOR":
    st.title("ASSESS")
elif mode == "REVIEWER":
    st.title("REVIEW")
else:
    st.title("REPORT")

st.write("\n\n")

#
# Display details about the assessment
#
with st.container(border=True):

    col_widths = [0.3, 0.7]
    col1, col2 = st.columns(col_widths)
    col1.write("__Assessor:__")
    if "assessor_first_name" in st.session_state:
        col2.write(f"{st.session_state.assessor_first_name} {st.session_state.assessor_last_name}")
    else:
        col2.write("N/A")

    col1.write("__Support Organization:__")
    col2.write(st.session_state.support_name)

    col1.write("__Venture:__")
    col2.write(st.session_state.venture_name)

    col1.write("__Project:__")
    col2.write(st.session_state.project_name)

st.write("\n\n")

#
# Present General Instructions
#

if mode == "ASSESSOR":
    st.write("__General Instructions:__")
    st.write("A level is considered “achieved” when the you can confidently defend that level with supporting documentation and consensus among your leadership team. ")
elif mode == "REVIEWER":
    st.write("__General Instructions:__")
    st.write("You will constructively challenge the ASSESSOR on each level they indicate that they have achieved. You should ask for evidence of achievement. If there is no tangible record, then you must reject the ASSESSOR’s indication and will instead indicate a lower level of achievement. Do not skip levels.")

st.write("\n\n")

# Add page indicator at top (above assessment table)
# Create a unique container to force re-render from top
page_anchor = st.empty()
with page_anchor.container():
    st.markdown(f"**Page {st.session_state.dim + 1} of {num_dims}**")

# Show draft indicator if this is a draft (no submission date)
if st.session_state.get('draft_record_id'):
    st.info("📝 **Auto-saving in progress...** Your work is being saved automatically every 5 minutes and when you navigate between pages.")

#
# Display and collect the questions and answers
#
with st.container(border=True):

    # Determine if this is an independent review (no assessor)
    is_independent_review = (st.session_state.mode == "REVIEWER" and 
                           st.session_state.get("assessment_name") is None)
    
    # Set column widths based on review type
    if is_independent_review:
        col_widths = [0.06, 0.12, 0.82]  # No ASSESS column for independent reviews
    else:
        col_widths = [0.06, 0.12, 0.12, 0.70]  # Normal layout with ASSESS column

    # ----- Heading Row -----
    with st.container():
        if is_independent_review:
            col1, col2, col3 = st.columns(col_widths)
            with col2:
                st.markdown("<div style='text-align: left'><b>REVIEW</b></div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div style='text-align: left; font-weight:bold;'>{dim}</div>", unsafe_allow_html=True)
        else:
            col1, col2, col3, col4 = st.columns(col_widths)
            with col2:
                st.markdown("<div style='text-align: left'><b>ASSESS</b></div>", unsafe_allow_html=True)
            with col3:
                if mode != "ASSESSOR":
                    st.markdown("<div style='text-align: left'><b>REVIEW</b></div>", unsafe_allow_html=True)
            with col4:
                st.markdown(f"<div style='text-align: left; font-weight:bold;'>{dim}</div>", unsafe_allow_html=True)
        st.markdown("<hr style='margin: 2px 0; border: 0.5px solid #e0e0e0;'>", unsafe_allow_html=True)

    # ----- Data Rows -----
    ROW_HEIGHT = 40  # Adjust to match checkbox height in your browser/view

    for i in range(numQ):
        with st.container():
            if is_independent_review:
                col1, col2, col3 = st.columns(col_widths)
                
                with col1:
                    st.markdown(
                        f"""
                        <div style='display: flex; align-items: center; height: {ROW_HEIGHT}px'>
                            {i}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with col2:
                    st.session_state.QR[st.session_state.dim, i] = st.checkbox(
                        f"Review Question {i+1}",
                        value=bool(st.session_state.QR[st.session_state.dim, i]),
                        key=f"QR_{st.session_state.dim}_{i}",
                        label_visibility="collapsed"
                    )
                with col3:
                    question = df.loc[df["Dimension"] == dim, f"Q{i}"].iloc[0]
                    st.markdown(
                        f"""
                        <div style='display: flex; align-items: center; height: {ROW_HEIGHT}px'>
                            {question}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                col1, col2, col3, col4 = st.columns(col_widths)

                with col1:
                    st.markdown(
                        f"""
                        <div style='display: flex; align-items: center; height: {ROW_HEIGHT}px'>
                            {i}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with col2:
                    st.session_state.QA[st.session_state.dim, i] = st.checkbox(
                        f"Assessment Question {i+1}",
                        value=bool(st.session_state.QA[st.session_state.dim, i]),
                        key=f"QA_{st.session_state.dim}_{i}",
                        disabled=not (mode == "ASSESSOR"),
                        label_visibility="collapsed"
                    )

                with col3:
                    if mode == "REVIEWER":
                        st.session_state.QR[st.session_state.dim, i] = st.checkbox(
                            f"Review Question {i+1}",
                            value=bool(st.session_state.QR[st.session_state.dim, i]),
                            key=f"QR_{st.session_state.dim}_{i}",
                            label_visibility="collapsed",
                            disabled=not (mode == "REVIEWER"),
                        )

                with col4:
                    question = df.loc[df["Dimension"] == dim, f"Q{i}"].iloc[0]
                    st.markdown(
                        f"""
                        <div style='display: flex; align-items: center; height: {ROW_HEIGHT}px'>
                            {question}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        
        # Add horizontal line after each row (except the last one)
        if i < numQ:
            st.markdown("<hr style='margin: 2px 0; border: 0.5px solid #e0e0e0;'>", unsafe_allow_html=True)

    # Comments section - only show ASSESSOR comments for non-independent reviews
    if not is_independent_review:
        st.session_state.TA[st.session_state.dim] = st.text_area(
            "ASSESSOR Comments",
            value=st.session_state.TA[st.session_state.dim],
            height=None,
            max_chars=1000,
            key=f"TA_{st.session_state.dim}",
            width="stretch",
            disabled=not (mode == "ASSESSOR")
        )

    if mode != "ASSESSOR":
        st.session_state.TR[st.session_state.dim] = st.text_area(
            "REVIEWER Comments",
            value=st.session_state.TR[st.session_state.dim],
            height=None,
            max_chars=1000,
            key=f"TR_{st.session_state.dim}",
            width="stretch",
            disabled=not (mode == "REVIEWER")
        )

#
# --------------------------------------------------------------------------------------
# Present specific instructions
#
with st.container(border=True):
    st.write("__Detailed Instructions:__")
    instructions = df.loc[df["Dimension"] == dim, "Instructions"].iloc[0]
    st.write(instructions)

#
# -------------------------------------------------------------------------------------------
# Navigate
# 

# Add page indicator at bottom
st.markdown(f"**Page {st.session_state.dim + 1} of {num_dims}**")
st.write("\n")

# Page selector using full width for segmented control
# Create page options (1, 2, 3, ... num_dims) - dynamically determined from Airtable structure
page_options = list(range(num_dims))

selected_page = st.segmented_control(
    "Go to page:",
    options=page_options,
    format_func=lambda x: str(x + 1),  # Display as 1, 2, 3... instead of 0, 1, 2...
    default=st.session_state.dim,
    key="page_selector"
)

# Handle page selection change
if selected_page is not None and selected_page != st.session_state.dim:
    reset_session_timer()
    auto_save_progress()
    st.session_state.dim = selected_page
    st.query_params["_reload"] = str(time.time())
    st.rerun()

# Navigation buttons - 4 buttons before submission, 3 after
st.write("")  # Add some spacing

if not st.session_state.submitted:
    # Before submission: 4 buttons
    nav_bottom_cols = st.columns([1, 1, 1, 1])
    
    with nav_bottom_cols[0]:
        if st.session_state.dim > 0:
            if st.button("← Prev", key="prev_button"):
                reset_session_timer()
                auto_save_progress()
                st.session_state.dim -= 1
                st.query_params["_reload"] = str(time.time())
                st.rerun()
    
    with nav_bottom_cols[1]:
        if st.button("Discard & Exit", key="discard_button"):
            reset_session_timer()  # User is active
            # Do not auto-save - discard changes
            st.switch_page("streamlit_app.py")
    
    with nav_bottom_cols[2]:
        if st.button("Save & Exit", key="save_exit_button"):
            reset_session_timer()  # User is active
            auto_save_progress()  # Save before leaving
            st.switch_page("streamlit_app.py")
    
    with nav_bottom_cols[3]:
        if st.session_state.dim < num_dims - 1:
            if st.button("Next →", key="next_button"):
                reset_session_timer()
                auto_save_progress()
                st.session_state.dim += 1
                st.query_params["_reload"] = str(time.time())
                st.rerun()
else:
    # After submission: 3 buttons
    nav_bottom_cols = st.columns([1, 1, 1])
    
    with nav_bottom_cols[0]:
        if st.session_state.dim > 0:
            if st.button("← Prev", key="prev_button"):
                reset_session_timer()
                st.session_state.dim -= 1
                st.query_params["_reload"] = str(time.time())
                st.rerun()
    
    with nav_bottom_cols[1]:
        if st.button("Return Home", key="return_home_button"):
            reset_session_timer()  # User is active
            st.switch_page("streamlit_app.py")
    
    with nav_bottom_cols[2]:
        if st.session_state.dim < num_dims - 1:
            if st.button("Next →", key="next_button"):
                reset_session_timer()
                st.session_state.dim += 1
                st.query_params["_reload"] = str(time.time())
                st.rerun()

# Submit button (only on last page, below navigation)
if st.session_state.dim == num_dims - 1:
    st.write("")  # Add some spacing
    submit_cols = st.columns([2, 1, 2])
    with submit_cols[1]:
        if not st.session_state.submitted:  # Only show active submit button if not submitted
            if st.button("Submit", key="submit_button"):
                reset_session_timer()  # User is active
                submit_record()
        else:
            st.button("Submit", key="submit_button_disabled", disabled=True)
            st.success("✓ Successfully submitted!")

