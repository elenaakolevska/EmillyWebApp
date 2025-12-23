from django.shortcuts import render, get_object_or_404
from .models import Delivery, DeliveryStatusHistory


def track_delivery(request, delivery_id):
    """Track delivery status"""
    delivery = get_object_or_404(Delivery, pk=delivery_id)
    
    # Get status history
    status_history = delivery.status_history.all()
    
    context = {
        'delivery': delivery,
        'order': delivery.order,
        'status_history': status_history,
    }
    return render(request, 'delivery/track_delivery.html', context)
