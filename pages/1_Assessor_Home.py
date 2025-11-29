from shared import *
from shared import check_session_timeout, reset_session_timer

display_logo()

# Check for session timeout at page entry
check_session_timeout()

st.title("Assessor Home")

if 'mode' not in st.session_state:
    st.session_state.mode = 'ASSESSOR'

# ---------------------------------------------------------------------------------
# Verify assessor session state is set
if 'assessor_email' not in st.session_state or 'assessor_id' not in st.session_state:
    st.error("Assessor information not found. Please log in again.")
    if st.button("Return to Login"):
        st.switch_page("streamlit_app.py")
    st.stop()

# Display current assessor
st.info(f"**Logged in as:** {st.session_state.assessor_email}")

# ---------------------------------------------------------------------------------
# Navigate

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Assess"):
        reset_session_timer()
        st.switch_page("pages/1_New_Assessment.py")
with col2:
    if st.button("Add New Project"):
        reset_session_timer()
        st.switch_page("pages/1_New_Project.py")
with col3:
    if st.button("Report"):
        reset_session_timer()
        st.switch_page("pages/12_Report.py")
with col4:
    if st.button("Log out"):
        # Store flags to clear AFTER logout completes
        logout_flags = {
            'eula_accepted': False,
            'login_attempted': False
        }
        
        # Call logout and handle its completion
        try:
            st.logout()
            # If we reach here, logout was called - now clear state
            for key, value in logout_flags.items():
                st.session_state[key] = value
            
            # Clear all other session state
            keys_to_delete = [k for k in st.session_state.keys() if k not in logout_flags.keys()]
            for key in keys_to_delete:
                del st.session_state[key]
                
        except Exception as e:
            # Logout failed - force clear everything anyway
            st.session_state.clear()
        
        # Use stop() to prevent further execution, then let Streamlit handle the redirect
        st.stop()
