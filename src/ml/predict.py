import joblib
import numpy as np
import os
import re

# --- Configuration ---
MODEL_DIR = "models/"

# --- Load ALL Models & Scalers ---
models = {}
scalers = {}

# Load Diabetes Model
try:
    models['diabetes'] = joblib.load(os.path.join(MODEL_DIR, "diabetes_model.pkl"))
    scalers['diabetes'] = joblib.load(os.path.join(MODEL_DIR, "diabetes_scaler.pkl"))
    print("✅ Diabetes models loaded.")
except FileNotFoundError:
    print("⚠️ WARNING: Diabetes models not found.")
    
# Load Cardiovascular Model
try:
    models['cardio'] = joblib.load(os.path.join(MODEL_DIR, "cardio_model.pkl"))
    scalers['cardio'] = joblib.load(os.path.join(MODEL_DIR, "cardio_scaler.pkl"))
    print("✅ Cardiovascular models loaded.")
except FileNotFoundError:
    print("⚠️ WARNING: Cardiovascular models not found.")

# Load Respiratory Model (if exists)
try:
    models['respiratory'] = joblib.load(os.path.join(MODEL_DIR, "respiratory_model.pkl"))
    scalers['respiratory'] = joblib.load(os.path.join(MODEL_DIR, "respiratory_scaler.pkl"))
    print("✅ Respiratory models loaded.")
except FileNotFoundError:
    print("⚠️ INFO: Respiratory model not found (optional).")

# --- EXPANDED NLP Keyword Libraries for ALL Diseases ---
DISEASE_KEYWORDS = {
    'diabetes': {
        'keywords': [
            'fatigue', 'tired', 'exhausted', 'weakness',
            'thirsty', 'thirst', 'dehydrated', 'excessive thirst',
            'urination', 'urine', 'peeing', 'frequent bathroom', 'polyuria',
            'blurred', 'vision', 'blurry', 'eyesight', 'eye problems',
            'hungry', 'hunger', 'appetite', 'increased appetite',
            'slow-healing', 'wounds', 'cuts', 'healing slowly',
            'numbness', 'tingling', 'pins and needles', 'neuropathy',
            'yeast', 'infection', 'itching', 'skin infection',
            'weight loss', 'losing weight', 'unexplained weight loss',
            'dry mouth', 'dry skin',
            'glucose', 'sugar', 'blood sugar', 'high sugar'
        ],
        'weight': 1.0
    },
    
    'cardio': {
        'keywords': [
            'chest pain', 'chest discomfort', 'angina', 'tightness', 'pressure',
            'shortness of breath', 'breathless', 'difficulty breathing',
            'dizzy', 'dizziness', 'lightheaded', 'vertigo',
            'faint', 'fainting', 'syncope', 'blackout',
            'fatigue', 'tired', 'exhausted', 'weakness',
            'swollen', 'swelling', 'edema', 'puffy legs', 'puffy ankles',
            'heartbeat', 'palpitations', 'racing heart', 'irregular heartbeat',
            'skipped beat', 'fluttering', 'heart flutter',
            'blood pressure', 'bp', 'hypertension', 'high blood pressure',
            'sweating', 'cold sweat', 'nausea', 'vomiting',
            'arm pain', 'jaw pain', 'neck pain', 'back pain',
            'heart attack', 'stroke', 'cardiac'
        ],
        'weight': 1.0
    },
    
    'respiratory': {
        'keywords': [
            'cough', 'coughing', 'persistent cough', 'chronic cough',
            'shortness of breath', 'breathless', 'difficulty breathing', 'dyspnea',
            'wheezing', 'wheeze', 'whistling sound',
            'chest tightness', 'chest congestion',
            'mucus', 'phlegm', 'sputum', 'coughing up mucus',
            'asthma', 'asthmatic',
            'pneumonia', 'bronchitis',
            'fever', 'high temperature',
            'sore throat', 'throat pain',
            'nasal congestion', 'stuffy nose', 'runny nose',
            'covid', 'coronavirus', 'covid-19',
            'tuberculosis', 'tb',
            'copd', 'emphysema',
            'lung pain', 'breathing problem'
        ],
        'weight': 1.0
    },
    
    'cancer': {
        'keywords': [
            'lump', 'mass', 'tumor', 'growth',
            'unexplained weight loss', 'rapid weight loss',
            'persistent pain', 'chronic pain',
            'fatigue', 'extreme tiredness',
            'night sweats', 'sweating at night',
            'fever', 'persistent fever',
            'bleeding', 'blood', 'abnormal bleeding',
            'cough', 'persistent cough', 'blood in cough',
            'difficulty swallowing', 'swallowing problem',
            'skin changes', 'mole changes', 'skin lesion',
            'jaundice', 'yellowing',
            'lymph nodes', 'swollen lymph nodes',
            'cancer', 'carcinoma', 'malignant'
        ],
        'weight': 1.2  # Higher weight due to severity
    },
    
    'thyroid': {
        'keywords': [
            'weight gain', 'weight loss', 'unexplained weight change',
            'fatigue', 'tired', 'exhausted',
            'hair loss', 'thinning hair',
            'cold intolerance', 'feeling cold', 'sensitivity to cold',
            'heat intolerance', 'feeling hot', 'sweating',
            'heart palpitations', 'rapid heartbeat',
            'mood swings', 'anxiety', 'depression',
            'constipation', 'bowel problems',
            'dry skin', 'skin changes',
            'neck swelling', 'goiter',
            'thyroid', 'hyperthyroid', 'hypothyroid'
        ],
        'weight': 0.9
    },
    
    'kidney': {
        'keywords': [
            'urination', 'frequent urination', 'decreased urination',
            'blood in urine', 'dark urine', 'foamy urine',
            'swelling', 'swollen legs', 'swollen ankles', 'edema',
            'fatigue', 'weakness', 'tired',
            'nausea', 'vomiting', 'loss of appetite',
            'back pain', 'flank pain', 'side pain',
            'high blood pressure', 'hypertension',
            'shortness of breath',
            'kidney', 'renal', 'kidney failure'
        ],
        'weight': 1.0
    },
    
    'liver': {
        'keywords': [
            'jaundice', 'yellowing', 'yellow skin', 'yellow eyes',
            'abdominal pain', 'stomach pain', 'belly pain',
            'swelling', 'abdominal swelling', 'ascites',
            'nausea', 'vomiting', 'loss of appetite',
            'fatigue', 'weakness',
            'dark urine', 'pale stool',
            'itching', 'skin itching',
            'liver', 'hepatitis', 'cirrhosis', 'fatty liver'
        ],
        'weight': 1.0
    }
}

