from shared import *

display_logo()

st.title("Demo Request")

st.write("Please request a demo via email.")

if st.button("Home"):
    st.switch_page("streamlit_app.py")
