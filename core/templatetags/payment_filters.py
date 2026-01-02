from django import template

register = template.Library()

@register.filter(name='final_amount')
def final_amount(order):
    """
    Calculate the final amount for an order.
    Returns the total_price (which is already the final amount after discount).
    """
    if order and hasattr(order, 'total_price'):
        return order.total_price
    return 0
