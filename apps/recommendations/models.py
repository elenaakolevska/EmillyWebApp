from django.db import models
from apps.products.models import Product, Category


class RecommendationRule(models.Model):
    """Rules for product recommendations (upselling)"""
    
    RULE_TYPE_CHOICES = [
        ('category_based', 'По категорија'),
        ('product_based', 'По производ'),
        ('bundle', 'Пакет понуда'),
    ]
    
    name = models.CharField(max_length=200)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    
    # Triggers
    trigger_category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='recommendation_triggers',
        null=True, 
        blank=True
    )
    trigger_product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='recommendation_triggers',
        null=True, 
        blank=True
    )
    
    # Recommended products
    recommended_products = models.ManyToManyField(
        Product, 
        related_name='recommended_in_rules',
        blank=True
    )
    recommended_categories = models.ManyToManyField(
        Category, 
        related_name='recommended_in_rules',
        blank=True
    )
    
    # Discount for bundle
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        help_text="Discount % for bundle offer"
    )
    
    priority = models.IntegerField(default=0, help_text="Higher priority rules show first")
    
    class Meta:
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_rule_type_display()})"
