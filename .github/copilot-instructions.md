# Copilot Instructions for AI Coding Agents

## Project Overview
This codebase is a Streamlit application for managing Impact Readiness Level (IRL) assessments and reviews, integrating with Airtable as the backend data source. The system supports role-based workflows for assessors and reviewers across ventures/projects.

**Core Architecture:**
- `streamlit_app.py`: Entry point with Auth0 authentication and role-based routing
- `pages/`: Role-specific Streamlit pages with numbered naming convention 
- `shared.py`: Common utilities, session management, and configuration
- `airtable_utils.py`: All Airtable CRUD operations and caching
- `fields.py`: Data structure definitions for IRL assessment dimensions

## Page Naming Convention & Navigation
Pages are prefixed by role and workflow step:
- `0_`: Public/demo pages (non-authenticated users)
- `1_`: Assessor workflow (create assessments, projects)
- `2_`: Reviewer workflow (initiate reviews, create ventures)  
- `12_`: Shared assessment/review execution and reporting

**Critical Navigation Pattern:**
```python
# Every page must include session timeout checks
from shared import check_session_timeout, reset_session_timer
check_session_timeout()  # At page entry
reset_session_timer()   # On user interactions
```

## Authentication & Session Management
- **Auth0 Integration:** Uses `st.user.is_logged_in` and `st.user.email` with fallback detection
- **30-minute session timeout:** Auto-logout implemented via `shared.py` timer functions
- **Role validation:** Users must exist in either Assessors or Reviewers Airtable tables
- **Cross-page state:** Extensive use of `st.session_state` for user context, assessment data

## Airtable Integration Patterns
**Table Structure:** Multiple related tables (assessors, reviewers, ventures, projects, data, support orgs)

**Critical Patterns:**
```python
# Always load secrets consistently
api_key = st.secrets["general"]["airtable_api_key"]
base_id = st.secrets["general"]["airtable_base_id"]
table_name = st.secrets["general"]["airtable_table_[tablename]"]

# Use cached loading with TTL
air_data, debug_info = load_airtable(table_name, base_id, api_key, debug=False)

# Filter by support organization using pandas masks
org_filter = air_data['Support Organization'] == st.session_state.support_id
```

**ID Relationships:** Airtable stores relationships as arrays of IDs. Use `airtable_value_from_id()` to resolve references between tables.

## Assessment Data Structure
**Dynamic Dimensions:** Assessment has 16 dimensions (calculated from `fields.py` TA_ fields)
- `QA_XX_Y`: Assessor question responses (16 dimensions × 10 questions each)
- `QR_XX_Y`: Reviewer question responses  
- `TA_XX`: Assessor total scores per dimension
- `TR_XX`: Reviewer total scores per dimension

**Session State Management:**
```python
# Clear assessment state when starting new assessment
for key in ['dim', 'QA', 'QR', 'TA', 'TR', 'assessment_record_id']:
    if key in st.session_state:
        del st.session_state[key]
```

## Developer Workflows
**Running:** `streamlit run streamlit_app.py` (no build step required)
**Debugging:** Set `debug = True` in pages to enable verbose Airtable API logging
**Cache Management:** Use `st.cache_data.clear()` at page entry to ensure fresh data

## Role-Based Logic Patterns
**Support Organization Filtering:** Both assessors and reviewers belong to support organizations. Filter data by support org to show only relevant ventures/projects.

**Independent Review Mode:** When reviewers initiate independent reviews, set assessor fields to default values and clear assessor session state.

**Mode Switching:** Use `st.session_state.mode = "ASSESSOR"` or `"REVIEWER"` to control page behavior in shared workflows.

## Error Handling & Edge Cases  
- **Auth fallback:** Graceful degradation when `st.user` attributes unavailable
- **Missing data:** Always check for record existence before accessing Airtable relationships
- **Session cleanup:** Clear session state on logout and navigation between major workflows
- **ID extraction:** Use helper functions to handle various Airtable ID formats (strings, lists, nested objects)

## Assessment/Review Execution Flow
**Core Execution Pattern:** All assessments and reviews execute through `pages/12_Assess_&_Review.py`

