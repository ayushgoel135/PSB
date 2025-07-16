from django.contrib import admin
from .models import Customer, AlternativeData, CreditApplication, RiskAssessment, PaymentHistory

class AlternativeDataInline(admin.TabularInline):
    model = AlternativeData
    extra = 1

class CreditApplicationInline(admin.TabularInline):
    model = CreditApplication
    extra = 0
    readonly_fields = ['applied_at', 'decision_at']
    can_delete = False

class RiskAssessmentInline(admin.StackedInline):
    model = RiskAssessment
    extra = 0
    can_delete = False

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'credit_score', 'income', 'employment_status']
    list_filter = ['credit_score', 'employment_status']
    search_fields = ['name', 'email', 'phone']
    inlines = [AlternativeDataInline, CreditApplicationInline]

@admin.register(CreditApplication)
class CreditApplicationAdmin(admin.ModelAdmin):
    list_display = ['customer', 'amount', 'term', 'status', 'applied_at']
    list_filter = ['status']
    search_fields = ['customer__name', 'purpose']
    inlines = [RiskAssessmentInline]
    actions = ['mark_as_approved', 'mark_as_rejected', 'mark_as_defaulted']
    
    def mark_as_approved(self, request, queryset):
        queryset.update(status='approved')
    mark_as_approved.short_description = "Mark selected applications as approved"
    
    def mark_as_rejected(self, request, queryset):
        queryset.update(status='rejected')
    mark_as_rejected.short_description = "Mark selected applications as rejected"
    
    def mark_as_defaulted(self, request, queryset):
        queryset.update(status='defaulted')
    mark_as_defaulted.short_description = "Mark selected applications as defaulted"

@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ['application', 'risk_score', 'probability_of_default', 'assessed_at']
    list_filter = ['risk_score']
    search_fields = ['application__customer__name']

@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ['application', 'amount_paid', 'due_date', 'paid_date', 'status']
    list_filter = ['status']
    search_fields = ['application__customer__name']