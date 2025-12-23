from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'product_price', 'quantity', 'subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['get_order_number', 'first_name', 'last_name', 'status', 'payment_method', 'total', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['first_name', 'last_name', 'phone', 'email', 'city']
    list_editable = ['status']
    inlines = [OrderItemInline]
    readonly_fields = ['user', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'status', 'payment_method')
        }),
        ('Customer Details', {
            'fields': ('first_name', 'last_name', 'phone', 'email')
        }),
        ('Delivery Address', {
            'fields': ('street_address', 'city')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'delivery_cost', 'discount', 'total')
        }),
        ('Additional', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'quantity', 'product_price', 'subtotal']
    list_filter = ['order__created_at']
    search_fields = ['product_name', 'order__first_name', 'order__last_name']
    readonly_fields = ['order', 'product', 'product_name', 'product_price', 'quantity', 'subtotal']
