import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    st.markdown("<h1 style='text-align: center;'>Ambulatory Surgical Center Quality Measures</h1>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center'>Facility</h1>", unsafe_allow_html=True)
    st.write('###')
    st.markdown('''
                **Overview**  
                Authorized by the Medicare Improvement and Extension Act-Tax Relief and Health Care Act of 2006, the Ambulatory Surgical Center Quality Reporting (ASCQR) Program is a pay-for-reporting program which collects and publicly reports facility-level quality measure data from ambulatory surgical centers (ASCs) paid under the ASC fee schedule for care provided in this setting. \n
                Key Features: \n
                1. **Date Filtering:** Users can easily filter data based on the date of report submission, enabling a focused analysis of specific time frames.  
                2. **Report Submission Rate Analysis:** The application goes beyond general submission rates by offering an in-depth analysis specific to each submetric within quality measures. This feature allows ASCs to assess their compliance on a granular level, ensuring a comprehensive understanding of the reporting landscape.  
                3. **Ranking Facilities and States:** Users can access rankings that highlight the performance of ASCs and states based on their report submission rates, fostering a healthy competitive environment and encouraging continuous improvement.  
                4. **Quality Measure Analysis:** The application dives deep into individual quality measures, offering visualizations for each sub-metric. This feature enables a granular understanding of performance and aids in identifying areas for improvement.  
                5. **Submetric Ranking:** ASCs and states are ranked based on the values of selected sub-metrics within each quality measure. This functionality promotes transparency and helps stakeholders identify leaders in specific aspects of quality reporting. \n
                The ASCQR Reporting Web App is designed to be a comprehensive solution, offering detailed insights into the submission rates and performance metrics of ASCs under the ASCQR Program. By focusing on submetric-specific analyses, the application empowers users to make data-driven decisions, promoting accuracy, transparency, and continuous improvement in ambulatory surgical center quality reporting.  
                ''')
    st.write('---')
    df = load_data()
    year = st.radio('Choose year', df['Year'].unique(), horizontal=True)
    df = df[df['Year']==year]
    st.dataframe(df, use_container_width=True)
    st.write('---')
    tabs = st.tabs(['Hospital report submission analysis', 'Hospital report submission ranking', 'Specific quality measure analysis'])
    with tabs[0]:
        reporting_analysis(df=df, key='original')
        st.write('---')
    with tabs[1]:
        reporting_ranking(df=df, key='ranking')
        st.write('---')
    with tabs[2]:
        asc_analysis(df_original=df, key='asc_analysis_original')
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
        choose_location = st.radio('Choose location to rank by', ['facilities', 'states'], horizontal=True, key=f'{key} top/bottom location')
    with cols[1]:
        amount_location = st.number_input(f'Amount of {choose_location}', value=3, step=1, min_value=1, max_value=df.shape[0], key=f'{key} top/bottom amount')
    
    df = pd.concat([df[f'{"Facility Name" if choose_location=="facilities" else "State"}'], df[[item for item in df.columns if 'Footnote' in item]]], axis=1)
    df['reports available'] = df.apply(lambda row: row.isna().sum(), axis=1)
    df = df.sort_values(by='reports available', ascending=False)
    if choose_location == 'states':
        df_groupped_states = df[['State', 'reports available']].groupby('State').mean().sort_values(by='reports available', ascending=False)

    tabs = st.tabs(['Rankings', 'Data'])
    with tabs[0]:
        cols = st.columns(2)
        with cols[0]:
            st.markdown(f"<h4 style='text-align: center;'>Top {amount_location} HIGHEST reporting {choose_location}</h4>", unsafe_allow_html=True)
            top_df = df[f"{'Facility Name'}"][:amount_location] if choose_location == 'facilities' else df_groupped_states.index[:amount_location]
            n = 1
            for location in top_df:
                st.write(f"{n}: {location if choose_location == 'facilities' else f'{location}: {state_abbrev[location].upper()}'}")
                n += 1
        with cols[1]:
            st.markdown(f"<h4 style='text-align: center;'>Top {amount_location} LOWEST reporting {choose_location}</h4>", unsafe_allow_html=True)
            bottom_df = df[f"{'Facility Name'}"][-amount_location:].tolist() if choose_location == 'facilities' else df_groupped_states.index[-amount_location:].tolist()
            n = 1
            for location in reversed(bottom_df):
                st.write(f"{n}: {location if choose_location == 'facilities' else f'{location}: {state_abbrev[location].upper()}'}")
                n += 1
    with tabs[1]:
        if choose_location == "states":
            st.dataframe(df_groupped_states, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)

