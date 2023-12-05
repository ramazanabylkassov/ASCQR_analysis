import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import numpy as np 

st.set_page_config(layout="wide", page_title='Ryte.ai')

asc_definitions = {
        "ASC-9": "Percentage of patients receiving appropriate recommendation for follow-up screening colonoscopy",
        "ASC-11": "Percentage of patients who had cataract surgery and had improvement in visual function within 90 days following the surgery",
        "ASC-12": "Rate of unplanned hospital visits after an outpatient colonoscopy",
        "ASC-13": "Percentage of patients who received anesthesia who had a body temperature of 96.8 Fahrenheit within 15 minutes of arriving in the post-anesthesia care unit",
        "ASC-14": "Percentage of cataract surgeries that had an unplanned additional eye surgery (anterior vitrectomy)",
        "ASC-17": "Rate of unplanned hospital visits within 7 days of an orthopedic surgery at an ASC",
        "ASC-18": "Rate of unplanned hospital visits within 7 days of a urology surgery at an ASC ",
        "ASC-20": "Percentage of all core healthcare personnel (HCP) eligible to work at the ASC for at least one day of the self-selected week, in each month of quarterly data reporting, who completed COVID-19 primary vaccination series.",
    }
footnote_dict = {
            '1': "The number of cases/patients is too few to report.",
            '2': "Data submitted were based on a sample of cases/patients.",
            '3': "Results are based on a shorter time period than required.",
            '4': "Data suppressed by CMS for one or more quarters.",
            '5': "Results are not available for this reporting period.",
            '6': "Fewer than 100 patients completed the HCAHPS survey. Use these scores with caution, as the number of surveys may be too low to reliably assess hospital performance.",
            '7': "No cases met the criteria for this measure.",
            '8': "The lower limit of the confidence interval cannot be calculated if the number of observed infections equals zero.",
            '9': "No data are available from the state/territory for this reporting period."
        }
state_abbrev = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}

def main():
    df = load_data()
    st.markdown("<h1 style='text-align: center;'>Ambulatory Surgical Center Quality Measures</h1>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center'>Facility</h1>", unsafe_allow_html=True)
    st.write('###')
    st.markdown('''**Overview**  
                Authorized by the Medicare Improvement and Extension Act-Tax Relief and Health Care Act of 2006, the Ambulatory Surgical Center Quality Reporting (ASCQR) Program is a pay-for-reporting program which collects and publicly reports facility-level quality measure data from ambulatory surgical centers (ASCs) paid under the ASC fee schedule for care provided in this setting.
                ''')
    st.write('---')

    # df = pd.read_csv('ASC_Facility.csv', sep=None, engine='python')
    year = st.radio('Choose year', df['Year'].unique(), horizontal=True)
    df = df[df['Year']==year]
    st.dataframe(df, use_container_width=True)
    st.write('---')
    tabs = st.tabs(['Hospital reporting analysis', 'Report submission ranking', 'Specific quality measure evaluation'])
    with tabs[0]:
        reporting_analysis(df=df, key='original')
        st.write('---')
    with tabs[1]:
        reporting_ranking(df=df, key='ranking')
        st.write('---')
    with tabs[2]:
        asc_analysis(df=df, key='asc_analysis_original')
        st.write('---')

@st.cache_data
def load_data():
    api_url = f"https://data.cms.gov/provider-data/api/1/datastore/query/4jcv-atw7/{0}"
    data = requests.get(api_url).json()
    df = pd.DataFrame(data['results'])
    new_columns = []
    for feature in df.columns:
        new_columns.append(data['schema']['ed8daedb-7687-58f8-b87d-794e938f4e90']['fields'][feature]['description'])
    df.columns = new_columns
    df.replace({"N/A": None, "": None, np.nan: None}, inplace=True)    
    return df

