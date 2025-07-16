from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Customer(models.Model):
    CREDIT_SCORE_CHOICES = [
        ('300-579', 'Poor'),
        ('580-669', 'Fair'),
        ('670-739', 'Good'),
        ('740-799', 'Very Good'),
        ('800-850', 'Excellent'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    credit_score = models.CharField(max_length=10, choices=CREDIT_SCORE_CHOICES)
    income = models.DecimalField(max_digits=12, decimal_places=2)
    employment_status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class AlternativeData(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    data_type = models.CharField(max_length=50)  # e.g., 'social_media', 'utility_payments'
    source = models.CharField(max_length=100)
    value = models.TextField()  # Could be JSON data
    confidence_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    collected_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.customer.name} - {self.data_type}"

class CreditApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('defaulted', 'Defaulted'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    term = models.IntegerField()  # in months
    purpose = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    decision_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.customer.name} - {self.amount}"

class RiskAssessment(models.Model):
    application = models.OneToOneField(CreditApplication, on_delete=models.CASCADE)
    probability_of_default = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    risk_score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    decision_reason = models.TextField()
    assessed_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Risk for {self.application.customer.name} - PD: {self.probability_of_default:.2%}"

class PaymentHistory(models.Model):
    application = models.ForeignKey(CreditApplication, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20)  # 'paid', 'late', 'missed'
    
    def __str__(self):
        return f"Payment for {self.application} - {self.status}"