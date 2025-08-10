import streamlit as st
import pandas as pd
from pyairtable import Table
import requests
import json

# Load secrets from .streamlit/secrets.toml
AIRTABLE_API_KEY = st.secrets["airtable_api_key"]
BASE_ID = st.secrets["airtable_base_id"]
TABLE_NAME = st.secrets["airtable_table_name"]

# Debug mode toggle
debug = st.checkbox("Enable Airtable debug mode", value=False)

@st.cache_data
def load_airtable(debug=False):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
    response = requests.get(url, headers=headers)
    try:
        data = response.json()
    except Exception as e:
        data = {"error": f"JSON parse error: {e}"}
    # Extract records if possible
    records = data.get("records", [])
    df = pd.DataFrame([r.get("fields", {}) for r in records]) if records else pd.DataFrame()
    details = {
        "url": url,
        "status_code": response.status_code,
        "response_headers": dict(response.headers),
        "raw_response": data,
        "records_count": len(records),
    }
    return df, details

st.title("Airtable Table Viewer (Debuggable)")

df, debug_details = load_airtable(debug=debug)

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

    


st.title("IRL Prototype")

with st.form(key="my_form"):
    username = st.text_input("Username")
    password = st.text_input("Password")
    st.form_submit_button("Login")

# determine whether this is the assessor or reviewer
assess = st.toggle("Enable ASSESSOR")
review = st.toggle("Enable REVIEWER")


# Create two columns for horizontal layout
col1, col2 = st.columns([0.05, 0.95])  # Adjust widths as desired

# First checkbox (no label)
with col1:
    cb1 = st.checkbox("", key="cb1", disabled=not assess)  # Empty string for no label

# Second checkbox (with label)
with col2:
    cb2 = st.checkbox("Descriptive label for second checkbox", key="cb2", disabled=not review)



import streamlit as st

col1, col2 = st.columns(2)

with col1:
    st.write('Boxed Column')
    st.checkbox("Option 1")
    st.checkbox("Option 2")
    st.checkbox("Option 3")

with col2:
    st.write('Plain Column')
    st.checkbox("Option A")
    st.checkbox("Option B")
    st.checkbox("Option C")


st.markdown("""
    <style>
    /* Target the first column of columns */
    [data-testid="stHorizontalBlock"] > div:nth-child(1) {
        background-color: #e3f3ff;
        padding: 16px;
        border-radius: 8px;
        /* Optional: make the column stand out with a border */
        border: 2px solid #3399ff;
    }
    </style>
    """, unsafe_allow_html=True)


st.markdown("""
    <style>
    /* Target the first column of columns */
    [data-testid="stHorizontalBlock"] > div:nth-child(2) {
        background-color: #ff0000;
        padding: 16px;
        border-radius: 8px;
        /* Optional: make the column stand out with a border */
        border: 2px solid #3399ff;
    }
    </style>
    """, unsafe_allow_html=True)





st.write(
    "Testing..."
)


st.checkbox("Q1 - ASSESSOR", disabled=not assess)
st.checkbox("Q1 - REVIEWER", disabled=not review)



st.checkbox("I agree")
st.feedback("thumbs")
st.pills("Tags", ["Sports", "Politics"])
st.radio("Pick one", ["cats", "dogs"])
st.segmented_control("Filter", ["Open", "Closed"])

st.text_area("ASSESSOR Comments")
st.text_area("REVIEWER Comments")


