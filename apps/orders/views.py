from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from apps.cart.views import get_or_create_cart
from apps.delivery.models import DeliveryOption, Delivery, DeliveryStatusHistory
from .models import Order, OrderItem


def checkout_delivery(request):
    """Delivery information step"""
    cart = get_or_create_cart(request)
    
    if not cart.items.exists():
        messages.warning(request, 'Вашата кошничка е празна.')
        return redirect('cart:cart_detail')
    
    delivery_options = DeliveryOption.objects.filter(is_active=True)
    
    if request.method == 'POST':
        # Save delivery info to session
        request.session['delivery_info'] = {
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'phone': request.POST.get('phone'),
            'email': request.POST.get('email', ''),
            'street_address': request.POST.get('street_address'),
            'city': request.POST.get('city'),
            'delivery_option_id': request.POST.get('delivery_option'),
        }
        
        return redirect('orders:checkout_payment')
    
    context = {
        'cart': cart,
        'delivery_options': delivery_options,
        'subtotal': cart.get_total(),
        'original_subtotal': cart.get_original_total(),
        'total_discount': cart.get_total_discount(),
        'has_discounts': cart.has_discounts(),
    }
    return render(request, 'checkout/delivery.html', context)


def checkout_payment(request):
    """Payment method step"""
    cart = get_or_create_cart(request)
    
    if not cart.items.exists():
        messages.warning(request, 'Вашата кошничка е празна.')
        return redirect('cart:cart_detail')
    
    delivery_info = request.session.get('delivery_info')
    if not delivery_info:
        messages.warning(request, 'Ве молиме внесете информации за достава.')
        return redirect('orders:checkout_delivery')
    
    # Get delivery option
    delivery_option = get_object_or_404(DeliveryOption, pk=delivery_info['delivery_option_id'])
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        # Create order with discount information
        subtotal = cart.get_total()  # This is already with discounts applied
        total_discount = cart.get_total_discount()  # Total savings from discounts
        delivery_cost = delivery_option.price
        total = subtotal + delivery_cost
        
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            first_name=delivery_info['first_name'],
            last_name=delivery_info['last_name'],
            phone=delivery_info['phone'],
            email=delivery_info['email'],
            street_address=delivery_info['street_address'],
            city=delivery_info['city'],
            payment_method=payment_method,
            subtotal=subtotal,
            delivery_cost=delivery_cost,
            discount=total_discount,  # Store the total discount amount
            total=total,
            status='pending',
        )
        
        # Create order items (store discounted prices if applicable)
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                product_price=item.get_unit_price(),  # Store discounted unit price
                quantity=item.quantity,
                subtotal=item.get_subtotal(),
            )
        
        # Create delivery record
        delivery = Delivery.objects.create(
            order=order,
            delivery_option=delivery_option,
            status='created',
        )
        
        # Create initial delivery status history
        DeliveryStatusHistory.objects.create(
            delivery=delivery,
            status='created',
            notes='Нарачката е креирана.',
        )
        
        # Clear cart
        cart.items.all().delete()
        
        # Clear session
        if 'delivery_info' in request.session:
            del request.session['delivery_info']
        
        return redirect('orders:order_confirmation', order_id=order.id)
    
    subtotal = cart.get_total()
    original_subtotal = cart.get_original_total()
    total_discount = cart.get_total_discount()
    has_discounts = cart.has_discounts()
    delivery_cost = delivery_option.price
    total = subtotal + delivery_cost
    
    context = {
        'cart': cart,
        'delivery_info': delivery_info,
        'delivery_option': delivery_option,
        'subtotal': subtotal,
        'original_subtotal': original_subtotal,
        'total_discount': total_discount,
        'has_discounts': has_discounts,
        'delivery_cost': delivery_cost,
        'total': total,
    }
    return render(request, 'checkout/payment.html', context)


def order_confirmation(request, order_id):
    """Order confirmation page"""
    order = get_object_or_404(Order, pk=order_id)
    
    # Security: ensure user can only see their own order
    if request.user.is_authenticated and order.user != request.user:
        if not request.user.is_staff:
            messages.error(request, 'Немате пристап до оваа нарачка.')
            return redirect('products:home')
    
    context = {
        'order': order,
    }
    return render(request, 'checkout/confirmation.html', context)


@login_required
def order_history(request):
    """View user's order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'orders/order_history.html', context)


@login_required
def order_detail(request, order_id):
    """View order details"""
    order = get_object_or_404(Order, pk=order_id)
    
    # Security check
    if order.user != request.user and not request.user.is_staff:
        messages.error(request, 'Немате пристап до оваа нарачка.')
        return redirect('orders:order_history')
    
    context = {
        'order': order,
    }
    return render(request, 'orders/order_detail.html', context)
