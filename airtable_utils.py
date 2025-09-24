# airtable_utils.py

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
from datetime import datetime, date


from fields import IRL_031_data_fields as expected_fields


@st.cache_data
def load_airtable(table_name, base_id, airtable_api_key, debug=True, view="Grid view"):
    """
    Loads records from an Airtable table.

    Parameters:
    - table_name (str): Name of the Airtable table
    - base_id (str): Airtable Base ID (required)
    - airtable_api_key (str): Airtable API Key (required)
    - debug (bool): Whether to return debug info
    - view (str): Airtable view to use (default: "Grid view")
    """
    if not base_id or not airtable_api_key:
        raise ValueError("You must provide both base_id and airtable_api_key.")
    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    headers = {"Authorization": f"Bearer {airtable_api_key}"}
    params = {"view": view}
    response = requests.get(url, headers=headers, params=params)
    try:
        data = response.json()
    except Exception as e:
        data = {"error": f"JSON parse error: {e}"}
    records = data.get("records", [])

    if (table_name == st.secrets["general"]["airtable_table_data"]):
        df = pd.DataFrame([
            {field: r.get("fields", {}).get(field, None) for field in expected_fields} | {"id": r["id"]}
            for r in records
        ]) if records else pd.DataFrame(columns=expected_fields + ["id"])

    else:
        df = pd.DataFrame(
            [{**r.get("fields", {}), "id": r["id"]} for r in records]
        ) if records else pd.DataFrame()

    debug_details = {
        "url": url,
        "status_code": response.status_code,
        "response_headers": dict(response.headers),
        "raw_response": data,
        "records_count": len(records),
    }

    if df.empty:
        st.warning("No records found in the Airtable table.")
    
    if debug:
        st.subheader("Airtable API Debug Information")
        st.code(f"Request URL: {debug_details['url']}", language="text")
        st.write("Status code:", debug_details["status_code"])
        st.write("Response headers:", debug_details["response_headers"])
        st.write("Raw JSON response:")
        st.json(debug_details["raw_response"])
        st.write("Records returned:", debug_details["records_count"])
        st.write("")
        st.dataframe(df)

    return df, debug_details



@st.cache_data
def airtable_value_from_id(table, id, field, debug=False):
    """
    accepts an airtable id value and uses it to pull the underlying text

    Parameters:
    - table (df): Imported table from Airtable
    - id (str): Airtable id
    - field (str): name of the field in Airtable to pull the  value from 
    - debug (bool): Whether to return debug info
    """

    #st.write(id)
    #st.write(type(id))

    row = table.loc[table["id"] == id[0]]
    #st.write(row)
    values = row.iloc[0][field]

    return values



def load_airtable_record(table_name, base_id, api_key, record_id, debug=False):
    """
    Load a specific record from Airtable into a pandas DataFrame.
    
    Parameters:
        api_key (str): Your Airtable API key.
        base_id (str): The base ID of your Airtable base.
        table_name (str): The table name within your base.
        record_id (str): The unique Airtable record ID you wish to retrieve.
    
    Returns:
        pd.DataFrame: DataFrame with a single row representing the record's fields.
    """
    table = Table(api_key, base_id, table_name)
    record = table.get(record_id)
    return pd.DataFrame([record["fields"]])



