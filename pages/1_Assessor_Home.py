from shared import *
from shared import check_session_timeout, reset_session_timer

display_logo()

# Check for session timeout at page entry
check_session_timeout()

st.title("Assessor Home")

if 'mode' not in st.session_state:
    st.session_state.mode = 'ASSESSOR'

# ---------------------------------------------------------------------------------
# initiate the pyairtable API
api_key = st.secrets["general"]["airtable_api_key"]
api = Api(api_key)

# ---------------------------------------------------------------------------------
# Load emails of assessors
base_id = st.secrets["general"]["airtable_base_id"]
table_name = st.secrets["general"]["airtable_table_assessors"]

air_assessors = api.table(base_id, table_name)
air_assessors = air_assessors.all()

df_assessors = pd.json_normalize(air_assessors)
assessor_emails = df_assessors['fields.Email'].tolist()

# ---------------------------------------------------------------------------------
# Select the assessor

### *** In the future this will happen automatically at login.
st.session_state.assessor_email = st.selectbox('Select an Assessor:', options = assessor_emails)

# ---------------------------------------------------------------------------------
# Navigate

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Assess"):
        reset_session_timer()
        st.switch_page("pages/1_New_Assessment.py")
with col2:
    if st.button("Add New Project"):
        reset_session_timer()
        st.switch_page("pages/1_New_Project.py")
with col3:
    if st.button("Report"):
        reset_session_timer()
        st.switch_page("pages/12_Report.py")

if st.button("Home"):
    reset_session_timer()
    st.switch_page("streamlit_app.py")
