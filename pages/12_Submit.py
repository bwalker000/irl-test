from shared import *

# This page saves the assessment to the airtable database
responses = {}

st.write(type(st.session_state.QA))
st.write(st.session_state.QA)


for dim in range(st.session_state.QA.shape[0]):
    for i, value in enumerate(st.session_state.QA[dim]):
        field_name = f"QA_{dim:02d}_{i}"
        responses[field_name] = value

for dim in range(st.session_state.QR.shape[0]):
    for i, value in enumerate(st.session_state.QR[dim]):
        field_name = f"QR_{dim:02d}_{i}"
        responses[field_name] = value

for dim, value in enumerate(st.session_state.TA):
    field_name = f"TA_{dim:02d}"
    responses[field_name] = value

for dim, value in enumerate(st.session_state.TR):
    field_name = f"TR_{dim:02d}"
    responses[field_name] = value

responses["Venture"] = st.session_state.venture_id
responses["Project"] = st.session_state.project_id
responses["Support"] = st.session_state.support_id
responses["ASSESSOR"] = st.session_state.assessor_email

today = date.today()
airtable_date = today.isoformat()

venture_name = st.session_state.venture_name
project_name = st.session_state.project_name

if st.session_state.mode == "ASSESSOR":
    responses["Name"] = venture_name + " - " + project_name + " - " + airtable_date
    responses["Assess_date"] = airtable_date
elif st.session_state.mode == "REVIEWER":
    responses["Review_date"] = airtable_date
#
#
#
api_key = st.secrets["general"]["airtable_api_key"]
base_id = st.secrets["general"]["airtable_base_id"]
table_name = st.secrets["general"]["airtable_table_data"]

table = Table(api_key, base_id, table_name)


# Convert numpy types to native Python types before sending to Airtable
cleaned_responses = {}
for k, v in responses.items():
    # Convert numpy bool to plain Python bool
    if isinstance(v, np.generic):
        v = v.item()  # Converts numpy types to native types
    cleaned_responses[k] = v

table.create(cleaned_responses)


if st.button("Home"):
    st.switch_page("streamlit_app.py")
