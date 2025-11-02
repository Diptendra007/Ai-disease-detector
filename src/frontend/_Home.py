import streamlit as st

# Page config
st.set_page_config(
    page_title="AI Health Detective",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .feature-card {
        padding: 1.5rem;
        border-radius: 10px;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        height: 100%;
        color: black; /* Makes text visible in dark mode */
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🩺 AI Health Detective</h1>
    <p style="font-size: 1.2rem; margin-top: 1rem;">
        Multi-Disease Early Detection System
    </p>
</div>
""", unsafe_allow_html=True)

# Main content
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h2>🔬 For Patients</h2>
        <p style="font-size: 1.1rem; line-height: 1.6;">
            Get instant AI-powered health analysis. Describe your symptoms and 
            receive comprehensive risk assessment for multiple diseases.
        </p>
        <ul style="font-size: 1rem; line-height: 1.8;">
            <li>✅ Auto-detect diseases from symptoms</li>
            <li>✅ Analyze 7+ critical conditions</li>
            <li>✅ Get a **Doctor Discussion Guide**</li>
            <li>✅ Download detailed health reports</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Correct path to the page
    if st.button("🩺 Start Health Analysis", type="primary", use_container_width=True):
        st.switch_page("pages/1_Patient_Analysis.py")

with col2:
    st.markdown("""
    <div class="feature-card">
        <h2>📊 For Healthcare Providers</h2>
        <p style="font-size: 1.1rem; line-height: 1.6;">
            Monitor all patients in one dashboard. Track risk scores, 
            view patient history, and manage clinical workflows efficiently.
        </p>
        <ul style="font-size: 1rem; line-height: 1.8;">
            <li>✅ View all patient records</li>
            <li>✅ Color-coded risk stratification</li>
            <li>✅ Search & filter capabilities</li>
            <li>✅ Real-time statistics</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Correct path to the page
    if st.button("📊 Open Admin Dashboard", type="secondary", use_container_width=True):
        st.switch_page("pages/2_Admin_Dashboard.py")

st.markdown("---")

# Supported Diseases
st.header("🦠 Diseases We Can Detect")
col1, col2, col3, col4 = st.columns(4)
diseases = [
    ("💉", "Diabetes", "Blood sugar disorders"),
    ("❤️", "Cardiovascular", "Heart conditions"),
    ("🫁", "Respiratory", "Lung problems"),
    ("🎗️", "Cancer", "Early warning signs"),
    ("🦋", "Thyroid", "Thyroid disorders"),
    ("🫘", "Kidney", "Renal issues"),
    ("🫀", "Liver", "Hepatic conditions")
]
for idx, (icon, name, desc) in enumerate(diseases[:7]): # Show 7
    col = [col1, col2, col3, col4][idx % 4]
    with col:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 8px; margin-bottom: 1rem;">
            <div style="font-size: 2rem;">{icon}</div>
            <div style="font-weight: bold; margin: 0.5rem 0;">{name}</div>
            <div style="font-size: 0.9rem; color: #666;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# How it works
st.header("🤖 How It Works")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 1️⃣ Describe Symptoms\nTell us what you're experiencing in detail.")
with col2:
    st.markdown("### 2️⃣ AI Analysis\nOur AI analyzes your symptoms and lab data.")
with col3:
    st.markdown("### 3️⃣ Get Report\nReceive a risk report and **safe** discussion topics.")

st.markdown("---")
st.info("⚠️ **Medical Disclaimer**: This AI provides informational health assessments only and is not medical advice. Always consult a qualified healthcare professional.")

# Sidebar
with st.sidebar:
    st.markdown("### 🩺 AI Health Detective")
    st.markdown("---")
    
    st.markdown("**Navigation:**")
    # --- THIS IS THE FIX (Line 131) ---
    st.page_link("_Home.py", label="Home", icon="🏠")
    st.page_link("pages/1_Patient_Analysis.py", label="Patient Analysis", icon="🩺")
    st.page_link("pages/2_Admin_Dashboard.py", label="Admin Dashboard", icon="📊")
    
    st.markdown("---")
    st.markdown("**Quick Stats:**")
    
    # Try to fetch stats from API
    try:
        import requests
        response = requests.get("http://127.0.0.1:5000/api/stats", timeout=2)
        if response.status_code == 200:
            stats = response.json()
            st.metric("Total Patients", stats.get('total_patients', 0))
            st.metric("High Risk", stats.get('high_risk_count', 0))
        else:
            st.info("API not connected")
    except:
        st.info("Start API to see stats")