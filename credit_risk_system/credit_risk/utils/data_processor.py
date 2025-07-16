import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .risk_calculator import calculate_alternative_data_score, calculate_risk_score, probability_of_default

def process_customer_data(customer):
    """
    Process customer data for risk assessment
    """
    # Get alternative data score
    alt_data_score = calculate_alternative_data_score(customer.id)
    
    # Prepare data dictionary
    data = {
        'customer_id': customer.id,
        'name': customer.name,
        'credit_score': customer.credit_score,
        'income': float(customer.income),
        'employment_status': customer.employment_status,
        'alternative_data_score': alt_data_score,
    }
    
    return data

def assess_application_risk(application):
    """
    Assess risk for a credit application
    """
    customer = application.customer
    
    # Process customer data
    customer_data = process_customer_data(customer)
    
    # Calculate risk score
    credit_score_mid = float(customer.credit_score.split('-')[0])
    risk_score = calculate_risk_score(
        credit_score=customer.credit_score,
        alternative_data_score=customer_data['alternative_data_score'],
        income=customer.income,
        loan_amount=application.amount,
        loan_term=application.term
    )
    
    # Calculate probability of default
    pd = probability_of_default(risk_score)
    
    # Determine decision reason
    if pd < 0.05:
        decision = "Low risk based on credit history and alternative data"
    elif pd < 0.15:
        decision = "Moderate risk - acceptable based on compensating factors"
    else:
        decision = "High risk - probability of default exceeds threshold"
    
    return {
        'probability_of_default': pd,
        'risk_score': risk_score,
        'decision_reason': decision
    }