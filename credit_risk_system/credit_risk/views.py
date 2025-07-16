from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from .models import Customer, CreditApplication, RiskAssessment, AlternativeData, PaymentHistory
from .forms import CustomerForm, CreditApplicationForm, AlternativeDataForm, RiskAssessmentFilterForm
from .utils.risk_calculator import RiskModel
from .utils.data_processor import assess_application_risk
from .utils.visualization import generate_risk_surface, generate_portfolio_risk_chart, generate_default_timeline
import json
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Initialize risk model
risk_model = RiskModel()

class DashboardView(LoginRequiredMixin, ListView):
    template_name = 'dashboard.html'
    model = CreditApplication
    context_object_name = 'applications'
    
    def get_queryset(self):
        return CreditApplication.objects.select_related('customer', 'riskassessment').all()[:10]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Portfolio stats
        total_applications = CreditApplication.objects.count()
        approved_applications = CreditApplication.objects.filter(status='approved').count()
        defaulted_applications = CreditApplication.objects.filter(status='defaulted').count()
        
        # Risk assessment stats
        risk_stats = RiskAssessment.objects.aggregate(
            avg_pd=Avg('probability_of_default'),
            avg_risk=Avg('risk_score')
        )
        
        # Generate visualizations
        customers = Customer.objects.all()[:50]  # Limit for demo
        defaulters = CreditApplication.objects.filter(status='defaulted').select_related('customer')[:20]
        
        context.update({
            'total_applications': total_applications,
            'approved_applications': approved_applications,
            'defaulted_applications': defaulted_applications,
            'avg_pd': risk_stats['avg_pd'],
            'avg_risk': risk_stats['avg_risk'],
            'risk_surface': generate_risk_surface(None),
            'portfolio_chart': generate_portfolio_risk_chart(customers),
            'default_timeline': generate_default_timeline(defaulters),
        })
        
        return context

class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'customer_list.html'
    context_object_name = 'customers'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query))
        
        return queryset.order_by('-created_at')

class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = 'customer_detail.html'
    context_object_name = 'customer'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.object
        
        # Get customer's applications
        applications = CreditApplication.objects.filter(customer=customer).select_related('riskassessment')
        
        # Get alternative data
        alternative_data = AlternativeData.objects.filter(customer=customer)
        
        # Get payment history if any applications exist
        payment_history = PaymentHistory.objects.none()
        if applications.exists():
            payment_history = PaymentHistory.objects.filter(application__in=applications)
        
        context.update({
            'applications': applications,
            'alternative_data': alternative_data,
            'payment_history': payment_history,
        })
        
        return context

class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customer_form.html'
    success_url = reverse_lazy('customer_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        return response

class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customer_form.html'
    success_url = reverse_lazy('customer_list')

class CreditApplicationCreateView(LoginRequiredMixin, CreateView):
    model = CreditApplication
    form_class = CreditApplicationForm
    template_name = 'application_form.html'
    
    def get_success_url(self):
        return reverse_lazy('assess_risk', kwargs={'pk': self.object.id})
    
    def form_valid(self, form):
        form.instance.status = 'pending'
        return super().form_valid(form)

class RiskAssessmentView(LoginRequiredMixin, DetailView):
    model = CreditApplication
    template_name = 'risk_assessment.html'
    context_object_name = 'application'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = self.object
        
        # Perform risk assessment if not already done
        if not hasattr(application, 'riskassessment'):
            assessment_data = assess_application_risk(application)
            
            # Create RiskAssessment record
            RiskAssessment.objects.create(
                application=application,
                probability_of_default=assessment_data['probability_of_default'],
                risk_score=assessment_data['risk_score'],
                decision_reason=assessment_data['decision_reason']
            )
            
            # Update application status based on PD
            if assessment_data['probability_of_default'] < 0.1:
                application.status = 'approved'
            else:
                application.status = 'rejected'
            application.save()
        
        # Get alternative data for visualization
        alternative_data = AlternativeData.objects.filter(customer=application.customer)
        
        context['alternative_data_json'] = json.dumps([
            {
                'data_type': ad.data_type,
                'confidence_score': float(ad.confidence_score),
                'value': ad.value[:50] + '...' if len(ad.value) > 50 else ad.value
            }
            for ad in alternative_data
        ])
        
        return context

class DefaulterTrackingView(LoginRequiredMixin, ListView):
    model = CreditApplication
    template_name = 'defaulter_tracking.html'
    context_object_name = 'defaulters'
    
    def get_queryset(self):
        return CreditApplication.objects.filter(status='defaulted').select_related('customer', 'riskassessment')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter form
        filter_form = RiskAssessmentFilterForm(self.request.GET or None)
        
        # Apply filters
        queryset = self.get_queryset()
        
        if filter_form.is_valid():
            risk_min = filter_form.cleaned_data.get('risk_score_min')
            risk_max = filter_form.cleaned_data.get('risk_score_max')
            pd_min = filter_form.cleaned_data.get('pd_min')
            pd_max = filter_form.cleaned_data.get('pd_max')
            status = filter_form.cleaned_data.get('status')
            
            if risk_min is not None:
                queryset = queryset.filter(riskassessment__risk_score__gte=risk_min)
            if risk_max is not None:
                queryset = queryset.filter(riskassessment__risk_score__lte=risk_max)
            if pd_min is not None:
                queryset = queryset.filter(riskassessment__probability_of_default__gte=pd_min/100)
            if pd_max is not None:
                queryset = queryset.filter(riskassessment__probability_of_default__lte=pd_max/100)
            if status:
                queryset = queryset.filter(status=status)
        
        context['filter_form'] = filter_form
        context['defaulters'] = queryset
        
        # Add statistics
        context['total_defaulters'] = queryset.count()
        if queryset.exists():
            context['avg_default_amount'] = queryset.aggregate(
                avg_amount=Avg('amount')
            )['avg_amount']
        
        return context

def approve_application(request, pk):
    application = get_object_or_404(CreditApplication, pk=pk)
    application.status = 'approved'
    application.save()
    return redirect('customer_detail', pk=application.customer.id)

def reject_application(request, pk):
    application = get_object_or_404(CreditApplication, pk=pk)
    application.status = 'rejected'
    application.save()
    return redirect('customer_detail', pk=application.customer.id)

def mark_as_defaulted(request, pk):
    application = get_object_or_404(CreditApplication, pk=pk)
    application.status = 'defaulted'
    application.save()
    return redirect('customer_detail', pk=application.customer.id)

def get_risk_data(request):
    # This would typically come from your database
    data = {
        'risk_scores': [int(x) for x in range(0, 101, 5)],
        'loan_terms': [int(x) for x in range(1, 13)],
        'pd_values': [[1 / (1 + 2.71828**(-0.1 * (x - 50))) * (1 + y/24) 
                      for x in range(0, 101, 5)] 
                     for y in range(1, 13)]
    }
    return JsonResponse(data)