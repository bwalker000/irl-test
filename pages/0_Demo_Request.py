from shared import *
from shared import check_session_timeout, reset_session_timer

display_logo()

# Check for session timeout at page entry (if logged in)
try:
    if hasattr(st, 'user') and hasattr(st.user, 'email') and st.user.email is not None:
        check_session_timeout()
except:
    pass

st.title("Demo Request")

st.write("Please request a demo via email.")

if st.button("Home"):
    reset_session_timer()  # User is active
    st.switch_page("streamlit_app.py")
