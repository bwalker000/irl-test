from shared import *

st.title("Assessor Home")

if 'mode' not in st.session_state:
    st.session_state.mode = 'ASSESSOR'


# Load secrets for Assessors Table
api_key = st.secrets["general"]["airtable_api_key"]

api = Api(api_key)

base_id = st.secrets["general"]["airtable_base_id"]
table_name = st.secrets["general"]["airtable_table_assessors"]

air_assessors = api.table(base_id, table_name)
air_assessors = air_assessors.all()

df_assessors = pd.json_normalize(air_assessors)
assessor_emails = df_assessors['fields.Email'].tolist()

assessor_emails


option = st.selectbox(
    "How would you like to be contacted?",
    ("Email", "Home phone", "Mobile phone"),
)



# Streamlit selectbox for choosing a the Assessor
### *** In the future this will happen automatically at login.
#assessor_email = st.selectbox('Select an Assessor:', options = assessor_emails)
assessor_email = st.selectbox('Select an Assessor:', ("CAT", "dog", "FiSh"))

if st.button("Assess"):
    st.session_state.assessor_email = assessor_email
    st.switch_page("pages/1_New_Assessment.py")
if st.button("Home"):
    st.switch_page("streamlit_app.py")
