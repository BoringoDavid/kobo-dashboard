import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

st.set_page_config(page_title="KoBoToolbox Dashboard", layout="wide")
st.title("📊 Data Collection Dashboard")

# Your credentials
TOKEN = "5753adfba72b3aba56b0948da6cc0c2d9c8e012f"
ASSET_ID = "aru4FnYa2aTc2BujrNmguz"

@st.cache_data(ttl=3600)
def load_and_clean_data():
    """Pull data from KoBoToolbox and clean it"""
    
    try:
        # st.info(" Fetching data from KoBoToolbox...")
        
        # Use v2 API endpoint (v1 is deprecated)
        url = f'https://kc.kobotoolbox.org/api/v2/assets/{ASSET_ID}/data.json'
        
        headers = {'Authorization': f'Token {TOKEN}'}
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        # Check if nested under 'results'
        if isinstance(data, dict) and 'results' in data:
            records = data['results']
        else:
            records = data
        
        # Convert to DataFrame
        df = pd.DataFrame(records)
        
        # st.success(f"✅ Loaded {len(df)} records from KoBoToolbox")
        
        # CLEANING PROCESS
        # st.info("🧹 Cleaning data...")
        
        initial_rows = len(df)
        
        # Remove duplicates by _id
        if '_id' in df.columns:
            df = df.drop_duplicates(subset=['_id'], keep='first')
        
        # Convert submission time to datetime
        if '_submission_time' in df.columns:
            df['_submission_time'] = pd.to_datetime(df['_submission_time'])
            df = df.sort_values('_submission_time', ascending=False)
        
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        final_rows = len(df)
        removed = initial_rows - final_rows
        
        # st.success(f"✅ Data cleaned! Removed {removed} duplicates. Final: {final_rows} records")
        
        return df
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

# Load data
df = load_and_clean_data()

