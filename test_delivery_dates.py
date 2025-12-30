#!/usr/bin/env python
"""
Test script to verify delivery date calculation logic.
This script tests the delivery date calculation for various scenarios.
"""
import os
import django
import sys
from datetime import datetime

# Setup Django environment
sys.path.append('/Users/saitejakaki/Desktop/fastCopy')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fastCopyConfig.settings')
django.setup()

from django.utils import timezone
from core.utils import calculate_delivery_date
from core.models import PublicHoliday

def test_delivery_dates():
    """Test various scenarios for delivery date calculation"""
    
    print("=" * 60)
    print("DELIVERY DATE CALCULATION TEST")
    print("=" * 60)
    print()
    
    # Test Case 1: Order before 8 PM
    print("Test 1: Order placed at 6:00 PM (Before 8 PM)")
    test_time_1 = timezone.make_aware(datetime(2025, 12, 30, 18, 0, 0))
    delivery_1 = calculate_delivery_date(test_time_1)
    print(f"  Order Time: {test_time_1}")
    print(f"  Delivery Date: {delivery_1}")
    print(f"  Expected: Next working day")
    print()
    
    # Test Case 2: Order after 8 PM
    print("Test 2: Order placed at 9:00 PM (After 8 PM)")
    test_time_2 = timezone.make_aware(datetime(2025, 12, 30, 21, 0, 0))
    delivery_2 = calculate_delivery_date(test_time_2)
    print(f"  Order Time: {test_time_2}")
    print(f"  Delivery Date: {delivery_2}")
    print(f"  Expected: Day after next working day")
    print()
    
    # Test Case 3: Order at exactly 8:00 PM
    print("Test 3: Order placed at exactly 8:00 PM")
    test_time_3 = timezone.make_aware(datetime(2025, 12, 30, 20, 0, 0))
    delivery_3 = calculate_delivery_date(test_time_3)
    print(f"  Order Time: {test_time_3}")
    print(f"  Delivery Date: {delivery_3}")
    print(f"  Expected: Next working day (8:00 PM is still 'before')")
    print()
    
    # Test Case 4: Order at 8:01 PM
    print("Test 4: Order placed at 8:01 PM")
    test_time_4 = timezone.make_aware(datetime(2025, 12, 30, 20, 1, 0))
    delivery_4 = calculate_delivery_date(test_time_4)
    print(f"  Order Time: {test_time_4}")
    print(f"  Delivery Date: {delivery_4}")
    print(f"  Expected: Day after next working day")
    print()
    
    # Check holidays
    print("=" * 60)
    print("REGISTERED PUBLIC HOLIDAYS")
    print("=" * 60)
    holidays = PublicHoliday.objects.all().order_by('date')
    if holidays.exists():
        for holiday in holidays:
            print(f"  {holiday.date} - {holiday.name}")
    else:
        print("  No public holidays registered")
    print()
    
    # Current time test
    print("=" * 60)
    print("CURRENT ORDER TEST")
    print("=" * 60)
    now = timezone.now()
    current_delivery = calculate_delivery_date(now)
    print(f"  Current Time: {now}")
    print(f"  Delivery Date: {current_delivery}")
    print()

if __name__ == "__main__":
    test_delivery_dates()
