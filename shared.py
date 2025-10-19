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
from fields import IRL_031_data_fields

# Common configuration values used across pages
# Calculate num_dims dynamically from the fields structure
num_dims = len([f for f in IRL_031_data_fields if f.startswith('TA_')])  # Count TA fields to get number of dimensions
numQ = 10       # Number of questions per dimension (this can remain hardcoded)

def display_logo():
    """Display the Impact Readiness Level logo in the upper left corner"""
    try:
        st.image("Logo.png", width=150)
    except:
        pass  # Silently fail if logo not found