def reporting_analysis(df=None, key=None):
    st.markdown(f"<h3 style='text-align: center;'>Hospital reporting analysis</h3>", unsafe_allow_html=True)
    st.write('###')
    tabs = st.tabs(['Graph', 'Data'])
    with tabs[0]:
        footnote_columns = [col for col in df.columns if col.endswith('Footnote')]
        df_footnotes = df[footnote_columns]
        all_value_counts = {col: df_footnotes[col].value_counts(dropna=False) for col in df_footnotes.columns}
        
        df_footnote_value_count = pd.DataFrame(all_value_counts)
        df_footnote_value_count.index = df_footnote_value_count.index.map(lambda x: f"{footnote_dict[x]}" if pd.notnull(x) else "Reports available")
        df_footnote_value_count.columns = df_footnote_value_count.columns.map(lambda x: f"{x.split()[0]}")        
        if len(footnote_columns) > 1:
            fig = px.bar(df_footnote_value_count.T, title=f"Hospital reports: {df['Year'].unique()[0]}")
            fig.update_layout(
                xaxis_title='',
                yaxis_title='',
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig = px.pie(df_footnote_value_count, values=footnote_columns[0].split()[0], hole=0.5, names=df_footnote_value_count.index, title=f"Hospital reports: {footnote_columns[0].split()[0]} {df['Year'].nunique()[0]}")
            st.plotly_chart(fig, use_container_width=True)
    with tabs[1]:
        st.dataframe(df_footnote_value_count, use_container_width=True)
    
def reporting_ranking(df=None, key=None):
    st.markdown(f"<h3 style='text-align: center;'>Report submission ranking</h3>", unsafe_allow_html=True)
    st.write('###')
    cols = st.columns(2)
    with cols[0]:
        choose_location = st.radio('Choose magnitude', ['hospitals', 'states'], horizontal=True, key=f'{key} top/bottom location')
    with cols[1]:
        amount_location = st.number_input(f'Amount of {choose_location}', value=3, step=1, min_value=1, max_value=df.shape[0], key=f'{key} top/bottom amount')
    
    df = pd.concat([df[f'{"Facility Name" if choose_location=="hospitals" else "State"}'], df[[item for item in df.columns if 'Footnote' in item]]], axis=1)
    df['reports available'] = df.apply(lambda row: row.isna().sum(), axis=1)
    df = df.sort_values(by='reports available', ascending=False)
    if choose_location == 'states':
        df_groupped_states = df[['State', 'reports available']].groupby('State').mean().sort_values(by='reports available', ascending=False)

    tabs = st.tabs(['Rankings', 'Data'])
    with tabs[0]:
        cols = st.columns(2)
        with cols[0]:
            st.markdown(f"<h4 style='text-align: center;'>Top {amount_location} most reporting {choose_location}</h4>", unsafe_allow_html=True)
            top_df = df[f"{'Facility Name'}"][:amount_location] if choose_location == 'hospitals' else df_groupped_states.index[:amount_location]
            n = 1
            for location in top_df:
                st.write(f"{n}: {location if choose_location == 'hospitals' else f'{location}: {state_abbrev[location].upper()}'}")
                n += 1
        with cols[1]:
            st.markdown(f"<h4 style='text-align: center;'>Top {amount_location} least reporting {choose_location}</h4>", unsafe_allow_html=True)
            bottom_df = df[f"{'Facility Name'}"][-amount_location:].tolist() if choose_location == 'hospitals' else df_groupped_states.index[-amount_location:].tolist()
            n = 1
            for location in reversed(bottom_df):
                st.write(f"{n}: {location if choose_location == 'hospitals' else f'{location}: {state_abbrev[location].upper()}'}")
                n += 1
    with tabs[1]:
        st.dataframe(df, use_container_width=True)

def asc_analysis(df=None, key=None):
    container = st.container()
    st.write('###')
    cols = st.columns(2)
    with cols[0]:
        asc_to_analyze = st.selectbox('Choose quality measure to analyze', list(asc_definitions.keys()), key=key)
        asc_features = [item for item in df.columns if f'{asc_to_analyze}' in item]
    with cols[1]:
        checkboxes = {}
        with st.form('asc_features_form'):
            for feature in asc_features:
                checkboxes[f'{feature}'] = st.checkbox(f'{feature}', value=True)
            selected_features = [item for item in checkboxes.keys() if checkboxes[item]]
            st.form_submit_button()

    container.markdown(f"<h3 style='text-align: center'>{asc_to_analyze}: {asc_definitions[asc_to_analyze]}</h3>", unsafe_allow_html=True)
    groups = []
    for i in range(0, len(selected_features), 2):
        groups.append(selected_features[i:i+2])
    for group in groups:
        cols = st.columns(2)
        for n, feature in enumerate(group):
            with cols[n]:
                if df[feature].nunique() > 10:    
                    fig = px.histogram(df[feature], title=f'{feature}')
                else:
                    mapped_values_footnote = df[feature].map(lambda x: f"{footnote_dict.get(x, 'Reports available')}" if pd.notnull(x) else 'Reports available')
                    fig = px.pie(
                        names=df[feature].unique() if 'Footnote' not in feature else mapped_values_footnote.unique(),
                        title=f'{feature}',
                        values=df[feature].value_counts(dropna=False).values,
                        hole=0.5
                    )
                st.plotly_chart(fig, use_container_width=True)

if __name__ == '__main__':
    main()
