from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product


class Order(models.Model):
    """Customer order"""
    
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Картичка'),
        ('bank_transfer', 'Банкарски трансфер'),
        ('cash_on_delivery', 'Плаќање при достава'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'На чекање'),
        ('confirmed', 'Потврдена'),
        ('processing', 'Во обработка'),
        ('shipped', 'Испратена'),
        ('delivered', 'Доставена'),
        ('cancelled', 'Откажана'),
    ]
    
    # User info
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    # Customer details
    first_name = models.CharField(max_length=100, verbose_name="Име")
    last_name = models.CharField(max_length=100, verbose_name="Презиме")
    phone = models.CharField(max_length=20, verbose_name="Телефонски број")
    email = models.EmailField(blank=True, verbose_name="Емаил")
    
    # Delivery address
    street_address = models.CharField(max_length=255, verbose_name="Улица и број")
    city = models.CharField(max_length=100, verbose_name="Град")
    
    # Order details
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Notes
    notes = models.TextField(blank=True, verbose_name="Забелешки")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} - {self.first_name} {self.last_name}"
    
    def get_order_number(self):
        """Format order number"""
        return f"EMY{self.id:06d}"


class OrderItem(models.Model):
    """Items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)  # Store name in case product is deleted
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name} (Order #{self.order.id})"
