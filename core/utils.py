import datetime
from datetime import timedelta
from django.utils import timezone
from .models import PublicHoliday

def calculate_delivery_date(order_time=None):
    """
    Calculate estimated delivery date based on WORKING DAYS:
    - Cutoff: 8 PM (20:00).
    - If order placed before 8 PM: Next working day.
    - If order placed after 8 PM (20:01+): Day after next working day.
    - Working Days: Mon-Sat (Sunday is Holiday).
    - Public Holidays: Skipped while counting.
    
    Examples:
    - Order on Monday 6 PM → Delivery Tuesday (next working day)
    - Order on Monday 8:01 PM → Delivery Wednesday (day after next working day)
    - Order on Saturday 6 PM → Delivery Monday (next working day, skip Sunday)
    - Order on Saturday 8:01 PM → Delivery Tuesday (day after next working day, skip Sunday)
    """
    if not order_time:
        order_time = timezone.now()
    
    # 1. Determine how many working days to add based on order time
    current_hour = order_time.hour
    current_minute = order_time.minute
    
    # After 8 PM check: hour > 20 OR (hour == 20 AND minute > 0)
    if current_hour > 20 or (current_hour == 20 and current_minute > 0):
        working_days_to_add = 2  # Day after next working day
    else:
        working_days_to_add = 1  # Next working day
    
    # 2. Start from tomorrow
    delivery_date = order_time.date() + timedelta(days=1)
    
    # 3. Count forward the required number of WORKING days
    working_days_counted = 0
    
    while working_days_counted < working_days_to_add:
        # Check if this date is a working day
        is_working_day = True
        
        # Check if Sunday (weekday 6)
        if delivery_date.weekday() == 6:
            is_working_day = False
        
        # Check if Public Holiday
        if PublicHoliday.objects.filter(date=delivery_date).exists():
            is_working_day = False
        
        # If it's a working day, count it
        if is_working_day:
            working_days_counted += 1
            
            # If we've counted enough working days, we're done
            if working_days_counted == working_days_to_add:
                break
        
        # Move to next day
        delivery_date += timedelta(days=1)
    
    return delivery_date

