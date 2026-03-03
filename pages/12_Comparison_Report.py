import streamlit as st
from shared import *
from shared import check_session_timeout, reset_session_timer
from draw import draw_diamond
import io
import re
from matplotlib.backends.backend_pdf import PdfPages

st.set_page_config(layout="centered")

display_logo()
check_session_timeout()
st.title("Comparison Report")

col_top1, col_top2 = st.columns([1, 1])
with col_top1:
    if st.button("Return to Report Selection"):
        reset_session_timer()
        st.switch_page("pages/12_Select_Report.py")
with col_top2:
    if st.button("Home"):
        reset_session_timer()
        st.switch_page("streamlit_app.py")

st.cache_data.clear()

api_key = st.secrets["general"]["airtable_api_key"]
base_id = st.secrets["general"]["airtable_base_id"]

table_data = st.secrets["general"]["airtable_table_data"]
table_assessment = st.secrets["general"]["airtable_table_assessment"]
table_milestones = st.secrets["general"]["airtable_table_milestones"]
table_ventures = st.secrets["general"]["airtable_table_ventures"]
table_projects = st.secrets["general"]["airtable_table_projects"]
table_assessors = st.secrets["general"]["airtable_table_assessors"]
table_reviewers = st.secrets["general"]["airtable_table_reviewers"]

air_data, _ = load_airtable(table_data, base_id, api_key, False)
air_assessment, _ = load_airtable(table_assessment, base_id, api_key, False)
air_milestones, _ = load_airtable(table_milestones, base_id, api_key, False)
air_ventures, _ = load_airtable(table_ventures, base_id, api_key, False)
air_projects, _ = load_airtable(table_projects, base_id, api_key, False)
air_assessors, _ = load_airtable(table_assessors, base_id, api_key, False)
air_reviewers, _ = load_airtable(table_reviewers, base_id, api_key, False)

if air_data.empty:
    st.warning("No records found in the Airtable table.")
    st.stop()


def normalize_linked_id(value):
    if isinstance(value, (list, tuple)):
        return value[0] if value else None
    return value


def has_linked_id(value, target_id):
    if isinstance(value, (list, tuple)):
        return target_id in value
    return value == target_id


def format_date(date_str):
    try:
        if pd.isna(date_str) or not date_str:
            return "[Pending]"
        date_obj = datetime.strptime(str(date_str), '%Y-%m-%d')
        return date_obj.strftime('%d-%b-%Y')
    except Exception:
        return "[Pending]"


def format_month_year(date_str):
    try:
        if pd.isna(date_str) or not date_str:
            return "[Pending]"
        date_obj = datetime.strptime(str(date_str), '%Y-%m-%d')
        return date_obj.strftime('%b-%y')
    except Exception:
        return "[Pending]"


def render_markdown_bold_text(ax, x, y, text, fontsize=8, ha='left', va='center'):
    """Render basic markdown bold (**text**) using matplotlib mathtext."""
    safe_text = str(text).replace('$', '\\$')
    safe_text = re.sub(r'\*\*(.*?)\*\*', r'$\\mathbf{\1}$', safe_text)
    ax.text(x, y, safe_text, fontsize=fontsize, ha=ha, va=va)


def initials(first_name, last_name, fallback="NA"):
    first = str(first_name).strip() if first_name is not None else ""
    last = str(last_name).strip() if last_name is not None else ""
    if first or last:
        return ((first[:1] or "") + (last[:1] or "")).upper() or fallback
    return fallback


def full_name(first_name, last_name, fallback="Unknown"):
    first = str(first_name).strip() if first_name is not None else ""
    last = str(last_name).strip() if last_name is not None else ""
    name = f"{first} {last}".strip()
    return name if name else fallback


def person_from_table(table_df, record_id):
    if not record_id:
        return {"first": "", "last": "", "full": "Unknown", "initials": "NA"}
    row = table_df[table_df["id"] == record_id]
    if row.empty:
        return {"first": "", "last": "", "full": "Unknown", "initials": "NA"}
    first = row.iloc[0].get("First Name", "")
    last = row.iloc[0].get("Last Name", "")
    return {
        "first": first,
        "last": last,
        "full": full_name(first, last),
        "initials": initials(first, last)
    }


