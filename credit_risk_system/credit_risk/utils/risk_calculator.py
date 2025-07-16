import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from joblib import dump, load
import os
from django.conf import settings

class RiskModel:
    def __init__(self):
        self.model = None
        self.model_path = os.path.join(settings.BASE_DIR, 'credit_risk', 'utils', 'risk_model.joblib')
        self.load_model()
        
    def load_model(self):
        if os.path.exists(self.model_path):
            self.model = load(self.model_path)
        else:
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
    
    def save_model(self):
        dump(self.model, self.model_path)
    
    def train_model(self, data):
        # Example training function - in reality you'd use your actual data
        X = data.drop('default', axis=1)
        y = data['default']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Model trained with accuracy: {accuracy:.2%}")
        self.save_model()
        return accuracy
    
    def predict_default_probability(self, customer_data):
        if not self.model:
            raise Exception("Model not loaded or trained")
        
        # Convert customer data to DataFrame
        df = pd.DataFrame([customer_data])
        
        # Predict probability
        proba = self.model.predict_proba(df)[0][1]
        return proba

# Example alternative data features that might be useful
ALTERNATIVE_DATA_FEATURES = {
    'social_media_activity': {
        'description': 'Frequency of social media posts',
        'weight': 0.15
    },
    'utility_payments': {
        'description': 'Timeliness of utility bill payments',
        'weight': 0.25
    },
    'ecommerce_behavior': {
        'description': 'Online shopping and return patterns',
        'weight': 0.20
    },
    'device_usage': {
        'description': 'Consistency of device usage patterns',
        'weight': 0.10
    },
    'geolocation_stability': {
        'description': 'Frequency of location changes',
        'weight': 0.15
    },
    'professional_network': {
        'description': 'Quality of professional connections',
        'weight': 0.15
    }
}

def calculate_alternative_data_score(customer_id):
    """
    Calculate a composite score based on alternative data sources
    """
    # In a real implementation, you would query the database for this customer's alternative data
    # For now, we'll return a mock score
    return np.random.uniform(0.5, 0.9)  # Random score between 0.5 and 0.9

def calculate_risk_score(credit_score, alternative_data_score, income, loan_amount, loan_term):
    """
    Calculate a comprehensive risk score combining traditional and alternative data
    """
    # Normalize credit score (assuming it's in the range 300-850)
    normalized_credit = (float(credit_score.split('-')[0]) - 300) / (850 - 300)
    
    # Calculate debt-to-income ratio factor
    try:
        dti = float(loan_amount) / float(income)
        dti_factor = max(0, 1 - dti / 0.5)  # Assuming 50% DTI is the threshold
    except:
        dti_factor = 0.5
    
    # Term factor - longer terms are riskier
    term_factor = max(0.1, 1 - (float(loan_term) / 60) ) # 60 months as max term
    
    # Composite score
    risk_score = 0.4 * normalized_credit + 0.3 * alternative_data_score + 0.2 * dti_factor + 0.1 * term_factor
    
    # Convert to 1-100 scale
    return int(risk_score * 100)

def probability_of_default(risk_score):
    """
    Convert risk score to probability of default using a logistic function
    """
    # Logistic function parameters can be calibrated to your portfolio
    return 1 / (1 + np.exp(-0.1 * (risk_score - 50)))