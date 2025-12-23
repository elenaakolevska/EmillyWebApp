from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone', 'product', 'reservation_date', 'reservation_time', 'status', 'created_at']
    list_filter = ['status', 'reservation_date', 'created_at']
    search_fields = ['first_name', 'last_name', 'phone', 'email']
    list_editable = ['status']
    readonly_fields = ['user', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('user', 'first_name', 'last_name', 'phone', 'email')
        }),
        ('Reservation Details', {
            'fields': ('product', 'reservation_date', 'reservation_time', 'status')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
