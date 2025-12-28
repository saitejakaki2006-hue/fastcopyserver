import datetime
from datetime import timedelta
from django.utils import timezone
from .models import PublicHoliday

def calculate_delivery_date(order_time=None):
    """
    Calculate estimated delivery date based on:
    - Cutoff: 8 PM (20:00).
    - If <= 8 PM: Next Day.
    - If > 8 PM: Day After Tomorrow.
    - Delivery Days: Mon-Sat (Sunday is Holiday).
    - Public Holidays: Skipped.
    """
    if not order_time:
        order_time = timezone.now()

    # Convert to local time if naive? Django usually uses TZ aware.
    # If order_time is timezone aware, we need to respect it.
    # Assuming order_time is 'current time' in server TZ (likely UTC or IST).
    # User said: "today date 28-12-2025... at 6pm" (Local Time).
    # We should convert to Local Time for 8 PM check if server is UTC.
    # But usually timezone.now() is sufficient if we compare with hour.
    
    # 1. Base Logic
    # 20:00 = 8 PM
    current_hour = order_time.hour
    
    # Check if late
    if current_hour >= 20: # 8 PM or later (User said "8:01pm" -> Day After. "6pm" -> Next Day)
                                # 8:00:00 is technically <= 20? No, 8 PM is 20.
                                # User said "at 6pm (18:00) -> 29 (Next Day)".
                                # "at 8:01pm (20:01) -> 30 (Day After)".
                                # So strictly > 20:00? 
                                # Let's say >= 20 means 8 PM+.
        days_to_add = 2
    else:
        days_to_add = 1
        
    delivery_date = order_time.date() + timedelta(days=days_to_add)
    
    # 2. Skip Holidays (Sunday & Public)
    while True:
        # Check Sunday (6)
        if delivery_date.weekday() == 6:
            delivery_date += timedelta(days=1)
            continue
            
        # Check Public Holiday
        if PublicHoliday.objects.filter(date=delivery_date).exists():
            delivery_date += timedelta(days=1)
            continue
            
        break
        
    return delivery_date
