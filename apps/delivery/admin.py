from django.contrib import admin
from django.utils import timezone
from .models import DeliveryOption, Delivery, DeliveryStatusHistory


@admin.register(DeliveryOption)
class DeliveryOptionAdmin(admin.ModelAdmin):
    list_display = ['name_mk', 'price', 'estimated_days', 'is_active']
    list_filter = ['is_active']
    list_editable = ['is_active']


class DeliveryStatusHistoryInline(admin.TabularInline):
    model = DeliveryStatusHistory
    extra = 0
    readonly_fields = ['status', 'notes', 'created_at']


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'delivery_option', 'courier_name', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__first_name', 'order__last_name', 'tracking_number', 'courier_name']
    list_editable = ['status']
    inlines = [DeliveryStatusHistoryInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order', 'delivery_option')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Tracking', {
            'fields': ('tracking_number', 'courier_name')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'packed_at', 'shipped_at', 'delivered_at')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
    
    readonly_fields = ['created_at']
    
    def save_model(self, request, obj, form, change):
        """Update timestamps when status changes"""
        if change:
            old_status = Delivery.objects.get(pk=obj.pk).status
            if old_status != obj.status:
                # Update timestamp based on new status
                if obj.status == 'packed' and not obj.packed_at:
                    obj.packed_at = timezone.now()
                elif obj.status == 'shipped' and not obj.shipped_at:
                    obj.shipped_at = timezone.now()
                elif obj.status == 'delivered' and not obj.delivered_at:
                    obj.delivered_at = timezone.now()
                
                # Create status history entry
                DeliveryStatusHistory.objects.create(
                    delivery=obj,
                    status=obj.status,
                    notes=f'Status updated by admin: {obj.get_status_display()}'
                )
        
        super().save_model(request, obj, form, change)


@admin.register(DeliveryStatusHistory)
class DeliveryStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['delivery', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    readonly_fields = ['delivery', 'status', 'notes', 'created_at']
