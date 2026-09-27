import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="KPI Dashboard", layout="wide", initial_sidebar_state="expanded")

KOBO_BASE_URL = "https://kc.kobotoolbox.org/api/v2"
KOBO_TOKEN = st.secrets.get("KOBO_TOKEN")
KOBO_ASSET_ID = st.secrets.get("KOBO_ASSET_ID")

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
</style>
""", unsafe_allow_html=True)

# ==================== CACHE DATA LOADING ====================
@st.cache_data(ttl=3600)
def fetch_kobo_data():
    """
    Fetch data from KoBoToolbox API with error handling
    Cache for 1 hour (3600 seconds)
    """
    try:
        headers = {
            "Authorization": f"Token {KOBO_TOKEN}",
            "Accept": "application/json"
        }
        
        url = f"{KOBO_BASE_URL}/assets/{KOBO_ASSET_ID}/data/?limit=10000&offset=0"
        response = requests.get(url, headers=headers, timeout=30)
        
        # Handle different HTTP errors
        if response.status_code == 401:
            return None, "❌ 401 Unauthorized - Check your KoBoToolbox API token"
        elif response.status_code == 404:
            return None, "❌ 404 Asset not found - Check your Asset ID"
        elif response.status_code != 200:
            return None, f"❌ API Error: {response.status_code}"
        
        # Parse JSON response
        data = response.json()
        results = data.get('results', [])
        
        # If no data, return empty DataFrame without error
        if not results:
            return pd.DataFrame(), None
        
        # Convert to DataFrame
        df = pd.DataFrame(results)
        return df, None
        
    except requests.exceptions.ConnectionError:
        return None, "❌ Connection error - Check your internet connection"
    except requests.exceptions.Timeout:
        return None, "❌ Request timeout - Try again"
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

# ==================== EMPTY STATE MESSAGE ====================
def show_empty_state_message():
    """
    Show temporary empty state message with auto-dismiss
    Message appears for 4 seconds then disappears
    """
    placeholder = st.empty()
    
    with placeholder.container():
        st.markdown("""
        <div class="empty-state-message">
        <h4>✓ Dashboard Ready - Awaiting Data</h4>
        <p>Your KoBoToolbox form is configured and ready to receive data.</p>
        <ul style="text-align: left; margin-left: 20px;">
            <li><strong>Next steps:</strong> Share the form URL with data collectors</li>
            <li><strong>Data:</strong> Will appear here automatically once submissions are received</li>
            <li><strong>Refresh:</strong> Dashboard updates every hour</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Auto-dismiss after 4 seconds
    # time.sleep(4)
    placeholder.empty()

# ==================== CATEGORY 1: PARTICIPANTS ====================
def display_category_1(df):
    """
    Category 1: Participants
    - FSCs (Farmer Service Centers)
    - Livelihood Participants (LPs)
    - Indirect Beneficiaries
    - Demographics (Gender, Age)
    """
    st.markdown('<div class="category-header"><h2>Category 1: Participants</h2></div>', 
                unsafe_allow_html=True)
    
    # Calculate metrics
    if len(df) > 0:
        fscs_count = df.get('fsc_count', pd.Series([0])).sum()
        lps_count = df.get('lp_count', pd.Series([0])).sum()
        indirect_count = df.get('indirect_beneficiaries', pd.Series([0])).sum()
    else:
        fscs_count = 0
        lps_count = 0
        indirect_count = 0
    
    total_participants = fscs_count + lps_count
    
    # Display metric cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total FSCs", int(fscs_count), delta=None)
    
    with col2:
        st.metric("Livelihood Participants", int(lps_count), delta=None)
    
    with col3:
        st.metric("Indirect Beneficiaries", int(indirect_count), delta=None)
    
    with col4:
        st.metric("Total Direct Beneficiaries", int(total_participants), delta=None)
    
    # FSCs by Sector
    st.subheader("FSCs Distribution by Sector (Gitoki & Kabarore)")
    col1, col2 = st.columns(2)
    
    with col1:
        fig_sector = go.Figure(data=[
            go.Bar(
                x=['Gitoki Sector', 'Kabarore Sector'],
                y=[0, 0],
                marker_color=['#1f77b4', '#ff7f0e'],
                text=[0, 0],
                textposition='auto'
            )
        ])
        fig_sector.update_layout(
            title="FSCs by Sector",
            xaxis_title="Sector",
            yaxis_title="Number of FSCs",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig_sector, use_container_width=True)
    
    # Demographics (Gender & Age)
    with col2:
        fig_demo = go.Figure(data=[
            go.Bar(name='Male', x=['Age 18-35', 'Age 35+'], y=[0, 0]),
            go.Bar(name='Female', x=['Age 18-35', 'Age 35+'], y=[0, 0])
        ])
        fig_demo.update_layout(
            title="Participants by Gender & Age",
            xaxis_title="Age Group",
            yaxis_title="Count",
            barmode='group',
            height=400
        )
        st.plotly_chart(fig_demo, use_container_width=True)

