#!/usr/bin/env python
"""
Test Order Creation with Delivery Date Calculation
This script creates a test order to verify delivery dates are automatically calculated.
"""
import os
import django
import sys

# Setup Django environment
sys.path.append('/Users/saitejakaki/Desktop/fastCopy')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fastCopyConfig.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth.models import User
from core.models import Order
from datetime import datetime

def test_order_creation():
    """Test creating an order and verify delivery date is automatically set"""
    
    print("\n" + "="*70)
    print(" "*15 + "ORDER CREATION TEST - DELIVERY DATE AUTO-CALCULATION")
    print("="*70)
    
    # Get or create a test user
    test_user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'first_name': 'Test',
            'email': 'test@fastcopy.in'
        }
    )
    
    if created:
        test_user.set_password('testpass123')
        test_user.save()
        print(f"\n✅ Created test user: {test_user.username}")
    else:
        print(f"\n✅ Using existing test user: {test_user.username}")
    
    # Create a test order WITHOUT explicitly setting delivery date
    print("\n📝 Creating test order without explicitly setting delivery date...")
    
    test_order = Order(
        user=test_user,
        transaction_id=f"TEST_ORDER_{int(timezone.now().timestamp())}",
        service_name="Test Printing Service",
        total_price=100.00,
        location="Test Campus",
        print_mode="B&W",
        side_type="single",
        copies=1,
        pages=10,
        payment_status="Success",
        status="Pending"
        # NOTE: We are NOT setting estimated_delivery_date here!
    )
    
    # Save the order - this should trigger automatic delivery date calculation
    test_order.save()
    
    print(f"\n✅ Order created successfully!")
    print(f"   Order ID:              {test_order.order_id}")
    print(f"   Transaction ID:        {test_order.transaction_id}")
    print(f"   Created At:            {test_order.created_at.strftime('%A, %d %B %Y at %I:%M %p')}")
    print(f"   Estimated Delivery:    {test_order.estimated_delivery_date.strftime('%A, %d %B %Y') if test_order.estimated_delivery_date else 'NOT SET ❌'}")
    
    # Verify the delivery date was set
    if test_order.estimated_delivery_date:
        print("\n🎉 SUCCESS! Delivery date was automatically calculated and saved!")
        
        # Calculate what it should be
        from core.utils import calculate_delivery_date
        expected_delivery = calculate_delivery_date(test_order.created_at)
        
        if test_order.estimated_delivery_date == expected_delivery:
            print("✅ Delivery date matches expected calculation!")
        else:
            print(f"⚠️  Delivery date mismatch!")
            print(f"   Expected: {expected_delivery}")
            print(f"   Got: {test_order.estimated_delivery_date}")
    else:
        print("\n❌ FAILED! Delivery date was NOT automatically set!")
        print("   This indicates the fix is not working properly.")
    
    # Clean up - delete test order
    print(f"\n🧹 Cleaning up test order...")
    test_order.delete()
    print("   Test order deleted.")
    
    print("\n" + "="*70)
    print(" "*25 + "TEST COMPLETE")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_order_creation()
