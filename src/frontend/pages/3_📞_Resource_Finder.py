import streamlit as st
import pandas as pd

# Page config
st.set_page_config(
    page_title="Resource Finder",
    page_icon="📞",
    layout="wide"
)

# --- Mock Database for Kolkata ---
# In a real app, this would come from a database or a Google Maps API
MOCK_DATA = {
    "Hospitals (Kolkata)": [
        {"name": "Apollo Gleneagles Hospital", "phone": "033-2320-3040", "address": "Canal Circular Rd, Kadapara"},
        {"name": "Fortis Hospital, Anandapur", "phone": "033-6628-4444", "address": "Anandapur, East Kolkata Township"},
        {"name": "CMRI (Calcutta Medical Research Institute)", "phone": "033-4090-4090", "address": "Alipore, New Alipore"},
        {"name": "Medica Superspecialty Hospital", "phone": "033-6652-0000", "address": "Mukundapur, E.M. Bypass"}
    ],
    "Doctors (by Specialization)": {
        "❤️ Cardiologist (Heart)": [
            {"name": "Dr. A. K. Bardhan", "phone": "+91 98300 XXXXX", "clinic": "Apollo Clinic, Gariahat"},
            {"name": "Dr. S. K. Mitra", "phone": "+91 98310 XXXXX", "clinic": "Fortis Hospital"},
            {"name": "Dr. P. K. Deb", "phone": "+91 98301 XXXXX", "clinic": "Medica Superspecialty"}
        ],
        "💉 Endocrinologist (Diabetes/Thyroid)": [
            {"name": "Dr. R. K. Das", "phone": "+91 94330 XXXXX", "clinic": "Manipal Hospital, Salt Lake"},
            {"name": "Dr. P. Sen", "phone": "+91 98362 XXXXX", "clinic": "Medica Superspecialty"}
        ],
        "🫁 Pulmonologist (Lungs/Respiratory)": [
            {"name": "Dr. B. K. Roy", "phone": "+91 90510 XXXXX", "clinic": "CMRI"},
            {"name": "Dr. A. K. Ghosh", "phone": "+91 98300 XXXXX", "clinic": "Apollo Gleneagles"}
        ],
         "🎗️ Oncologist (Cancer)": [
            {"name": "Dr. Subhankar Deb", "phone": "+91 98745 XXXXX", "clinic": "Tata Medical Center"},
            {"name": "Dr. G. K. Basu", "phone": "+91 98311 XXXXX", "clinic": "Fortis Hospital"}
        ]
    },
    "Ambulance Services (Kolkata)": [
        {"name": "Apollo 24/7 Ambulance", "phone": "1066"},
        {"name": "Fortis Emergency Services", "phone": "033-6628-4444"},
        {"name": "Kolkata Police Ambulance", "phone": "100 / 102"},
        {"name": "Medica Emergency", "phone": "033-6652-0000"}
    ],
    "Medical Shops (24/7, Kolkata)": [
        {"name": "Apollo Pharmacy (Multiple Locations)", "phone": "1860-500-0101", "location": "Gariahat, Salt Lake, etc."},
        {"name": "Frank Ross Pharmacy (Park Street Area)", "phone": "033-4026-4444", "location": "Park Street"},
        {"name": "Dey's Medical", "phone": "033-2287-1234", "location": "Hazra"}
    ]
}

# --- Page Layout ---
st.title("📞 Emergency & Resource Finder")
st.info("⚠️ This is a demo page with placeholder data for Kolkata. In a real app, this would use your live location.")
st.markdown("---")

# --- Display Logic ---
col1, col2 = st.columns(2)

with col1:
    st.header("🏥 Hospitals & 🚑 Ambulance")
    
    with st.expander("**Click to see Emergency Ambulance Numbers**", expanded=True):
        for item in MOCK_DATA["Ambulance Services (Kolkata)"]:
            st.markdown(f"**{item['name']}**\n- **Phone:** `{item['phone']}`")
            st.divider()
            
    with st.expander("**Click to see Major Hospitals**", expanded=True):
        for item in MOCK_DATA["Hospitals (Kolkata)"]:
            st.markdown(f"**{item['name']}**\n- **Phone:** `{item['phone']}`\n- **Address:** {item['address']}")
            st.divider()
            
    with st.expander("**Click to see 24/7 Medical Shops**"):
        for item in MOCK_DATA["Medical Shops (24/7, Kolkata)"]:
            st.markdown(f"**{item['name']}**\n- **Phone:** `{item['phone']}`\n- **Location:** {item['location']}")
            st.divider()

with col2:
    st.header("👨‍⚕️ Doctors by Specialization")
    
    with st.expander("**Click to see Specialists**", expanded=True):
        for specialty, docs in MOCK_DATA["Doctors (by Specialization)"].items():
            st.markdown(f"#### {specialty}")
            for doc in docs:
                st.markdown(f"• **{doc['name']}** at {doc['clinic']} (Phone: `{doc['phone']}`)")
            st.markdown("---")

# --- Sidebar Navigation ---
# This just adds the links to the sidebar for this page
with st.sidebar:
    st.markdown("### 🩺 AI Health Detective")
    st.markdown("---")
    st.markdown("**Navigation:**")
    st.page_link("_Home.py", label="Home", icon="🏠")
    st.page_link("pages/1_Patient_Analysis.py", label="Patient Analysis", icon="🩺")
    st.page_link("pages/2_Admin_Dashboard.py", label="Admin Dashboard", icon="📊")
    st.page_link("pages/3_📞_Resource_Finder.py", label="Resource Finder", icon="📞") # <-- Current Page
    st.markdown("---")