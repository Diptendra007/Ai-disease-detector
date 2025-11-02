import pandas as pd
# --- 1. IMPORT THE NEW "BRAIN" ---
import xgboost as xgb
# We still need these
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os

print("Starting model training script...")

# --- Configuration ---
RAW_DATA_DIR = "data/raw/"
MODEL_DIR = "models/"
os.makedirs(MODEL_DIR, exist_ok=True) 

# --- 1. Diabetes Model Training ---
try:
    print("\n--- Training Diabetes Detective (XGBoost) ---")
    diabetes_data_path = os.path.join(RAW_DATA_DIR, "diabetes.csv")
    data = pd.read_csv(diabetes_data_path)
    
    X = data.drop('Outcome', axis=1)
    y = data['Outcome']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # --- 2. USE THE NEW "BRAIN" ---
    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    
    model.fit(X_train_scaled, y_train)
    
    acc = model.score(X_test_scaled, y_test)
    print(f"Diabetes Model (XGBoost) accuracy: {acc * 100:.2f}%")
    joblib.dump(model, os.path.join(MODEL_DIR, "diabetes_model.pkl"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "diabetes_scaler.pkl"))
    print("Diabetes model and scaler saved.")

except FileNotFoundError:
    print(f"Error: 'diabetes.csv' not found in {RAW_DATA_DIR}. Skipping diabetes model.")
except Exception as e:
    print(f"An error occurred during diabetes training: {e}")

# --- 2. Cardiovascular Model Training (from cardio_train.csv) ---
try:
    print("\n--- Training Cardiovascular Detective (XGBoost) ---")
    heart_data_path = os.path.join(RAW_DATA_DIR, "cardio_train.csv")
    data = pd.read_csv(heart_data_path, sep=';') 
    
    if 'id' in data.columns:
        data = data.drop("id", axis=1) 
    data['age'] = (data['age'] / 365.25).round().astype(int)
    
    X = data.drop('cardio', axis=1)
    y = data['cardio']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # --- 2. USE THE NEW "BRAIN" ---
    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    
    model.fit(X_train_scaled, y_train)
    
    acc = model.score(X_test_scaled, y_test)
    print(f"Cardiovascular Model (XGBoost) accuracy: {acc * 100:.2f}%")
    joblib.dump(model, os.path.join(MODEL_DIR, "cardio_model.pkl"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "cardio_scaler.pkl"))
    print("Cardiovascular model and scaler saved.")

except FileNotFoundError:
    print(f"Error: 'cardio_train.csv' not found in {RAW_DATA_DIR}. Skipping cardio model.")
except Exception as e:
    print(f"An error occurred during cardio training: {e}")

print("\nTraining script complete.")