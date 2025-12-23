from django.db import models
from apps.orders.models import Order


class DeliveryOption(models.Model):
    """Available delivery options"""
    name = models.CharField(max_length=100)
    name_mk = models.CharField(max_length=100, verbose_name="Македонско име")
    description = models.TextField(blank=True)
    description_mk = models.TextField(blank=True, verbose_name="Македонски опис")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_days = models.IntegerField(help_text="Estimated delivery time in days")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name_mk} - {self.price} ден."


class Delivery(models.Model):
    """Delivery tracking for orders"""
    
    STATUS_CHOICES = [
        ('created', 'Креирана'),
        ('packed', 'Спакувана'),
        ('shipped', 'Испратена'),
        ('in_transit', 'Во транспорт'),
        ('out_for_delivery', 'На испорака'),
        ('delivered', 'Доставена'),
        ('failed', 'Неуспешна'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    delivery_option = models.ForeignKey(DeliveryOption, on_delete=models.SET_NULL, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    
    # Tracking
    tracking_number = models.CharField(max_length=100, blank=True)
    courier_name = models.CharField(max_length=100, blank=True, verbose_name="Куриерска служба")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    packed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True, verbose_name="Забелешки")
    
    class Meta:
        verbose_name_plural = "Deliveries"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Delivery for Order #{self.order.id} - {self.get_status_display()}"


class DeliveryStatusHistory(models.Model):
    """Track delivery status changes"""
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Delivery Status Histories"
    
    def __str__(self):
        return f"{self.delivery.order.get_order_number()} - {self.status} at {self.created_at}"
