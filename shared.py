# import dependencies
import streamlit as st
import pandas as pd
import matplotlib as mp
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pyairtable import Table
from pyairtable.formulas import match
from pyairtable import Api
import requests
import json
import numpy as np
import os
from airtable_utils import load_airtable
from airtable_utils import airtable_value_from_id
from airtable_utils import load_airtable_record
from airtable_utils import assessor_or_reviewer
from airtable_utils import submit_record
from datetime import datetime, date
from fields import IRL_050_data_fields
import time

# Common configuration values used across pages
# Calculate num_dims dynamically from the fields structure
num_dims = len([f for f in IRL_050_data_fields if f.startswith('TA_')])  # Count TA fields to get number of dimensions
numQ = 10       # Number of questions per dimension (this can remain hardcoded)

# Session timeout configuration
IDLE_TIMEOUT = 1800  # 30 minutes in seconds

def display_logo():
    """Display the Impact Readiness Level logo in the upper left corner"""
    try:
        st.image("Logo.png", width=150)
    except:
        pass  # Silently fail if logo not found

def check_session_timeout():
    """Check if user has been idle too long and force logout"""
    if 'last_activity' not in st.session_state:
        st.session_state.last_activity = time.time()
    
    current_time = time.time()
    idle_time = current_time - st.session_state.last_activity
    
    if idle_time > IDLE_TIMEOUT:
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        # Force logout
        try:
            st.logout()
        except:
            pass
        st.warning("Your session has expired due to inactivity. Please log in again.")
        st.stop()
    
    # Update last activity time
    st.session_state.last_activity = current_time

def reset_session_timer():
    """Reset the inactivity timer on user interaction"""
    st.session_state.last_activity = time.time()

