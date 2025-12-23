from .models import Cart


def cart_count(request):
    """Add cart item count to all templates"""
    count = 0
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.get_item_count()
        except Cart.DoesNotExist:
            count = 0
    elif request.session.session_key:
        try:
            cart = Cart.objects.get(session_key=request.session.session_key)
            count = cart.get_item_count()
        except Cart.DoesNotExist:
            count = 0
    
    return {
        'cart_item_count': count
    }

