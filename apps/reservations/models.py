from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product


class Reservation(models.Model):
    """Fitting appointment reservations"""
    
    STATUS_CHOICES = [
        ('pending', 'На чекање'),
        ('confirmed', 'Потврдена'),
        ('completed', 'Завршена'),
        ('cancelled', 'Откажана'),
        ('no_show', 'Не се појави'),
    ]
    
    # Customer info
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=100, verbose_name="Име")
    last_name = models.CharField(max_length=100, verbose_name="Презиме")
    phone = models.CharField(max_length=20, verbose_name="Телефонски број")
    email = models.EmailField(blank=True, verbose_name="Емаил")
    
    # Reservation details
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    reservation_date = models.DateField(verbose_name="Датум")
    reservation_time = models.TimeField(verbose_name="Време")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, verbose_name="Забелешки")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-reservation_date', '-reservation_time']
    
    def __str__(self):
        return f"Reservation: {self.first_name} {self.last_name} - {self.reservation_date}"