if st.session_state.mode == "REVIEWER":
    reviewer_id = st.session_state.reviewer_id[0] if isinstance(st.session_state.reviewer_id, (list, tuple)) else st.session_state.reviewer_id
    reviewer_row = air_reviewers[air_reviewers['id'] == reviewer_id]
    reviewer_support_id = None
    if not reviewer_row.empty:
        support = reviewer_row.iloc[0].get('Support Organization')
        reviewer_support_id = normalize_linked_id(support)

    reviewed_by_me = air_data["REVIEWER"].apply(lambda x: has_linked_id(x, reviewer_id))
    has_completed_assessment = (
        air_data["Assess_date"].notna() &
        (air_data["Assess_date"] != "") &
        (air_data["Assess_date"] != pd.NaT)
    )
    is_not_draft = ~air_data["Name"].astype(str).str.contains("DRAFT", na=False)

    if reviewer_support_id:
        is_in_reviewer_support_org = air_data["Support Organization"].apply(lambda x: has_linked_id(x, reviewer_support_id))
        review_capable = is_in_reviewer_support_org & has_completed_assessment
        air_data = air_data[(reviewed_by_me | review_capable) & is_not_draft]
    else:
        air_data = air_data[reviewed_by_me & is_not_draft]

elif st.session_state.mode == "ASSESSOR":
    assessor_id = st.session_state.assessor_id[0] if isinstance(st.session_state.assessor_id, (list, tuple)) else st.session_state.assessor_id
    air_data = air_data[air_data["ASSESSOR"].apply(lambda x: has_linked_id(x, assessor_id))]
    is_not_draft = ~air_data["Name"].astype(str).str.contains("DRAFT", na=False)
    air_data = air_data[is_not_draft]
else:
    st.warning("Unknown mode.")
    st.stop()

if air_data.empty:
    st.warning("No available records for comparison reporting.")
    st.stop()

air_data = air_data.copy()
air_data["venture_id_norm"] = air_data["Venture"].apply(normalize_linked_id)
air_data["project_id_norm"] = air_data["Project"].apply(normalize_linked_id)

valid_completed = (
    air_data["Assess_date"].notna() &
    (air_data["Assess_date"] != "") &
    (air_data["Assess_date"] != pd.NaT)
)
air_data = air_data[valid_completed]

if air_data.empty:
    st.warning("No completed assessments found for comparison.")
    st.stop()

venture_map = {row["id"]: row.get("Name", row["id"]) for _, row in air_ventures.iterrows()}
project_map = {row["id"]: row.get("Name", row["id"]) for _, row in air_projects.iterrows()}

# Show all ventures/projects from database in dropdowns (not only those currently in filtered records)
venture_ids = sorted([vid for vid in air_ventures["id"].dropna().unique().tolist()], key=lambda x: venture_map.get(x, str(x)))
if not venture_ids:
    st.warning("No venture records available.")
    st.stop()

selected_venture_id = st.selectbox(
    "Select company (venture):",
    options=venture_ids,
    format_func=lambda vid: venture_map.get(vid, vid)
)

venture_row = air_ventures[air_ventures["id"] == selected_venture_id]
linked_projects = []
if not venture_row.empty:
    proj_val = venture_row.iloc[0].get("Projects")
    if isinstance(proj_val, (list, tuple)):
        linked_projects = [pid for pid in proj_val if pid in project_map]

# Also include projects linked by Venture reference in Projects table
projects_by_venture = air_projects[
    air_projects["Venture"].apply(lambda x: has_linked_id(x, selected_venture_id))
]["id"].dropna().tolist() if "Venture" in air_projects.columns else []

project_ids = sorted(list(set(linked_projects + projects_by_venture)), key=lambda x: project_map.get(x, str(x)))

if not project_ids:
    st.warning("No projects available for the selected company.")
    st.stop()

selected_project_id = st.selectbox(
    "Select project:",
    options=project_ids,
    format_func=lambda pid: project_map.get(pid, pid)
)

scope_records = air_data[
    (air_data["venture_id_norm"] == selected_venture_id) &
    (air_data["project_id_norm"] == selected_project_id)
].copy()

if scope_records.empty:
    st.warning("No records available for the selected company/project.")
    st.stop()

scope_records["_display"] = scope_records.apply(
    lambda row: f"{row.get('Name', 'Unnamed')} | Assess: {format_date(row.get('Assess_date'))} | Review: {format_date(row.get('Review_date'))} | ID: {row['id'][-6:]}",
    axis=1
)

record_options = scope_records["id"].tolist()
record_label_map = dict(zip(scope_records["id"], scope_records["_display"]))

st.write("Select assessments/reviews to include:")
selected_records = []
for rid in record_options:
    checkbox_key = f"comparison_record_{rid}"
    checked = st.checkbox(record_label_map.get(rid, rid), value=True, key=checkbox_key)
    if checked:
        selected_records.append(rid)

