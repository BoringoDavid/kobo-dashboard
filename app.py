import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="KPI Dashboard", layout="wide", initial_sidebar_state="expanded")

st.title("📊 KPI Monitoring Dashboard")
st.markdown("Real-time tracking of project KPIs across all categories")

# Credentials from secrets or defaults
TOKEN = st.secrets["KOBO_TOKEN"]
ASSET_ID = st.secrets["ASSET_ID"]
    
# Cache data loading
@st.cache_data(ttl=3600)
def load_kobo_data():
    """Load and clean data from KoBoToolbox with pagination"""
    try:
        url = f'https://kc.kobotoolbox.org/api/v2/assets/{ASSET_ID}/data'
        headers = {'Authorization': f'Token {TOKEN}'}
        
        all_records = []
        limit = 10000  # Get up to 10000 records per request
        offset = 0
        
        while True:
            # Fetch with pagination parameters
            params = {'limit': limit, 'offset': offset}
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract results
            if isinstance(data, dict) and 'results' in data:
                records = data['results']
            else:
                records = data
            
            if not records:
                break  # No more records
            
            all_records.extend(records)
            offset += limit
        
        st.info(f"✅ Fetched {len(all_records)} total submissions")
        
        df = pd.DataFrame(all_records)
        
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

# Helper function to safely access columns
def safe_metric(df, column, aggregation='count', format_str=None):
    """Safely get metric value if column exists"""
    if column not in df.columns or len(df) == 0:
        return None
    
    try:
        if aggregation == 'count':
            return df[column].notna().sum()
        elif aggregation == 'sum':
            return df[column].sum()
        elif aggregation == 'mean':
            return df[column].mean()
        elif aggregation == 'max':
            return df[column].max()
    except:
        return None

def safe_value_counts(df, column):
    """Safely get value counts for a column"""
    if column not in df.columns or len(df) == 0:
        return None
    try:
        return df[column].value_counts()
    except:
        return None

# Load data
df = load_kobo_data()

if df is None:
    st.error("❌ Could not load data. Please check your KoBoToolbox credentials.")
    st.stop()

# =============== CHECK IF DATA EXISTS ===============
if len(df) == 0:
    st.warning("⚠️ No data submitted yet!")
    st.info("""
    Your KoBoToolbox form is ready but has no submissions yet.
    
    **Next steps:**
    1. Share the form URL with your data collectors
    2. They fill out the form on mobile or desktop
    3. Submissions will appear here automatically
    4. Dashboard will refresh every hour with new data
    
    **Form is deployed and ready!** ✅
    """)
    st.stop()

# Data is available - proceed with dashboard
st.success(f"✅ Loaded {len(df)} submissions")

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
    else:
        st.metric("This Week", "N/A")

with col3:
    if '_submission_time' in df_filtered.columns:
        st.metric("Latest Update", df_filtered['_submission_time'].max().strftime('%Y-%m-%d'))
    else:
        st.metric("Latest Update", "N/A")

with col4:
    missing = (df_filtered.isna().sum().sum() / (len(df_filtered) * len(df_filtered.columns)) * 100) if len(df_filtered) > 0 else 0
    st.metric("Data Completeness", f"{100 - missing:.1f}%")

st.markdown("---")

# =============== CATEGORY TABS ===============
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Jobs",
    "Youth FSC",
    "Women FSC",
    "Food Systems",
    "Off-Farm",
    "On-Farm"
])

