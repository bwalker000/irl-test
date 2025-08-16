from shared import *

# Load secrets
AIRTABLE_API_KEY = st.secrets["general"]["airtable_api_key"]
BASE_ID = st.secrets["general"]["airtable_base_id"]


st.title("Impact Readiness Level")

if st.button("Home"):
    st.switch_page("streamlit_app.py")
if st.button("Login"):
    st.switch_page("pages/0_Login.py")
if st.button("Demo Request"):
    st.switch_page("pages/0_Demo_Request.py")