# ==================== CATEGORY 2: PERFORMANCE ====================
def display_category_2(df):
    """
    Category 2: FSCs and LPs' Performance
    - 2.1 Trainings & Skills Development
    - 2.2 Access to Finance
    - 2.3 Access to Market
    - 2.4 Post Harvest Management (PHM)
    - 2.5 Income & Earnings
    """
    st.markdown('<div class="category-header"><h2>Category 2: Performance</h2></div>', 
                unsafe_allow_html=True)
    
    # Key performance metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Trainings Completed", 0)
    with col2:
        st.metric("FSCs with Business Plans", 0)
    with col3:
        st.metric("Access to Finance", 0)
    with col4:
        st.metric("Market Linkages", 0)
    
    # ========== 2.1 Trainings & Skills Development ==========
    st.subheader("2.1 Trainings & Skills Development")
    col1, col2 = st.columns(2)
    
    with col1:
        fig_skills = go.Figure(data=[
            go.Bar(
                x=['Skills Dev', 'Vocational', 'Business Plans', 'Mgt Skills'],
                y=[0, 0, 0, 0],
                marker_color='#2ecc71',
                text=[0, 0, 0, 0],
                textposition='auto'
            )
        ])
        fig_skills.update_layout(
            title="Training Types Completed",
            yaxis_title="Count",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig_skills, use_container_width=True)
    
    with col2:
        training_data = {
            'Training Type': [
                'GAP Training', 'Climate Resilience (CSA)', 'Financial Literacy',
                'Bookkeeping', 'Crop/Livestock Insurance', 'Tailoring', 'Carpentry',
                'Painting', 'Hair Dressing', 'Manicure/Pedicure'
            ],
            'Count': [0] * 10
        }
        fig_training_detail = px.bar(
            training_data,
            x='Count',
            y='Training Type',
            orientation='h',
            title="Detailed Training Types"
        )
        fig_training_detail.update_layout(height=400)
        st.plotly_chart(fig_training_detail, use_container_width=True)
    
    # ========== 2.2 Access to Finance ==========
    st.subheader("2.2 Access to Finance (Loans & Grants)")
    col1, col2 = st.columns(2)
    
    with col1:
        fig_loans = go.Figure(data=[
            go.Bar(
                name='Males',
                x=['Revolving Loans', 'Grants'],
                y=[0, 0]
            ),
            go.Bar(
                name='Females',
                x=['Revolving Loans', 'Grants'],
                y=[0, 0]
            )
        ])
        fig_loans.update_layout(
            title="Access to Finance (Gender Segregated)",
            barmode='group',
            height=400
        )
        st.plotly_chart(fig_loans, use_container_width=True)
    
    with col2:
        finance_metrics = {
            'Metric': ['Total Loans', 'Total Grants', 'Avg Loan Amount', 'Avg Grant Amount'],
            'Value': [0, 0, 0, 0]
        }
        fig_finance = px.bar(
            finance_metrics,
            x='Metric',
            y='Value',
            title="Finance Summary (RWF)",
            color='Value',
            color_continuous_scale='Blues'
        )
        fig_finance.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_finance, use_container_width=True)
    
    # ========== 2.3 Access to Market ==========
    st.subheader("2.3 Access to Market")
    col1, col2 = st.columns(2)
    
    with col1:
        commodities = {
            'Commodity': ['Agro Inputs', 'Beans', 'Chili', 'Coffee', 'Soybeans', 
                         'Banana', 'Sweet Potatoes', 'Irish Potatoes', 'Maize', 
                         'Sorghum', 'Vet Products', 'Livestock Products'],
            'Sales (RWF)': [0] * 12
        }
        fig_commodities = px.bar(
            commodities,
            x='Commodity',
            y='Sales (RWF)',
            title="Sales by Commodity Type"
        )
        fig_commodities.update_layout(
            xaxis_tickangle=-45,
            height=400
        )
        st.plotly_chart(fig_commodities, use_container_width=True)
    
    with col2:
        fig_buyers = go.Figure(data=[
            go.Pie(
                labels=['Linked with Big Buyers', 'Not Linked'],
                values=[0, 0],
                hole=0.4,
                marker_colors=['#2ecc71', '#e74c3c']
            )
        ])
        fig_buyers.update_layout(
            title="FSCs Linked with Big Buyers"
        )
        st.plotly_chart(fig_buyers, use_container_width=True)
    
    # Market linkage details
    st.info("**Market Linkages:** Number of contracts signed, types of products under agreement, big buyer information")
    
    # ========== 2.4 Post Harvest Management (PHM) ==========
    st.subheader("2.4 Post Harvest Management (PHM)")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("FSCs Trained in PHM", 0)
        fig_phm = go.Figure(data=[
            go.Bar(
                x=['Male', 'Female'],
                y=[0, 0],
                marker_color=['#3498db', '#e74c3c'],
                text=[0, 0],
                textposition='auto'
            )
        ])
        fig_phm.update_layout(
            title="PHM Training by Gender",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig_phm, use_container_width=True)
    
    with col2:
        st.metric("PHM Materials Distributed", 0)
        phm_materials = {
            'Material Type': ['Storage Bags', 'Drying Racks', 'Packaging', 'Tools', 'Other'],
            'Quantity': [0, 0, 0, 0, 0]
        }
        fig_phm_mat = px.bar(
            phm_materials,
            x='Material Type',
            y='Quantity',
            title="PHM Materials Distribution",
            color='Quantity',
            color_continuous_scale='Viridis'
        )
        fig_phm_mat.update_layout(height=400)
        st.plotly_chart(fig_phm_mat, use_container_width=True)
    
    # ========== 2.5 Income & Earnings ==========
    st.subheader("2.5 Income & Earnings")
    col1, col2 = st.columns(2)
    
    with col1:
        income_metrics = {
            'Metric': ['Avg Monthly Income', 'Quarterly Turnover', 'Service Commissions'],
            'Amount (RWF)': [0, 0, 0]
        }
        fig_income = px.bar(
            income_metrics,
            x='Metric',
            y='Amount (RWF)',
            title="Income Metrics",
            color='Amount (RWF)',
            color_continuous_scale='Greens'
        )
        fig_income.update_layout(height=400)
        st.plotly_chart(fig_income, use_container_width=True)
    
    with col2:
        st.markdown("""
        **Income Sources Tracked:**
        - Monthly income from sales
        - Business venture income
        - Service commissions:
          - Vaccinations
          - Artificial insemination
          - Other value chain services
        """)

