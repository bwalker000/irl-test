# airtable_utils.py

import streamlit as st
import pandas as pd
from pyairtable import Table
from pyairtable.formulas import match
from pyairtable import Api
import requests
import json
import numpy as np
import os
from datetime import datetime, date


from fields import IRL_050_data_fields as expected_fields


@st.cache_data(ttl=60)  # Cache for 60 seconds max
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

    def process_value(v):
        if isinstance(v, list):
            return tuple(v)  # Convert lists to tuples as they are hashable
        return v

    if (table_name == st.secrets["general"]["airtable_table_data"]):
        df = pd.DataFrame([
            {field: process_value(r.get("fields", {}).get(field, None)) for field in expected_fields} | {"id": r["id"]}
            for r in records
        ]) if records else pd.DataFrame(columns=expected_fields + ["id"])

    else:
        df = pd.DataFrame([
            {k: process_value(v) for k, v in r.get("fields", {}).items()} | {"id": r["id"]}
            for r in records
        ]) if records else pd.DataFrame()

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
            return True
        elif user_email in reviewer_emails:
            st.session_state.mode = 'REVIEWER'
            return True
        else:
            return False
    return True if 'mode' in st.session_state else False



def auto_save_progress():
    """
    Auto-save current assessment/review progress as a draft.
    Overwrites any existing draft for this venture/project/mode combination.
    """
    # Build draft record similar to submit_record but without dates
    responses = {}
    
    # Save question responses
    for dim in range(st.session_state.QA.shape[0]):
        for i, value in enumerate(st.session_state.QA[dim]):
            field_name = f"QA_{dim:02d}_{i}"
            responses[field_name] = value

    for dim in range(st.session_state.QR.shape[0]):
        for i, value in enumerate(st.session_state.QR[dim]):
            field_name = f"QR_{dim:02d}_{i}"
            responses[field_name] = value

    # Save text responses
    for dim, value in enumerate(st.session_state.TA):
        field_name = f"TA_{dim:02d}"
        responses[field_name] = value

    for dim, value in enumerate(st.session_state.TR):
        field_name = f"TR_{dim:02d}"
        responses[field_name] = value

    # Add metadata
    responses["Venture"] = ([st.session_state.venture_id] if isinstance(st.session_state.venture_id, str) 
                          else list(st.session_state.venture_id) if isinstance(st.session_state.venture_id, (list, tuple)) 
                          else [])
    
    responses["Project"] = ([st.session_state.project_id] if isinstance(st.session_state.project_id, str)
                          else list(st.session_state.project_id) if isinstance(st.session_state.project_id, (list, tuple))
                          else [])
    
    responses["Support Organization"] = ([st.session_state.support_id[0]] if isinstance(st.session_state.support_id, (list, tuple)) and st.session_state.support_id
                                       else [st.session_state.support_id] if st.session_state.support_id
                                       else [])
    
    # For independent reviews, assessor_id might be empty
    if st.session_state.mode == "REVIEWER" and (
        st.session_state.get('assessor_first_name', 'N/A') == 'N/A' or 
        not st.session_state.get('assessor_id')
    ):
        responses["ASSESSOR"] = []
    else:
        responses["ASSESSOR"] = ([st.session_state.assessor_id[0]] if isinstance(st.session_state.assessor_id, (list, tuple)) and st.session_state.assessor_id
                               else [st.session_state.assessor_id] if st.session_state.assessor_id
                               else [])

    venture_name = st.session_state.venture_name
    project_name = st.session_state.project_name
    
    # Create DRAFT name
    draft_name = f"DRAFT - {venture_name} - {project_name}"
    
    if st.session_state.mode == "REVIEWER":
        # Add reviewer ID
        responses["REVIEWER"] = ([st.session_state.reviewer_id[0]] if isinstance(st.session_state.reviewer_id, (list, tuple))
                               else [st.session_state.reviewer_id] if st.session_state.reviewer_id
                               else [])
        # Preserve assessment date if reviewing existing assessment
        if st.session_state.get('assessment_name') and st.session_state.get('assess_date'):
            responses["Assess_date"] = st.session_state.assess_date
    
    responses["Name"] = draft_name
    # Note: No Assess_date or Review_date = indicates this is a draft
    
    api_key = st.secrets["general"]["airtable_api_key"]
    base_id = st.secrets["general"]["airtable_base_id"]
    table_name = st.secrets["general"]["airtable_table_data"]
    table = Table(api_key, base_id, table_name)

    # Clean numpy types
    cleaned_responses = {}
    for k, v in responses.items():
        if isinstance(v, np.generic):
            v = v.item()
        elif isinstance(v, pd.Series):
            if v.shape == (1,):
                v = v.item()
            else:
                v = v.tolist()
        elif isinstance(v, pd.DataFrame):
            v = v.to_dict(orient="records")
        cleaned_responses[k] = v

    # Check if draft already exists and update it, otherwise create new
    if 'draft_record_id' in st.session_state and st.session_state.draft_record_id:
        try:
            table.update(st.session_state.draft_record_id, cleaned_responses)
        except:
            # If update fails (record deleted), create new
            record = table.create(cleaned_responses)
            st.session_state.draft_record_id = record['id']
    else:
        record = table.create(cleaned_responses)
        st.session_state.draft_record_id = record['id']


