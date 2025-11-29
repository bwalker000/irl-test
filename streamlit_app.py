from shared import *

display_logo()

st.title("Impact Readiness Level")

# Initialize session state for submission tracking
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# Initialize EULA and login attempt states
if 'eula_accepted' not in st.session_state:
    st.session_state.eula_accepted = False

if 'login_attempted' not in st.session_state:
    st.session_state.login_attempted = False

# Check if user is logged in with error handling
try:
    user_logged_in = st.user.is_logged_in
except AttributeError:
    # Fallback if st.user.is_logged_in is not available
    user_logged_in = hasattr(st, 'user') and hasattr(st.user, 'email') and st.user.email is not None

# If logged in, check for session timeout
if user_logged_in:
    check_session_timeout()  # This will auto-logout if idle too long
    
    try:
        user_email = st.user.email
        st.write(f"User Email: {user_email}\n\n")

        # Reset timer on any page interaction
        reset_session_timer()

        # Check if user is registered as assessor or reviewer
        is_registered = assessor_or_reviewer()
        
        if not is_registered:
            st.error("Your email is not registered as an ASSESSOR or REVIEWER.")
            if st.button("Log out"):
                # Clear session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                # Log out of Auth0
                try:
                    st.logout()
                except:
                    st.rerun()
        else:
            # Show interface for registered users - redirect to home pages
            if st.session_state.mode == "ASSESSOR":
                st.write("User Mode: ASSESSOR")
                st.session_state.assessor_email = user_email
                st.info("Redirecting to Assessor Home...")
                st.switch_page("pages/1_Assessor_Home.py")

            elif st.session_state.mode == "REVIEWER":
                st.write("User Mode: REVIEWER")
                st.session_state.reviewer_email = user_email
                st.info("Redirecting to Reviewer Home...")
                st.switch_page("pages/2_Reviewer_Home.py")

    except Exception as e:
        st.error(f"Error accessing user information: {str(e)}")
        st.info("Authentication may not be properly configured. Please check your Streamlit configuration.")
        if st.button("Return to Login"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
# Show Demo Request button only on the main screen when not logged in
if not user_logged_in:
    # Check if user attempted login but hasn't accepted EULA
    if st.session_state.login_attempted and not st.session_state.eula_accepted:
        st.header("End User License Agreement")
        st.warning("You must accept the End User License Agreement to proceed with login.")
        
        # Load EULA from external file
        eula_file_found = True
        try:
            with open("EULA.md", "r") as f:
                eula_text = f.read()
        except FileNotFoundError:
            st.error("❌ **EULA file not found. Unable to proceed with login.**")
            st.error("Please contact support at [support email]. The End User License Agreement file is missing from the system.")
            eula_text = "**Error:** EULA document could not be loaded."
            eula_file_found = False
        
        # Display EULA text in an expandable section (only if file was found)
        if eula_file_found:
            with st.expander("📋 Please read and accept the End User License Agreement", expanded=True):
                st.markdown(eula_text)
        
            # EULA acceptance checkbox and buttons
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                eula_checkbox = st.checkbox("I have read and agree to the End User License Agreement")
            with col2:
                if st.button("I Accept", disabled=not eula_checkbox, type="primary"):
                    st.session_state.eula_accepted = True
                    try:
                        st.login("auth0")
                    except Exception as e:
                        st.error(f"Login failed: {str(e)}")
                        st.info("Please check your authentication configuration.")
            with col3:
                if st.button("Cancel"):
                    st.session_state.login_attempted = False
                    st.rerun()
            
            if not eula_checkbox:
                st.info("Please read and check the agreement above to proceed with login.")
        else:
            # EULA file not found - only show Cancel button
            if st.button("Cancel"):
                st.session_state.login_attempted = False
                st.rerun()
            
    else:
        # Normal login screen (no EULA attempted yet)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Log in"):
                st.session_state.login_attempted = True
                if not st.session_state.eula_accepted:
                    st.rerun()
                else:
                    try:
                        st.login("auth0")
                    except Exception as e:
                        st.error(f"Login failed: {str(e)}")
                        st.info("Please check your authentication configuration.")
        with col2:
            st.empty()            if st.button("Demo Request"):
                st.switch_page("pages/0_Demo_Request.py")
