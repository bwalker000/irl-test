from shared import *
from shared import check_session_timeout, reset_session_timer

display_logo()
check_session_timeout()

st.title("Select Report Type")

col1, col2 = st.columns(2)
with col1:
    if st.button("Single Report", type="primary"):
        reset_session_timer()
        st.switch_page("pages/12_Report.py")
with col2:
    if st.button("Comparison Report"):
        reset_session_timer()
        st.switch_page("pages/12_Comparison_Report.py")

if st.button("Home"):
    reset_session_timer()
    st.switch_page("streamlit_app.py")