def submit_record():
    # This code saves the assessment to the airtable database
    responses = {}

    # DEBUG: Show session state values before processing
    st.write("### DEBUG - Session State Values Before Processing")
    st.write(f"**venture_id:** {st.session_state.venture_id} (type: {type(st.session_state.venture_id)})")
    st.write(f"**project_id:** {st.session_state.project_id} (type: {type(st.session_state.project_id)})")
    st.write(f"**support_id:** {st.session_state.support_id} (type: {type(st.session_state.support_id)})")
    st.write(f"**assessor_id:** {st.session_state.assessor_id} (type: {type(st.session_state.assessor_id)})")

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

    # Helper function to extract ID from various data types
    def extract_id(value):
        if isinstance(value, pd.Series):
            # If it's a Series, get the first (and likely only) value
            return value.iloc[0] if len(value) > 0 else None
        elif isinstance(value, (list, tuple)):
            # If it's a list or tuple, get the first element
            return value[0] if len(value) > 0 else None
        elif isinstance(value, str):
            # If it's already a string, return as-is
            return value
        else:
            # For other types, convert to string or return None
            return str(value) if value is not None else None

    # Extract IDs using the helper function
    venture_id = extract_id(st.session_state.venture_id)
    project_id = extract_id(st.session_state.project_id)
    support_id = extract_id(st.session_state.support_id)
    assessor_id = extract_id(st.session_state.assessor_id)

    # Convert IDs to lists for Airtable linked records
    responses["Venture"] = [venture_id] if venture_id else []
    responses["Project"] = [project_id] if project_id else []
    responses["Support Organization"] = [support_id] if support_id else []
    
    # For independent reviews, assessor_id might be empty
    if st.session_state.mode == "REVIEWER" and (
        st.session_state.get('assessor_first_name', 'N/A') == 'N/A' or 
        not st.session_state.get('assessor_id')
    ):
        responses["ASSESSOR"] = []  # Independent review, no assessor
    else:
        responses["ASSESSOR"] = [assessor_id] if assessor_id else []

    # DEBUG: Show what was assigned to responses
    st.write("### DEBUG - Linked Record Fields After Processing")
    st.write(f"**Venture:** {responses['Venture']} (type: {type(responses['Venture'])})")
    st.write(f"**Project:** {responses['Project']} (type: {type(responses['Project'])})")  
    st.write(f"**Support Organization:** {responses['Support Organization']} (type: {type(responses['Support Organization'])})")
    st.write(f"**ASSESSOR:** {responses['ASSESSOR']} (type: {type(responses['ASSESSOR'])})")

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
        
        # DEBUG: Show what we just set for reviewer mode
        st.write("### DEBUG - REVIEWER Mode Field Assignment")
        st.write(f"**Setting Name:** {responses['Name']}")
        st.write(f"**Setting Review_date:** {responses['Review_date']}")
        st.write(f"**Assessment Name in session:** {st.session_state.get('assessment_name', 'None')}")
        
        # Add reviewer ID to the record
        responses["REVIEWER"] = ([st.session_state.reviewer_id[0]] if isinstance(st.session_state.reviewer_id, (list, tuple))
                               else [st.session_state.reviewer_id] if st.session_state.reviewer_id
                               else [])
        
        # Preserve the original assessment date if reviewing an existing assessment
        if st.session_state.get('assessment_name'):
            responses["Assess_date"] = st.session_state.get('assess_date')
            st.write(f"**Preserving Assess_date:** {responses['Assess_date']} (existing assessment review)")
        # For independent reviews, ensure we don't preserve any assessment date
        elif not st.session_state.get('assessment_name'):
            # This is an independent review - make sure no Assess_date is set
            responses.pop("Assess_date", None)
            st.write("**Independent review detected - removed any Assess_date**")

    api_key = st.secrets["general"]["airtable_api_key"]
    base_id = st.secrets["general"]["airtable_base_id"]
    table_name = st.secrets["general"]["airtable_table_data"]

    table = Table(api_key, base_id, table_name)

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

    # DEBUG: Show final cleaned responses for linked records
    st.write("### DEBUG - Final Cleaned Responses for Linked Records")
    for key in ['Venture', 'Project', 'Support Organization', 'ASSESSOR', 'REVIEWER']:
        if key in cleaned_responses:
            st.write(f"**{key}:** {cleaned_responses[key]} (type: {type(cleaned_responses[key])})")
    
    # DEBUG: Show Name and Review_date specifically for independent reviews
    st.write("### DEBUG - Name and Date Fields")
    st.write(f"**Name:** {cleaned_responses.get('Name', 'NOT SET')} (type: {type(cleaned_responses.get('Name', 'NOT SET'))})")
    st.write(f"**Review_date:** {cleaned_responses.get('Review_date', 'NOT SET')} (type: {type(cleaned_responses.get('Review_date', 'NOT SET'))})")
    st.write(f"**Assess_date:** {cleaned_responses.get('Assess_date', 'NOT SET')} (type: {type(cleaned_responses.get('Assess_date', 'NOT SET'))})")
    st.write(f"**Mode:** {st.session_state.mode}")
    st.write(f"**Assessment Name:** {st.session_state.get('assessment_name', 'None (Independent Review)')}")

    # TEMPORARILY BYPASS CONFIRMATION - AUTO SUBMIT FOR DEBUGGING
    st.write("### 🚀 AUTO-SUBMITTING FOR DEBUG (No confirmation needed)")
    print("🔥 TERMINAL: AUTO-SUBMITTING - Starting submission process...")
    st.write("### 🔥 AUTO-SUBMITTING - Starting submission process...")
    print("📝 TERMINAL: About to call Airtable API...")
    st.write("### 📝 About to call Airtable API...")
    
    try:
            # Determine which record to update
            record_id_to_update = None
            
            # Priority 1: If reviewing an existing assessment, update that record
            if st.session_state.mode == "REVIEWER" and st.session_state.get('assessment_record_id'):
                record_id_to_update = st.session_state.assessment_record_id
                st.write(f"**DEBUG:** Updating existing assessment record: {record_id_to_update}")
            # Priority 2: If there's a draft, overwrite it
            elif st.session_state.get('draft_record_id'):
                record_id_to_update = st.session_state.draft_record_id
                st.write(f"**DEBUG:** Updating draft record: {record_id_to_update}")
            else:
                st.write("**DEBUG:** Creating new record")
            
            print("🚀 TERMINAL: ATTEMPTING AIRTABLE OPERATION...")
            st.write("### 🚀 ATTEMPTING AIRTABLE OPERATION...")
            
            if record_id_to_update:
                print(f"📞 TERMINAL: Calling table.update() with record_id: {record_id_to_update}")
                print(f"📞 TERMINAL: Data being sent: Name={cleaned_responses.get('Name')}, Review_date={cleaned_responses.get('Review_date')}")
                st.write(f"**Calling table.update() with record_id: {record_id_to_update}**")
                result = table.update(record_id_to_update, cleaned_responses)
                print(f"✅ TERMINAL: UPDATE SUCCESS - Result: {result}")
            else:
                print("📞 TERMINAL: Calling table.create() for new record")
                st.write("**Calling table.create() for new record**")
                result = table.create(cleaned_responses)
                print(f"✅ TERMINAL: CREATE SUCCESS - Result: {result}")

            print("🎉 TERMINAL: Record submitted successfully!")
            st.success("🎉 Record submitted successfully!")
            
            # DEBUG: Show what was actually submitted AFTER successful submission
            print("### 🎯 TERMINAL: FINAL DEBUG - What Was Actually Submitted to Airtable")
            print(f"TERMINAL: Operation: {'UPDATE' if record_id_to_update else 'CREATE'}")
            if record_id_to_update:
                print(f"TERMINAL: Record ID Updated: {record_id_to_update}")
            print(f"TERMINAL: Name sent: {cleaned_responses.get('Name', 'NOT SENT')}")
            print(f"TERMINAL: Review_date sent: {cleaned_responses.get('Review_date', 'NOT SENT')}")
            print(f"TERMINAL: Assess_date sent: {cleaned_responses.get('Assess_date', 'NOT SENT')}")
            print(f"TERMINAL: REVIEWER sent: {cleaned_responses.get('REVIEWER', 'NOT SENT')}")
            print(f"TERMINAL: Venture sent: {cleaned_responses.get('Venture', 'NOT SENT')}")
            print(f"TERMINAL: Project sent: {cleaned_responses.get('Project', 'NOT SENT')}")
            
            st.write("### 🎯 FINAL DEBUG - What Was Actually Submitted to Airtable")
            st.write(f"**Operation:** {'UPDATE' if record_id_to_update else 'CREATE'}")
            if record_id_to_update:
                st.write(f"**Record ID Updated:** {record_id_to_update}")
            st.write(f"**Name sent:** {cleaned_responses.get('Name', 'NOT SENT')}")
            st.write(f"**Review_date sent:** {cleaned_responses.get('Review_date', 'NOT SENT')}")
            st.write(f"**Assess_date sent:** {cleaned_responses.get('Assess_date', 'NOT SENT')}")
            st.write(f"**REVIEWER sent:** {cleaned_responses.get('REVIEWER', 'NOT SENT')}")
            st.write(f"**Venture sent:** {cleaned_responses.get('Venture', 'NOT SENT')}")
            st.write(f"**Project sent:** {cleaned_responses.get('Project', 'NOT SENT')}")
            
            st.write("### 📋 AIRTABLE API RESPONSE:")
            st.json(result)
            
            # Clean up draft reference
            if 'draft_record_id' in st.session_state:
                del st.session_state.draft_record_id

            # Mark as submitted to prevent resubmission
            st.session_state.submitted = True
            
            print("✅ TERMINAL: SUBMISSION COMPLETE - Session state updated")
            st.write("### ✅ SUBMISSION COMPLETE - Session state updated")

            if st.session_state.mode == "ASSESSOR":
                st.success("Assessment submitted successfully!")
            elif st.session_state.mode == "REVIEWER":
                st.success("Review submitted successfully!")
                
        except Exception as e:
            print(f"💥 TERMINAL: SUBMISSION FAILED - Exception occurred: {str(e)}")
            print(f"TERMINAL: Record ID to update: {locals().get('record_id_to_update', 'NOT SET')}")
            print(f"TERMINAL: Cleaned responses keys: {list(cleaned_responses.keys()) if 'cleaned_responses' in locals() else 'NOT AVAILABLE'}")
            
            st.error("### 💥 SUBMISSION FAILED - Exception occurred!")
            st.error(f"**Error message:** {str(e)}")
            st.write("**Full error details:**")
            st.exception(e)
            st.write("### 📋 DEBUG INFO AT TIME OF ERROR:")
            st.write(f"**Record ID to update:** {locals().get('record_id_to_update', 'NOT SET')}")
            st.write(f"**Cleaned responses keys:** {list(cleaned_responses.keys()) if 'cleaned_responses' in locals() else 'NOT AVAILABLE'}")
            st.write(f"**Table object:** {table if 'table' in locals() else 'NOT AVAILABLE'}")

    # Show home button
    if st.button("Return to Home"):
        # Store current user state that we want to preserve
        preserved_state = {
            'mode': st.session_state.mode,
            'assessor_id': st.session_state.get('assessor_id'),
            'reviewer_id': st.session_state.get('reviewer_id'),
        }

        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        # Restore preserved state
        for key, value in preserved_state.items():
            st.session_state[key] = value
            
        st.switch_page("streamlit_app.py")


