import streamlit as st

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

st.selectbox("Pick one", ["cats", "dogs"])
st.multiselect("Buy", ["milk", "apples", "potatoes"])
st.slider("Pick a number", 0, 100)
st.select_slider("Pick a size", ["S", "M", "L"])
st.text_input("First name")
st.number_input("Pick a number", 0, 10)
st.text_area("Text to translate")
st.date_input("Your birthday")


