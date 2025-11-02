from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
from datetime import datetime
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.predict import make_prediction

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# In-memory patient storage (for demo - use database in production)
PATIENTS_DB = []
PATIENT_COUNTER = 1000

# --- Helper Functions ---
def generate_patient_id():
    global PATIENT_COUNTER
    PATIENT_COUNTER += 1
    return f"P{PATIENT_COUNTER}"

def calculate_overall_risk(detected_diseases):
    """Calculate overall risk from multiple diseases"""
    if not detected_diseases:
        return 0.0
    
    # Get highest risk score
    max_risk = max([d['final_risk_score'] for d in detected_diseases])
    return max_risk / 100  # Convert to 0-1 scale

def get_primary_diagnosis(detected_diseases):
    """Get the disease with highest risk as primary diagnosis"""
    if not detected_diseases:
        return "No diagnosis"
    
    sorted_diseases = sorted(detected_diseases, key=lambda x: x['final_risk_score'], reverse=True)
    return sorted_diseases[0]['disease_name']

# --- API Endpoints ---

@app.route('/predict', methods=['POST'])
def predict():
    """
    Enhanced API endpoint for multi-disease prediction with patient storage.
    """
    data = request.get_json(force=True)
    
    # Extract data
    patient_info = data.get('patient_info', {})
    symptoms = data.get('symptoms') or data.get('unstructured_notes', '')
    disease_type = data.get('disease_type', 'auto')
    health_data = data.get('health_data') or data.get('structured_data', {})
    
    # Validation
    if not symptoms or not symptoms.strip():
        return jsonify({
            "error": "Missing symptoms. Please describe your symptoms."
        }), 400
    
    # Call prediction function
    result = make_prediction(disease_type, health_data, symptoms)
    
    if "error" in result:
        return jsonify(result), 500
    
    # Generate patient ID
    patient_id = generate_patient_id()
    
    # Calculate overall metrics
    if result.get('detection_mode') == 'auto' and 'detected_diseases' in result:
        overall_risk = calculate_overall_risk(result['detected_diseases'])
        primary_diagnosis = get_primary_diagnosis(result['detected_diseases'])
    else:
        overall_risk = result.get('final_risk_score', 0) / 100
        primary_diagnosis = result.get('disease_name', 'Unknown')
    
    # Create patient record
    patient_record = {
        'patient_id': patient_id,
        'name': patient_info.get('name', 'Anonymous'),
        'age': patient_info.get('age', 'N/A'),
        'gender': patient_info.get('gender', 'N/A'),
        'phone': patient_info.get('phone', ''),
        'symptoms': symptoms,
        'health_data': health_data,
        'primary_diagnosis': primary_diagnosis,
        'overall_risk': round(overall_risk, 2),
        'detected_diseases': result.get('detected_diseases', [result]),
        'timestamp': datetime.now().isoformat(),
        'last_seen': datetime.now().strftime('%Y-%m-%d'),
        'full_report': result
    }
    
    # Store patient record
    PATIENTS_DB.append(patient_record)
    
    # Add patient info to result
    result['patient_info'] = patient_info
    result['patient_id'] = patient_id
    result['symptoms'] = symptoms
    result['health_data'] = health_data
    
    return jsonify(result)

@app.route('/api/patients', methods=['GET'])
def get_patients():
    """
    Get list of all patients for dashboard.
    Returns simplified patient list for table view.
    """
    patient_list = []
    
    for patient in PATIENTS_DB:
        patient_list.append({
            'patient_id': patient['patient_id'],
            'name': patient['name'],
            'age': patient['age'],
            'gender': patient['gender'],
            'primary_diagnosis': patient['primary_diagnosis'],
            'last_seen': patient['last_seen'],
            'mock_risk': patient['overall_risk'],  # Using 'mock_risk' for compatibility
            'timestamp': patient['timestamp']
        })
    
    # Sort by timestamp (most recent first)
    patient_list.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return jsonify(patient_list)

@app.route('/api/patients/<patient_id>', methods=['GET'])
def get_patient_details(patient_id):
    """
    Get detailed information for a specific patient.
    """
    for patient in PATIENTS_DB:
        if patient['patient_id'] == patient_id:
            return jsonify(patient)
    
    return jsonify({"error": "Patient not found"}), 404

@app.route('/api/patients/<patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    """
    Delete a patient record.
    """
    global PATIENTS_DB
    original_length = len(PATIENTS_DB)
    PATIENTS_DB = [p for p in PATIENTS_DB if p['patient_id'] != patient_id]
    
    if len(PATIENTS_DB) < original_length:
        return jsonify({"message": "Patient deleted successfully"})
    else:
        return jsonify({"error": "Patient not found"}), 404

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """
    Get overall statistics for dashboard.
    """
    if not PATIENTS_DB:
        return jsonify({
            'total_patients': 0,
            'high_risk_count': 0,
            'moderate_risk_count': 0,
            'low_risk_count': 0,
            'disease_distribution': {}
        })
    
    total = len(PATIENTS_DB)
    high_risk = sum(1 for p in PATIENTS_DB if p['overall_risk'] > 0.7)
    moderate_risk = sum(1 for p in PATIENTS_DB if 0.4 < p['overall_risk'] <= 0.7)
    low_risk = sum(1 for p in PATIENTS_DB if p['overall_risk'] <= 0.4)
    
    # Disease distribution
    disease_counts = {}
    for patient in PATIENTS_DB:
        diagnosis = patient['primary_diagnosis']
        disease_counts[diagnosis] = disease_counts.get(diagnosis, 0) + 1
    
    return jsonify({
        'total_patients': total,
        'high_risk_count': high_risk,
        'moderate_risk_count': moderate_risk,
        'low_risk_count': low_risk,
        'disease_distribution': disease_counts
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "AI Health Detective API is running",
        "total_patients": len(PATIENTS_DB),
        "supported_diseases": [
            "diabetes", "cardio", "respiratory", "cancer", 
            "thyroid", "kidney", "liver"
        ]
    })

@app.route('/diseases', methods=['GET'])
def list_diseases():
    """List all supported diseases"""
    diseases = {
        "diabetes": "Diabetes Mellitus",
        "cardio": "Cardiovascular Disease",
        "respiratory": "Respiratory Disorders",
        "cancer": "Cancer Detection",
        "thyroid": "Thyroid Disorders",
        "kidney": "Kidney Disease",
        "liver": "Liver Disease"
    }
    return jsonify(diseases)

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🩺 AI HEALTH DETECTIVE - Multi-Disease Detection API")
    print("="*70)
    print("✅ Server: http://127.0.0.1:5000")
    print("\n📋 Endpoints:")
    print("   POST   /predict                : Disease prediction")
    print("   GET    /api/patients           : Get all patients")
    print("   GET    /api/patients/<id>      : Get patient details")
    print("   DELETE /api/patients/<id>      : Delete patient")
    print("   GET    /api/stats              : Get statistics")
    print("   GET    /health                 : Health check")
    print("   GET    /diseases               : List diseases")
    print("\n🤖 Features:")
    print("   • Auto-detect diseases from symptoms")
    print("   • Multi-disease prediction")
    print("   • Patient record storage")
    print("   • Clinical dashboard support")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)