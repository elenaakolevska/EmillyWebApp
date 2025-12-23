from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    """Product categories: Wedding Dress, Formal Dress, Suit, Accessory, etc."""
    name = models.CharField(max_length=100, unique=True)
    name_mk = models.CharField(max_length=100, help_text="Macedonian name")
    slug = models.SlugField(unique=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name_mk


class Product(models.Model):
    """Product model for all items in the boutique"""
    
    SIZE_CHOICES = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
        ('36', '36'),
        ('38', '38'),
        ('40', '40'),
        ('42', '42'),
        ('44', '44'),
        ('46', '46'),
        ('48', '48'),
        ('50', '50'),
        ('52', '52'),
        ('универзална', 'Универзална'),
    ]
    
    COLOR_CHOICES = [
        ('бела', 'Бела'),
        ('црна', 'Црна'),
        ('црвена', 'Црвена'),
        ('сина', 'Сина'),
        ('зелена', 'Зелена'),
        ('жолта', 'Жолта'),
        ('розова', 'Розова'),
        ('сива', 'Сива'),
        ('кафена', 'Кафена'),
        ('портокалова', 'Портокалова'),
        ('виолетова', 'Виолетова'),
        ('златна', 'Златна'),
        ('сребрена', 'Сребрена'),
        ('слонова-коска', 'Слонова Коска'),
        ('бордо', 'Бордо'),
        ('темно-сина', 'Темно Сина'),
        ('смарагдна', 'Смарагдна'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=20, choices=SIZE_CHOICES)
    color = models.CharField(max_length=50, choices=COLOR_CHOICES)
    availability = models.BooleanField(default=True)
    image_path = models.CharField(max_length=500, help_text="Path to product image")
    
    # Additional fields
    is_featured = models.BooleanField(default=False, help_text="Show in featured products")
    is_new = models.BooleanField(default=False, help_text="Show in new collection")
    is_popular = models.BooleanField(default=False, help_text="Show in popular models")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'availability']),
            models.Index(fields=['is_featured', 'is_new', 'is_popular']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.category.name})"
    
    def get_image_url(self):
        """Return the URL path for the product image"""
        return f"/static/products/{self.image_path}"
