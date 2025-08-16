from shared import *

# Load secrets
AIRTABLE_API_KEY = st.secrets["general"]["airtable_api_key"]
BASE_ID = st.secrets["general"]["airtable_base_id"]
TABLE_NAME = st.secrets["general"]["airtable_table_assessment"]

# Debug mode toggle
debug = st.checkbox("Enable Airtable debug mode", value=False)

@st.cache_data
def load_airtable(debug=False):
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
    params = {"view": "Grid view"}  # Or "My Custom View"
    response = requests.get(url, headers=headers, params=params)
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

# load airtable data
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

#
#------------------------------------------------
#

num_dims = df.shape[0]
numQ = 10

if 'dim' not in st.session_state:
    st.session_state.dim = 0

    # ASSESSOR Question answers
    st.session_state.QA = np.zeros((num_dims, numQ), dtype=bool)

    # REVIEWER Question answers
    st.session_state.QR = np.zeros((num_dims, numQ), dtype=bool)

    # ASSESSOR Text responses
    st.session_state.TA = [""]*10

    # REVIEWER Text responses
    st.session_state.TR = [""]*10



st.title("ASSESS / REVIEW")

dims = (
    df["Dimension"]
    .tolist()              # convert to list
)
dim = dims[st.session_state.dim]

if (st.session_state.mode == "ASSESSOR"):
    live_col = 1
    mode = "ASSESSOR"
elif (mode == "REVIEWER"):
    live_col = 2
    mode = "REVIEWER" 
else:
    live_col = None


# Create three columns for horizontal layout. [a, b, c] are relative widths
col1, col2, col3 = st.columns([0.12, 0.12, 0.76], vertical_alignment="center")

# First checkbox (no label)
with col1:
    st.markdown("<div style='text-align: center'>ASSESS</div>", unsafe_allow_html=True)
    for i in range(numQ):
        st.session_state.QA[st.session_state.dim, i] = st.checkbox(
            "",
            value=bool(st.session_state.QA[st.session_state.dim, i]),  # supply the stored value here
            key=f"QA_{st.session_state.dim}_{i}",
            disabled=not (mode == "ASSESSOR"),
        )
# Second checkbox (with label)
with col2:
    st.markdown("<div style='text-align: center'>REVIEW</div>", unsafe_allow_html=True)
    for i in range(numQ):
        st.session_state.QR[st.session_state.dim, i] = st.checkbox(
            "",
            value=bool(st.session_state.QR[st.session_state.dim, i]),  # supply the stored value here
            key=f"QR_{st.session_state.dim}_{i}",
            disabled=not (mode == "REVIEWER"),
        )
# Question
with col3:
    st.write(f"**{dim}**")
    for i in range(numQ):  # Loops from 0 to 9
        col_name = f"Q{i}"  
        st.write(df.loc[df["Dimension"] == dim, col_name].iloc[0])


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

#
# --------------------------------------------------------------------------------------
# Gather comments
#

st.session_state.TA[st.session_state.dim] = st.text_area(
    "ASSESSOR Comments",
    value=st.session_state.TA[st.session_state.dim],            # <- prepopulate with previous value
    height=None,
    max_chars=10000,
    key=f"TA_{st.session_state.dim}",                           # <- use a simple, unique key
    width="stretch",
    disabled=not (mode == "ASSESSOR")
)

st.session_state.TR[st.session_state.dim] = st.text_area(
    "REVIEWER Comments",
    value=st.session_state.TR[st.session_state.dim],            # <- prepopulate with previous value
    height=None,
    max_chars=10000,
    key=f"TR_{st.session_state.dim}",                           # <- use a simple, unique key
    width="stretch",
    disabled=not (mode == "REVIEWER")
)

#
# -------------------------------------------------------------------------------------------
# Navigate
# 

col1, col2, col3 = st.columns(3)
with col1:
    if st.session_state.dim > 0:
        if st.button("Previous"):
            st.session_state.dim -= 1
            st.rerun()
with col2:
    if st.session_state.dim < num_dims - 1:
        if st.button("Next"):
            st.session_state.dim += 1
            st.rerun()
with col3:
    if st.session_state.dim == num_dims - 1:
        if st.button("Submit"):
            st.switch_page("pages/12_Report.py")