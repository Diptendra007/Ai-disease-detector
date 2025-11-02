import streamlit as st
import requests
from datetime import datetime
import pandas as pd # Import pandas for the report

# Page config
st.set_page_config(
    page_title="Patient Analysis",
    page_icon="🩺",
    layout="wide"
)

# Session State
if 'page' not in st.session_state:
    st.session_state.page = 'input'
if 'report_data' not in st.session_state:
    st.session_state.report_data = {}

# API Call Function
def call_api(payload):
    """Calls the backend API for disease detection"""
    API_URL = "http://127.0.0.1:5000/predict"
    
    try:
        with st.spinner('🔍 AI is analyzing your health data...'):
            response = requests.post(API_URL, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if "error" in result:
                st.error(f"❌ Error: {result['error']}")
                return None
            else:
                st.session_state.report_data = result
                st.session_state.page = 'report'
                st.rerun()
    
    except requests.exceptions.ConnectionError:
        st.error("❌ **Connection Error**: Could not connect to API.")
        st.info("💡 Start the Flask server: `python src/api/main.py`")
        return None
    except requests.exceptions.HTTPError as e:
        # Try to show the specific error from the API
        try:
            error_json = e.response.json()
            st.error(f"❌ Server Error: {error_json.get('error', 'Analysis complete, but no disease keywords matched.')}")
        except:
            st.error(f"❌ HTTP Error: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

# --- FIXED: SAFE RECOMMENDATIONS FUNCTION ---
def get_comprehensive_recommendations(diseases_data):
    """
    Generate SAFE, ACTIONABLE recommendations and topics for a doctor.
    This replaces the dangerous "medicine" suggestions.
    """
    
    DISEASE_INFO = {
        'diabetes': {
            'doctors': ["🏥 Endocrinologist", "👨‍⚕️ General Physician", "👁️ Ophthalmologist"],
            'doctor_discussion_topics': [
                "Blood sugar medication options (e.g., Metformin)",
                "The need for Insulin therapy",
                "Dietary plans for blood sugar management",
                "Risks of diabetic eye problems (retinopathy)"
            ],
            'lifestyle': ["🥗 Low-carb, high-fiber diet", "🏃 30 min exercise daily", "⚖️ Maintain BMI <25", "🚭 Quit smoking"]
        },
        'cardio': {
            'doctors': ["❤️ Cardiologist", "🏥 General Physician", "🩺 Vascular Surgeon"],
            'doctor_discussion_topics': [
                "Preventive blood thinners (e.g., Aspirin)",
                "Cholesterol-lowering medication (e.g., Statins)",
                "Blood pressure medication (e.g., Amlodipine)",
                "Surgical/stent options if risk is high"
            ],
            'lifestyle': ["🧂 Reduce salt (<5g/day)", "🥗 DASH diet", "🏃 Exercise", "🚭 Quit smoking"]
        },
        'respiratory': {
            'doctors': ["🫁 Pulmonologist", "🏥 General Physician"],
            'doctor_discussion_topics': [
                "Need for a rescue inhaler (Bronchodilators)",
                "Long-term inflammation control (Corticosteroids)"
            ],
            'lifestyle': ["🚭 Avoid smoking & pollutants", "😷 Wear mask", "💨 Breathing exercises"]
        },
        'cancer': {
            'doctors': ["🎗️ Oncologist", "🏥 Surgeon", "🩺 Radiologist"],
            'doctor_discussion_topics': [
                "Urgency of a consultation",
                "Need for a biopsy or advanced imaging (CT/MRI)"
            ],
            'lifestyle': ["🚨 Seek immediate medical attention", "🥗 Healthy diet", "🚭 Avoid tobacco"]
        },
        'thyroid': {
            'doctors': ["🦋 Endocrinologist", "🏥 General Physician"],
            'doctor_discussion_topics': [
                "Hormone replacement therapy (e.g., Levothyroxine)",
                "Anti-thyroid medication (e.g., Methimazole)"
            ],
            'lifestyle': ["🥗 Balanced diet (check iodine)", "😴 Regular sleep", "😰 Stress management"]
        },
        'kidney': {
            'doctors': ["🫘 Nephrologist", "🏥 Urologist"],
            'doctor_discussion_topics': [
                "Kidney-protective medications (e.g., ACE inhibitors)",
                "Fluid management (e.g., Diuretics)"
            ],
            'lifestyle': ["💧 Stay hydrated", "🧂 Low sodium", "🥩 Limit protein"]
        },
        'liver': {
            'doctors': ["🫁 Hepatologist", "🏥 Gastroenterologist"],
            'doctor_discussion_topics': [
                "Medications to protect the liver",
                "Managing complications (e.g., Lactulose)"
            ],
            'lifestyle': ["🚫 Avoid alcohol completely", "🥗 Low-fat diet", "⚖️ Healthy weight"]
        }
    }
    
    all_recommendations = []
    
    for disease_data in diseases_data:
        disease = disease_data.get('disease_type')
        risk_score = disease_data.get('final_risk_score', 0)
        
        if not disease or disease not in DISEASE_INFO:
            continue
        
        info = DISEASE_INFO[disease]
        
        discussion_topics = []
        if risk_score > 40: # Only show topics if risk is moderate/high
            discussion_topics = info.get('doctor_discussion_topics', [])
        
        all_recommendations.append({
            'disease': disease,
            'disease_name': disease_data.get('disease_name', 'Unknown'),
            'risk_score': risk_score,
            'risk_category': disease_data.get('risk_category', 'LOW'),
            'doctors': info.get('doctors', []),
            'discussion_topics': discussion_topics,  # <-- SAFE
            'lifestyle': info.get('lifestyle', [])
        })
    
    return all_recommendations
# --- END SAFE FUNCTION ---


# INPUT PAGE
def show_input_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🩺 AI Health Analysis")
        st.markdown("### Describe your symptoms for instant AI diagnosis")
    
    st.markdown("---")
    
    st.info("🤖 **AI will automatically detect** possible diseases from your symptoms!")
    
    # Use st.form for a cleaner submission process
    with st.form(key="patient_form"):
        st.header("📋 Patient Information (Optional)")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", "Anonymous")
            age = st.number_input("Age", 1, 120, 40)
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            phone = st.text_input("Phone (Optional)", "")
        
        st.markdown("---")
        
        # Symptoms (MOST IMPORTANT)
        st.header("📝 Step 1: Describe Your Symptoms")
        symptoms = st.text_area(
            "Be as detailed as possible:",
            placeholder="Example: I've been having chest pain and feeling dizzy. My father had heart problems. I also feel breathless when walking...",
            height=150
        )
        
        # Optional Health Data
        st.header("📊 Step 2 (Optional): Add Health Data")
        with st.expander("Expand to add lab data for better accuracy"):
            col1, col2, col3 = st.columns(3)
            with col1:
                height = st.number_input("Height (cm)", 100, 250, 170)
                weight = st.number_input("Weight (kg)", 20.0, 200.0, 70.0)
                glucose = st.number_input("Glucose (mg/dL)", 0, 400, 100)
            with col2:
                systolic_bp = st.number_input("Systolic BP", 60, 250, 120)
                diastolic_bp = st.number_input("Diastolic BP", 40, 150, 80)
                cholesterol = st.selectbox("Cholesterol", [1, 2, 3], 
                    format_func=lambda x: ['1: Normal', '2: Above Normal', '3: High'][x-1])
            with col3:
                smoke = st.selectbox("Smoker?", [0, 1], format_func=lambda x: ['No', 'Yes'][x])
                alcohol = st.selectbox("Alcohol?", [0, 1], format_func=lambda x: ['No', 'Yes'][x])
                active = st.selectbox("Active?", [0, 1], format_func=lambda x: ['No', 'Yes'][x])
        
        st.markdown("---")
        submit_button = st.form_submit_button(label="🔬 **Analyze My Health**", type="primary", use_container_width=True)

        if submit_button:
            if not symptoms.strip():
                st.error("⚠️ Please describe your symptoms first!")
            else:
                # Calculate BMI
                bmi = round(weight / ((height/100) ** 2), 1)
                
                # Create the full data payloads
                health_data = {
                    # For diabetes model
                    'Pregnancies': 0, 'Glucose': glucose, 'BloodPressure': systolic_bp,
                    'SkinThickness': 20, 'Insulin': 80, 'BMI': bmi,
                    'DiabetesPedigreeFunction': 0.5, 'Age': age,
                    # For cardio model
                    'age': age, 'gender': 1 if gender == "Female" else 2,
                    'height': height, 'weight': weight, 'ap_hi': systolic_bp,
                    'ap_lo': diastolic_bp, 'cholesterol': cholesterol,
                    'gluc': 1 if glucose < 100 else 2 if glucose < 126 else 3,
                    'smoke': smoke, 'alco': alcohol, 'active': active
                }
                
                payload = {
                    "patient_info": {"name": name, "age": age, "gender": gender, "phone": phone},
                    "symptoms": symptoms,
                    "disease_type": "auto",
                    "health_data": health_data
                }
                call_api(payload)

# REPORT PAGE
def show_report_page():
    data = st.session_state.report_data
    
    st.title("📊 Health Analysis Report")
    st.markdown(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    
    patient_id = data.get('patient_id', 'N/A')
    st.success(f"✅ **Patient ID:** {patient_id} (Record saved to clinical dashboard)")
    st.markdown("---")
    
    if data.get('detection_mode') == 'auto' and 'detected_diseases' in data:
        detected = data['detected_diseases']
        
        st.header(f"🔍 AI Analysis Result: Detected {len(detected)} Possible Condition(s)")
        
        for idx, disease_data in enumerate(detected, 1):
            disease_name = disease_data['disease_name']
            risk_score = disease_data['final_risk_score']
            risk_cat = disease_data['risk_category']
            
            with st.container():
                if risk_cat == 'HIGH':
                    st.error(f"### {idx}. {disease_name} - {risk_score:.1f}% Risk ⚠️")
                elif risk_cat == 'MODERATE':
                    st.warning(f"### {idx}. {disease_name} - {risk_score:.1f}% Risk ⚠")
                else:
                    st.success(f"### {idx}. {disease_name} - {risk_score:.1f}% Risk ✓")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Risk Confidence", f"{disease_data['confidence_score']:.1f}%", 
                              help="Based on NLP and/or ML model analysis.")
                with col2:
                    st.metric("Matched Symptoms", disease_data['symptom_count'])
                with col3:
                    st.metric("Lab Data Used (ML)", "✓ Yes" if disease_data['model_used'] else "✗ No")
                
                if disease_data['matched_symptoms']:
                    st.write("**Key Symptoms:** " + ", ".join(disease_data['matched_symptoms'][:5]))
                st.markdown("---")
        
        # --- SAFE RECOMMENDATIONS ---
        st.header("💡 Doctor Discussion Guide")
        recommendations = get_comprehensive_recommendations(detected)
        
        for rec in recommendations:
            if rec['risk_score'] < 30: # Only show recommendations for diseases with some risk
                continue
            
            st.subheader(f"For {rec['disease_name']} ({rec['risk_category']} RISK):")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**👨‍⚕️ Recommended Doctors:**")
                for doc in rec['doctors']: st.markdown(f"• {doc}")
                
                st.markdown("\n**🌟 Lifestyle Changes:**")
                for item in rec['lifestyle']: st.markdown(f"• {item}")
            
            with col2:
                st.markdown("**🩺 Medical Topics to Discuss:**")
                if rec['discussion_topics']:
                    st.info("Your AI report identified these topics. Discuss them with your doctor.")
                    for topic in rec['discussion_topics']:
                        st.markdown(f"• {topic}")
                else:
                    st.success("No specific medical topics flagged. Discuss your general health.")
            st.markdown("---")
        # --- END SAFE SECTION ---
    
    # Action buttons
    col1, col2, col3 = st.columns([2,2,1])
    with col1:
        if st.button("🔄 Start New Analysis", use_container_width=True):
            st.session_state.page = 'input'
            st.session_state.report_data = {}
            st.rerun()
    
    # --- NAVIGATION LINKS FIXED ---
    with col2:
        # Correctly links to the sibling page
        st.page_link("pages/2_Admin_Dashboard.py", label="📊 View Admin Dashboard", use_container_width=True)
    with col3:
        # Correctly links to the main _Home.py file
        st.page_link("_Home.py", label="🏠 Home", use_container_width=True)
    # --- END FIXED ---

# Main Router
def main():
    if st.session_state.page == 'input':
        show_input_page()
    elif st.session_state.page == 'report':
        show_report_page()

if __name__ == "__main__":
    main()