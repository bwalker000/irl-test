from shared import *

st.title("Impact Readiness Level")

# this resets a flag telling whether a review / assessment has been submitted.
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

if not st.user.is_logged_in:
    if st.button("Log in"):
        st.login("auth0")

if st.user.is_logged_in:

    st.write(f"User Email: {st.user.email}\n\n")

    if 'mode' not in st.session_state:
        assessor_or_reviewer()

    if st.session_state.mode == "ASSESSOR":
        st.write("User Mode: ASSESSOR")
        st.session_state.assessor_email = st.user.email
        if st.button("Assess"):
            st.switch_page("pages/1_New_Assessment.py")
        if st.button("Report"):
            st.switch_page("pages/12_Report.py")

    elif st.session_state.mode == "REVIEWER":
        st.write("User Mode: REVIEWER")
        st.session_state.reviewer_email = st.user.email
        if st.button("Review"):
            st.switch_page("pages/2_Initiate_Review.py")
        if st.button("Report"):
            st.switch_page("pages/12_Report.py")    

    if st.button("Log out"):
        st.logout()

if st.button("Demo Request"):
    st.switch_page("pages/0_Demo_Request.py")
