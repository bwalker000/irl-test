from shared import *
from airtable_utils import load_airtable

st.title("Reviewer Home")

if 'mode' not in st.session_state:
    st.session_state.mode = 'REVIEWER'

# Load secrets
api_key = st.secrets["general"]["airtable_api_key"]
base_id = st.secrets["general"]["airtable_base_id"]
table_name = st.secrets["general"]["airtable_table_reviewers"]

# Debug mode toggle
debug = st.checkbox("Enable Airtable debug mode", value=False)

# load airtable data
df, debug_details = load_airtable(table_name, base_id, api_key, debug=True)

if debug:
    st.subheader("Airtable API Debug Information")
    st.code(f"Request URL: {debug_details['url']}", language="text")
    st.write("Status code:", debug_details["status_code"])
    st.write("Response headers:", debug_details["response_headers"])
    st.write("Raw JSON response:")
    st.json(debug_details["raw_response"])
    st.write("Records returned:", debug_details["records_count"])

if df.empty:
    st.warning("No records found in the Airtable table.")
else:
    st.dataframe(df)

names = df['Name']

# Streamlit selectbox for choosing a Name
selected_name = st.selectbox('Select a Name:', options=names)

# Use the selected name for further processing
st.write(f'You selected: {selected_name}')

if st.button("Review"):
    st.switch_page("pages/12_Assess_&_Review.py")
if st.button("Home"):
    st.switch_page("streamlit_app.py")