# ==================== CATEGORY 3: IMPACT ====================
def display_category_3(df):
    """
    Category 3: Impact
    - 3.1 Green Jobs Creation
    - 3.2 Business & Income Growth (Trends)
    - 3.3 Service Delivery to Farmers
    """
    st.markdown('<div class="category-header"><h2>Category 3: Impact</h2></div>', 
                unsafe_allow_html=True)
    
    # ========== 3.1 Green Jobs Creation ==========
    st.subheader("3.1 Green Jobs Creation")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Jobs Created", 0)
    with col2:
        st.metric("Green Jobs (Male)", 0)
    with col3:
        st.metric("Green Jobs (Female)", 0)
    
    col1, col2 = st.columns(2)
    
    with col1:
        job_categories = {
            'Job Category': ['Tree Nursery', 'Tree Planting', 'Terracing', 'Conservation Ag', 
                           'Rainwater Harvesting', 'Carpentry', 'Tailoring', 'Hair Dressing'],
            'Count': [0] * 8
        }
        fig_jobs = px.bar(
            job_categories,
            x='Count',
            y='Job Category',
            orientation='h',
            title="Green Jobs by Category",
            color='Count',
            color_continuous_scale='RdYlGn'
        )
        fig_jobs.update_layout(height=400)
        st.plotly_chart(fig_jobs, use_container_width=True)
    
    with col2:
        job_types = {
            'Job Type': ['Full Time', 'Part Time', 'Contractual', 'Casual'],
            'Male': [0, 0, 0, 0],
            'Female': [0, 0, 0, 0]
        }
        fig_job_types = go.Figure(data=[
            go.Bar(name='Male', x=job_types['Job Type'], y=job_types['Male']),
            go.Bar(name='Female', x=job_types['Job Type'], y=job_types['Female'])
        ])
        fig_job_types.update_layout(
            title="Jobs by Type & Gender",
            barmode='group',
            height=400
        )
        st.plotly_chart(fig_job_types, use_container_width=True)
    
    # Wage metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Average Monthly Wage (RWF)", "0", delta=None)
    with col2:
        st.metric("Job Security Rate", "0%", delta=None)
    
    # ========== 3.2 Business & Income Growth (Trends) ==========
    st.subheader("3.2 Business & Income Growth (Trends Over Time)")
    col1, col2 = st.columns(2)
    
    # Time series data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    
    with col1:
        fig_sales_trend = go.Figure(data=[
            go.Scatter(
                x=months,
                y=[0] * 6,
                mode='lines+markers',
                name='Current Sales',
                line=dict(color='#3498db', width=3),
                marker=dict(size=8)
            ),
            go.Scatter(
                x=months,
                y=[0] * 6,
                mode='lines+markers',
                name='Baseline Sales',
                line=dict(color='#95a5a6', width=2, dash='dash'),
                marker=dict(size=6)
            )
        ])
        fig_sales_trend.update_layout(
            title="Sales Growth Over Time (Comparison with Baseline)",
            xaxis_title="Month",
            yaxis_title="Sales (RWF)",
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig_sales_trend, use_container_width=True)
    
    with col2:
        fig_income_trend = go.Figure(data=[
            go.Scatter(
                x=months,
                y=[0] * 6,
                mode='lines+markers',
                name='Income',
                fill='tozeroy',
                line=dict(color='#2ecc71', width=3),
                marker=dict(size=8)
            )
        ])
        fig_income_trend.update_layout(
            title="Income Growth Over Time",
            xaxis_title="Month",
            yaxis_title="Income (RWF)",
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig_income_trend, use_container_width=True)
    
    # ========== 3.3 Service Delivery to Farmers ==========
    st.subheader("3.3 Service Delivery to Farmers")
    col1, col2 = st.columns(2)
    
    with col1:
        fig_farmers_served = go.Figure(data=[
            go.Scatter(
                x=months,
                y=[0] * 6,
                mode='lines+markers',
                name='All Farmers',
                line=dict(width=3, color='#3498db')
            ),
            go.Scatter(
                x=months,
                y=[0] * 6,
                mode='lines+markers',
                name='Young Farmers (18-35 years)',
                line=dict(width=3, color='#e74c3c')
            )
        ])
        fig_farmers_served.update_layout(
            title="Farmers Served Over Time (Total vs Young Farmers)",
            xaxis_title="Month",
            yaxis_title="Number of Farmers",
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig_farmers_served, use_container_width=True)
    
    with col2:
        fig_young_farmers = go.Figure(data=[
            go.Bar(
                x=['Male (18-35)', 'Female (18-35)'],
                y=[0, 0],
                marker_color=['#3498db', '#e74c3c'],
                text=[0, 0],
                textposition='auto'
            )
        ])
        fig_young_farmers.update_layout(
            title="Young Farmers Served by Gender",
            yaxis_title="Count",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig_young_farmers, use_container_width=True)

