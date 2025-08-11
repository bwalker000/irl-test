# import dependencies
import streamlit as st
import pandas as pd
from pyairtable import Table
import requests
import json

# Load secrets
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


num_dims = df.shape[0]
numQ = 10

st.title("IRL Prototype")

# determine whether this is the assessor or reviewer
assess = st.toggle("Enable ASSESSOR")
review = st.toggle("Enable REVIEWER")

# Create three columns for horizontal layout. [a, b, c] are relative widths
col1, col2, col3 = st.columns([0.05, 0.05, 0.90], vertical_alignment="center")

# First checkbox (no label)
with col1:
    cb0A = st.checkbox("", key="cb0A", disabled=not assess)  # Empty string for no label

# Second checkbox (with label)
with col2:
    cb0R = st.checkbox("", key="cb0R", disabled=not review)

with col3:
    st.write('Dimension 1, Question 0?')





#col1, col2 = st.columns(2)

#with col1:
#    st.write('Boxed Column')
#    st.checkbox("Option 1")
#    st.checkbox("Option 2")
#    st.checkbox("Option 3")

#with col2:
#    st.write('Plain Column')
#    st.checkbox("Option A")
#    st.checkbox("Option B")
#    st.checkbox("Option C")

if assess:
    live_col = 1
elif review:
    live_col = 2
else:
    live_col = None

st.write(live_col)

st.markdown(f"""
    <style>
    [data-testid="stHorizontalBlock"] > div:nth-child({live_col}) {{
        background-color: #e3f3ff;
        padding: 4px;
        border-radius: 4px;
        /* Optional: make the column stand out with a border */
       //border: 2px solid #3399ff;
    }}
    </style>
    """, unsafe_allow_html=True)





st.checkbox("Q1 - ASSESSOR", disabled=not assess)
st.checkbox("Q1 - REVIEWER", disabled=not review)

st.text_area("ASSESSOR Comments")
st.text_area("REVIEWER Comments")