# ===== INDIVIDUAL GREEN JOBS (youth) =====
with tab1:
    st.subheader("Category 1: Individual Green Jobs (Youth)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        job_count = safe_metric(df_filtered, 'job_type', 'count')
        st.metric("Total Youth Employed", job_count if job_count else "0")
    
    with col2:
        avg_wage = safe_metric(df_filtered, 'avg_wage_monthly', 'mean')
        st.metric("Average Monthly Wage (RWF)", f"{avg_wage:,.0f}" if avg_wage else "No data")
    
    with col3:
        avg_security = safe_metric(df_filtered, 'job_security_perceived', 'mean')
        st.metric("Avg Job Security (1-5)", f"{avg_security:.1f}" if avg_security else "No data")
    
    # Job Type Distribution
    job_counts = safe_value_counts(df_filtered, 'job_type')
    if job_counts is not None and len(job_counts) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                values=job_counts.values,
                names=job_counts.index,
                title="Job Type Distribution",
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            wage_by_type = df_filtered[df_filtered['job_type'].notna()].groupby('job_type')['avg_wage_monthly'].mean() if 'avg_wage_monthly' in df_filtered.columns else None
            if wage_by_type is not None and len(wage_by_type) > 0:
                fig = px.bar(
                    x=wage_by_type.index,
                    y=wage_by_type.values,
                    title="Average Wage by Job Type",
                    labels={'x': 'Job Type', 'y': 'Average Wage (RWF)'}
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No job type data available yet")

# ===== TAB 2: YOUTH-LED FSC (18-35 YEARS) =====
with tab2:
    st.subheader("Category 2: Youth-Led FSC (18-35 Years)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        youth_fsc = safe_metric(df_filtered, 'fsc_youth_businessplan', 'count')
        st.metric("FSC Count", youth_fsc if youth_fsc else "0")
    
    with col2:
        farmers = safe_metric(df_filtered, 'fsc_youth_farmers_served', 'sum')
        st.metric("Farmers Served", f"{farmers:,.0f}" if farmers and farmers > 0 else "0")
    
    with col3:
        avg_turnover = safe_metric(df_filtered, 'fsc_youth_turnover_q', 'mean')
        st.metric("Avg Quarterly Turnover", f"{avg_turnover:,.0f}" if avg_turnover else "No data")
    
    with col4:
        employees = safe_metric(df_filtered, 'fsc_youth_employees', 'sum')
        st.metric("Total Employees", f"{employees:,.0f}" if employees and employees > 0 else "0")
    
    # Business Plans
    plan_status = safe_value_counts(df_filtered, 'fsc_youth_businessplan')
    if plan_status is not None and len(plan_status) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                values=plan_status.values,
                names=['Yes', 'No'][:len(plan_status)],
                title="FSCs with Actionable Business Plans"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'fsc_youth_savings' in df_filtered.columns:
                savings_data = df_filtered['fsc_youth_savings'].dropna()
                if len(savings_data) > 0:
                    fig = px.box(
                        y=savings_data,
                        title="Savings Distribution (RWF)",
                        labels={'y': 'Savings (RWF)'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No Youth FSC data available yet")
    
    # Financial Metrics
    st.subheader("💰 Financial Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_turnover = safe_metric(df_filtered, 'fsc_youth_turnover_q', 'sum')
        st.metric("Total Quarterly Turnover", f"{total_turnover:,.0f}" if total_turnover and total_turnover > 0 else "0")
    
    with col2:
        total_sales = safe_metric(df_filtered, 'fsc_youth_sales_income', 'sum')
        st.metric("Total Sales Income", f"{total_sales:,.0f}" if total_sales and total_sales > 0 else "0")
    
    with col3:
        total_loans = safe_metric(df_filtered, 'fsc_youth_loans_total', 'sum')
        st.metric("Total Loans Received", f"{total_loans:,.0f}" if total_loans and total_loans > 0 else "0")

# ===== TAB 3: WOMEN FSC (36+ YEARS) =====
with tab3:
    st.subheader("Category 3: Women FSC (36+ Years)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        women_fsc = safe_metric(df_filtered, 'fsc_women_businessplan', 'count')
        st.metric("FSC Count", women_fsc if women_fsc else "0")
    
    with col2:
        farmers = safe_metric(df_filtered, 'fsc_women_farmers_served', 'sum')
        st.metric("Farmers Served", f"{farmers:,.0f}" if farmers and farmers > 0 else "0")
    
    with col3:
        avg_turnover = safe_metric(df_filtered, 'fsc_women_turnover_q', 'mean')
        st.metric("Avg Quarterly Turnover", f"{avg_turnover:,.0f}" if avg_turnover else "No data")
    
    with col4:
        employees = safe_metric(df_filtered, 'fsc_women_employees', 'sum')
        st.metric("Total Employees", f"{employees:,.0f}" if employees and employees > 0 else "0")
    
    # Business Plans & Savings
    plan_status = safe_value_counts(df_filtered, 'fsc_women_businessplan')
    if plan_status is not None and len(plan_status) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
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
    else:
        st.info("No Women FSC data available yet")
    
    # Financial Metrics
    st.subheader("💰 Financial Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_turnover = safe_metric(df_filtered, 'fsc_women_turnover_q', 'sum')
        st.metric("Total Quarterly Turnover", f"{total_turnover:,.0f}" if total_turnover and total_turnover > 0 else "0")
    
    with col2:
        total_sales = safe_metric(df_filtered, 'fsc_women_sales_income', 'sum')
        st.metric("Total Sales Income", f"{total_sales:,.0f}" if total_sales and total_sales > 0 else "0")
    
    with col3:
        total_loans = safe_metric(df_filtered, 'fsc_women_loans_total', 'sum')
        st.metric("Total Loans Received", f"{total_loans:,.0f}" if total_loans and total_loans > 0 else "0")

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
        count = safe_metric(df_filtered, field, 'sum')
        if count is not None and count > 0:
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
    else:
        st.info("No food systems data available yet")
    
    # Commodities to schools
    if 'commodities_schools_value' in df_filtered.columns:
        st.subheader("🏫 Commodities to Schools")
        value = safe_metric(df_filtered, 'commodities_schools_value', 'sum')
        st.metric("Total Value of Commodities Sold (RWF)", f"{value:,.0f}" if value and value > 0 else "0")

# ===== TAB 5: LIVELIHOOD - OFF-FARM =====
with tab5:
    st.subheader("Category 5: Livelihood - Off-Farm")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        offarm_count = safe_metric(df_filtered, 'livelihoods_offarm_business', 'count')
        st.metric("Off-Farm Participants", offarm_count if offarm_count else "0")
    
    with col2:
        total_assets = safe_metric(df_filtered, 'offarm_assets_value', 'sum')
        st.metric("Total Asset Value", f"{total_assets:,.0f}" if total_assets and total_assets > 0 else "0")
    
    with col3:
        total_rev = safe_metric(df_filtered, 'offarm_revenues_q', 'sum')
        st.metric("Total Quarterly Revenue", f"{total_rev:,.0f}" if total_rev and total_rev > 0 else "0")
    
    with col4:
        if 'offarm_businessplan' in df_filtered.columns:
            with_plan = (df_filtered['offarm_businessplan'] == '1').sum()
            st.metric("With Business Plan", with_plan)
    
    # Charts
    plan_status = safe_value_counts(df_filtered, 'offarm_businessplan')
    if plan_status is not None and len(plan_status) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                values=plan_status.values,
                names=['Yes', 'No'][:len(plan_status)],
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
    else:
        st.info("No off-farm data available yet")

# ===== TAB 6: LIVELIHOOD - ON-FARM =====
with tab6:
    st.subheader("Category 6: Livelihood - On-Farm")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        onfarm_count = safe_metric(df_filtered, 'onfarm_main_income', 'count')
        st.metric("On-Farm Participants", onfarm_count if onfarm_count else "0")
    
    with col2:
        total_rev = safe_metric(df_filtered, 'onfarm_revenue_total', 'sum')
        st.metric("Total Revenue", f"{total_rev:,.0f}" if total_rev and total_rev > 0 else "0")
    
    with col3:
        total_land = safe_metric(df_filtered, 'onfarm_land_owned', 'sum')
        st.metric("Total Land (ha)", f"{total_land:.1f}" if total_land and total_land > 0 else "0")
    
    with col4:
        if 'onfarm_irrigation_access' in df_filtered.columns:
            irrigation = (df_filtered['onfarm_irrigation_access'] == '1').sum()
            st.metric("With Irrigation Access", irrigation)
    
    # Charts
    income_dist = safe_value_counts(df_filtered, 'onfarm_main_income')
    if income_dist is not None and len(income_dist) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
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
    else:
        st.info("No on-farm data available yet")

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
