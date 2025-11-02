# AI-Powered Early Disease Detection System

This project is a prototype for the Hacksprint Kolkata Edition (Problem 5), designed to predict the risk of diabetes based on patient health data.

## How to Run

1.  **Clone the repository**
    ```bash
    git clone [your-repo-url]
    cd disease-detector
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Get Data**
    * Download the "Pima Indians Diabetes Database" from Kaggle or another source.
    * Save it as `diabetes.csv`.
    * Place the file in the `data/raw/` directory.

4.  **Train the Model (Run once)**
    * This script will read `data/raw/diabetes.csv` and save the trained model and scaler to the `models/` folder.
    ```bash
    python src/ml/train.py
    ```

5.  **Run the Application (2 Terminals)**

    * **Terminal 1: Start the API Server**
        ```bash
        python src/api/main.py
        ```
        *This will serve the model at `http://127.0.0.1:5000`*

    * **Terminal 2: Start the Frontend Dashboard**
        ```bash
        streamlit run src/frontend/app.py
        ```
        *This will open the dashboard in your browser.*

6.  **Use the App!**
    * Open the Streamlit URL from your terminal.
    * Adjust the patient data sliders and click "Check Risk Score."