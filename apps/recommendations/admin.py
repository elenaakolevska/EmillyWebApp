from django.contrib import admin
from .models import RecommendationRule


@admin.register(RecommendationRule)
class RecommendationRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'rule_type', 'trigger_category', 'trigger_product', 'discount_percentage', 'is_active', 'priority']
    list_filter = ['rule_type', 'is_active', 'trigger_category']
    search_fields = ['name']
    list_editable = ['is_active', 'priority']
    filter_horizontal = ['recommended_products', 'recommended_categories']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'rule_type', 'is_active', 'priority')
        }),
        ('Triggers', {
            'fields': ('trigger_category', 'trigger_product')
        }),
        ('Recommendations', {
            'fields': ('recommended_products', 'recommended_categories', 'discount_percentage')
        }),
    )
