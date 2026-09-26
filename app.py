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