import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import time

# ==================== PAGE CONFIG ====================
st.set_page_config( 
    page_title="FSCs Dashboard", 
    page_icon="", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)
# ==================== CONFIGURATION ====================
KOBO_BASE_URL = "https://kc.kobotoolbox.org/api/v2"
KOBO_TOKEN = st.secrets.get("KOBO_TOKEN")
KOBO_ASSET_ID_KPI = st.secrets.get("KOBO_ASSET_ID_KPI")
KOBO_ASSET_ID_FSCs = st.secrets.get("KOBO_ASSET_ID_FSCs")
KOBO_ASSET_ID_LIVELIHOOD = st.secrets.get("KOBO_ASSET_ID_LIVELIHOOD")


# Configure page 
st.set_page_config( 
    page_title="FSCs Dashboard", 
    page_icon="", 
    layout="wide", 
    initial_sidebar_state="expanded" 
) 
 
st.markdown(f""" 
    <style> 
        :root {{ 
            /* NISR Primary Brand Colors */ 
            --navy-blue: #1f4788; 
            --light-blue: #4a90e2; 
            --orange: #ff9500; 
            --purple: #7c3aed; 
             
            /* Supporting Colors */ 
            --grid-line: #e5e7eb; 
            --text-primary: #1f2937; 
            --text-secondary: #6b7280; 
            --text-muted: #9ca3af; 
            --bg-white: #ffffff; 
            --bg-light: #f9fafb; 
            --border-color: #d1d5db; 
        }} 
 
        /* ========== GLOBAL STYLES ========== */ 
        .main {{ 
            background-color: var(--bg-light); 
        }} 
 
        h1, h2, h3 {{ 
            color: var(--navy-blue); 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
        }} 
 
        h1 {{ font-size: 32px; font-weight: 700; margin-bottom: 8px; }} 
        h2 {{ font-size: 24px; font-weight: 600; margin-top: 20px; }} 
        h3 {{ font-size: 18px; font-weight: 600; }} 
 
        /* ========== STAT TILES (1 & Similar) ========== */ 
        .stat-tile {{ 
            background: var(--bg-white); 
            border-radius: 12px; 
            padding: 24px; 
            border-left: 5px solid var(--navy-blue); 
            box-shadow: 0 2px 8px rgba(0,0,0,0.08); 
            transition: all 0.3s ease; 
        }} 
 
        .stat-tile:hover {{ 
            box-shadow: 0 4px 16px rgba(31,71,136,0.15); 
            transform: translateY(-2px); 
        }} 
 
        .stat-tile-value {{ 
            font-size: 32px; 
            font-weight: 700; 
            color: var(--navy-blue); 
            margin-bottom: 4px; 
        }} 
 
        .stat-tile-label {{ 
            font-size: 14px; 
            color: var(--text-secondary); 
            font-weight: 500; 
            text-transform: uppercase; 
            letter-spacing: 0.5px; 
        }} 
 
        .stat-tile-icon {{ 
            font-size: 28px; 
            margin-bottom: 8px; 
        }} 
 
        /* ========== CHART CONTAINERS ========== */ 
        .chart-container {{ 
            background: var(--bg-white); 
            border-radius: 12px; 
            padding: 20px; 
            border: 1px solid var(--border-color); 
            margin-bottom: 20px; 
        }} 
 
        .chart-title {{ 
            font-size: 16px; 
            font-weight: 600; 
            color: var(--text-primary); 
            margin-bottom: 16px; 
        }} 
 
        /* ========== PIE CHARTS (2, etc) ========== */ 
        .pie-chart {{ 
            background: var(--bg-white); 
            padding: 20px; 
            border-radius: 12px; 
            border: 1px solid var(--border-color); 
        }} 
 
        /* ========== BAR CHARTS (Indicators #3, #5, etc) ========== */ 
        .bar-chart {{ 
            background: var(--bg-white); 
            padding: 20px; 
            border-radius: 12px; 
            border: 1px solid var(--border-color); 
        }} 
 
        /* ========== GAUGE CHARTS (Indicators #8, #15, etc) ========== */ 
        .gauge-chart {{ 
            background: var(--bg-white); 
            padding: 20px; 
            border-radius: 12px; 
            border: 1px solid var(--border-color); 
            text-align: center; 
        }} 
 
        /* ========== DATA QUALITY NOTES ========== */ 
        .data-note {{ 
            background: var(--bg-light); 
            border-left: 4px solid var(--light-blue); 
            padding: 12px 16px; 
            margin-top: 20px; 
            border-radius: 4px; 
            font-size: 12px; 
            color: var(--text-secondary); 
        }} 
 
        /* ========== METRIC CARDS ========== */ 
        .stMetric {{ 
            background-color: var(--bg-white); 
            padding: 20px; 
            border-radius: 8px; 
            border-left: 4px solid var(--navy-blue); 
            box-shadow: 0 1px 3px rgba(0,0,0,0.1); 
        }} 
 
        /* ========== SIDEBAR STYLING ========== */ 
        .sidebar-header {{ 
            background: linear-gradient(135deg, var(--navy-blue) 0%, var(--light-blue) 100%); 
            padding: 20px; 
            border-radius: 10px; 
            color: white; 
            margin-bottom: 20px; 
        }} 
 
        .sidebar-header h2 {{ 
            color: white; 
            margin: 0; 
            font-size: 24px; 
        }} 
 
        .sidebar-header p {{ 
            color: rgba(255,255,255,0.8); 
            margin: 5px 0 0 0; 
            font-size: 14px; 
        }} 
 
        /* ========== DIVIDERS ========== */ 
        .header-divider {{ 
            border-bottom: 3px solid var(--light-blue); 
            margin: 20px 0; 
        }} 
 
        /* ========== LEGEND STYLING ========== */ 
        .legend {{ 
            display: flex; 
            gap: 20px; 
            margin-top: 15px; 
            flex-wrap: wrap; 
        }} 
 
        .legend-item {{ 
            display: flex; 
            align-items: center; 
            gap: 8px; 
            font-size: 12px; 
            color: var(--text-secondary); 
        }} 
 
        .legend-color {{ 
            width: 16px; 
            height: 16px; 
            border-radius: 3px; 
        }} 
 
        /* ========== COLOR-CODED CELLS ========== */ 
        .color-navy {{ color: var(--navy-blue); }} 
        .color-light-blue {{ color: var(--light-blue); }} 
        .color-orange {{ color: var(--orange); }} 
        .color-purple {{ color: var(--purple); }} 
 
        .bg-navy {{ background-color: var(--navy-blue); }} 
        .bg-light-blue {{ background-color: var(--light-blue); }} 
        .bg-orange {{ background-color: var(--orange); }} 
        .bg-purple {{ background-color: var(--purple); }} 
 
        /* ========== RESPONSIVE GRID ========== */ 
        .metrics-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px; 
            margin-bottom: 20px; 
        }} 
 
        /* ========== INFO & WARNING BOXES ========== */ 
        .info-box {{ 
            background: #dbeafe; 
            border-left: 4px solid var(--light-blue); 
            padding: 12px 16px; 
            border-radius: 4px; 
            font-size: 13px; 
            color: #1e40af; 
        }} 
 
        .warning-box {{ 
            background: #fef3c7; 
            border-left: 4px solid #f59e0b; 
            padding: 12px 16px; 
            border-radius: 4px; 
            font-size: 13px; 
            color: #92400e; 
        }} 
 
        /* ========== SECTION HEADERS ========== */ 
        .section-header {{ 
            border-bottom: 2px solid var(--navy-blue); 
            padding-bottom: 12px; 
            margin-bottom: 20px; 
        }} 
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
            return None, " 401 Unauthorized" 
        elif response.status_code == 404: 
            return None, " 404 Asset not found" 
        elif response.status_code != 200: 
            return None, f" API Error: {response.status_code}" 
         
        data = response.json() 
        results = data.get('results', []) 
         
        if not results: 
            return pd.DataFrame(), None 
         
        df = pd.DataFrame(results) 
        return df, None 
         
    except Exception as e: 
        return None, f" Error: {str(e)}" 
 
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


# ==================== 1: HEADLINE FOR FSCS PROFILING ====================
def calculate_headline_kpis(df):
    """Calculate 6 headline KPI metrics from FSCs data - CORRECTED COLUMN NAMES"""
    kpis = {}
    
    # KPI 1: Total FSCs
    kpis['total_fscs'] = len(df)
    
    # KPI 2: Total Jobs Created (g2/q2_2)
    kpis['total_jobs'] = int(pd.to_numeric(df['g2/q2_2'], errors='coerce').sum()) if 'g2/q2_2' in df.columns else 0
    
    # KPI 3: Farmers Served (g4/g4_9/q4_9_women + g4/g4_9/q4_9_men)
    farmers_women = int(pd.to_numeric(df['g4/g4_9/q4_9_women'], errors='coerce').sum()) if 'g4/g4_9/q4_9_women' in df.columns else 0
    farmers_men = int(pd.to_numeric(df['g4/g4_9/q4_9_men'], errors='coerce').sum()) if 'g4/g4_9/q4_9_men' in df.columns else 0
    kpis['farmers_served'] = farmers_women + farmers_men
    
    # KPI 4: Green Jobs (g2/q2_6 with percentage)
    green_jobs = int(pd.to_numeric(df['g2/q2_6'], errors='coerce').sum()) if 'g2/q2_6' in df.columns else 0
    kpis['green_jobs'] = green_jobs
    kpis['green_jobs_pct'] = round((green_jobs / kpis['total_jobs'] * 100) if kpis['total_jobs'] > 0 else 0, 1)
    
    # KPI 5: Business Plans (g5/q5_1 = "yes")
    business_plans = len(df[df['g5/q5_1'].astype(str).str.lower() == 'yes']) if 'g5/q5_1' in df.columns else 0
    kpis['business_plans'] = business_plans
    kpis['business_plans_pct'] = round((business_plans / kpis['total_fscs'] * 100) if kpis['total_fscs'] > 0 else 0, 1)
    
    # KPI 6: Financing Need (g3/q3_12)
    kpis['financing_need'] = int(pd.to_numeric(df['g3/q3_12'], errors='coerce').sum()) if 'g3/q3_12' in df.columns else 0
    
    return kpis

def render_headline_kpis(df):
    """Render 6 KPI stat tiles"""
    if df.empty:
        st.warning("No FSCs data available")
        return
    
    kpis = calculate_headline_kpis(df)
    
    st.markdown('<div class="section-header"><h3 class="color-navy">Headline Metrics - FSCs Impact Overview</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col5, col6 = st.columns(2)
    
    with col1:
        st.markdown(f'<div class="stat-tile"><div class="stat-tile-icon"></div><div class="stat-tile-value">{kpis["total_fscs"]}</div><div class="stat-tile-label">Total FSCs</div></div>', unsafe_allow_html=True)
        st.caption("Farmer Service Centers documented")
    
    with col2:
        jobs = f"{kpis['total_jobs']:,}" if kpis['total_jobs'] >= 1000 else str(kpis['total_jobs'])
        st.markdown(f'<div class="stat-tile"><div class="stat-tile-icon"></div><div class="stat-tile-value">{jobs}+</div><div class="stat-tile-label">Jobs Created</div></div>', unsafe_allow_html=True)
        st.caption("Employment opportunities")
    
    with col3:
        farmers = f"{kpis['farmers_served']:,}" if kpis['farmers_served'] >= 1000 else str(kpis['farmers_served'])
        st.markdown(f'<div class="stat-tile"><div class="stat-tile-icon"></div><div class="stat-tile-value">{farmers}+</div><div class="stat-tile-label">Farmers Served</div></div>', unsafe_allow_html=True)
        st.caption("Direct agricultural beneficiaries")
    
    with col4:
        st.markdown(f'<div class="stat-tile"><div class="stat-tile-icon"></div><div class="stat-tile-value">{kpis["green_jobs"]} ({kpis["green_jobs_pct"]:.1f}%)</div><div class="stat-tile-label">Green Jobs</div></div>', unsafe_allow_html=True)
        st.caption("Climate-smart livelihoods")
    
    with col5:
        st.markdown(f'<div class="stat-tile"><div class="stat-tile-icon"></div><div class="stat-tile-value">{kpis["business_plans"]} ({kpis["business_plans_pct"]:.1f}%)</div><div class="stat-tile-label">Business Plans</div></div>', unsafe_allow_html=True)
        st.caption("FSCs with formalized strategies")
    
    with col6:
        financing = f"${kpis['financing_need'] / 1000:.0f}K" if kpis['financing_need'] >= 1000 else f"${kpis['financing_need']}"
        st.markdown(f'<div class="stat-tile"><div class="stat-tile-icon"></div><div class="stat-tile-value">{financing}</div><div class="stat-tile-label">Financing Need</div></div>', unsafe_allow_html=True)
        st.caption("Total capital for growth")
    
    st.markdown(f'<div class="data-note"><b>Data:</b> {len(df)} FSCs | {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M UTC")}</div>', unsafe_allow_html=True)


# OTHER FSCS PROFILE  CHARTS
# ==================== 2: GENDER DISTRIBUTION ====================
def render_gender_distribution(df):
    """2: Gender of FSC s - Pie Chart"""
    if df.empty:
        st.warning("No data available")
        return
    
    gender_data = df['g1/q1_4'].value_counts() if 'g1/q1_4' in df.columns else pd.Series()
    
    if gender_data.empty:
        st.info("No gender data available")
        return
    
    # Map Kinyarwanda to English
    gender_map = {'gabo': 'Male', 'gore': 'Female'}
    labels = [gender_map.get(g, g) for g in gender_data.index]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=gender_data.values,
        marker=dict(colors=['#1f4788', '#ff9500']),
        hole=0
    )])
    fig.update_layout(title="FSC  Gender Distribution", height=500)
    st.plotly_chart(fig, use_container_width=True)

# ==================== 3: EMPLOYEE GENDER SPLIT ====================
def render_employee_gender_split(df):
    """3: Employee Gender Distribution - Vertical Bar"""
    if df.empty:
        st.warning("No data available")
        return
    
    women_employees = int(pd.to_numeric(df['g2/g2_3/q2_3_women'], errors='coerce').sum()) if 'g2/g2_3/q2_3_women' in df.columns else 0
    men_employees = int(pd.to_numeric(df['g2/g2_3/q2_3_men'], errors='coerce').sum()) if 'g2/g2_3/q2_3_men' in df.columns else 0
    total_employees = women_employees + men_employees
    
    women_pct = (women_employees / total_employees * 100) if total_employees > 0 else 0
    men_pct = (men_employees / total_employees * 100) if total_employees > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Female Employees", int(women_employees))
    with col2:
        st.metric("Male Employees", int(men_employees))
    with col3:
        st.metric("Total Employees", int(total_employees))
    
    fig = go.Figure(data=[
        go.Bar(name='Female', x=['Employees'], y=[women_employees], marker_color='#ff9500'),
        go.Bar(name='Male', x=['Employees'], y=[men_employees], marker_color='#1f4788')
    ])
    fig.update_layout(title="Employee Gender Split", barmode='group', height=400, yaxis_title="Number of Employees")
    st.plotly_chart(fig, use_container_width=True)

# ==================== 4: VALUE CHAINS COVERAGE ====================
def render_value_chains(df):
    """4: Value Chains Served - Vertical Bar"""
    if df.empty:
        st.warning("No data available")
        return
    
    chains = {
        'Tubers': len(df[df['g2/g2_14/q2_14_tubers'].notna()]) if 'g2/g2_14/q2_14_tubers' in df.columns else 0,
        'Cereals': len(df[df['g2/g2_14/q2_14_cereals'].notna()]) if 'g2/g2_14/q2_14_cereals' in df.columns else 0,
        'Vegetables': len(df[df['g2/g2_14/q2_14_vegetables'].notna()]) if 'g2/g2_14/q2_14_vegetables' in df.columns else 0,
        'Fruits': len(df[df['g2/g2_14/q2_14_fruits'].notna()]) if 'g2/g2_14/q2_14_fruits' in df.columns else 0,
        'Livestock': len(df[df['g2/g2_14/q2_14_livestock'].notna()]) if 'g2/g2_14/q2_14_livestock' in df.columns else 0,
        'Cash Crops': len(df[df['g2/g2_14/q2_14_cashcrops'].notna()]) if 'g2/g2_14/q2_14_cashcrops' in df.columns else 0,
    }
    
    chains = {k: v for k, v in sorted(chains.items(), key=lambda x: x[1], reverse=True)}
    
    fig = go.Figure(data=[
        go.Bar(x=list(chains.keys()), y=list(chains.values()), marker_color='#4a90e2')
    ])
    fig.update_layout(title="Value Chains Served by FSCs", height=400, yaxis_title="Number of FSCs")
    st.plotly_chart(fig, use_container_width=True)

# ==================== 5: FINANCIAL SERVICES ACCESS ====================
def render_financial_access(df):
    """5: Financial Services Access - Vertical Bar with Percentages"""
    if df.empty:
        st.warning("No data available")
        return
    
    bank_account = len(df[df['g3/q3_5'].astype(str).str.lower() == 'yes']) if 'g3/q3_5' in df.columns else 0
    bank_loan = len(df[df['g3/q3_6'].astype(str).str.lower() == 'yes']) if 'g3/q3_6' in df.columns else 0
    
    total = len(df)
    bank_account_pct = (bank_account / total * 100) if total > 0 else 0
    bank_loan_pct = (bank_loan / total * 100) if total > 0 else 0
    
    # Create metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("With Bank Account", f"{int(bank_account)} ({bank_account_pct:.1f}%)")
    with col2:
        st.metric("With Bank Loan", f"{int(bank_loan)} ({bank_loan_pct:.1f}%)")
    
    # Vertical bar chart
    fig = go.Figure(data=[
        go.Bar(x=['Bank Account', 'Bank Loan'], y=[bank_account_pct, bank_loan_pct], marker_color=['#1f4788', '#ff9500'],
               text=[f'{bank_account_pct:.1f}%', f'{bank_loan_pct:.1f}%'],
               textposition='outside')
    ])
    fig.update_layout(title="Financial Services Access (%)", height=400, yaxis_title="Percentage (%)", yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig, use_container_width=True)

# ==================== 6: MARKET LINKAGES ====================
def render_market_linkages(df):
    """6: Market Linkages (Written Contracts) - Donut"""
    if df.empty:
        st.warning("No data available")
        return
    
    has_contracts = len(df[df['g4/q4_1'].astype(str).str.lower() == 'yes']) if 'g4/q4_1' in df.columns else 0
    no_contracts = len(df) - has_contracts
    
    fig = go.Figure(data=[go.Pie(
        labels=['With Contracts', 'No Contracts'],
        values=[has_contracts, no_contracts],
        marker=dict(colors=['#1f4788', '#e5e7eb']),
        hole=0.4
    )])
    fig.update_layout(title="FSCs with Written Market Contracts", height=500)
    st.plotly_chart(fig, use_container_width=True)

# ==================== 7: EDUCATION LEVEL ====================
def render_education_distribution(df):
    """7: FSC  Education Level - Vertical Bar"""
    if df.empty:
        st.warning("No data available")
        return
    
    education = df['g1/q1_9'].value_counts() if 'g1/q1_9' in df.columns else pd.Series()
    
    if education.empty:
        st.info("No education data available")
        return
    
    colors_list = ['#1f4788', '#4a90e2', '#ff9500', '#7c3aed']
    colors = colors_list[:len(education)]
    
    fig = go.Figure(data=[
        go.Bar(x=education.index, y=education.values, marker_color=colors)
    ])
    fig.update_layout(title="FSC  Education Level", height=400, yaxis_title="Number of FSCs")
    st.plotly_chart(fig, use_container_width=True)


#===================== FOR LIVELHOOD PROFILING=======================================

# Translation dictionaries
LIVELIHOOD_SOURCE_MAP = {
    'ubuhinzi': 'Agriculture',
    'nyakabyizi': 'Wage per day',
    'akazi_gahemba': 'Salary workers',
    'ubucuruzi_buto': 'Retail trade / small trading',
    'ubworozi': 'Livestock',
    'ibindi': 'Other'
}

FINANCIAL_SERVICE_MAP = {
    'bwite': 'Personal',
    'ubundi': 'For other'
}

def calculate_livelihood_kpis(df):
    """Calculate headline KPIs for Livelihood Profile"""
    total_hh = len(df)
    
    # Income from q4_1 (numeric)
    avg_income = pd.to_numeric(df['icyiciro_4/q4_1'], errors='coerce').mean()
    
    # Diversified livelihoods (multiple income sources)
    income_cols = [col for col in df.columns if 'icyiciro_2' in col and 'q2_' in col]
    if income_cols:
        has_multiple = (df[income_cols].notna().sum(axis=1) >= 2).sum()
        diversified = (has_multiple / total_hh * 100) if total_hh > 0 else 0
    else:
        diversified = 0
    
    # Financial access (has personal or other savings)
    if 'icyiciro_5/q5_1' in df.columns:
        financial_access = (df['icyiciro_5/q5_1'].notna().sum() / total_hh * 100) if total_hh > 0 else 0
    else:
        financial_access = 0
    
    # Primary livelihood source count
    if 'icyiciro_3/q3_1' in df.columns:
        primary_source = df['icyiciro_3/q3_1'].value_counts().idxmax()
        primary_source_english = LIVELIHOOD_SOURCE_MAP.get(primary_source, primary_source)
    else:
        primary_source_english = "N/A"
    
    # Asset ownership (has productive asset)
    if 'icyiciro_4/q4_2' in df.columns:
        asset_ownership = (df['icyiciro_4/q4_2'].notna().sum() / total_hh * 100) if total_hh > 0 else 0
    else:
        asset_ownership = 0
    
    return {
        'Total Households': total_hh,
        'Avg Income': f"RWF {avg_income:,.0f}" if avg_income > 0 else "N/A",
        'Diversified %': f"{diversified:.1f}%",
        'Financial Access %': f"{financial_access:.1f}%",
        'Asset Ownership %': f"{asset_ownership:.1f}%",
        'Primary Source': primary_source_english
    }

def render_livelihood_kpis(df):
    """Display headline KPIs for Livelihood Profile"""
    kpis = calculate_livelihood_kpis(df)
    
    st.markdown("### Livelihood Profile")
    cols = st.columns(3)
    
    with cols[0]:
        st.markdown(f"<div class='stat-tile'><h4>Total Households</h4><h2 style='color:#1f4788'>{kpis['Total Households']}</h2></div>", unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown(f"<div class='stat-tile'><h4>Avg Income</h4><h2 style='color:#1f4788'>{kpis['Avg Income']}</h2></div>", unsafe_allow_html=True)
    
    with cols[2]:
        st.markdown(f"<div class='stat-tile'><h4>Diversified %</h4><h2 style='color:#ff9500'>{kpis['Diversified %']}</h2></div>", unsafe_allow_html=True)
    
    cols2 = st.columns(3)
    
    with cols2[0]:
        st.markdown(f"<div class='stat-tile'><h4>Financial Access %</h4><h2 style='color:#4a90e2'>{kpis['Financial Access %']}</h2></div>", unsafe_allow_html=True)
    
    with cols2[1]:
        st.markdown(f"<div class='stat-tile'><h4>Asset Ownership %</h4><h2 style='color:#7b68ee'>{kpis['Asset Ownership %']}</h2></div>", unsafe_allow_html=True)
    
    with cols2[2]:
        st.markdown(f"<div class='stat-tile'><h4>Primary Source</h4><h2 style='color:#1f4788'>{kpis['Primary Source']}</h2></div>", unsafe_allow_html=True)
    
    st.markdown("---")

def render_livelihood_sources(df):
    """Indicator 2: Primary Livelihood Sources (Pie Chart with English labels)"""
    st.markdown("### Indicator 2: Primary Livelihood Sources")
    
    if 'icyiciro_3/q3_1' in df.columns:
        source_counts = df['icyiciro_3/q3_1'].value_counts()
        
        # Translate labels to English
        source_labels = [LIVELIHOOD_SOURCE_MAP.get(src, src) for src in source_counts.index]
        
        fig = go.Figure(data=[go.Pie(
            labels=source_labels,
            values=source_counts.values,
            marker=dict(colors=['#1f4788', '#ff9500', '#4a90e2', '#7b68ee', '#2ecc71', '#e74c3c']),
            textposition='inside',
            textinfo='label+percent'
        )])
        fig.update_layout(height=500, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Column 'icyiciro_3/q3_1' not found.")

def render_income_distribution(df):
    """Indicator 3: Income Level Distribution (Bar Chart with Income Ranges)"""
    st.markdown("### Indicator 3: Income Level Distribution")
    
    if 'icyiciro_4/q4_1' in df.columns:
        # Convert to numeric and create income brackets
        income_data = pd.to_numeric(df['icyiciro_4/q4_1'], errors='coerce').dropna()
        
        # Create income ranges
        bins = [0, 50000, 100000, 250000, 500000, float('inf')]
        labels = ['0-50,000', '50,000-100,000', '100,000-250,000', '250,000-500,000', '500,000+']
        income_brackets = pd.cut(income_data, bins=bins, labels=labels)
        
        bracket_counts = income_brackets.value_counts().sort_index()
        
        fig = go.Figure(data=[go.Bar(
            x=bracket_counts.index,
            y=bracket_counts.values,
            marker=dict(color='#1f4788'),
            text=bracket_counts.values,
            textposition='outside'
        )])
        fig.update_layout(
            title="Households by Income Range (RWF)",
            xaxis_title="Income Range (RWF)",
            yaxis_title="Number of Households",
            height=700,
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Column 'icyiciro_4/q4_1' not found.")

def render_household_gender_distribution(df):
    """Indicator 4: Household Leader Gender Distribution (REPLACED from diversification)"""
    st.markdown("### Indicator 4: Household Leader Gender Distribution")
    
    if 'icyiciro_1/q1_7' in df.columns:
        gender_map = {'gabo': 'Male', 'gore': 'Female'}
        gender_counts = df['icyiciro_1/q1_7'].map(gender_map).value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=gender_counts.index,
            values=gender_counts.values,
            hole=0.4,
            marker=dict(colors=['#1f4788', '#ff9500']),
            textposition='inside',
            textinfo='label+percent'
        )])
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Column 'icyiciro_1/q1_7' not found.")

def render_asset_ownership(df):
    """Indicator 5: Asset Ownership (Bar Chart with proper English labels)"""
    st.markdown("### Indicator 5: Asset Ownership")
    
    # Define asset column labels
    asset_labels = {
        'icyiciro_4/q4_2': 'Land Property',
        'icyiciro_4/q4_3': 'Equipment',
        'icyiciro_4/q4_4': 'Livestock',
        'icyiciro_4/q4_5': 'Business Stock',
        'icyiciro_4/q4_6': 'Savings'
    }
    
    asset_cols = [col for col in df.columns if col in asset_labels]
    
    if asset_cols:
        asset_ownership = {}
        for col in asset_cols:
            asset_name = asset_labels[col]
            ownership = df[col].notna().sum()
            asset_ownership[asset_name] = ownership
        
        fig = go.Figure(data=[go.Bar(
            x=list(asset_ownership.keys()),
            y=list(asset_ownership.values()),
            marker=dict(color='#4a90e2'),
            text=list(asset_ownership.values()),
            textposition='outside'
        )])
        fig.update_layout(
            title="Asset Ownership Count",
            xaxis_title="Asset Type",
            yaxis_title="Number of Households",
            height=700,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Cannot find asset columns.")

def render_financial_services(df):
    """Indicator 6: Financial Services Access - FIXED LOGIC"""
    st.markdown("### Indicator 6: Financial Services Access")
    
    services = {}
    
    # Fix: Count actual "yes" responses (non-null) not just presence
    if 'icyiciro_5/q5_1' in df.columns:
        has_service = df['icyiciro_5/q5_1'].notna().sum()
        services['Has Savings'] = (has_service / len(df) * 100) if len(df) > 0 else 0
    
    if 'icyiciro_5/q5_2' in df.columns:
        has_service = df['icyiciro_5/q5_2'].notna().sum()
        services['Has Loan'] = (has_service / len(df) * 100) if len(df) > 0 else 0
    
    if 'icyiciro_5/q5_3' in df.columns:
        has_service = df['icyiciro_5/q5_3'].notna().sum()
        services['Has Insurance'] = (has_service / len(df) * 100) if len(df) > 0 else 0
    
    if services:
        fig = go.Figure(data=[go.Bar(
            x=list(services.keys()),
            y=list(services.values()),
            marker=dict(color=['#1f4788', '#ff9500', '#4a90e2']),
            text=[f"{v:.1f}%" for v in services.values()],
            textposition='outside'
        )])
        fig.update_layout(
            title="Financial Services Access (%)",
            yaxis_title="Percentage (%)",
            yaxis=dict(range=[0, 100]),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Cannot find financial services columns.")

def render_livestock_comparison(df):
    """Indicator 7: Livestock Types Owned (Bar Chart)"""
    st.markdown("### Indicator 7: Livestock Ownership Comparison")
    
    # Livestock translation map
    livestock_map = {
        'ihene': 'Goat',
        'inkwavu': 'Rabbit',
        'ingurube': 'Pig',
        'inkoko_imbata': 'Chicken'
    }
    
    if 'icyiciro_5/q5_7' in df.columns:
        # Flatten livestock data (split space-separated values)
        livestock_list = []
        for value in df['icyiciro_5/q5_7'].dropna():
            # Split by space and translate each livestock type
            for livestock in str(value).split():
                english_name = livestock_map.get(livestock, livestock)
                livestock_list.append(english_name)
        
        # Count livestock types
        livestock_counts = pd.Series(livestock_list).value_counts().sort_values(ascending=False)
        
        # Create bar chart
        fig = go.Figure(data=[go.Bar(
            x=livestock_counts.index,
            y=livestock_counts.values,
            marker=dict(color=['#1f4788', '#ff9500', '#4a90e2', '#7b68ee']),
            text=livestock_counts.values,
            textposition='outside'
        )])
        fig.update_layout(
            title="Livestock Types Owned by Households",
            xaxis_title="Livestock Type",
            yaxis_title="Number of Households",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Column 'icyiciro_5/q5_7' not found.")


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
        unique_s = df_fscs['g1/q1_1'].nunique() if 'g1/q1_1' in df_fscs.columns else 0 
        st.metric("Unique s", unique_s) 
     
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
        st.metric("Male s", int(male_count)) 
     
    with col3: 
        female_count = (df_fscs['g1/q1_4'] == 'gore').sum() if 'g1/q1_4' in df_fscs.columns else 0 
        st.metric("Female s", int(female_count)) 
     
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
     
 
    st.subheader("FSCs Income Distribution") 
    if 'q2_5' in df_fscs.columns: 
        fig_income = px.histogram(df_fscs, x='q2_5', nbins=20,  
                                title="Distribution of Monthly Income", 
                                labels={'q2_5': 'Monthly Income (RWF)'}) 
        st.plotly_chart(fig_income, use_container_width=True) 
     
# ==================== MAP SECTION ==================== 
def display_gatsibo_map(): 
    """Display Eastern Province with district and sector boundaries""" 
    st.subheader("📍 Project Locations - Eastern Province, Rwanda") 
    
    import folium
    from folium import GeoJson
    
    # Center on Eastern Province (Gatsibo is in Eastern Province)
    m = folium.Map(
        location=[-1.95, 30.35],
        zoom_start=9,
        tiles='OpenStreetMap'
    )
    
    # Add markers for the two working sectors
    folium.Marker(
        location=[-1.95, 30.35],
        popup='Gitoki Sector - FSCs Profile',
        tooltip='FSCs Profile Data Collection',
        icon=folium.Icon(color='blue', icon='info-sign', prefix='glyphicon')
    ).add_to(m)
    
    folium.Marker(
        location=[-1.92, 30.42],
        popup='Kabarore Sector - Livelihood Profile',
        tooltip='Livelihood Profile Data Collection',
        icon=folium.Icon(color='orange', icon='info-sign', prefix='glyphicon')
    ).add_to(m)
    
    # Add a circle around working areas
    folium.Circle(
        location=[-1.6439, 30.3102],
        radius=5000,
        color='#1f4788',
        fill=True,
        fillColor='#1f4788',
        fillOpacity=0.2,
        popup='Gitoki Working Area'
    ).add_to(m)
    
    folium.Circle(
        location=[-1.6211, 30.3850],
        radius=5000,
        color='#ff9500',
        fill=True,
        fillColor='#ff9500',
        fillOpacity=0.2,
        popup='Kabarore Working Area'
    ).add_to(m)

    
    # Display map
    st.markdown("**Eastern Province - Gatsibo District with Working Sectors**")
    folium_static(m)    
 
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
        with st.expander("Data Loading Warnings"): 
            for source, error in errors.items(): 
                st.warning(f"{source}: {error}") 
     
    # Get individual dataframes 
    df_kpi = data.get('KPI', pd.DataFrame()) 
    df_fscs_profile = data.get('FSCs_Profile', pd.DataFrame()) 
    df_livelihood_profile = data.get('Livelihood_Profile', pd.DataFrame()) 
     
    # Create tabs 
    tab1, tab2, tab3, tab4,tab5= st.tabs([ 
        "FSCs Profile", 
        "Livelihood Profile", 
        "Financial Inclusion", 
        "Capacity & Growth", 
        "Geographic Distribution"
    ]) 
     
    # FSCS PROFILING
    with tab1: 
        st.subheader("FSCs Profile Dashboard") 
        
       
        st.markdown('<h2 style="color: var(--navy-blue);">1: Headline KPIs</h2>', unsafe_allow_html=True)
        render_headline_kpis(df_fscs_profile)
        st.divider()
        
        # 2: Gender Distribution
        st.markdown('<h2 style="color: var(--navy-blue);">2: Gender Distribution</h2>', unsafe_allow_html=True)
        render_gender_distribution(df_fscs_profile)
        st.divider()
        
        # 3: Employee Gender Split
        st.markdown('<h2 style="color: var(--navy-blue);">3: Employee Gender</h2>', unsafe_allow_html=True)
        render_employee_gender_split(df_fscs_profile)
        st.divider()
        
        # 4: Value Chains
        st.markdown('<h2 style="color: var(--navy-blue);">4: Value Chains</h2>', unsafe_allow_html=True)
        render_value_chains(df_fscs_profile)
        st.divider()
        
        # 5: Financial Services
        st.markdown('<h2 style="color: var(--navy-blue);">5: Financial Services</h2>', unsafe_allow_html=True)
        render_financial_access(df_fscs_profile)
        st.divider()
        
        # 6: Market Linkages
        st.markdown('<h2 style="color: var(--navy-blue);">6: Market Linkages</h2>', unsafe_allow_html=True)
        render_market_linkages(df_fscs_profile)
        st.divider()
        
        # 7: Education
        st.markdown('<h2 style="color: var(--navy-blue);">7: Education Level</h2>', unsafe_allow_html=True)
        render_education_distribution(df_fscs_profile)
     
    # Livelyhood Profile Tab 
    with tab2:  # Livelihood Profile Tab
        st.markdown("# Livelihood Profile Dashboard")
        
        all_data, all_errors = fetch_all_sources()
        livelihood_df = all_data['Livelihood_Profile']
        
        if livelihood_df.empty:
            st.error(" No Livelihood data available")
        else:
            render_livelihood_kpis(livelihood_df)
            render_livelihood_sources(livelihood_df)
            render_income_distribution(livelihood_df)
            render_household_gender_distribution(livelihood_df) 
            render_asset_ownership(livelihood_df)
            render_financial_services(livelihood_df)
            render_livestock_comparison(livelihood_df)  

    # Livelihood Profile Tab 
    with tab3: 
        display_livelihood_profile(df_livelihood_profile) 
     
    # Map Tab 
    with tab5: 
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
     
if __name__ == "__main__": 
    main() 
