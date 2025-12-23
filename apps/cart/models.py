from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product


class Cart(models.Model):
    """Shopping cart for users (authenticated or session-based)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Cart (session: {self.session_key})"
    
    def get_total(self):
        """Calculate total cart value (with discounts applied)"""
        return sum(item.get_subtotal() for item in self.items.all())
    
    def get_original_total(self):
        """Calculate total cart value before discounts"""
        return sum(item.product.price * item.quantity for item in self.items.all())
    
    def get_total_discount(self):
        """Calculate total discount amount"""
        return sum(item.get_total_discount() for item in self.items.all())
    
    def has_discounts(self):
        """Check if cart has any discounted items"""
        return any(item.discount_percentage > 0 for item in self.items.all())
    
    def get_item_count(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """Individual items in the shopping cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Discount percentage applied (e.g., 15.00)")
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('cart', 'product')
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    def get_unit_price(self):
        """Get unit price after discount"""
        if self.discount_percentage > 0:
            discount_multiplier = (100 - self.discount_percentage) / 100
            return self.product.price * discount_multiplier
        return self.product.price
    
    def get_subtotal(self):
        """Calculate subtotal for this item"""
        return self.get_unit_price() * self.quantity
    
    def get_total_discount(self):
        """Calculate total discount amount"""
        if self.discount_percentage > 0:
            original_total = self.product.price * self.quantity
            discounted_total = self.get_subtotal()
            return original_total - discounted_total
        return 0