if not selected_records:
    st.info("Please select at least one record.")
    st.stop()

selected_df = scope_records[scope_records["id"].isin(selected_records)].copy()

comparison_columns = []
for _, row in selected_df.iterrows():
    assessor_id = normalize_linked_id(row.get("ASSESSOR"))
    reviewer_id = normalize_linked_id(row.get("REVIEWER"))

    if assessor_id:
        person = person_from_table(air_assessors, assessor_id)
        comparison_columns.append({
            "role": "ASSESSOR",
            "symbol": "●",
            "person": person,
            "initials": person["initials"],
            "date": row.get("Assess_date"),
            "record_id": row.get("id"),
            "record_name": row.get("Name"),
            "source": row,
            "field_prefix": "QA"
        })

    if reviewer_id and pd.notna(row.get("Review_date")) and str(row.get("Review_date")).strip() != "":
        person = person_from_table(air_reviewers, reviewer_id)
        comparison_columns.append({
            "role": "REVIEWER",
            "symbol": "◆",
            "person": person,
            "initials": person["initials"],
            "date": row.get("Review_date"),
            "record_id": row.get("id"),
            "record_name": row.get("Name"),
            "source": row,
            "field_prefix": "QR"
        })

if not comparison_columns:
    st.warning("No assessor/reviewer columns could be derived from selected records.")
    st.stop()


def parse_date_for_sort(date_str):
    try:
        return datetime.strptime(str(date_str), "%Y-%m-%d")
    except Exception:
        return datetime(1900, 1, 1)


comparison_columns = sorted(
    comparison_columns,
    key=lambda c: (parse_date_for_sort(c["date"]), c["person"]["full"], c["role"])
)

question_text_by_dim = {}
for dim in range(num_dims):
    question_text_by_dim[dim] = {}
    for q in range(numQ):
        field = f"Q{q}"
        if field in air_assessment.columns:
            question_text_by_dim[dim][q] = str(air_assessment.iloc[dim].get(field, f"Question {q}"))
        else:
            question_text_by_dim[dim][q] = f"Question {q}"

milestone_color_by_id = {}
for _, row in air_milestones.iterrows():
    mid = row.get("id")
    raw = row.get("Color")
    if pd.isna(raw) or not raw:
        color = "#FFFFFF"
    else:
        color = raw if str(raw).startswith("#") else f"#{raw}"
    milestone_color_by_id[mid] = color


def milestone_color_for(dim, q):
    try:
        milestone_field = f"Q{q} Milestone"
        milestone_id = air_assessment.iloc[dim].get(milestone_field)
        milestone_id = normalize_linked_id(milestone_id)
        return milestone_color_by_id.get(milestone_id, "#FFFFFF")
    except Exception:
        return "#FFFFFF"


def get_response_value(column_info, dim, q):
    field_name = f"{column_info['field_prefix']}_{dim:02d}_{q}"
    source = column_info["source"]
    if field_name in source.index:
        return bool(source.get(field_name))
    return False


letter_width = 8.5
letter_height = 11
margin = 0.5
page_width = letter_width - 2 * margin
page_height = letter_height - 2 * margin
font_size = 10
column_dx = 0.9 * 7.15 / num_dims
question_col_width = 0.3
section_gap = 0.5
section_header_gap = 0.2
section_bottom_padding = 0.62

# Keep column width fixed (as in standard report), but dynamically size row height
# so exactly two dimensions fit on each page without clipping.
body_top_y = page_height - 1.2
body_bottom_y = 0.35
available_height = body_top_y - body_bottom_y
section_height = (available_height - section_gap) / 2
cell_dy = (section_height - section_header_gap - section_bottom_padding) / numQ

# Safety bounds for readability while guaranteeing print fit.
cell_dy = max(0.18, min(cell_dy, 0.33))

marker_fontsize = 7.5 if column_dx >= 0.36 else 6.5
column_label_fontsize = 7 if column_dx >= 0.36 else 6


figures = []
tooltip_payloads = []


fig_header = plt.figure(figsize=(letter_width, letter_height))
ax_header = fig_header.add_axes([
    margin / letter_width,
    margin / letter_height,
    page_width / letter_width,
    page_height / letter_height
])
ax_header.set_xlim(0, page_width)
ax_header.set_ylim(0, page_height)
ax_header.set_axis_off()