def assessor_or_reviewer():
    if 'mode' not in st.session_state:
        user_email = st.user.email

        # Load secrets
        api_key = st.secrets["general"]["airtable_api_key"]
        base_id = st.secrets["general"]["airtable_base_id"]
        table_name_assessors = st.secrets["general"]["airtable_table_assessors"]
        table_name_reviewers = st.secrets["general"]["airtable_table_reviewers"]

        # Debug mode toggle
        #debug = st.checkbox("Enable Airtable debug mode", value=False)
        debug = False

        # load airtable data for assessors
        air_assessors, debug_details = load_airtable(table_name_assessors, base_id, api_key, debug)
        assessor_emails = air_assessors['Email'].tolist()
        air_assessors = air_assessors.loc[ air_assessors["Email"] == user_email ]
        st.session_state.assessor_id = air_assessors['id'].tolist()
        #st.write(st.session_state.assessor_id)

        # load airtable data for reviewers
        air_reviewers, debug_details = load_airtable(table_name_reviewers, base_id, api_key, debug)
        reviewer_emails = air_reviewers['Email'].tolist()
        air_reviewers = air_reviewers.loc[ air_reviewers["Email"] == user_email ]
        st.session_state.reviewer_id = air_reviewers['id'].tolist()
        #st.write(st.session_state.reviewer_id)             

        # set the mode based on the email found
        if user_email in assessor_emails:
            st.session_state.mode = 'ASSESSOR'
        elif user_email in reviewer_emails:

            st.session_state.mode = 'REVIEWER'
        else:
            st.warning("Your email is not registered as an ASSESSOR or REVIEWER. Please contact the system administrator.")
            st.stop()
    return st.session_state.mode 



def submit_record():
    # This code saves the assessment to the airtable database
    responses = {}

    #st.write(type(st.session_state.QA))
    #st.write(st.session_state.QA)

    for dim in range(st.session_state.QA.shape[0]):
        for i, value in enumerate(st.session_state.QA[dim]):
            field_name = f"QA_{dim:02d}_{i}"
            responses[field_name] = value

    for dim in range(st.session_state.QR.shape[0]):
        for i, value in enumerate(st.session_state.QR[dim]):
            field_name = f"QR_{dim:02d}_{i}"
            responses[field_name] = value

    for dim, value in enumerate(st.session_state.TA):
        field_name = f"TA_{dim:02d}"
        responses[field_name] = value

    for dim, value in enumerate(st.session_state.TR):
        field_name = f"TR_{dim:02d}"
        responses[field_name] = value

    responses["Venture"] = st.session_state.venture_id
    responses["Project"] = st.session_state.project_id
    responses["Support Organization"] = st.session_state.support_id
    responses["ASSESSOR"] = st.session_state.assessor_id

    today = datetime.now().date()
    airtable_date = today.isoformat()

    venture_name = st.session_state.venture_name
    project_name = st.session_state.project_name


    if st.session_state.mode == "ASSESSOR":
        responses["Name"] = venture_name + " - " + project_name + " - " + airtable_date
        responses["Assess_date"] = airtable_date
    elif st.session_state.mode == "REVIEWER":
        responses["Name"] = venture_name + " - " + project_name + " - " + airtable_date   
        responses["Review_date"] = airtable_date


    api_key = st.secrets["general"]["airtable_api_key"]
    base_id = st.secrets["general"]["airtable_base_id"]
    table_name = st.secrets["general"]["airtable_table_data"]

    table = Table(api_key, base_id, table_name)


    # Convert numpy types to native Python types before sending to Airtable
    #cleaned_responses = {}
    #for k, v in responses.items():
        # Convert numpy bool to plain Python bool
    #    if isinstance(v, np.generic):
    #        v = v.item()  # Converts numpy types to native types
    #    cleaned_responses[k] = v

    cleaned_responses = {}
    for k, v in responses.items():
        if isinstance(v, np.generic):
            v = v.item()
        elif isinstance(v, pd.Series):
            # If Series is a single value
            if v.shape == (1,):
                v = v.item()
            else:
                v = v.tolist()
        elif isinstance(v, pd.DataFrame):
            v = v.to_dict(orient="records")
        cleaned_responses[k] = v



    # write the new table to airtable
    table.create(cleaned_responses)


    if st.session_state.mode == "ASSESSOR":
        st.success("Assessment submitted successfully!")
    elif st.session_state.mode == "REVIEWER":
        st.success("Review submitted successfully!")

    if st.button("Home"):
        st.switch_page("streamlit_app.py")
        st.stop()


