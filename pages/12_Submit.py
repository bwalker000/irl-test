from shared import *

# This page saves the assessment to the airtable database
responses = {}

for (dim, i), value in st.session_state.QA.items():
    field_name = f"QA_{dim:02d}_{i}"
    responses[field_name] = value

for (dim, i), value in st.session_state.QR.items():
    field_name = f"QR_{dim:02d}_{i}"
    responses[field_name] = value

for dim, value in st.session_state.TA.items():
    field_name = f"TA_{dim:02d}"
    responses[field_name] = value

for dim, value in st.session_state.TR.items():
    field_name = f"TR_{dim:02d}"
    responses[field_name] = value

responses["Venture"]=st.session_state.venture_id
responses["Project"]=st.session_state.project_id
responses["Support"]=st.session_state.support_id
responses["ASSESSOR"]=st.session_state.assessor

today = date.today()
airtable_date = today.isoformat()

if st.session_state.mode="ASSESSOR":
    responses["Name"]=
    responses["Assess_date"]=airtable_date
elif st.session_state.mode="REVIEWER":

#
#
#
api_key = st.secrets["general"]["airtable_api_key"]
base_id = st.secrets["general"]["airtable_base_id"]
table_name = st.secrets["general"]["airtable_table_data"]

table = Table(API_KEY, BASE_ID, TABLE_NAME)
table.create(responses)



if st.button("Home"):
    st.switch_page("streamlit_app.py")
    