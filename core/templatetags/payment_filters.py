from django import template

register = template.Library()

@register.filter(name='final_amount')
def final_amount(order):
    """
    Calculate the final amount for an order.
    Logic: Original Price (or Total Price) - Discount Amount
    """
    if not order:
        return 0
        
    try:
        # Get values, defaulting to 0 if None
        original = order.original_price if order.original_price is not None else order.total_price
        discount = order.discount_amount if order.discount_amount is not None else 0
        
        # Calculate final paid amount
        paid_amount = float(original) - float(discount)
        return round(paid_amount, 2)
    except:
        # Fallback
        if hasattr(order, 'total_price'):
            return order.total_price
        return 0
