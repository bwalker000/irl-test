# import dependencies
import streamlit as st
import pandas as pd
from pyairtable import Table
import requests
import json
import numpy as np

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

dims = (
    df["Dimension"]
    .tolist()              # convert to list
)

dims

# ASSESSOR Question answers
QA = np.zeros((num_dims, numQ), dtype=bool)
# REVIEWER Question answers
QR = np.zeros((num_dims, numQ), dtype=bool)

st.title("IRL Prototype")

modes = ["assess", "review", "report"]
mode = st.radio("Choose one:", modes)

dim = st.radio("Choose one:", dims)

# Create three columns for horizontal layout. [a, b, c] are relative widths
col1, col2, col3 = st.columns([0.12, 0.12, 0.76], vertical_alignment="center")

# First checkbox (no label)
with col1:
    st.markdown("<div style='text-align: center'>ASSESS</div>", unsafe_allow_html=True)
    for i in range(numQ):
        QA[0,i] = st.checkbox("", key=f"QA_{0}_{i}", disabled = not (mode == "assess") )

# Second checkbox (with label)
with col2:
    st.markdown("<div style='text-align: center'>REVIEW</div>", unsafe_allow_html=True)
    for i in range(numQ):
        QR[0,i] = st.checkbox("", key=f"QR_{0}_{i}", disabled = not (mode == "review") )



with col3:
    st.write(f"**{dim}**")
    st.write(df["Q0"][dim])
    st.write(df["Q1"][dim])
    st.write(df["Q2"][dim])
    st.write(df["Q3"][dim])
    st.write(df["Q4"][dim])
    st.write(df["Q5"][dim])
    st.write(df["Q6"][dim])    
    st.write(df["Q7"][dim])
    st.write(df["Q8"][dim])
    st.write(df["Q9"][dim])
    
#QA
#QR

if (mode == "assess"):
    live_col = 1
elif (mode == "review"):
    live_col = 2
else:
    live_col = None

#st.write(live_col)

for i in range(1, 3):
    if (i == live_col):
        st.markdown(f"""
            <style>
            [data-testid="stHorizontalBlock"] > div:nth-child({i}) {{
                background-color: #e3f3ff;
                padding: 8px;
                border-radius: 4px;
                /* Optional: make the column stand out with a border */
            border: 2px solid #3399ff;
            }}
            </style>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <style>
            [data-testid="stHorizontalBlock"] > div:nth-child({i}) {{
                background-color: #ffffff;
                padding: 8px;
                border-radius: 4px;
                /* Optional: make the column stand out with a border */
            border: 2px solid #3399ff;
            }}
            </style>
            """, unsafe_allow_html=True)

st.text_area("ASSESSOR Comments")
st.text_area("REVIEWER Comments")