# Feature configurations for each disease
FEATURE_CONFIGS = {
    'diabetes': {
        'features': ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 
                    'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age'],
        'required': ['Glucose', 'BMI', 'Age']
    },
    'cardio': {
        'features': ['age', 'gender', 'height', 'weight', 'ap_hi', 'ap_lo', 
                    'cholesterol', 'gluc', 'smoke', 'alco', 'active'],
        'required': ['age', 'ap_hi', 'ap_lo']
    },
    'respiratory': {
        'features': ['age', 'smoking', 'cough_duration', 'fever', 'oxygen_level'],
        'required': ['age']
    }
}

def detect_disease_from_symptoms(symptoms_text):
    """
    Automatically detect which disease(s) the symptoms indicate.
    Returns: List of (disease, confidence_score) tuples sorted by confidence
    """
    if not symptoms_text or not symptoms_text.strip():
        return []
    
    symptoms_lower = symptoms_text.lower()
    disease_scores = {}
    
    for disease, config in DISEASE_KEYWORDS.items():
        keywords = config['keywords']
        weight = config['weight']
        matched_keywords = []
        
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, symptoms_lower):
                matched_keywords.append(keyword)
        
        if matched_keywords:
            # Score = (number of matches * weight) / sqrt(total keywords)
            # This normalizes scores across diseases with different keyword counts
            score = (len(matched_keywords) * weight * 100) / (len(keywords) ** 0.5)
            disease_scores[disease] = {
                'score': min(score, 100),  # Cap at 100
                'matched_keywords': list(set(matched_keywords)),
                'match_count': len(matched_keywords)
            }
    
    # Sort by score descending
    sorted_diseases = sorted(
        disease_scores.items(), 
        key=lambda x: x[1]['score'], 
        reverse=True
    )
    
    return sorted_diseases

def analyze_symptoms(symptoms_text, disease_type):
    """
    Analyze symptoms for a specific disease type.
    Returns: (symptom_count, detected_symptoms_list)
    """
    if disease_type not in DISEASE_KEYWORDS:
        return 0, []
    
    keywords = DISEASE_KEYWORDS[disease_type]['keywords']
    symptoms_lower = symptoms_text.lower()
    detected_symptoms = []
    
    for keyword in keywords:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, symptoms_lower):
            detected_symptoms.append(keyword)
    
    unique_symptoms = list(set(detected_symptoms))
    return len(unique_symptoms), unique_symptoms

