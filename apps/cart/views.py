from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from apps.products.models import Product
from apps.recommendations.models import RecommendationRule
from .models import Cart, CartItem


def get_or_create_cart(request):
    """Get or create cart for user or session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


def cart_detail(request):
    """Display shopping cart"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    
    # Get recommendations based on cart contents
    from decimal import Decimal
    recommended_products = []
    if cart_items.exists():
        # Get categories in cart
        categories_in_cart = set(item.product.category for item in cart_items)
        
        # Find active recommendation rules
        rules = RecommendationRule.objects.filter(
            is_active=True,
            trigger_category__in=categories_in_cart
        )
        
        product_ids_in_cart = [item.product.id for item in cart_items]
        
        for rule in rules:
            # Get recommended products from categories or specific products
            if rule.recommended_categories.exists():
                # Get products from recommended categories
                for category in rule.recommended_categories.all():
                    products = Product.objects.filter(
                        category=category,
                        availability=True
                    ).exclude(id__in=product_ids_in_cart)[:4]
                    
                    for product in products:
                        discount_multiplier = (Decimal('100') - rule.discount_percentage) / Decimal('100')
                        discounted_price = product.price * discount_multiplier
                        savings = product.price - discounted_price
                        
                        recommended_products.append({
                            'product': product,
                            'discount': rule.discount_percentage,
                            'discounted_price': discounted_price,
                            'savings': savings,
                        })
            
            # Also check for specific recommended products
            for product in rule.recommended_products.filter(availability=True).exclude(id__in=product_ids_in_cart):
                discount_multiplier = (Decimal('100') - rule.discount_percentage) / Decimal('100')
                discounted_price = product.price * discount_multiplier
                savings = product.price - discounted_price
                
                recommended_products.append({
                    'product': product,
                    'discount': rule.discount_percentage,
                    'discounted_price': discounted_price,
                    'savings': savings,
                })
    
    # Calculate delivery estimate (mock)
    delivery_cost = 200  # Standard delivery
    
    # Separate accessories from other recommended products
    recommended_accessories = []
    recommended_other = []
    
    for rec in recommended_products:
        product_category = rec['product'].category.slug if rec['product'].category else ''
        if 'accessor' in product_category.lower() or 'додато' in (rec['product'].category.name_mk or '').lower():
            recommended_accessories.append(rec)
        else:
            recommended_other.append(rec)
    
    # Calculate discount totals
    subtotal = cart.get_total()
    original_total = cart.get_original_total()
    total_discount = cart.get_total_discount()
    has_discounts = cart.has_discounts()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'original_subtotal': original_total,
        'total_discount': total_discount,
        'has_discounts': has_discounts,
        'delivery_cost': delivery_cost,
        'total': subtotal + delivery_cost,
        'recommended_accessories': recommended_accessories[:4],  # Show max 4 accessory recommendations
        'recommended_products': recommended_other[:4],  # Show max 4 other recommendations
    }
    return render(request, 'cart/cart_detail.html', context)


def add_to_cart(request, product_id):
    """Add product to cart"""
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id, availability=True)
        cart = get_or_create_cart(request)
        
        # Get discount percentage if provided (for recommendation items)
        from decimal import Decimal, InvalidOperation
        discount_str = request.POST.get('discount', '0')
        
        # Clean up the discount string - handle locale formatting (comma vs period)
        discount_str = str(discount_str).strip().replace(',', '.')
        
        try:
            discount_percentage = Decimal(discount_str)
        except (ValueError, TypeError, InvalidOperation):
            discount_percentage = Decimal('0')
        
        # Ensure discount is within valid range (0-100)
        if discount_percentage < 0:
            discount_percentage = Decimal('0')
        elif discount_percentage > 100:
            discount_percentage = Decimal('100')
        
        # Check if product already in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'discount_percentage': discount_percentage}
        )
        
        if not created:
            cart_item.quantity += 1
            # Update discount if a better discount is provided
            if discount_percentage > cart_item.discount_percentage:
                cart_item.discount_percentage = discount_percentage
            cart_item.save()
            if discount_percentage > 0 and discount_percentage > cart_item.discount_percentage:
                messages.success(request, f'Количината на {product.name} е зголемена и попустот е ажуриран!')
            else:
                messages.success(request, f'Количината на {product.name} е зголемена.')
        else:
            if discount_percentage > 0:
                messages.success(request, f'{product.name} е додаден во кошничката со {discount_percentage:.0f}% попуст!')
            else:
                messages.success(request, f'{product.name} е додаден во кошничката.')
        
        return redirect('cart:cart_detail')
    
    return redirect('products:home')


def update_cart_item(request, item_id):
    """Update cart item quantity"""
    if request.method == 'POST':
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Количината е ажурирана.')
        else:
            cart_item.delete()
            messages.success(request, 'Производот е отстранет од кошничката.')
        
        return redirect('cart:cart_detail')
    
    return redirect('cart:cart_detail')


def remove_from_cart(request, item_id):
    """Remove item from cart"""
    if request.method == 'POST':
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        product_name = cart_item.product.name
        cart_item.delete()
        messages.success(request, f'{product_name} е отстранет од кошничката.')
    
    return redirect('cart:cart_detail')


def apply_coupon(request):
    """Apply coupon code (mock implementation)"""
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code', '').strip()
        
        # Mock coupon validation
        if coupon_code.upper() == 'WELCOME10':
            messages.success(request, 'Купонот е применет! Добивте 10% попуст.')
        elif coupon_code:
            messages.error(request, 'Невалиден купон.')
        
    return redirect('cart:cart_detail')
