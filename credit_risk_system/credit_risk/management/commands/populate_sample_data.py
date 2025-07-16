from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from credit_risk.models import Customer, AlternativeData, CreditApplication, RiskAssessment, PaymentHistory
import random
import json
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Populates the database with sample data for testing'
    
    def handle(self, *args, **options):
        # Create a test user
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}
        )
        if created:
            user.set_password('admin')
            user.save()
        
        # Credit score categories
        credit_scores = ['300-579', '580-669', '670-739', '740-799', '800-850']
        
        # Employment statuses
        employment_statuses = [
            'Employed Full-time', 'Employed Part-time', 'Self-employed', 
            'Unemployed', 'Retired', 'Student'
        ]
        
        # Loan purposes
        loan_purposes = [
            'Home improvement', 'Debt consolidation', 'Business investment',
            'Education', 'Medical expenses', 'Vehicle purchase', 'Other'
        ]
        
        # Alternative data types
        alt_data_types = [
            'social_media', 'utility_payments', 'ecommerce', 
            'mobile_usage', 'geolocation', 'professional_network'
        ]
        
        # Create 50 customers
        for i in range(1, 51):
            customer, created = Customer.objects.get_or_create(
                name=f'Customer {i}',
                defaults={
                    'email': f'customer{i}@example.com',
                    'phone': f'555-{1000+i}',
                    'address': f'{i} Main St, City, State',
                    'credit_score': random.choice(credit_scores),
                    'income': round(random.uniform(30000, 150000), 2),
                    'employment_status': random.choice(employment_statuses)
                }
            )
            
            # Add 1-3 alternative data points per customer
            for j in range(random.randint(1, 3)):
                AlternativeData.objects.create(
                    customer=customer,
                    data_type=random.choice(alt_data_types),
                    source=random.choice(['Facebook', 'LinkedIn', 'Experian', 'Plaid', 'Equifax']),
                    value=json.dumps({'activity_level': random.choice(['low', 'medium', 'high'])}),
                    confidence_score=round(random.uniform(0.5, 0.95), 2)
                )
            
            # Create 1-3 credit applications per customer
            for k in range(random.randint(1, 3)):
                app = CreditApplication.objects.create(
                    customer=customer,
                    amount=round(random.uniform(1000, 50000), 2),
                    term=random.choice([6, 12, 24, 36, 48, 60]),
                    purpose=random.choice(loan_purposes),
                    status=random.choice(['pending', 'approved', 'rejected', 'defaulted'])
                )
                
                # Create risk assessment for each application
                risk_score = random.randint(1, 100)
                pd = 1 / (1 + 2.71828**(-0.1 * (risk_score - 50)))
                
                RiskAssessment.objects.create(
                    application=app,
                    probability_of_default=pd,
                    risk_score=risk_score,
                    decision_reason=f"Automated assessment with score {risk_score}"
                )
                
                # If approved, create payment history
                if app.status == 'approved' or app.status == 'defaulted':
                    for m in range(app.term):
                        due_date = datetime.now() - timedelta(days=(app.term - m) * 30)
                        paid_date = due_date + timedelta(days=random.randint(0, 15)) if random.random() > 0.2 else None
                        
                        PaymentHistory.objects.create(
                            application=app,
                            amount_paid=round(app.amount / app.term, 2),
                            due_date=due_date,
                            paid_date=paid_date,
                            status='paid' if paid_date else 'missed'
                        )
        
        self.stdout.write(self.style.SUCCESS('Successfully populated sample data'))