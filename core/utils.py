import datetime
from datetime import timedelta
from django.utils import timezone
from .models import PublicHoliday

def calculate_delivery_date(order_time=None):
    """
    Calculate estimated delivery date based on WORKING DAYS:
    - Cutoff: 8 PM (20:00).
    - If order placed BEFORE 8 PM (19:59 or earlier): Next working day.
    - If order placed AT or AFTER 8 PM (20:00+): Day after next working day.
    - Working Days: Mon-Sat (Sunday is Holiday).
    - Public Holidays: Skipped while counting.
    - SATURDAY EXCEPTION: Orders on Saturday always deliver on Monday (skip cutoff rule).
    
    Examples:
    - Order on Monday 6 PM → Delivery Tuesday (next working day)
    - Order on Monday 8:00 PM → Delivery Wednesday (day after next working day)
    - Order on Monday 8:01 PM → Delivery Wednesday (day after next working day)
    - Order on Saturday 6 PM → Delivery Monday (next working day, skip Sunday)
    - Order on Saturday 8:00 PM → Delivery Monday (Saturday exception, not Tuesday)
    """
    if not order_time:
        order_time = timezone.now()
    
    # CRITICAL FIX: Convert to local timezone (IST) before checking hour
    # timezone.now() returns UTC, so 9 PM IST (21:00) becomes ~3:30 PM UTC (15:30)
    # causing the check to fail. This fixes it.
    order_time = timezone.localtime(order_time)
    
    # 1. Determine how many working days to add based on order time
    current_hour = order_time.hour
    current_weekday = order_time.weekday()  # 0=Monday, 5=Saturday, 6=Sunday
    
    # SATURDAY EXCEPTION: Orders placed on Saturday always get next working day (Monday)
    # regardless of time
    if current_weekday == 5:  # Saturday
        working_days_to_add = 1  # Next working day (Monday, skipping Sunday)
    # AT or AFTER 8 PM check: hour >= 20
    elif current_hour >= 20:
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
        
        # Check if Public Holiday (from database)
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


def count_color_pages(page_range_string, total_pages):
    """
    Parse page range string and return count of color pages.
    
    Args:
        page_range_string: String like "1,3,5-7" specifying which pages are color
        total_pages: Total number of pages in the document
    
    Returns:
        Integer count of color pages
    
    Examples:
        count_color_pages("1,3,5-7", 10) → 5 pages (1, 3, 5, 6, 7)
        count_color_pages("1-10,15", 20) → 11 pages
        count_color_pages("", 10) → 0 pages
    """
    if not page_range_string:
        return 0
    
    color_pages_set = set()
    parts = page_range_string.replace(' ', '').split(',')
    
    for part in parts:
        if not part:  # Skip empty parts
            continue
            
        if '-' in part:
            # Handle range like "5-7"
            try:
                start, end = part.split('-')
                for i in range(int(start), int(end) + 1):
                    if 1 <= i <= total_pages:
                        color_pages_set.add(i)
            except (ValueError, IndexError):
                # Skip invalid ranges
                continue
        else:
            # Handle single page like "3"
            try:
                page = int(part)
                if 1 <= page <= total_pages:
                    color_pages_set.add(page)
            except ValueError:
                # Skip invalid page numbers
                continue
    
    return len(color_pages_set)

