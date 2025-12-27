from .models import CartItem

def cart_count(request):
    """
    Returns the total number of items in the user's cart for global template access.
    Usage in templates: {{ cart_item_count }}
    """
    if request.user.is_authenticated:
        # Count actual rows in the DB for the logged-in user
        count = CartItem.objects.filter(user=request.user).count()
    else:
        # Fallback to session count for guest users (if any)
        cart = request.session.get('cart', [])
        count = len(cart)
        
    return {
        'cart_item_count': count
    }