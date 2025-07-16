from django import forms
from .models import Customer, CreditApplication, AlternativeData

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        exclude = ['user']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'income': forms.NumberInput(attrs={'step': '0.01'}),
        }

class CreditApplicationForm(forms.ModelForm):
    class Meta:
        model = CreditApplication
        fields = '__all__'
        exclude = ['status', 'decision_at']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
            'purpose': forms.Textarea(attrs={'rows': 3}),
        }

class AlternativeDataForm(forms.ModelForm):
    class Meta:
        model = AlternativeData
        fields = '__all__'
        widgets = {
            'value': forms.Textarea(attrs={'rows': 3}),
            'confidence_score': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '1'}),
        }

class RiskAssessmentFilterForm(forms.Form):
    MIN_RISK = 1
    MAX_RISK = 100
    
    risk_score_min = forms.IntegerField(
        label='Minimum Risk Score',
        required=False,
        widget=forms.NumberInput(attrs={'min': MIN_RISK, 'max': MAX_RISK}),
        initial=MIN_RISK
    )
    risk_score_max = forms.IntegerField(
        label='Maximum Risk Score',
        required=False,
        widget=forms.NumberInput(attrs={'min': MIN_RISK, 'max': MAX_RISK}),
        initial=MAX_RISK
    )
    pd_min = forms.FloatField(
        label='Minimum PD (%)',
        required=False,
        widget=forms.NumberInput(attrs={'step': '0.1', 'min': '0', 'max': '100'}),
        initial=0
    )
    pd_max = forms.FloatField(
        label='Maximum PD (%)',
        required=False,
        widget=forms.NumberInput(attrs={'step': '0.1', 'min': '0', 'max': '100'}),
        initial=100
    )
    status = forms.ChoiceField(
        label='Application Status',
        choices=[('', 'All')] + CreditApplication.STATUS_CHOICES,
        required=False
    )