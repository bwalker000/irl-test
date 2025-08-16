from shared import *

# Load secrets
#AIRTABLE_API_KEY = st.secrets["general"]["airtable_api_key"]
#BASE_ID = st.secrets["general"]["airtable_base_id"]
#TABLE_NAME = st.secrets["general"]["airtable_table_assessment"]

if st.button("Home"):
    st.switch_page("streamlit_app.py")
if st.button("Login"):
    st.switch_page("pages/0_Login.py")
if st.button("Demo Request"):
    st.switch_page("pages/0_Demo_Request.py")
if st.button("Assess or Review"):
    st.switch_page("pages/12_Assess_&_Review.py")
