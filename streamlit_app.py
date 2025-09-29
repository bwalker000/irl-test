from shared import *

st.title("Impact Readiness Level")

# Initialize session state for submission tracking
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# Load secrets
#api_key = st.secrets["general"]["airtable_api_key"]
#base_id = st.secrets["general"]["airtable_base_id"]
#table_name = st.secrets["general"]["airtable_table_assessors"]

#api = Api(api_key)
#table = api.table(base_id, table_name)
#records = table.all()

#records

#'testing match with Anissa'

#test = table.all(formula=match({"First Name": "Anissa"}))

#test

#if st.button("Home"):
#    st.switch_page("streamlit_app.py")

# Show Demo Request button only on the main screen when not logged in
if not st.user.is_logged_in:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Log in"):
            st.login("auth0")
    with col2:
        if st.button("Demo Request"):
            st.switch_page("pages/0_Demo_Request.py")

# Handle logged-in state
if st.user.is_logged_in:
    st.write(f"User Email: {st.user.email}\n\n")

    # Check if user is registered as assessor or reviewer
    is_registered = assessor_or_reviewer()
    
    if not is_registered:
        st.error("Your email is not registered as an ASSESSOR or REVIEWER.")
        if st.button("Log out"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            # Log out of Auth0
            st.logout()
    else:
        # Show interface for registered users
        if st.session_state.mode == "ASSESSOR":
            st.write("User Mode: ASSESSOR")
            st.session_state.assessor_email = st.user.email
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Assess"):
                    st.switch_page("pages/1_New_Assessment.py")
            with col2:
                if st.button("Report"):
                    st.switch_page("pages/12_Report.py")
            with col3:
                if st.button("Log out"):
                    st.logout()

        elif st.session_state.mode == "REVIEWER":
            st.write("User Mode: REVIEWER")
            st.session_state.reviewer_email = st.user.email
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Review"):
                    st.switch_page("pages/2_Initiate_Review.py")
            with col2:
                if st.button("Report"):
                    st.switch_page("pages/12_Report.py")
            with col3:
                if st.button("Log out"):
                    st.logout()
