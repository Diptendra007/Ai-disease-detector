import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(layout="wide", page_title="Admin Dashboard", page_icon="📊")

# API Configuration
API_BASE_URL = "http://127.0.0.1:5000/api"

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .metric-value { font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0; }
    .metric-label { font-size: 1rem; opacity: 0.9; }
</style>
""", unsafe_allow_html=True)

# --- Data Fetching Functions ---
@st.cache_data(ttl=30)
def get_patient_list():
    try:
        response = requests.get(f"{API_BASE_URL}/patients", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Connection Error: Could not connect to API. Is Flask server running?")
        return None
    except Exception as e:
        st.error(f"❌ Error fetching patients: {e}")
        return None

@st.cache_data(ttl=30)
def get_statistics():
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=5)
        response.raise_for_status()
        return response.json()
    except:
        return None

def get_patient_details(patient_id):
    try:
        response = requests.get(f"{API_BASE_URL}/patients/{patient_id}", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching patient details: {e}")
        return None

def delete_patient(patient_id):
    try:
        response = requests.delete(f"{API_BASE_URL}/patients/{patient_id}", timeout=5)
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Error deleting patient: {e}")
        return False

# --- Main Page ---
st.title("📊 Clinical Admin Dashboard")
st.markdown("Monitor all patients with AI-driven risk stratification")

# --- Navigation Buttons ---
col1, col2, col3 = st.columns([3, 1, 1])
with col2:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
with col3:
    st.page_link("_Home.py", label="🏠 Home", use_container_width=True)
st.markdown("---")

stats = get_statistics()
patient_data = get_patient_list()

# --- Statistics Cards ---
if stats:
    st.subheader("📈 Overview Statistics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Total Patients</div><div class='metric-value'>{stats['total_patients']}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card' style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);'><div class='metric-label'>High Risk</div><div class='metric-value'>{stats['high_risk_count']}</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card' style='background: linear-gradient(135deg, #ffa500 0%, #ff7e00 100%);'><div class='metric-label'>Moderate Risk</div><div class='metric-value'>{stats['moderate_risk_count']}</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card' style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);'><div class='metric-label'>Low Risk</div><div class='metric-value'>{stats['low_risk_count']}</div></div>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Disease Distribution Chart
    if stats.get('disease_distribution'): # Use .get() for safety
        st.subheader("🦠 Disease Distribution (Primary Diagnosis)")
        fig = px.pie(
            values=list(stats['disease_distribution'].values()),
            names=list(stats['disease_distribution'].keys()),
            title="Patient Distribution by Primary Diagnosis",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")

# --- Patient List Table ---
if patient_data:
    st.subheader("🏥 Patient Worklist")
    
    df = pd.DataFrame(patient_data)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_query = st.text_input("🔍 Search Patient (by Name or ID)", "")
    with col2:
        risk_filter = st.selectbox("Filter by Risk", ["All", "High Risk (>70%)", "Moderate Risk (40-70%)", "Low Risk (<40%)"])
    with col3:
        sort_by = st.selectbox("Sort by", ["Last Seen", "Risk Score", "Name"])
    
    # Apply filters
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df['name'].str.contains(search_query, case=False, na=False) | 
            filtered_df['patient_id'].str.contains(search_query, case=False, na=False)
        ]
    if risk_filter == "High Risk (>70%)":
        filtered_df = filtered_df[filtered_df['mock_risk'] > 0.7]
    elif risk_filter == "Moderate Risk (40-70%)":
        filtered_df = filtered_df[filtered_df['mock_risk'] > 0.4]
    elif risk_filter == "Low Risk (<40%)":
        filtered_df = filtered_df[filtered_df['mock_risk'] <= 0.4]
    
    if sort_by == "Last Seen":
        filtered_df = filtered_df.sort_values('last_seen', ascending=False)
    elif sort_by == "Risk Score":
        filtered_df = filtered_df.sort_values('mock_risk', ascending=False)
    elif sort_by == "Name":
        filtered_df = filtered_df.sort_values('name')
    
    st.markdown(f"**Showing {len(filtered_df)} of {len(df)} patients**")
    
    # Display table headers
    cols = st.columns([1, 2, 1, 1, 2, 1, 2])
    headers = ["ID", "Name", "Age/Sex", "Risk", "Diagnosis", "Last Seen", "Actions"]
    for col, header in zip(cols, headers):
        col.markdown(f"**{header}**")
    st.divider()

    # Display table rows
    for idx, row in filtered_df.iterrows():
        col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 2, 1, 1, 2, 1, 2])
        with col1:
            st.write(f"{row['patient_id']}")
        with col2:
            st.write(row['name'])
        with col3:
            st.write(f"{row.get('age', 'N/A')}, {row.get('gender', 'N/A')}") # Use .get() for safety
        with col4:
            risk_pct = int(row['mock_risk'] * 100)
            if row['mock_risk'] > 0.7: st.markdown(f"🔴 **{risk_pct}%**")
            elif row['mock_risk'] > 0.4: st.markdown(f"🟡 **{risk_pct}%**")
            else: st.markdown(f"🟢 **{risk_pct}%**")
        with col5:
            st.write(row['primary_diagnosis'])
        with col6:
            st.write(row['last_seen'])
        with col7:
            subcol1, subcol2 = st.columns(2)
            if subcol1.button("👁️ View", key=f"view_{row['patient_id']}", use_container_width=True):
                st.session_state['selected_patient'] = row['patient_id']
            if subcol2.button("🗑️ Del", key=f"del_{row['patient_id']}", use_container_width=True):
                if delete_patient(row['patient_id']):
                    st.success(f"Deleted {row['name']}")
                    st.cache_data.clear()
                    st.rerun()
        st.divider()
    
    # Patient Details Modal (simplified)
    if 'selected_patient' in st.session_state:
        patient_details = get_patient_details(st.session_state['selected_patient'])
        if patient_details:
            # The 'with st.dialog' error was fixed in the previous turn
            if st.dialog("Patient Details", width="large"):
                st.subheader(f"📋 Detailed Report: {patient_details['name']}")
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown("**Patient Information**")
                    st.write(f"**ID:** {patient_details['patient_id']}")
                    st.write(f"**Name:** {patient_details['name']}")
                    st.write(f"**Age:** {patient_details['age']}")
                    st.write(f"**Gender:** {patient_details['gender']}")
                    risk_score = patient_details['overall_risk'] * 100
                    st.markdown("**Overall Risk**")
                    if risk_score > 70: st.error(f"🔴 HIGH RISK: {risk_score:.1f}%")
                    elif risk_score > 40: st.warning(f"🟡 MODERATE RISK: {risk_score:.1f}%")
                    else: st.success(f"🟢 LOW RISK: {risk_score:.1f}%")
                
                with col2:
                    st.markdown("**Symptoms Reported**")
                    st.info(patient_details['symptoms'])
                    st.markdown("**Detected Diseases**")
                    for disease in patient_details['detected_diseases']:
                        st.write(f"• **{disease.get('disease_name', 'N/A')}:** {disease.get('final_risk_score', 0):.1f}% risk")
                
                if st.button("✖️ Close Details"):
                    del st.session_state['selected_patient']
                    st.rerun()

else:
    st.warning("⚠️ No patient data available. Patients will appear here after using the Patient Analysis tool.")
    # --- THIS IS THE FIX (Line 221) ---
    st.page_link("pages/1_Patient_Analysis.py", label="🩺 Go to Patient Analysis", use_container_width=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📊 Dashboard Controls")
    st.markdown("---")
    st.markdown("**Navigation:**")
    st.page_link("_Home.py", label="Home", icon="🏠")
    # --- THIS IS THE FIX (Line 229) ---
    st.page_link("pages/1_Patient_Analysis.py", label="Patient Analysis", icon="🩺")
    st.markdown("---")
    if stats:
        st.markdown("**Risk Distribution:**")
        fig = go.Figure(data=[go.Pie(
            labels=['High', 'Moderate', 'Low'],
            values=[stats['high_risk_count'], stats['moderate_risk_count'], stats['low_risk_count']],
            marker_colors=['#f5576c', '#ffa500', '#4facfe'],
            hole=.3
        )])
        fig.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)