ax_header.text(page_width / 2, page_height - 0.2, "Impact Readiness Level™", fontsize=12, ha='center', va='top', fontweight='bold')
ax_header.text(page_width / 2, page_height - 0.45, "Comparison Report", fontsize=12, ha='center', va='top', fontweight='bold')
ax_header.text(0, page_height - 0.9, f"Company (Venture): {venture_map.get(selected_venture_id, selected_venture_id)}", fontsize=10, ha='left', va='top')
ax_header.text(0, page_height - 1.15, f"Project: {project_map.get(selected_project_id, selected_project_id)}", fontsize=10, ha='left', va='top')

legend_y = page_height - 1.5
ax_header.text(0, legend_y, "Comparison Legend", fontsize=10, ha='left', va='top', fontweight='bold')
legend_y -= 0.25

# Single-column legend layout (up to ~16 entries expected)
legend_cols = 1
legend_col_gap = 0.0
legend_col_width = page_width
legend_row_height = 0.18

for legend_col_idx in range(legend_cols):
    x0 = legend_col_idx * (legend_col_width + legend_col_gap)
    ax_header.text(x0, legend_y, "Symbol", fontsize=8.5, ha='left', va='top', fontweight='bold')
    ax_header.text(x0 + 0.55, legend_y, "Role", fontsize=8.5, ha='left', va='top', fontweight='bold')
    ax_header.text(x0 + 1.35, legend_y, "Name", fontsize=8.5, ha='left', va='top', fontweight='bold')
    ax_header.text(x0 + legend_col_width - 1.1, legend_y, "Date", fontsize=8.5, ha='left', va='top', fontweight='bold')

legend_y -= 0.17

for idx, col in enumerate(comparison_columns):
    legend_col_idx = idx // 16
    legend_row_idx = idx % 16

    if legend_col_idx >= legend_cols:
        break

    x0 = legend_col_idx * (legend_col_width + legend_col_gap)
    y0 = legend_y - (legend_row_idx * legend_row_height)

    role_label = "Assessor" if col['role'] == "ASSESSOR" else "Reviewer"
    ax_header.text(x0, y0, f"{col['symbol']}{col['initials']}", fontsize=8.5, ha='left', va='top')
    ax_header.text(x0 + 0.55, y0, role_label, fontsize=8.5, ha='left', va='top')
    ax_header.text(x0 + 1.35, y0, col['person']['full'], fontsize=8.5, ha='left', va='top')
    ax_header.text(x0 + legend_col_width - 1.1, y0, format_date(col['date']), fontsize=8.5, ha='left', va='top')

# If there are more entries than can fit in the cover legend, notify user
max_legend_entries = legend_cols * 16
if len(comparison_columns) > max_legend_entries:
    ax_header.text(0, legend_y - (16 * legend_row_height) - 0.05,
                   f"+ {len(comparison_columns) - max_legend_entries} additional entries (see matrix column labels)",
                   fontsize=8, ha='left', va='top', color='#606060')

# Milestone color legend on cover page (no progress calculation)
legend_rows_used = min(len(comparison_columns), max_legend_entries)
legend_bottom_y = legend_y - max(legend_rows_used - 1, 0) * legend_row_height

milestones_sorted = air_milestones.copy()

def milestone_sort_key(row):
    for field_name in ["Order", "Milestone", "Level", "Name"]:
        if field_name in row.index:
            raw_val = row.get(field_name)
            if pd.notna(raw_val):
                match = re.search(r"\d+", str(raw_val))
                if match:
                    return int(match.group(0))
    return 10_000

if not milestones_sorted.empty:
    milestones_sorted = milestones_sorted.copy()
    milestones_sorted["_sort_key"] = milestones_sorted.apply(milestone_sort_key, axis=1)
    sort_columns = ["_sort_key"]
    if "Name" in milestones_sorted.columns:
        sort_columns.append("Name")
    milestones_sorted = milestones_sorted.sort_values(by=sort_columns)

# Single-column layout
milestone_row_h = 0.16
milestone_rows = len(milestones_sorted)

# Keep milestones near bottom, but always above footer (y > 0.22)
milestone_bottom_target = 0.32
milestone_start_y_bottom_anchored = milestone_bottom_target + max(milestone_rows - 1, 0) * milestone_row_h

# Ensure milestone block does not collide with comparison legend block above
milestone_start_y_max = legend_bottom_y - 0.50
milestone_start_y = min(milestone_start_y_bottom_anchored, milestone_start_y_max)

# Ensure first milestone title remains safely on-page
milestone_start_y = min(milestone_start_y, page_height - 1.25)