# ==================== MAIN DASHBOARD ====================
def main():
    """Main dashboard function"""
    
    # Title and description
    st.title("FSCs Monitoring Dashboard")
    st.markdown("**Real-time tracking of project KPIs across all categories**")
    st.markdown("---")
    
    # Try to fetch data from KoBoToolbox
    df, error = fetch_kobo_data()
    
    # Handle API errors
    if error:
        st.error(error)
        if "401" in error:
            st.error("""
            **How to fix 401 Unauthorized:**
            
            1. Go to https://kc.kobotoolbox.org/admin/
            2. Click your profile (top right) → Account Settings
            3. Copy your API Token
            4. Go to ~/.streamlit/secrets.toml (or Streamlit Cloud Secrets)
            5. Add: `kobo_token = "YOUR_TOKEN_HERE"`
            6. Save and restart the dashboard
            """)
        return
    
    # Handle connection issues
    if df is None:
        st.error("❌ Could not load data from KoBoToolbox")
        return
    
    # Handle empty data (show message then empty graphs)
    if len(df) == 0:
        show_empty_state_message()
    
    # Display all three categories
    display_category_1(df)
    st.divider()
    
    display_category_2(df)
    st.divider()
    
    display_category_3(df)
    
    # Footer
    # st.divider()
    # col1, col2, col3 = st.columns(3)
    # with col1:
    #     st.text("📅 Last updated: Every hour")
    # with col2:
    #     if len(df) > 0:
    #         st.text(f"📊 Total records: {len(df)}")
    #     else:
    #         st.text("📊 Waiting for data...")
    # with col3:
    #     st.text("NISR KPI Dashboard v2.0")

# ==================== RUN DASHBOARD ====================
if __name__ == "__main__":
    main()
