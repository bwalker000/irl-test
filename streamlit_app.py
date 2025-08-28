from shared import *

st.title("Impact Readiness Level")



# Load secrets
api_key = st.secrets["general"]["airtable_api_key"]
base_id = st.secrets["general"]["airtable_base_id"]
table_name = st.secrets["general"]["airtable_table_assessors"]

api = Api(api_key)
table = api.table(base_id, table_name)
records = table.all()

records

'testing match with Anissa'

test = table.all(formula=match({"First Name": "Anissa"}))

test

if st.button("Home"):
    st.switch_page("streamlit_app.py")
if st.button("Login"):
    st.switch_page("pages/0_Login.py")
if st.button("Demo Request"):
    st.switch_page("pages/0_Demo_Request.py")