legend_title_y = milestone_start_y + 0.20
ax_header.text(0, legend_title_y, "Milestones", fontsize=9.5, ha='left', va='top', fontweight='bold')

for idx, (_, ms_row) in enumerate(milestones_sorted.iterrows()):
    x0 = 0
    y0 = milestone_start_y - idx * milestone_row_h
    if y0 < 0.22:
        break

    raw_color = ms_row.get("Color")
    if pd.isna(raw_color) or not raw_color:
        ms_color = "#FFFFFF"
    else:
        ms_color = raw_color if str(raw_color).startswith("#") else f"#{raw_color}"

    # Square swatch, no border
    swatch = patches.Rectangle((x0, y0 - 0.10), 0.11, 0.11, facecolor=ms_color, edgecolor='none', lw=0)
    ax_header.add_patch(swatch)

    ms_name = str(ms_row.get("Name", "Milestone"))
    ms_label = str(ms_row.get("Label", ""))
    text_val = f"Milestone **{ms_name}**: {ms_label}" if ms_label else f"Milestone **{ms_name}**"
    render_markdown_bold_text(ax_header, x0 + 0.16, y0 - 0.04, text_val, fontsize=8, ha='left', va='center')

ax_header.text(0, 0.1, "DO NOT DUPLICATE - DO NOT DISTRIBUTE", fontsize=8, ha='left', va='bottom', color='#808080')
ax_header.text(page_width / 2, 0.1, "v. 0.50", fontsize=8, ha='center', va='bottom', color='#808080')
ax_header.text(page_width, 0.1, "© Impact Readiness Ltd. 2024-6", fontsize=8, ha='right', va='bottom', color='#808080')

figures.append(fig_header)
tooltip_payloads.append(None)


def draw_dimension_section(ax, dim, top_y, columns, tooltip_cells):
    section_title = air_assessment.iloc[dim].get("Dimension", f"Dimension {dim}")
    ax.text(0, top_y, f"{section_title}", fontsize=11, ha='left', va='top', fontweight='bold')

    matrix_top = top_y - section_header_gap
    matrix_bottom = matrix_top - (numQ * cell_dy)
    start_x = 0.05

    for q in range(numQ):
        y0 = matrix_bottom + q * cell_dy
        cy = y0 + cell_dy / 2
        ax.text(start_x, cy, q, fontsize=font_size, ha='left', va='center', fontweight='bold')

        for col_idx, col in enumerate(columns):
            x0 = start_x + question_col_width + col_idx * column_dx
            color = milestone_color_for(dim, q)
            rect = patches.Rectangle((x0, y0), column_dx, cell_dy, facecolor=color, edgecolor='white', lw=0.5)
            ax.add_patch(rect)

            if get_response_value(col, dim, q):
                label = f"{col['symbol']}{col['initials']}"
                ax.text(x0 + column_dx / 2, cy, label, fontsize=marker_fontsize, ha='center', va='center', fontweight='bold')

            tooltip_cells.append({
                "x0": x0,
                "y0": y0,
                "x1": x0 + column_dx,
                "y1": y0 + cell_dy,
                "title": f"{section_title} | Q{q}: {question_text_by_dim[dim][q]}"
            })

    # Add month-year at the bottom of each column (e.g., Mar-26)
    label_y = matrix_bottom - 0.08
    for col_idx, col in enumerate(columns):
        x0 = start_x + question_col_width + col_idx * column_dx
        cx = x0 + column_dx / 2
        date_label = format_month_year(col['date'])
        ax.text(cx, label_y, date_label, fontsize=column_label_fontsize, ha='center', va='top')

    return matrix_bottom - section_bottom_padding