**Session State Initialization:**
```python
# Assessment matrix: 16 dimensions × 10 questions each
st.session_state.QA = np.zeros((num_dims, numQ), dtype=bool)  # Assessor responses
st.session_state.QR = np.zeros((num_dims, numQ), dtype=bool)  # Reviewer responses
st.session_state.TA = [""]*num_dims  # Assessor text comments
st.session_state.TR = [""]*num_dims  # Reviewer text comments
st.session_state.dim = 0  # Current dimension (0-15)
```

**Three Execution Modes:**
1. **New Assessment** (`mode="ASSESSOR"`): Creates fresh assessment data
2. **Review Existing Assessment** (`mode="REVIEWER"` + `assessment_record_id`): Loads existing assessor data, reviewer adds responses
3. **Independent Review** (`mode="REVIEWER"` + `assessor_id=[]`): Reviewer-only assessment with assessor fields set to defaults

**Draft/Resume Logic:**
- Auto-saves progress via `auto_save_progress()` on navigation and timeout
- Resume drafts detected by matching venture/project without completion dates
- Copy previous assessments feature allows reusing past responses

**Navigation Flow:**
- Previous/Next buttons move between dimensions (`st.session_state.dim`)
- Submit button appears only on final dimension (15)
- Home button triggers auto-save before returning to `streamlit_app.py`

## Page Transition Logic & `st.switch_page()` Patterns
**Role-Based Entry Points:**
```python
# Assessor workflow
"streamlit_app.py" → "pages/1_Assessor_Home.py" → "pages/1_New_Assessment.py" → "pages/12_Assess_&_Review.py"

# Reviewer workflow  
"streamlit_app.py" → "pages/2_Reviewer_Home.py" → "pages/2_Initiate_Review.py" → "pages/12_Assess_&_Review.py"
```

**Critical Transition Rules:**
1. **Always call `reset_session_timer()` before `st.switch_page()`** to maintain session activity
2. **Call `auto_save_progress()` before leaving assessment pages** to preserve work
3. **Use `st.rerun()` within same page** for state updates (dimension navigation)
4. **Return to `streamlit_app.py`** for main navigation hub and logout scenarios

**Session State Cleanup Patterns:**
```python
# Clear assessment state when starting new workflow
for key in ['dim', 'QA', 'QR', 'TA', 'TR', 'assessment_record_id', 'draft_record_id']:
    if key in st.session_state:
        del st.session_state[key]
```

**Mode-Specific Navigation:**
- Independent reviews: Clear `assessment_name = None` and `assessor_id = []`
- Draft resumption: Set `draft_record_id` before transitioning to execution
- Assessment copying: Pre-populate arrays before transitioning

## Submission & Data Persistence
**Submit Flow:** `pages/12_Assess_&_Review.py` Submit button → `submit_record()` in `airtable_utils.py`

**Three Submission Workflows:**
1. **Assess and Submit** (`mode="ASSESSOR"`): Assessor creates new assessment, sets `Assess_date`
2. **Review Existing Assessment** (`mode="REVIEWER"` + `assessment_record_id`): Reviewer adds review data to existing assessment record, sets `Review_date` and preserves original `Assess_date`
3. **Independent Review** (`mode="REVIEWER"` + `assessor_id=[]`): Reviewer creates standalone review with no assessor data, sets `Review_date` only

**Record Update Logic:**
- **Priority 1:** Update existing assessment record if `assessment_record_id` exists (review workflow)
- **Priority 2:** Update draft record if `draft_record_id` exists (resume workflow)  
- **Default:** Create new record (new assessment or independent review)

**Data Transformation:**
- Convert numpy boolean arrays to Python bools for Airtable compatibility
- Extract IDs from lists/tuples for linked record fields
- Wrap single IDs in arrays for Airtable linked record format
- Independent reviews: Set `ASSESSOR` field to empty array `[]`

## Key Files for Reference
- `pages/12_Assess_&_Review.py`: Core execution engine with dimension navigation and submission logic
- `pages/2_Initiate_Review.py`: Independent review setup and existing assessment loading
- `pages/1_New_Assessment.py`: Draft detection, resume logic, and assessment copying
- `airtable_utils.py`: `submit_record()`, `auto_save_progress()`, and `assessor_or_reviewer()` functions
- `shared.py`: Session timeout, configuration, and common utilities
