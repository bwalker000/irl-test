# airtable_utils.py

from shared import *

@st.cache_data
def load_airtable(table_name, debug=False, base_id=None, airtable_api_key=None, view="Grid view"):
    # Use default from env if not provided
    base_id = base_id or os.getenv("BASE_ID")
    airtable_api_key = airtable_api_key or os.getenv("AIRTABLE_API_KEY")
    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    headers = {"Authorization": f"Bearer {airtable_api_key}"}
    params = {"view": view}
    response = requests.get(url, headers=headers, params=params)
    try:
        data = response.json()
    except Exception as e:
        data = {"error": f"JSON parse error: {e}"}
    records = data.get("records", [])
    df = pd.DataFrame([r.get("fields", {}) for r in records]) if records else pd.DataFrame()
    details = {
        "url": url,
        "status_code": response.status_code,
        "response_headers": dict(response.headers),
        "raw_response": data,
        "records_count": len(records),
    }
    return df, details