for page_start_dim in range(0, num_dims, 2):
    fig = plt.figure(figsize=(letter_width, letter_height))
    ax = fig.add_axes([
        margin / letter_width,
        margin / letter_height,
        page_width / letter_width,
        page_height / letter_height
    ])
    ax.set_xlim(0, page_width)
    ax.set_ylim(0, page_height)
    ax.set_axis_off()

    ax.text(page_width / 2, page_height - 0.2, "Impact Readiness Level™", fontsize=11, ha='center', va='top', fontweight='bold')
    ax.text(page_width / 2, page_height - 0.45, "Comparison Report", fontsize=10, ha='center', va='top')
    ax.text(0, page_height - 0.75, f"Company: {venture_map.get(selected_venture_id, selected_venture_id)}", fontsize=9, ha='left', va='top')
    ax.text(0, page_height - 0.95, f"Project: {project_map.get(selected_project_id, selected_project_id)}", fontsize=9, ha='left', va='top')

    tooltip_cells = []

    top_y = body_top_y
    top_y = draw_dimension_section(ax, page_start_dim, top_y, comparison_columns, tooltip_cells)

    if page_start_dim + 1 < num_dims:
        top_y = top_y - section_gap
        draw_dimension_section(ax, page_start_dim + 1, top_y, comparison_columns, tooltip_cells)

    ax.text(0, 0.1, "DO NOT DUPLICATE - DO NOT DISTRIBUTE", fontsize=8, ha='left', va='bottom', color='#808080')
    ax.text(page_width / 2, 0.1, "v. 0.50", fontsize=8, ha='center', va='bottom', color='#808080')
    ax.text(page_width, 0.1, "© Impact Readiness Ltd. 2024-6", fontsize=8, ha='right', va='bottom', color='#808080')

    figures.append(fig)
    tooltip_payloads.append(tooltip_cells)

col_dl1, col_dl2 = st.columns([1, 2])
with col_dl1:
    pdf_placeholder = st.empty()

for idx, fig in enumerate(figures):
    st.pyplot(fig)

# Attach tooltip handlers once across all dimension pages so hover works for every dimension
tooltip_pages = [cells for cells in tooltip_payloads if cells]
if tooltip_pages:
    tooltip_pages_json = json.dumps(tooltip_pages)
    st.components.v1.html(f"""
    <script>
    (function() {{
        const pages = {tooltip_pages_json};
        const pageW = {page_width};
        const pageH = {page_height};

        function initTooltipsAllPages() {{
            let tooltip = window.parent.document.getElementById('floating-tooltip-comparison');
            if (!tooltip) {{
                tooltip = window.parent.document.createElement('div');
                tooltip.id = 'floating-tooltip-comparison';
                tooltip.style.cssText = 'position: fixed; display: none; background: rgba(255,255,255,0.98); border: 2px solid #333; border-radius: 8px; padding: 8px; max-width: 420px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 10000; pointer-events: none; font-family: sans-serif; font-size: 13px;';
                window.parent.document.body.appendChild(tooltip);
            }}

            let imgs = window.parent.document.querySelectorAll('img[alt="User-uploaded image"]');
            if (imgs.length === 0) imgs = window.parent.document.querySelectorAll('[data-testid="stImage"] img');
            if (imgs.length === 0) imgs = window.parent.document.querySelectorAll('img');

            const needed = pages.length;
            if (imgs.length < needed) {{
                setTimeout(initTooltipsAllPages, 200);
                return;
            }}

            const targetImgs = Array.from(imgs).slice(-needed);

            targetImgs.forEach((img, idx) => {{
                if (img.dataset.comparisonTooltipBound === '1') return;
                img.dataset.comparisonTooltipBound = '1';

                const cells = pages[idx] || [];
                img.addEventListener('mousemove', function(e) {{
                    const rect = img.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;

                    const figX = (x / rect.width) * pageW;
                    const figY = pageH - (y / rect.height) * pageH;

                    let found = null;
                    for (const cell of cells) {{
                        if (figX >= cell.x0 && figX <= cell.x1 && figY >= cell.y0 && figY <= cell.y1) {{
                            found = cell;
                            break;
                        }}
                    }}

                    if (found) {{
                        tooltip.innerHTML = found.title;
                        tooltip.style.left = (e.clientX + 15) + 'px';
                        tooltip.style.top = (e.clientY + 15) + 'px';
                        tooltip.style.display = 'block';
                    }} else {{
                        tooltip.style.display = 'none';
                    }}
                }});

                img.addEventListener('mouseleave', function() {{
                    tooltip.style.display = 'none';
                }});
            }});
        }}

        setTimeout(initTooltipsAllPages, 250);
    }})();
    </script>
    """, height=0)

pdf_buffer = io.BytesIO()
with PdfPages(pdf_buffer) as pdf:
    for fig in figures:
        pdf.savefig(fig, dpi=300)
pdf_buffer.seek(0)

pdf_placeholder.download_button(
    label="Save Comparison Report as PDF",
    data=pdf_buffer,
    file_name=f"IRL_Comparison_Report_{venture_map.get(selected_venture_id, 'Venture')}_{project_map.get(selected_project_id, 'Project')}.pdf",
    mime="application/pdf",
    key="comparison_pdf_download"
)

for fig in figures:
    plt.close(fig)
