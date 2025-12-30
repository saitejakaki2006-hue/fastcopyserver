#!/usr/bin/env python
"""
Update script to backfill estimated_delivery_date for existing orders.
This will set delivery dates for any orders that are missing them.
"""
import os
import django
import sys

# Setup Django environment
sys.path.append('/Users/saitejakaki/Desktop/fastCopy')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fastCopyConfig.settings')
django.setup()

from django.utils import timezone
from core.models import Order
from core.utils import calculate_delivery_date

def update_existing_orders():
    """Update all orders missing estimated_delivery_date"""
    
    print("=" * 60)
    print("UPDATING EXISTING ORDERS WITH DELIVERY DATES")
    print("=" * 60)
    print()
    
    # Find all orders without estimated_delivery_date
    orders_without_date = Order.objects.filter(estimated_delivery_date__isnull=True)
    total_count = orders_without_date.count()
    
    print(f"Found {total_count} orders without estimated delivery dates")
    print()
    
    if total_count == 0:
        print("All orders already have delivery dates. Nothing to update.")
        return
    
    updated_count = 0
    for order in orders_without_date:
        # Use the order's created_at timestamp to calculate delivery date
        if order.created_at:
            order.estimated_delivery_date = calculate_delivery_date(order.created_at)
            order.save()
            updated_count += 1
            print(f"  Updated Order {order.order_id}: Delivery date set to {order.estimated_delivery_date}")
    
    print()
    print(f"Successfully updated {updated_count} orders")
    print("=" * 60)

if __name__ == "__main__":
    update_existing_orders()
