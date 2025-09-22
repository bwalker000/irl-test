from shared import *

# options:
# ASSESSOR:
#   new assessment
#   view report
# REVIEWER:
#   review assessment
#   independent review
#   view report
#   view trend_report

# check to see if the user is an ASSESSOR or REVIEWER

# Determine whether the user is an ASSESSOR or REVIEWER
if 'mode' not in st.session_state:
    if st.user.is_logged_in:
        user_email = st.user.email
        # Load secrets
        api_key = st.secrets["general"]["airtable_api_key"]
        base_id = st.secrets["general"]["airtable_base_id"]
        table_name_assessors = st.secrets["general"]["airtable_table_assessors"]
        table_name_reviewers = st.secrets["general"]["airtable_table_reviewers"]

        # Debug mode toggle
        #debug = st.checkbox("Enable Airtable debug mode", value=False)
        debug = False

        # load airtable data for assessors
        air_assessors, debug_details = load_airtable(table_name_assessors, base_id, api_key, debug)
        assessor_emails = air_assessors['Email'].tolist()
        air_assessors = air_assessors.loc[ air_assessors["Email"] == user_email ]
        st.session_state.assessor_id = air_assessors['id'].tolist()
        # load airtable data for reviewers
        air_reviewers, debug_details = load_airtable(table_name_reviewers, base_id,
                                                    api_key, debug)
        reviewer_emails = air_reviewers['Email'].tolist()
        air_reviewers = air_reviewers.loc[ air_reviewers["Email"] == user_email ]
        st.session_state.reviewer_id = air_reviewers['id'].tolist()
        # set the mode based on the email found
        if user_email in assessor_emails:
            st.session_state.mode = 'ASSESSOR'
        elif user_email in reviewer_emails:
            st.session_state.mode = 'REVIEWER'
        else:
            st.warning("Your email is not registered as an ASSESSOR or REVIEWER. Please contact the system administrator.")
    else:
        st.warning("You are not logged in. Please log in to continue.")
        st.stop()
# Display the user role
st.title(f"{st.session_state.mode} Home")
#st.write(f"Hello, {st.user.name}!")
#st.write(f"Your email: {st.user.email}")
#st.write(f"Your user ID: {st.user.id}")
#st.write(f"Your role: {st.session_state.mode}")
#st.write(f"Your assessor ID: {st.session_state.assessor_id}")
#st.write(f"Your reviewer ID: {st.session_state.reviewer_id}")
# Navigate based on the user role
if st.session_state.mode == "ASSESSOR":
    if st.button("Assess"):
        st.switch_page("pages/1_New_Assessment.py")
    if st.button("Report"):
        st.switch_page("pages/12_Report.py")
if st.session_state.mode == "REVIEWER":
    if st.button("Review"):
        st.switch_page("pages/2_Initiate_Review.py")
    if st.button("Report"):
        st.switch_page("pages/12_Report.py")
if st.button("Home"):
    st.switch_page("streamlit_app.py")
if st.button("Log out"):
    st.logout()
#-----------------------------------------------------------------------------------------
# Load the assessment data if an assessment has been selected


