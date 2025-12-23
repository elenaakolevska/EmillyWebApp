from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_mk', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'name_mk']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'size', 'color', 'availability', 'is_featured', 'is_new', 'is_popular']
    list_filter = ['category', 'availability', 'is_featured', 'is_new', 'is_popular', 'size', 'color']
    search_fields = ['name', 'description']
    list_editable = ['availability', 'is_featured', 'is_new', 'is_popular']
    list_per_page = 50
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description', 'price')
        }),
        ('Product Details', {
            'fields': ('size', 'color', 'availability', 'image_path')
        }),
        ('Display Options', {
            'fields': ('is_featured', 'is_new', 'is_popular')
        }),
    )