if df is not None and len(df) > 0:
    
    st.divider()
    
    # KPI Metrics
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Total Responses", len(df))
    
    if '_submission_time' in df.columns:
        this_week = len(df[df['_submission_time'] > pd.Timestamp.now() - pd.Timedelta(days=7)])
        col2.metric("This Week", this_week)
        
        last_update = df['_submission_time'].max()
        col3.metric("Last Update", last_update.strftime('%Y-%m-%d %H:%M'))
    
    # Data quality
    missing_pct = (df.isna().sum().sum() / (len(df) * len(df.columns)) * 100) if len(df) > 0 else 0
    col4.metric("Data Quality", f"{100 - missing_pct:.1f}%")
    
    # Submissions over time
    if '_submission_time' in df.columns:
        st.subheader("📈 Submissions Over Time")
        daily = df.groupby(df['_submission_time'].dt.date).size().reset_index(name='count')
        daily.columns = ['Date', 'Responses']
        fig = px.line(daily, x='Date', y='Responses', markers=True, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Data preview
    st.subheader("📋 Data Preview")
    st.dataframe(df, use_container_width=True)
    
    # Download data
    csv = df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download Data as CSV",
        data=csv,
        file_name=f"kobo_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
else:
    st.error("❌ Could not load data. Check your credentials.")












# Real implementation cadebase
#========================================================


import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import json

st.set_page_config(page_title="KPI Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for better styling
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 14px;
        opacity: 0.9;
    }
    </style>
""", unsafe_allow_html=True)

# Title and intro
st.title("SHOEA HEZA KPI Monitoring Dashboard")
st.markdown("Real-time tracking of project KPIs across all categories")

# Credentials from secrets or defaults
try:
    TOKEN = st.secrets["KOBO_TOKEN"]
    ASSET_ID = st.secrets["ASSET_ID"]
except:
    TOKEN = "YOUR_KOBO_TOKEN"
    ASSET_ID = "aru4FnYa2aTc2BujrNmguz"

# Cache data loading
@st.cache_data(ttl=3600)
def load_kobo_data():
    """Load and clean data from KoBoToolbox"""
    try:
        url = f'https://kc.kobotoolbox.org/api/v2/assets/{ASSET_ID}/data.json'
        headers = {'Authorization': f'Token {TOKEN}'}
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if isinstance(data, dict) and 'results' in data:
            records = data['results']
        else:
            records = data
        
        df = pd.DataFrame(records)
        
        # Convert submission time
        if '_submission_time' in df.columns:
            df['_submission_time'] = pd.to_datetime(df['_submission_time'])
            df = df.sort_values('_submission_time', ascending=False)
        
        # Remove duplicates
        if '_id' in df.columns:
            df = df.drop_duplicates(subset=['_id'], keep='first')
        
        return df
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Load data
df = load_kobo_data()

if df is not None and len(df) > 0:
    
    # =============== SIDEBAR - FILTERS ===============
    st.sidebar.markdown("### 🔍 Filters")
    
    # Date range filter
    if '_submission_time' in df.columns:
        min_date = df['_submission_time'].min().date()
        max_date = df['_submission_time'].max().date()
        date_range = st.sidebar.date_input(
            "Select Date Range:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Filter by date
        if len(date_range) == 2:
            df_filtered = df[
                (df['_submission_time'].dt.date >= date_range[0]) &
                (df['_submission_time'].dt.date <= date_range[1])
            ].copy()
        else:
            df_filtered = df.copy()
    else:
        df_filtered = df.copy()
    
    # =============== TOP SUMMARY METRICS ===============
    st.markdown("---")
    st.subheader("📈 Overall Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Submissions", len(df_filtered), delta=f"Total: {len(df)}")
    
    with col2:
        if '_submission_time' in df_filtered.columns:
            this_week = len(df_filtered[df_filtered['_submission_time'] > pd.Timestamp.now() - pd.Timedelta(days=7)])
            st.metric("This Week", this_week)
    
    with col3:
        if '_submission_time' in df_filtered.columns:
            st.metric("Latest Update", df_filtered['_submission_time'].max().strftime('%Y-%m-%d'))
    
    with col4:
        missing = (df_filtered.isna().sum().sum() / (len(df_filtered) * len(df_filtered.columns)) * 100) if len(df_filtered) > 0 else 0
        st.metric("Data Completeness", f"{100 - missing:.1f}%")
    
    st.markdown("---")
    
    # =============== CATEGORY TABS ===============
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "👥 Jobs",
        "🌾 Youth FSC",
        "👩 Women FSC",
        "🏪 Food Systems",
        "🏢 Off-Farm",
        "🌱 On-Farm"
    ])
    
    # ===== TAB 1: INDIVIDUAL EMPLOYED YOUTHS (JOBS) =====
    with tab1:
        st.subheader("Category 1: Individual Employed Youths (Jobs)")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            job_count = df_filtered['job_type'].notna().sum()
            st.metric("Total Youth Employed", job_count)
        
        with col2:
            if 'avg_wage_monthly' in df_filtered.columns:
                avg_wage = df_filtered['avg_wage_monthly'].mean()
                st.metric("Average Monthly Wage (RWF)", f"{avg_wage:,.0f}" if not pd.isna(avg_wage) else "N/A")
        
        with col3:
            if 'job_security_perceived' in df_filtered.columns:
                avg_security = df_filtered['job_security_perceived'].mean()
                st.metric("Avg Job Security (1-5)", f"{avg_security:.1f}" if not pd.isna(avg_security) else "N/A")
        
        # Job Type Distribution
        if 'job_type' in df_filtered.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                job_counts = df_filtered['job_type'].value_counts()
                if len(job_counts) > 0:
                    fig = px.pie(
                        values=job_counts.values,
                        names=job_counts.index,
                        title="Job Type Distribution",
                        hole=0.4
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'avg_wage_monthly' in df_filtered.columns:
                    wage_by_type = df_filtered.groupby('job_type')['avg_wage_monthly'].mean().sort_values(ascending=False)
                    if len(wage_by_type) > 0:
                        fig = px.bar(
                            x=wage_by_type.index,
                            y=wage_by_type.values,
                            title="Average Wage by Job Type",
                            labels={'x': 'Job Type', 'y': 'Average Wage (RWF)'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
        
        # Benefits received
        if 'employee_benefits' in df_filtered.columns:
            st.subheader("Employee Benefits")
            benefits_data = df_filtered['employee_benefits'].dropna().tolist()
            if benefits_data:
                st.info(f"✅ {len(benefits_data)} respondents reported benefits")
    
    # ===== TAB 2: YOUTH-LED FSC (18-35 YEARS) =====
    with tab2:
        st.subheader("Category 2: Youth-Led FSC (18-35 Years)")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            youth_fsc = df_filtered['fsc_youth_businessplan'].notna().sum()
            st.metric("FSC Count", youth_fsc)
        
        with col2:
            if 'fsc_youth_farmers_served' in df_filtered.columns:
                farmers = df_filtered['fsc_youth_farmers_served'].sum()
                st.metric("Farmers Served", f"{farmers:,.0f}" if farmers > 0 else "0")
        
        with col3:
            if 'fsc_youth_turnover_q' in df_filtered.columns:
                avg_turnover = df_filtered['fsc_youth_turnover_q'].mean()
                st.metric("Avg Quarterly Turnover", f"{avg_turnover:,.0f}" if not pd.isna(avg_turnover) else "N/A")
        
        with col4:
            if 'fsc_youth_employees' in df_filtered.columns:
                employees = df_filtered['fsc_youth_employees'].sum()
                st.metric("Total Employees", f"{employees:,.0f}" if employees > 0 else "0")
        
        # Business Plans
        col1, col2 = st.columns(2)
        
        with col1:
            if 'fsc_youth_businessplan' in df_filtered.columns:
                plan_status = df_filtered['fsc_youth_businessplan'].value_counts()
                fig = px.pie(
                    values=plan_status.values,
                    names=['Yes', 'No'][:len(plan_status)],
                    title="FSCs with Actionable Business Plans"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'fsc_youth_savings' in df_filtered.columns:
                savings_data = df_filtered[['fsc_youth_businessplan', 'fsc_youth_savings']].dropna()
                if len(savings_data) > 0:
                    fig = px.box(
                        y=savings_data['fsc_youth_savings'],
                        title="Savings Distribution (RWF)",
                        labels={'y': 'Savings (RWF)'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # Financial Metrics
        if 'fsc_youth_turnover_q' in df_filtered.columns or 'fsc_youth_sales_income' in df_filtered.columns:
            st.subheader("💰 Financial Metrics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'fsc_youth_turnover_q' in df_filtered.columns:
                    total_turnover = df_filtered['fsc_youth_turnover_q'].sum()
                    st.metric("Total Quarterly Turnover", f"{total_turnover:,.0f}" if total_turnover > 0 else "0")
            
            with col2:
                if 'fsc_youth_sales_income' in df_filtered.columns:
                    total_sales = df_filtered['fsc_youth_sales_income'].sum()
                    st.metric("Total Sales Income", f"{total_sales:,.0f}" if total_sales > 0 else "0")
            
            with col3:
                if 'fsc_youth_loans_total' in df_filtered.columns:
                    total_loans = df_filtered['fsc_youth_loans_total'].sum()
                    st.metric("Total Loans Received", f"{total_loans:,.0f}" if total_loans > 0 else "0")
    
    # ===== TAB 3: WOMEN FSC (36+ YEARS) =====
    with tab3:
        st.subheader("Category 3: Women FSC (36+ Years)")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            women_fsc = df_filtered['fsc_women_businessplan'].notna().sum()
            st.metric("FSC Count", women_fsc)
        
        with col2:
            if 'fsc_women_farmers_served' in df_filtered.columns:
                farmers = df_filtered['fsc_women_farmers_served'].sum()
                st.metric("Farmers Served", f"{farmers:,.0f}" if farmers > 0 else "0")
        
        with col3:
            if 'fsc_women_turnover_q' in df_filtered.columns:
                avg_turnover = df_filtered['fsc_women_turnover_q'].mean()
                st.metric("Avg Quarterly Turnover", f"{avg_turnover:,.0f}" if not pd.isna(avg_turnover) else "N/A")
        
        with col4:
            if 'fsc_women_employees' in df_filtered.columns:
                employees = df_filtered['fsc_women_employees'].sum()
                st.metric("Total Employees", f"{employees:,.0f}" if employees > 0 else "0")
        
        # Business Plans & Savings
        col1, col2 = st.columns(2)
        
        with col1:
            if 'fsc_women_businessplan' in df_filtered.columns:
                plan_status = df_filtered['fsc_women_businessplan'].value_counts()
                fig = px.pie(
                    values=plan_status.values,
                    names=['Yes', 'No'][:len(plan_status)],
                    title="FSCs with Actionable Business Plans"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'fsc_women_savings' in df_filtered.columns:
                savings_data = df_filtered['fsc_women_savings'].dropna()
                if len(savings_data) > 0:
                    fig = px.box(
                        y=savings_data,
                        title="Savings Distribution (RWF)",
                        labels={'y': 'Savings (RWF)'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # Financial Metrics
        if 'fsc_women_turnover_q' in df_filtered.columns:
            st.subheader("💰 Financial Metrics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_turnover = df_filtered['fsc_women_turnover_q'].sum()
                st.metric("Total Quarterly Turnover", f"{total_turnover:,.0f}" if total_turnover > 0 else "0")
            
            with col2:
                if 'fsc_women_sales_income' in df_filtered.columns:
                    total_sales = df_filtered['fsc_women_sales_income'].sum()
                    st.metric("Total Sales Income", f"{total_sales:,.0f}" if total_sales > 0 else "0")
            
            with col3:
                if 'fsc_women_loans_total' in df_filtered.columns:
                    total_loans = df_filtered['fsc_women_loans_total'].sum()
                    st.metric("Total Loans Received", f"{total_loans:,.0f}" if total_loans > 0 else "0")
    
    # ===== TAB 4: FOOD SYSTEMS (MARKET ACTORS) =====
    with tab4:
        st.subheader("Category 4: Food Systems (Market Actors)")
        
        actors_data = []
        actor_fields = [
            ('aggregators_count', 'Market Aggregators'),
            ('offtakers_count', 'Offtakers/Buyers'),
            ('mechanisation_providers', 'Mechanisation Providers'),
            ('financial_providers', 'Financial Service Providers'),
            ('digital_providers', 'Digital Service Providers'),
            ('inputs_distributors', 'Inputs Distributors'),
            ('phl_providers', 'PHL Providers'),
            ('crop_insurance', 'Crop Insurance Providers'),
            ('advisory_services', 'Advisory Services'),
            ('research_partners', 'Research Partners'),
            ('schools_serviced', 'Schools Serviced'),
        ]
        
        for field, label in actor_fields:
            if field in df_filtered.columns:
                count = df_filtered[field].sum()
                actors_data.append({'Type': label, 'Count': count})
        
        if actors_data:
            actors_df = pd.DataFrame(actors_data).sort_values('Count', ascending=True)
            
            fig = px.barh(
                actors_df,
                x='Count',
                y='Type',
                title="Market Actors Summary",
                labels={'Count': 'Number', 'Type': 'Actor Type'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Commodities sold to schools
        if 'commodities_schools_value' in df_filtered.columns:
            st.subheader("🏫 Commodities to Schools")
            value = df_filtered['commodities_schools_value'].sum()
            st.metric("Total Value of Commodities Sold (RWF)", f"{value:,.0f}" if value > 0 else "0")
    
    # ===== TAB 5: LIVELIHOOD - OFF-FARM =====
    with tab5:
        st.subheader("Category 5: Livelihood - Off-Farm")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            offarm_count = df_filtered['livelihoods_offarm_business'].notna().sum()
            st.metric("Off-Farm Participants", offarm_count)
        
        with col2:
            if 'offarm_assets_value' in df_filtered.columns:
                total_assets = df_filtered['offarm_assets_value'].sum()
                st.metric("Total Asset Value", f"{total_assets:,.0f}" if total_assets > 0 else "0")
        
        with col3:
            if 'offarm_revenues_q' in df_filtered.columns:
                total_rev = df_filtered['offarm_revenues_q'].sum()
                st.metric("Total Quarterly Revenue", f"{total_rev:,.0f}" if total_rev > 0 else "0")
        
        with col4:
            if 'offarm_businessplan' in df_filtered.columns:
                with_plan = (df_filtered['offarm_businessplan'] == '1').sum()
                st.metric("With Business Plan", with_plan)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            if 'offarm_businessplan' in df_filtered.columns:
                plan_dist = df_filtered['offarm_businessplan'].value_counts()
                fig = px.pie(
                    values=plan_dist.values,
                    names=['Yes', 'No'][:len(plan_dist)],
                    title="Participants with Business Plans"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'offarm_contracts' in df_filtered.columns:
                contracts = df_filtered['offarm_contracts'].dropna()
                if len(contracts) > 0:
                    fig = px.box(
                        y=contracts,
                        title="Contracts Distribution",
                        labels={'y': 'Number of Contracts'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    # ===== TAB 6: LIVELIHOOD - ON-FARM =====
    with tab6:
        st.subheader("Category 6: Livelihood - On-Farm")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            onfarm_count = df_filtered['onfarm_main_income'].notna().sum()
            st.metric("On-Farm Participants", onfarm_count)
        
        with col2:
            if 'onfarm_revenue_total' in df_filtered.columns:
                total_rev = df_filtered['onfarm_revenue_total'].sum()
                st.metric("Total Revenue", f"{total_rev:,.0f}" if total_rev > 0 else "0")
        
        with col3:
            if 'onfarm_land_owned' in df_filtered.columns:
                total_land = df_filtered['onfarm_land_owned'].sum()
                st.metric("Total Land (ha)", f"{total_land:.1f}" if total_land > 0 else "0")
        
        with col4:
            if 'onfarm_irrigation_access' in df_filtered.columns:
                irrigation = (df_filtered['onfarm_irrigation_access'] == '1').sum()
                st.metric("With Irrigation Access", irrigation)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            if 'onfarm_main_income' in df_filtered.columns:
                income_dist = df_filtered['onfarm_main_income'].value_counts()
                if len(income_dist) > 0:
                    fig = px.bar(
                        x=income_dist.index,
                        y=income_dist.values,
                        title="Main Income Sources",
                        labels={'x': 'Income Source', 'y': 'Count'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'onfarm_land_owned' in df_filtered.columns:
                land_data = df_filtered['onfarm_land_owned'].dropna()
                if len(land_data) > 0:
                    fig = px.box(
                        y=land_data,
                        title="Land Ownership Distribution (ha)",
                        labels={'y': 'Land (hectares)'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # Crops produced
        if 'onfarm_crops' in df_filtered.columns:
            st.subheader("🌾 Crops Produced")
            crops_count = df_filtered['onfarm_crops'].notna().sum()
            st.info(f"✅ {crops_count} participants reported crops produced")
    
    # =============== DATA EXPORT ===============
    st.markdown("---")
    st.subheader("📥 Data Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv = df_filtered.to_csv(index=False)
        st.download_button(
            label="⬇️ Download Filtered Data (CSV)",
            data=csv,
            file_name=f"kpi_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        st.info("💡 Tip: Use the date filter to export specific periods of data")
    
    # =============== RAW DATA VIEW ===============
    with st.expander("🔍 View Raw Data"):
        st.dataframe(df_filtered, use_container_width=True)
    
    # Last update time
    st.markdown("---")
    st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    st.markdown("*Data refreshes every hour*")

else:
    st.error("❌ Could not load data. Please check your KoBoToolbox credentials.")
    st.info("Ensure your KOBO_TOKEN and ASSET_ID are set in Streamlit secrets.")
