import streamlit as st
import pandas as pd
import requests

# User inputs (for demo; in production, store secrets securely)
#AIRTABLE_API_KEY = st.secrets.get("airtable_api_key", "airtable_api_key")
#BASE_ID = st.secrets.get("airtable_base_id", "airtable_base_id")
#TABLE_NAME = st.secrets.get("airtable_table_name", "airtable_table_name")
AIRTABLE_API_KEY = st.secrets["airtable_api_key"]
BASE_ID = st.secrets["airtable_base_id"]
TABLE_NAME = st.secrets["airtable_table_name"]

@st.cache_data
def load_airtable():
    try:
        table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)
        records = table.all()  # Returns list of dicts
        if not records:
            return pd.DataFrame()  # Empty if no records
        return pd.DataFrame([rec.get("fields", {}) for rec in records])
    except Exception as e:
        st.error(f"Error loading Airtable data: {e}")
        return pd.DataFrame()

st.title("Airtable Table Viewer")

df = load_airtable()

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