def predict_with_model(disease_type, health_data):
    """
    Make prediction using trained ML model if available.
    Returns: (ml_score, model_used)
    """
    if disease_type not in models or models[disease_type] is None:
        return None, False
    
    try:
        feature_config = FEATURE_CONFIGS.get(disease_type, {})
        feature_order = feature_config.get('features', [])
        
        # Extract features
        features = np.array([[health_data.get(key, 0) for key in feature_order]])
        
        # Scale features
        features_scaled = scalers[disease_type].transform(features)
        
        # Get prediction probability
        ml_score_prob = models[disease_type].predict_proba(features_scaled)[0][1]
        ml_model_score = ml_score_prob * 100
        
        return ml_model_score, True
        
    except Exception as e:
        print(f"Model prediction error for {disease_type}: {e}")
        return None, False

def make_prediction(disease_type, health_data, symptoms):
    """
    Main prediction function - can work with or without trained models.
    
    Args:
        disease_type: 'auto' for auto-detection, or specific disease name
        health_data: Dictionary of health metrics
        symptoms: Text description of symptoms
    
    Returns:
        Dictionary with prediction results
    """
    
    # AUTO-DETECT mode
    if disease_type == 'auto' or not disease_type:
        detected_diseases = detect_disease_from_symptoms(symptoms)
        
        if not detected_diseases:
            return {
                "error": "Could not detect any specific disease from symptoms. Please provide more detailed symptoms or select a specific disease type."
            }
        
        # Return top 3 detected diseases
        results = {
            'detection_mode': 'auto',
            'detected_diseases': []
        }
        
        for disease, info in detected_diseases[:3]:  # Top 3
            symptom_count = info['match_count']
            symptom_score = min(symptom_count * 5, 50)  # Cap at 50% from symptoms
            
            # Try to get ML score if model exists and data is available
            ml_score, model_used = predict_with_model(disease, health_data)
            
            if ml_score is not None:
                final_score = (ml_score * 0.7) + (symptom_score * 0.3)
            else:
                final_score = symptom_score * 2  # Double weight if no model
            
            final_score = min(final_score, 100)
            
            results['detected_diseases'].append({
                'disease_type': disease,
                'disease_name': disease.title(),
                'confidence_score': round(info['score'], 1),
                'ml_model_score': round(ml_score, 1) if ml_score else None,
                'symptom_score': symptom_score,
                'final_risk_score': round(final_score, 1),
                'matched_symptoms': info['matched_keywords'][:5],  # Top 5
                'symptom_count': symptom_count,
                'model_used': model_used,
                'risk_category': 'HIGH' if final_score > 70 else 'MODERATE' if final_score > 40 else 'LOW'
            })
        
        return results
    
    # SPECIFIC DISEASE mode
    else:
        if disease_type not in DISEASE_KEYWORDS:
            return {"error": f"Unknown disease type: {disease_type}"}
        
        # Analyze symptoms
        symptom_count, detected_symptoms = analyze_symptoms(symptoms, disease_type)
        symptom_risk_boost = symptom_count * 5
        
        # Try ML prediction
        ml_score, model_used = predict_with_model(disease_type, health_data)
        
        if ml_score is None:
            # No model available - use symptom-based scoring
            ml_score = 0
            final_score = min(symptom_risk_boost * 2, 100)
            model_used = False
        else:
            final_score = ml_score + symptom_risk_boost
            final_score = min(final_score, 100)
        
        risk_category = 'HIGH' if final_score > 70 else 'MODERATE' if final_score > 40 else 'LOW'
        
        return {
            'detection_mode': 'specific',
            'disease_type': disease_type,
            'disease_name': disease_type.title(),
            'ml_model_score': round(ml_score, 2) if model_used else None,
            'nlp_symptom_count': symptom_count,
            'detected_symptoms': detected_symptoms[:10],  # Top 10
            'symptom_risk_boost': symptom_risk_boost,
            'final_risk_score': round(final_score, 2),
            'risk_category': risk_category,
            'model_used': model_used
        }

# --- Test function ---
if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing Multi-Disease Detection System")
    print("="*60)
    
    # Test auto-detection
    test_symptoms = """
    I've been having a persistent cough for 3 weeks now with some chest tightness.
    I'm also feeling very tired and have shortness of breath when I walk upstairs.
    Sometimes I wheeze at night.
    """
    
    print("\n--- Auto-Detection Test ---")
    result = make_prediction('auto', {}, test_symptoms)
    
    if 'detected_diseases' in result:
        print(f"\nDetected {len(result['detected_diseases'])} possible conditions:")
        for disease in result['detected_diseases']:
            print(f"\n{disease['disease_name']}:")
            print(f"  - Risk Score: {disease['final_risk_score']}%")
            print(f"  - Confidence: {disease['confidence_score']}%")
            print(f"  - Symptoms: {', '.join(disease['matched_symptoms'][:3])}")