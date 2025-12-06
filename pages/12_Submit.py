from shared import *
from pyairtable import Api

# This page saves the assessment to the airtable database
responses = {}

#st.write(type(st.session_state.QA))
#st.write(st.session_state.QA)


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

# Extract single IDs from lists if needed (matching Support Organization pattern)
venture_id = st.session_state.venture_id
if isinstance(venture_id, (list, tuple)):
    venture_id = venture_id[0]

project_id = st.session_state.project_id
if isinstance(project_id, (list, tuple)):
    project_id = project_id[0]

support_id = st.session_state.support_id
if isinstance(support_id, (list, tuple)):
    support_id = support_id[0]

assessor_id = st.session_state.assessor_id
if isinstance(assessor_id, (list, tuple)):
    assessor_id = assessor_id[0]

responses["Venture"] = [venture_id]  # Wrap in list for Airtable linked record
responses["Project"] = [project_id]  # Wrap in list for Airtable linked record  
responses["Support Organization"] = [support_id]  # Wrap in list for Airtable linked record
responses["ASSESSOR"] = [assessor_id] if assessor_id else []  # Handle empty assessor for independent reviews

today = datetime.now().date()
airtable_date = today.isoformat()

venture_name = st.session_state.venture_name
project_name = st.session_state.project_name


if st.session_state.mode == "ASSESSOR":
    responses["Name"] = venture_name + " - " + project_name + " - " + airtable_date
    responses["Assess_date"] = airtable_date
elif st.session_state.mode == "REVIEWER":
    responses["Name"] = venture_name + " - " + project_name + " - " + airtable_date   
    responses["Review_date"] = airtable_date


api_key = st.secrets["general"]["airtable_api_key"]
base_id = st.secrets["general"]["airtable_base_id"]
table_name = st.secrets["general"]["airtable_table_data"]

# Use modern pyairtable API
api = Api(api_key)
base = api.base(base_id)
table = base.table(table_name)

# Convert numpy types to native Python types before sending to Airtable
cleaned_responses = {}
for k, v in responses.items():
    # Convert numpy bool to plain Python bool
    if isinstance(v, np.generic):
        v = v.item()  # Converts numpy types to native types
    cleaned_responses[k] = v


# write the new table to airtable
table.create(cleaned_responses)


if st.session_state.mode == "ASSESSOR":
    st.success("Assessment submitted successfully!")
elif st.session_state.mode == "REVIEWER":
    st.success("Review submitted successfully!")

if st.button("Home"):
    st.switch_page("streamlit_app.py")
    st.stop()
