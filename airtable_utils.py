# airtable_utils.py
from shared import *

@st.cache_data
def load_airtable(table_name, base_id, airtable_api_key, debug=False, view="Grid view"):
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
