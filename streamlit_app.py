#pip install pyairtable

import streamlit as st

import os
from pyairtable import Api

# connect to Airtable
api = Api(os.environ['patdNMT424EkcYEgR.df1fcd9d087d6977be07d02c2b53bdd64afffc583e736a5be174aec174083df1'])

table = api.table('appExampleBaseId', 'tblExampleTableId')

st.write(table.all())


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


