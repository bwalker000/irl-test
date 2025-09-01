from shared import *

# Assumptions:
#        A specific ASSESSOR is intrinsically tied to:
#            A specific venture
#        A specific venture is intrinsically tied to:
#            A specific support organization
#        The ASSESSOR can select which project they are interested in assessing.


st.title("Initiate a Review of an existing Assessment")

# Debug mode toggle
#debug = st.checkbox("Enable Airtable debug mode", value=False)
debug = False

# ---------------------------------------------------------------------------------
# initiate the pyairtable API
api_key = st.secrets["general"]["airtable_api_key"]
api = Api(api_key)

#---------------------------------------------------------------------------------
# The only options available should be for the support org associated with the reviewer

# 1. Figure out which ventures are associated with the reviewers support org.
# 2. Reviewer selects which assessment they would like to review
# 3. Then move on to performing the review

#---------------------------------------------------------------------------------
# load airtable Reviewers table
base_id = st.secrets["general"]["airtable_base_id"]
table_name = st.secrets["general"]["airtable_table_reviewers"]

air_reviewers = api.table(base_id, table_name)

record = air_reviewers.all(formula=match({"Email": st.session_state.reviewer_email}))

df_record = pd.json_normalize(record)

st.session_state.reviewer_id  = df_record["id"].tolist()
st.session_state.reviewer_first_name  = df_record["fields.First Name"].tolist()
st.session_state.reviewer_last_name  = df_record["fields.Last Name"].tolist()
st.session_state.support_id = df_record["fields.Support Organizations"].tolist()

#---------------------------------------------------------------------------------
# Load name of the id of support organization

# load airtable Support table
table_name = st.secrets["general"]["airtable_table_support"]
air_support = api.table(base_id, table_name)

record = air_support.get(st.session_state.support_id[0][0])

df_record = pd.json_normalize(record)

st.session_state.support_name = df_record["fields.Name"].tolist()


#---------------------------------------------------------------------------------
# Select between independent review OR review of assessment

option_map = {
    0: "Review Existing Assessment",
    1: "Perform Independent Review",
}

st.session_state.review_mode = st.segmented_control(
    "",
    options=option_map.keys(),
    format_func=lambda option: option_map[option],
    selection_mode="single",
)

#---------------------------------------------------------------------------------
# no review mode selected

if st.session_state.review_mode == None:
    st.write("Select a review mode to continue")

#---------------------------------------------------------------------------------
# Perform a review of an existing assessment

elif st.session_state.review_mode == 0:
    st.write("Select among existing assessments to review")

    table_name = st.secrets["general"]["airtable_table_data"]
    air_data = api.table(base_id, table_name)

    st.session_state.support_id
    st.write(pd.json_normalize(air_data.all()))

    air_data_records = air_data.all(formula=match({"Support Organization": st.session_state.support_id[0][0]}))

    df_air_data_records = pd.json_normalize(air_data_records)

    df_air_data_records

# prepare a list of existing assessments
# clean up the list for review. 
# perhaps present a dataframe with a radio button?


#---------------------------------------------------------------------------------
# Perform an independent review

elif st.session_state.review_mode == 1:
    st.write("Perform an independent review")

# Easier to make a single list with all ventures and projects.

# go into the "Support Organizations" table and select all ventures associated with this support org
# then got into the "Ventures" table and select all the projects associated with those ventures







# Build a set of ventures associated with the support org

venture_ids = df_record["fields.Ventures"].tolist()

venture_ids

# load airtable Data table for records corresponding to the support org
table_name = st.secrets["general"]["airtable_table_data"]

st.write('testing')




table = Table(api_key, base_id, table_name)
formula = match({"Support Organization": st.session_state.support_id[0]})

records = table.all(formula=formula)
record_ids = [record["id"] for record in records]

records
pd.json_normalize(records)


record_ids


#---------------------------------------------------------------------------------
# Prepare a list of the assessments ready for review

# Do I want a pulldown, or a list with a radio button? 
# Seems like there is too much information for a pulldown.
# That leads to a list with a single select radio button.

# Does the assesssment need to be tied to the reviewer, or just the support org?
# I think that the support org.

# Need to find all assessments associated with the support org
# Then need to filter out all the assessments that have had a review performed.
# Then need to build the selection mechanism.





# load airtable ASSESSORs table
table_name = st.secrets["general"]["airtable_table_assessors"]
air_assessors, debug_details = load_airtable(table_name, base_id, api_key, debug)

# load airtable Ventures table
table_name = st.secrets["general"]["airtable_table_ventures"]
air_ventures, debug_details = load_airtable(table_name, base_id, api_key, debug)



row = air_assessors.loc[air_assessors["Email"] == st.session_state.assessor_email]

st.session_state.assessor_id = row["id"].tolist()

st.session_state.assessor_first_name = row.iloc[0]["First Name"]
st.session_state.assessor_last_name = row.iloc[0]["Last Name"]

st.session_state.support_id = row.iloc[0]["Organization"]
st.session_state.venture_id = row.iloc[0]["Venture"]

st.session_state.support_name = airtable_value_from_id(air_support, 
        st.session_state.support_id, "Name")
st.session_state.venture_name = airtable_value_from_id(air_ventures, 
        st.session_state.venture_id, "Name")

#
# Display details about the assessment
#
with st.container(border=True):

    col1, col2 = st.columns(2)
    col1.write("__Assessor:__")
    col2.write(f"{st.session_state.assessor_first_name} {st.session_state.assessor_last_name}")

    col1.write("__Support Organization:__")
    col2.write(st.session_state.support_name)

    col1.write("__Venture:__")
    col2.write(st.session_state.venture_name)

    #
    # Select among projects
    #

    # Load secrets
    table_name = st.secrets["general"]["airtable_table_projects"]

    # load airtable data
    air_projects, debug_details = load_airtable(table_name, base_id, api_key, debug)

    #air_projects
    #venture_id
    #air_projects.iloc[0]["Venture"][0]

    records = air_projects[air_projects["Venture"].apply(lambda x: x[0] == st.session_state.venture_id[0])]

    project_names = records['Name']

    # Streamlit selectbox for choosing the Project
    st.session_state.project_name = st.selectbox('__Project:__', options=project_names)

    #st.write("\n")

if st.button("Continue to Review"):

    # Need to load in the assessment data.

    st.switch_page("pages/12_Assess_&_Review.py")

if st.button("Home"):
    st.switch_page("streamlit_app.py")
