# Copilot Instructions for AI Coding Agents

## Project Overview
This codebase is a Streamlit application for managing assessments and reviews, integrating with Airtable as the backend data source. The main logic is split across:
- `streamlit_app.py`: Main entry point for the app.
- `pages/`: Contains Streamlit pages, named by user role and workflow step (see below).
- Utility modules: `airtable_utils.py`, `fields.py`, `shared.py` for shared logic and Airtable integration.

## Page Naming Convention
- All page files in `pages/` start with a digit:
  - `0_`: Non-customer (public/login/demo/about)
  - `1_`: Assessor workflow
  - `2_`: Reviewer workflow
- Example: `2_Initiate_Review.py` is for reviewers to start a review.

## Data Flow & Architecture
- Session state (`st.session_state`) is used to pass user, assessment, and review context between pages.
- Airtable tables are loaded via `load_airtable()` (see `shared.py` and `airtable_utils.py`). Table names are stored in `st.secrets`.
- Data selection and filtering is performed using Pandas DataFrames after loading from Airtable.
- Navigation between pages uses `st.switch_page()`.

## Developer Workflows
- No explicit build step; run with `streamlit run streamlit_app.py`.
- Debugging: Use the `debug` variable in pages to enable verbose Airtable output.
- Requirements: All dependencies are listed in `requirements.txt`.

## Project-Specific Patterns
- Always use session state for cross-page data (e.g., `st.session_state.assessor_id`).
- When filtering Airtable data, use Pandas masks for support org, review status, etc.
- For independent reviews, set assessor fields to default values (see `2_Initiate_Review.py`).
- Page logic is role-driven; check session state to determine user type and available actions.

## Integration Points
- Airtable API: All data is fetched and updated via Airtable tables, with table names/IDs in `st.secrets`.
- Streamlit UI: Use segmented controls, selectboxes, and buttons for navigation and selection.

## Key Files
- `streamlit_app.py`: App entry, home page, navigation.
- `pages/`: All workflow steps, organized by role and step.
- `airtable_utils.py`, `shared.py`: Airtable and shared logic.
- `requirements.txt`: Python dependencies.

## Example Patterns
- Reviewer workflow: See `pages/2_Initiate_Review.py` for session state setup and Airtable filtering.
- Assessor workflow: See `pages/1_New_Assessment.py`.

---
If any section is unclear or missing, please provide feedback to improve these instructions.
