import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import time

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="NISR KPI & Profile Dashboard", 
    layout="wide", 
    initial_sidebar_state="expanded"
)
# ==================== CONFIGURATION ====================
KOBO_BASE_URL = "https://kc.kobotoolbox.org/api/v2"
KOBO_TOKEN = st.secrets.get("KOBO_TOKEN")
KOBO_ASSET_ID_KPI = st.secrets.get("KOBO_ASSET_ID_KPI")
KOBO_ASSET_ID_FSCs = st.secrets.get("KOBO_ASSET_ID_FSCs")
KOBO_ASSET_ID_LIVELIHOOD = st.secrets.get("KOBO_ASSET_ID_LIVELIHOOD")


# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    .empty-state-message {
        background: #e8f4f8;
        border-left: 4px solid #0288d1;
        padding: 15px;
        border-radius: 5px;
        margin: 20px 0;
    }
    .category-header {
        border-bottom: 3px solid #667eea;
        padding-bottom: 10px;
        margin-top: 30px;
    }
    .stat-box {
        background: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== CACHE DATA LOADING ====================
@st.cache_data(ttl=3600)
def fetch_kobo_data(asset_id):
    """Fetch data from KoBoToolbox API"""
    try:
        headers = {
            "Authorization": f"Token {KOBO_TOKEN}",
            "Accept": "application/json"
        }
        
        url = f"{KOBO_BASE_URL}/assets/{asset_id}/data/?limit=10000&offset=0"
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 401:
            return None, "❌ 401 Unauthorized"
        elif response.status_code == 404:
            return None, "❌ 404 Asset not found"
        elif response.status_code != 200:
            return None, f"❌ API Error: {response.status_code}"
        
        data = response.json()
        results = data.get('results', [])
        
        if not results:
            return pd.DataFrame(), None
        
        df = pd.DataFrame(results)
        return df, None
        
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

@st.cache_data(ttl=3600)
def fetch_all_sources():
    """Fetch data from all 3 KoBoToolbox forms"""
    data = {}
    errors = {}
    
    df_kpi, error_kpi = fetch_kobo_data(KOBO_ASSET_ID_KPI)
    data['KPI'] = df_kpi if df_kpi is not None else pd.DataFrame()
    if error_kpi:
        errors['KPI'] = error_kpi
    
    df_fscs, error_fscs = fetch_kobo_data(KOBO_ASSET_ID_FSCs)
    data['FSCs_Profile'] = df_fscs if df_fscs is not None else pd.DataFrame()
    if error_fscs:
        errors['FSCs'] = error_fscs
    
    df_livelihood, error_livelihood = fetch_kobo_data(KOBO_ASSET_ID_LIVELIHOOD)
    data['Livelihood_Profile'] = df_livelihood if df_livelihood is not None else pd.DataFrame()
    if error_livelihood:
        errors['Livelihood'] = error_livelihood
    
    return data, errors

# ==================== MAP SECTION ====================
def display_gatsibo_map():
    """Display map of Gatsibo district with highlighted sectors"""
    st.subheader("📍 Project Locations - Gatsibo District")
    
    # Create GeoJSON for Gatsibo with Gitoki and Kabarore sectors
    fig = go.Figure(data=go.Scattergeo(
        lat=[-1.95, -1.92],
        lon=[30.35, 30.42],
        mode='markers+text',
        marker=dict(
            size=30,
            color=['#FF6B6B', '#4ECDC4'],
            line=dict(width=2, color='white')
        ),
        text=['Gitoki Sector', 'Kabarore Sector'],
        textposition='top center',
        hovertext=['FSCs Profile Data', 'Livelihood Profile Data'],
        hoverinfo='text'
    ))
    
    fig.update_layout(
        title='Project Working Areas in Gatsibo',
        geo=dict(
            scope='africa',
            projection_type='mercator',
            center=dict(lat=-1.93, lon=30.385),
            # zoom=10,
            showland=True,
            landcolor='rgb(243, 243, 243)',
            # coastcolor='rgb(204, 204, 204)',
            coastlinecolor='rgb(204, 204, 204)',
        ),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ==================== CATEGORY 1: PARTICIPANTS ====================
def display_category_1(df):
    """Category 1: Participants"""
    st.markdown('<div class="category-header"><h2>Category 1: Participants</h2></div>', 
                unsafe_allow_html=True)
    
    fscs_count = df.get('fsc_count', pd.Series([0])).sum() if len(df) > 0 else 0
    lps_count = df.get('lp_count', pd.Series([0])).sum() if len(df) > 0 else 0
    indirect_count = df.get('indirect_beneficiaries', pd.Series([0])).sum() if len(df) > 0 else 0
    total_participants = fscs_count + lps_count
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total FSCs", int(fscs_count))
    with col2:
        st.metric("Livelihood Participants", int(lps_count))
    with col3:
        st.metric("Indirect Beneficiaries", int(indirect_count))
    with col4:
        st.metric("Total Direct Beneficiaries", int(total_participants))
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_sector = go.Figure(data=[
            go.Bar(x=['Gitoki', 'Kabarore'], y=[0, 0], marker_color=['#1f77b4', '#ff7f0e'])
        ])
        fig_sector.update_layout(title="FSCs by Sector", height=400, showlegend=False)
        st.plotly_chart(fig_sector, use_container_width=True)
    
    with col2:
        fig_demo = go.Figure(data=[
            go.Bar(name='Male', x=['18-35', '35+'], y=[0, 0]),
            go.Bar(name='Female', x=['18-35', '35+'], y=[0, 0])
        ])
        fig_demo.update_layout(title="Participants by Gender & Age", height=400, barmode='group')
        st.plotly_chart(fig_demo, use_container_width=True)

# ==================== CATEGORY 2: PERFORMANCE ====================
def display_category_2(df):
    """Category 2: FSCs and LPs' Performance"""
    st.markdown('<div class="category-header"><h2>Category 2: Performance</h2></div>', 
                unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Trainings Completed", 0)
    with col2:
        st.metric("FSCs with Business Plans", 0)
    with col3:
        st.metric("Access to Finance", 0)
    with col4:
        st.metric("Market Linkages", 0)
    
    st.subheader("2.1 Trainings & Skills Development")
    col1, col2 = st.columns(2)
    
    with col1:
        fig_skills = px.bar(x=['Skills Dev', 'Vocational', 'Business Plans', 'Mgt Skills'], 
                           y=[0, 0, 0, 0], title="Training Types")
        st.plotly_chart(fig_skills, use_container_width=True)
    
    with col2:
        training_types = ['GAP', 'Climate', 'Finance', 'Book', 'Insurance', 'Tailoring', 'Carpentry', 'Hair']
        # fig_training = px.barh(y=training_types,x=[0]*8,  title="Detailed Training Types")
        fig_training = px.bar(y=training_types, x=[0]*8, orientation='h', title="Detailed Training Types")
        st.plotly_chart(fig_training, use_container_width=True)
    
    st.subheader("2.2 Access to Finance")
    col1, col2 = st.columns(2)
    
    with col1:
        fig_loans = go.Figure(data=[
            go.Bar(name='Male', x=['Loans', 'Grants'], y=[0, 0]),
            go.Bar(name='Female', x=['Loans', 'Grants'], y=[0, 0])
        ])
        fig_loans.update_layout(title="Access to Finance", barmode='group', height=400)
        st.plotly_chart(fig_loans, use_container_width=True)
    
    with col2:
        fig_finance = px.bar(x=['Total Loans', 'Total Grants', 'Avg Loan', 'Avg Grant'], 
                            y=[0, 0, 0, 0], title="Finance Summary (RWF)")
        st.plotly_chart(fig_finance, use_container_width=True)
    
    st.subheader("2.3 Access to Market")
    col1, col2 = st.columns(2)
    
    with col1:
        commodities = ['Agro', 'Beans', 'Chili', 'Coffee', 'Soybeans', 'Banana', 'Potatoes', 
                      'Maize', 'Sorghum', 'Vet', 'Livestock']
        fig_commodities = px.bar(x=commodities, y=[0]*11, title="Sales by Commodity")
        fig_commodities.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_commodities, use_container_width=True)
    
    with col2:
        fig_buyers = go.Figure(data=[go.Pie(labels=['Linked', 'Not Linked'], values=[0, 0], hole=0.4)])
        fig_buyers.update_layout(title="FSCs Linked with Buyers", height=400)
        st.plotly_chart(fig_buyers, use_container_width=True)
    
    st.subheader("2.4 Post Harvest Management (PHM)")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("FSCs Trained in PHM", 0)
        fig_phm = px.bar(x=['Male', 'Female'], y=[0, 0], title="PHM Training by Gender")
        st.plotly_chart(fig_phm, use_container_width=True)
    
    with col2:
        st.metric("PHM Materials Distributed", 0)
        fig_phm_mat = px.bar(x=['Storage', 'Racks', 'Packaging', 'Tools'], y=[0, 0, 0, 0], 
                            title="PHM Materials")
        st.plotly_chart(fig_phm_mat, use_container_width=True)
    
    st.subheader("2.5 Income & Earnings")
    fig_income = px.bar(x=['Monthly Income', 'Quarterly', 'Commissions'], y=[0, 0, 0], 
                       title="Income Metrics (RWF)")
    st.plotly_chart(fig_income, use_container_width=True)

# ==================== CATEGORY 3: IMPACT ====================
def display_category_3(df):
    """Category 3: Impact"""
    st.markdown('<div class="category-header"><h2>Category 3: Impact</h2></div>', 
                unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Jobs Created", 0)
    with col2:
        st.metric("Green Jobs (Male)", 0)
    with col3:
        st.metric("Green Jobs (Female)", 0)
    
    st.subheader("3.1 Green Jobs by Category")
    job_cats = ['Tree Nursery', 'Tree Plant', 'Terracing', 'Conservation', 'Rainwater', 'Carpentry', 'Tailoring']
    # fig_jobs = px.barh( y=job_cats,x=[0]*7, title="Green Jobs by Category")
    fig_jobs = px.bar(
        y=job_cats,
        x=[0]*7,
        orientation='h',
        title="Green Jobs by Category"
    )
    st.plotly_chart(fig_jobs, use_container_width=True)
    
    st.subheader("3.2 Business & Income Growth")
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    col1, col2 = st.columns(2)
    
    with col1:
        fig_sales = go.Figure(data=[
            go.Scatter(x=months, y=[0]*6, mode='lines+markers', name='Current', line=dict(color='#3498db')),
            go.Scatter(x=months, y=[0]*6, mode='lines+markers', name='Baseline', 
                      line=dict(color='#95a5a6', dash='dash'))
        ])
        fig_sales.update_layout(title="Sales Growth", height=400)
        st.plotly_chart(fig_sales, use_container_width=True)
    
    with col2:
        fig_income = go.Figure(data=[
            go.Scatter(x=months, y=[0]*6, mode='lines+markers', fill='tozeroy', 
                      name='Income', line=dict(color='#2ecc71'))
        ])
        fig_income.update_layout(title="Income Growth", height=400)
        st.plotly_chart(fig_income, use_container_width=True)
    
    st.subheader("3.3 Service Delivery to Farmers")
    col1, col2 = st.columns(2)
    
    with col1:
        fig_farmers = go.Figure(data=[
            go.Scatter(x=months, y=[0]*6, mode='lines+markers', name='All Farmers'),
            go.Scatter(x=months, y=[0]*6, mode='lines+markers', name='Young (18-35)')
        ])
        fig_farmers.update_layout(title="Farmers Served", height=400)
        st.plotly_chart(fig_farmers, use_container_width=True)
    
    with col2:
        fig_young = px.bar(x=['Male', 'Female'], y=[0, 0], title="Young Farmers by Gender")
        st.plotly_chart(fig_young, use_container_width=True)

# ==================== FSCs PROFILE SECTION ====================
def display_fscs_profile(df_fscs):
    """Display FSCs Profile with real field names"""
    
    st.markdown('<div class="category-header"><h2>👥 FSCs Profile</h2></div>', 
                unsafe_allow_html=True)
    
    if len(df_fscs) == 0:
        st.info("No FSCs profile data available yet")
        return
    
    # Key metrics from real fields
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total FSCs", len(df_fscs))
    
    with col2:
        unique_leaders = df_fscs['g1/q1_1'].nunique() if 'g1/q1_1' in df_fscs.columns else 0
        st.metric("Unique Leaders", unique_leaders)
    
    with col3:
        avg_income = df_fscs['q2_5'].mean() if 'q2_5' in df_fscs.columns else 0
        st.metric("Avg Monthly Income (RWF)", f"{int(avg_income):,}")
    
    with col4:
        total_employees = df_fscs['g2_2'].sum() if 'g2_2' in df_fscs.columns else 0
        st.metric("Total Employees", int(total_employees))
    
    st.subheader("FSCs Key Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        green_jobs = df_fscs['q2_6'].sum() if 'q2_6' in df_fscs.columns else 0
        st.metric("Green Jobs", int(green_jobs))
    
    with col2:
        male_count = (df_fscs['g1/q1_4'] == 'gabo').sum() if 'g1/q1_4' in df_fscs.columns else 0
        st.metric("Male Leaders", int(male_count))
    
    with col3:
        female_count = (df_fscs['g1/q1_4'] == 'gore').sum() if 'g1/q1_4' in df_fscs.columns else 0
        st.metric("Female Leaders", int(female_count))
    
    st.subheader("FSCs by Sector")
    col1, col2 = st.columns(2)
    
    with col1:
        if 'g1/q1_14' in df_fscs.columns:
            sector_counts = df_fscs['g1/q1_14'].value_counts().head(10)
            fig_sector = px.bar(x=sector_counts.index, y=sector_counts.values, 
                              title="FSCs by Sector", labels={'x': 'Sector', 'y': 'Count'})
            st.plotly_chart(fig_sector, use_container_width=True)
        else:
            st.info("Sector data not available")
    
    # with col2:
    #     if 'g1/q1_13' in df_fscs.columns:
    #         district_counts = df_fscs['g1/q1_13'].value_counts().head(10)
    #         fig_district = px.bar(x=district_counts.index, y=district_counts.values,
    #                             title="FSCs by District", labels={'x': 'District', 'y': 'Count'})
    #         st.plotly_chart(fig_district, use_container_width=True)
    #     else:
    #         st.info("District data not available")
            
    
    st.subheader("FSCs Income Distribution")
    if 'q2_5' in df_fscs.columns:
        fig_income = px.histogram(df_fscs, x='q2_5', nbins=20, 
                                title="Distribution of Monthly Income",
                                labels={'q2_5': 'Monthly Income (RWF)'})
        st.plotly_chart(fig_income, use_container_width=True)
    
    # st.subheader("FSCs Profile Data Sample")
    # key_cols = ['g1/q1_1', 'g1/q1_2', 'g1/q1_5', 'g1/q1_14', 'g2_2', 'q2_5']
    # available_cols = [col for col in key_cols if col in df_fscs.columns]
    
    # if available_cols:
    #     st.dataframe(df_fscs[available_cols].head(20), use_container_width=True)
        
    #     csv = df_fscs[available_cols].to_csv(index=False)
    #     st.download_button(
    #         label="Download FSCs Profile (CSV)",
    #         data=csv,
    #         file_name=f"fscs_profile_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
    #         mime="text/csv"
    #     )

# ==================== LIVELIHOOD PROFILE SECTION ====================
def display_livelihood_profile(df_livelihood):
    """Display Livelihood Profile with real field names"""
    
    st.markdown('<div class="category-header"><h2>Livelihood Profile</h2></div>', 
                unsafe_allow_html=True)
    
    if len(df_livelihood) == 0:
        st.info("No Livelihood profile data available yet")
        return
    
    # Key metrics from real fields
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Participants", len(df_livelihood))
    
    with col2:
        # avg_household = df_livelihood['icyiciro_2/q2_1'].mean() if 'icyiciro_2/q2_1' in df_livelihood.columns else 0
        avg_household = pd.to_numeric(df_livelihood['icyiciro_2/q2_1'], errors='coerce').mean() if 'icyiciro_2/q2_1' in df_livelihood.columns else 0
        st.metric("Avg Household Size", f"{avg_household:.1f}")
    
    with col3:
        # avg_income = df_livelihood['icyiciro_4/q4_1'].mean() if 'icyiciro_4/q4_1' in df_livelihood.columns else 0
        avg_income = pd.to_numeric(df_livelihood['icyiciro_4/q4_1'], errors='coerce').mean() if 'icyiciro_4/q4_1' in df_livelihood.columns else 0
        st.metric("Avg Monthly Income (RWF)", f"{int(avg_income):,}")
    
    with col4:
        # avg_land = df_livelihood['icyiciro_5/q5_2'].mean() if 'icyiciro_5/q5_2' in df_livelihood.columns else 0
        avg_land = round(pd.to_numeric(df_livelihood['icyiciro_5/q5_2'], errors='coerce').mean(), 2) if 'icyiciro_5/q5_2' in df_livelihood.columns else 0
        st.metric("Avg Land Size (Ha)", f"{avg_land:.2f}")
    
    st.subheader("Livelihood Key Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        male_count = (df_livelihood['icyiciro_1/q1_7'] == 'gabo').sum() if 'icyiciro_1/q1_7' in df_livelihood.columns else 0
        st.metric("Male Participants", int(male_count))
    
    with col2:
        female_count = (df_livelihood['icyiciro_1/q1_7'] == 'gore').sum() if 'icyiciro_1/q1_7' in df_livelihood.columns else 0
        st.metric("Female Participants", int(female_count))
    
    with col3:
        trained = (df_livelihood['q6_1'] == 'yego').sum() if 'q6_1' in df_livelihood.columns else 0
        st.metric("Trained Participants", int(trained))
    
    st.subheader("Participants by Sector")
    col1, col2 = st.columns(2)
    
    with col1:
        if 'icyiciro_1/umurenge' in df_livelihood.columns:
            sector_counts = df_livelihood['icyiciro_1/umurenge'].value_counts().head(10)
            fig_sector = px.bar(x=sector_counts.index, y=sector_counts.values,
                              title="Participants by Sector", labels={'x': 'Sector', 'y': 'Count'})
            st.plotly_chart(fig_sector, use_container_width=True)
        else:
            st.info("Sector data not available")
    
    # with col2:
    #     if 'icyiciro_1/akarere' in df_livelihood.columns:
    #         district_counts = df_livelihood['icyiciro_1/akarere'].value_counts().head(10)
    #         fig_district = px.bar(x=district_counts.index, y=district_counts.values,
    #                             title="Participants by District", labels={'x': 'District', 'y': 'Count'})
    #         st.plotly_chart(fig_district, use_container_width=True)
    #     else:
    #         st.info("District data not available")
    
    st.subheader("Income Distribution")
    col1, col2 = st.columns(2)
    
    with col1:
        if 'icyiciro_4/q4_1' in df_livelihood.columns:
            fig_income = px.histogram(df_livelihood, x='icyiciro_4/q4_1', nbins=20,
                                    title="Monthly Income Distribution",
                                    labels={'icyiciro_4/q4_1': 'Income (RWF)'})
            st.plotly_chart(fig_income, use_container_width=True)
    
    with col2:
        if 'icyiciro_5/q5_2' in df_livelihood.columns:
            fig_land = px.histogram(df_livelihood, x='icyiciro_5/q5_2', nbins=15,
                                  title="Land Size Distribution",
                                  labels={'icyiciro_5/q5_2': 'Land (Ha)'})
            st.plotly_chart(fig_land, use_container_width=True)
    
    # st.subheader("Livelihood Profile Data Sample")
    # key_cols = ['icyiciro_1/q1_1', 'icyiciro_1/q1_7', 'icyiciro_1/q1_8', 
    #            'icyiciro_2/q2_1', 'icyiciro_4/q4_1', 'icyiciro_5/q5_2']
    # available_cols = [col for col in key_cols if col in df_livelihood.columns]
    
    # if available_cols:
    #     st.dataframe(df_livelihood[available_cols].head(20), use_container_width=True)
        
    #     csv = df_livelihood[available_cols].to_csv(index=False)
    #     st.download_button(
    #         label="📥 Download Livelihood Profile (CSV)",
    #         data=csv,
    #         file_name=f"livelihood_profile_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
    #         mime="text/csv"
        # )

# ==================== MAIN DASHBOARD ====================
def main():
    """Main dashboard function"""
    
    st.title("FSCs & Livelihood Monitoring Dashboard")
    st.markdown("**Real-time tracking of KPIs, FSCs Profile, and Livelihood Profile**")
    st.markdown("---")
    
    # Fetch all data sources
    data, errors = fetch_all_sources()
    
    # Display errors if any
    if errors:
        with st.expander("⚠️ Data Loading Warnings"):
            for source, error in errors.items():
                st.warning(f"{source}: {error}")
    
    # Get individual dataframes
    df_kpi = data.get('KPI', pd.DataFrame())
    df_fscs_profile = data.get('FSCs_Profile', pd.DataFrame())
    df_livelihood_profile = data.get('Livelihood_Profile', pd.DataFrame())
    
    # Create tabs
    tab1, tab2, tab3, tab4= st.tabs([
        "KPI Dashboard",
        "FSCs Profile",
        "Livelihood Profile",
        "Map",
        # "📈 Analytics"
    ])
    
    # KPI Dashboard Tab
    with tab1:
        st.subheader("KPI Monitoring Dashboard (All Graphs Visible)")
        
        if len(df_kpi) == 0:
            st.info("✓ Dashboard ready - waiting for KPI data submissions")
        
        display_category_1(df_kpi)
        st.divider()
        
        display_category_2(df_kpi)
        st.divider()
        
        display_category_3(df_kpi)
    
    # FSCs Profile Tab
    with tab2:
        display_fscs_profile(df_fscs_profile)
    
    # Livelihood Profile Tab
    with tab3:
        display_livelihood_profile(df_livelihood_profile)
    
    # Map Tab
    with tab4:
        display_gatsibo_map()
        
        st.subheader("Project Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Gitoki Sector**
            - District: Gatsibo
            - Province: Eastern
            - FSCs: Focus on agricultural value chains
            - Livelihood: Mixed farming and commerce
            """)
        
        with col2:
            st.markdown("""
            **Kabarore Sector**
            - District: Gatsibo
            - Province: Eastern
            - FSCs: Services and input supply
            - Livelihood: Diversified income activities
            """)
    
    # Analytics Tab
    with tab5:
        st.subheader("📈 Cross-Source Analytics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total FSCs (Profile)", len(df_fscs_profile))
        with col2:
            st.metric("Total Livelihood Participants", len(df_livelihood_profile))
        with col3:
            st.metric("KPI Records", len(df_kpi))
        with col4:
            total = len(df_fscs_profile) + len(df_livelihood_profile) + len(df_kpi)
            st.metric("Total Records", total)
        
        st.info("Advanced analytics and comparisons coming soon!")
        
        # Data completeness summary
        st.subheader("Data Completeness Summary")
        
        summary_data = {
            'Data Source': ['KPI', 'FSCs Profile', 'Livelihood Profile'],
            'Records': [len(df_kpi), len(df_fscs_profile), len(df_livelihood_profile)],
            'Fields': [len(df_kpi.columns) if len(df_kpi) > 0 else 0,
                      len(df_fscs_profile.columns) if len(df_fscs_profile) > 0 else 0,
                      len(df_livelihood_profile.columns) if len(df_livelihood_profile) > 0 else 0]
        }
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
    
    # Footer
    # st.divider()
    # col1, col2, col3, col4, col5 = st.columns(5)
    
    # with col1:
    #     st.text("📅 Auto-refresh: Every hour")
    # with col2:
    #     st.text(f"📊 KPI: {len(df_kpi)} records")
    # with col3:
    #     st.text(f"👥 FSCs: {len(df_fscs_profile)} records")
    # with col4:
    #     st.text(f"🌾 Livelihood: {len(df_livelihood_profile)} records")
    # with col5:
    #     st.text("v3.5 - Dashboard Ready")

if __name__ == "__main__":
    main()