def asc_analysis(df_original=None, key=None):
    container = st.container()
    st.write('###')
    cols = st.columns(2)
    with cols[0]:
        asc_to_analyze = st.selectbox('Choose quality measure to analyze', list(asc_definitions.keys()), key=key)
        asc_features = [item for item in df_original.columns if f'{asc_to_analyze}' in item]
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
                if df_original[feature].nunique() > 10:    
                    fig = px.histogram(df_original[feature], title=f'{feature}')
                else:
                    mapped_values_footnote = df_original[feature].map(lambda x: f"{footnote_dict.get(x, 'Reports available')}" if pd.notnull(x) else 'Reports available')
                    fig = px.pie(
                        names=df_original[feature].unique() if 'Footnote' not in feature else mapped_values_footnote.unique(),
                        title=f'{feature}',
                        values=df_original[feature].value_counts(dropna=False).values,
                        hole=0.5
                    )
                st.plotly_chart(fig, use_container_width=True)

    st.write('---')

    cols = st.columns(2)
    with cols[0]:
        st.markdown(f"<h3 style='text-align: right'>Ranking based on the </h3>", unsafe_allow_html=True)
    with cols[1]:
        subfeature = st.selectbox('Choose the sub-feature to rank', [item for item in asc_features if all(keyword not in item for keyword in ['Performance', 'Footnote'])], label_visibility="collapsed")

    cols = st.columns(2)
    with cols[0]:
        location = st.radio('Select location to rank by', ['facilities', 'states'], horizontal=True)
    with cols[1]:
        container = st.container()
    
    if location == 'facilities':
        df_ranking = df_original[['Facility Name', f'{subfeature}']].set_index('Facility Name')
    else:
        df_ranking = df_original[['State', f'{subfeature}']].set_index('State')

    df_ranking[f'{subfeature}'] = pd.to_numeric(df_ranking[f'{subfeature}'], errors='coerce')
    df_ranking.dropna(inplace=True)

    if location == 'states':
        df_ranking = df_ranking.groupby('State').mean().reset_index()
        df_ranking['State'] = df_ranking['State'].replace(state_abbrev)
        df_ranking = df_ranking.set_index('State')
    
    amount_location = container.number_input(f'Amount of {location}', value=3 if df_ranking.shape[0] >= 3 else df_ranking.shape[0], step=1, min_value=1, max_value=df_ranking.shape[0], key=f'measure ranking amount location')

    df_ranking = df_ranking.sort_values(by=f'{subfeature}', ascending=False)
    st.markdown(f"Amount of **{location}** submitted **{subfeature}** report: **{len(df_ranking.index)}**")

    tabs = st.tabs(['Graphs', 'Data'])
    with tabs[0]:
        cols = st.columns(2)
        with cols[0]:
            df = df_ranking[:amount_location].sort_values(by=f'{subfeature}', ascending=True)
            fig = px.histogram(df, y=df.index, x=df[subfeature], title=f'Top {amount_location} HIGHEST indicators among {location}', orientation='h')
            fig.update_xaxes(title_text=subfeature)
            st.plotly_chart(fig, use_container_width=True)
        with cols[1]:
            df = df_ranking.tail(amount_location).sort_values(by=f'{subfeature}', ascending=True)
            fig = px.histogram(df, y=df.index, x=df[subfeature], title=f'Top {amount_location} LOWEST indicators among {location}', orientation='h')
            fig.update_xaxes(title_text=subfeature)
            st.plotly_chart(fig, use_container_width=True)
        
        
    with tabs[1]:
        st.dataframe(df_ranking, use_container_width=True)

if __name__ == '__main__':
    main()
