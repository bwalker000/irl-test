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

# Show Demo Request button only on the main screen when not logged in
if not st.user.is_logged_in:
    # Check if user attempted login but hasn't accepted EULA
    if st.session_state.login_attempted and not st.session_state.eula_accepted:
        st.header("End User License Agreement")
        st.warning("You must accept the End User License Agreement to proceed with login.")
        
        # Display EULA text in an expandable section
        with st.expander("📋 Please read and accept the End User License Agreement", expanded=True):
            st.markdown("""
            **IMPACT READINESS LEVEL™ END USER LICENSE AGREEMENT**
            
            **IMPORTANT - READ CAREFULLY:** This End User License Agreement ("EULA") is a legal agreement between you (either an individual or a single entity) and Impact Readiness Ltd. for the Impact Readiness Level™ software application and associated documentation.
            
            **1. GRANT OF LICENSE**
            Subject to the terms of this EULA, you are granted a limited, non-exclusive, non-transferable license to use the Impact Readiness Level™ software for evaluation and assessment purposes only.
            
            **2. RESTRICTIONS**
            - You may NOT duplicate, distribute, or share this software or any outputs
            - You may NOT reverse engineer, decompile, or disassemble the software
            - You may NOT modify, adapt, or create derivative works
            - All assessment data and reports are confidential and proprietary
            - You may NOT duplicate, reuse, or paraphrase any survey instruments, questions, or assessment methodologies
            
            **3. CONFIDENTIALITY**
            All information, data, methodologies, and outputs from this software are CONFIDENTIAL and proprietary to Impact Readiness Ltd. You agree to maintain strict confidentiality and not disclose any information to third parties.
            
            **4. INTELLECTUAL PROPERTY**
            Impact Readiness Level™ is a trademark of Impact Readiness Ltd. All rights, title, and interest in the software, including all survey instruments, questions, assessment methodologies, and evaluation frameworks, remain with Impact Readiness Ltd. All elements of this software are copyrighted material and may not be duplicated, reused, or paraphrased without express written permission.
            
            **5. NO WARRANTY**
            This software is provided "AS IS" without warranty of any kind, either express or implied.
            
            **6. LIMITATION OF LIABILITY**
            Impact Readiness Ltd. shall not be liable for any damages arising from the use of this software.
            
            **7. TERMINATION**
            This license is effective until terminated. Your rights under this license will terminate automatically without notice if you fail to comply with any term of this EULA.
            
            By clicking "I Accept" below, you acknowledge that you have read this EULA, understand it, and agree to be bound by its terms and conditions.
            """)
        
        # EULA acceptance checkbox and buttons
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            eula_checkbox = st.checkbox("I have read and agree to the End User License Agreement")
        with col2:
            if st.button("I Accept", disabled=not eula_checkbox, type="primary"):
                st.session_state.eula_accepted = True
                st.login("auth0")
        with col3:
            if st.button("Cancel"):
                st.session_state.login_attempted = False
                st.rerun()
        
        if not eula_checkbox:
            st.info("Please read and check the agreement above to proceed with login.")
            
    else:
        # Normal login screen (no EULA attempted yet)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Log in"):
                st.session_state.login_attempted = True
                if not st.session_state.eula_accepted:
                    st.rerun()
                else:
                    st.login("auth0")
        with col2:
            if st.button("Demo Request"):
                st.switch_page("pages/0_Demo_Request.py")

# Handle logged-in state
if st.user.is_logged_in:
    st.write(f"User Email: {st.user.email}\n\n")

    # Check if user is registered as assessor or reviewer
    is_registered = assessor_or_reviewer()
    
    if not is_registered:
        st.error("Your email is not registered as an ASSESSOR or REVIEWER.")
        if st.button("Log out"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            # Log out of Auth0
            st.logout()
    else:
        # Show interface for registered users
        if st.session_state.mode == "ASSESSOR":
            st.write("User Mode: ASSESSOR")
            st.session_state.assessor_email = st.user.email
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Assess"):
                    st.switch_page("pages/1_New_Assessment.py")
            with col2:
                if st.button("Report"):
                    st.switch_page("pages/12_Report.py")
            with col3:
                if st.button("Log out"):
                    st.logout()

        elif st.session_state.mode == "REVIEWER":
            st.write("User Mode: REVIEWER")
            st.session_state.reviewer_email = st.user.email
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Review"):
                    st.switch_page("pages/2_Initiate_Review.py")
            with col2:
                if st.button("Report"):
                    st.switch_page("pages/12_Report.py")
            with col3:
                if st.button("Log out"):
                    # Clear EULA acceptance and login attempt on logout
                    st.session_state.eula_accepted = False
                    st.session_state.login_attempted = False
                    st.logout()
