from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.products.models import Product
from .models import Reservation


def create_reservation(request):
    """Create a fitting reservation"""
    product_id = request.GET.get('product')
    product = None
    
    if product_id:
        product = get_object_or_404(Product, pk=product_id)
    
    if request.method == 'POST':
        # Create reservation
        reservation = Reservation(
            user=request.user if request.user.is_authenticated else None,
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            phone=request.POST.get('phone'),
            email=request.POST.get('email', ''),
            reservation_date=request.POST.get('reservation_date'),
            reservation_time=request.POST.get('reservation_time'),
            notes=request.POST.get('notes', ''),
        )
        
        if product_id:
            reservation.product = product
        
        reservation.save()
        
        messages.success(request, 'Вашата резервација е успешно креирана!')
        return redirect('reservations:reservation_confirmation', reservation_id=reservation.id)
    
    context = {
        'product': product,
    }
    return render(request, 'reservations/create.html', context)


def reservation_confirmation(request, reservation_id):
    """Reservation confirmation page"""
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    
    context = {
        'reservation': reservation,
    }
    return render(request, 'reservations/confirmation.html', context)


@login_required
def my_reservations(request):
    """View user's reservations"""
    reservations = Reservation.objects.filter(user=request.user).order_by('-reservation_date', '-reservation_time')
    
    context = {
        'reservations': reservations,
    }
    return render(request, 'reservations/my_reservations.html', context)
