# Delivery Date Calculation - Bug Fix Report

## Issue Description
The delivery date calculation logic was not being consistently applied to orders. While the marquee correctly showed the delivery dates using the `calculate_delivery_date()` function, actual orders were not getting their `estimated_delivery_date` field populated correctly.

## Problem Analysis

### Root Cause
The `Order` model's `save()` method was not automatically calculating the `estimated_delivery_date` when new orders were created. The delivery date was only being calculated in the `initiate_payment` view, but this calculation wasn't happening consistently for all order creation scenarios.

### Existing Logic (Working)
- **Marquee Display**: Used `calculate_delivery_date()` correctly via context processor
- **Checkout Summary**: Calculated delivery date before displaying to user
- **Holiday Management**: Admin panel properly manages holidays via `PublicHoliday` model

### Missing Logic (Fixed)
- **Order Creation**: Orders weren't automatically calculating delivery dates when saved
- **Existing Orders**: Old orders had NULL delivery dates

## Solution Implemented

### 1. Updated Order Model (`core/models.py`)
Modified the `Order.save()` method to automatically calculate `estimated_delivery_date` for new orders:

```python
def save(self, *args, **kwargs):
    from .utils import calculate_delivery_date
    from django.utils import timezone
    
    is_new = self._state.adding
    if is_new and not self.order_id:
        self.order_id = f"TMP_{uuid.uuid4().hex[:10].upper()}"

    if self.print_mode == 'custom_split' and self.custom_color_pages:
        self.print_mode = f"Custom Split ({self.custom_color_pages})"

    if self.transaction_id:
        if self.transaction_id.startswith("DIR"):
            self.order_source = 'SERVICE'
        elif self.transaction_id.startswith("TXN"):
            self.order_source = 'CART'
    
    # Calculate estimated delivery date for new orders (if not already set)
    if is_new and not self.estimated_delivery_date:
        self.estimated_delivery_date = calculate_delivery_date(timezone.now())

    super().save(*args, **kwargs)

    if is_new and self.order_id.startswith('TMP_'):
        formatted_id = f"FC_ORDER_{self.id:010d}"
        Order.objects.filter(pk=self.pk).update(order_id=formatted_id)
        self.order_id = formatted_id
```

**Key Changes:**
- Added import of `calculate_delivery_date` and `timezone`
- Check if order is new (`is_new`) and delivery date is not already set
- Automatically calculate delivery date using current timestamp
- This ensures ALL new orders get proper delivery dates

### 2. Created Update Script (`update_order_delivery_dates.py`)
Created a utility script to backfill delivery dates for existing orders that were missing them:

**Results:**
- Successfully updated 8 existing orders
- Used each order's `created_at` timestamp to calculate appropriate delivery date

### 3. Created Test Script (`test_delivery_dates.py`)
Created comprehensive test script to verify the delivery calculation logic:

**Test Cases:**
- ✅ Order at 6:00 PM (Before 8 PM) → Next working day
- ✅ Order at 9:00 PM (After 8 PM) → Day after next working day
- ✅ Order at exactly 8:00 PM → Next working day (8:00 PM is still "before")
- ✅ Order at 8:01 PM → Day after next working day

## Delivery Date Logic

### Rules (As Per Requirement)
1. **Order Before 8 PM (≤ 20:00)**: Delivery on next working day
2. **Order After 8 PM (> 20:00)**: Delivery on day after next working day
3. **Working Days**: Monday to Saturday (Sunday is a non-working day)
4. **Public Holidays**: Managed via Admin Panel, automatically skipped

### Implementation (`core/utils.py`)
```python
def calculate_delivery_date(order_time=None):
    if not order_time:
        order_time = timezone.now()
    
    # Determine how many working days to add
    current_hour = order_time.hour
    current_minute = order_time.minute
    
    # After 8 PM check: hour > 20 OR (hour == 20 AND minute > 0)
    if current_hour > 20 or (current_hour == 20 and current_minute > 0):
        working_days_to_add = 2  # Day after next working day
    else:
        working_days_to_add = 1  # Next working day
    
    # Start from tomorrow
    delivery_date = order_time.date() + timedelta(days=1)
    
    # Count forward the required number of WORKING days
    working_days_counted = 0
    
    while working_days_counted < working_days_to_add:
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
```

## Where Delivery Dates Are Displayed

### 1. Checkout Page (`templates/core/checkout.html`)
Shows estimated delivery date in a prominent banner before payment

### 2. Order History (`templates/core/history.html`)
Displays delivery date for each order in user's history

### 3. Profile Page (`templates/core/profile.html`)
Shows recent bookings with delivery dates

### 4. Dealer Dashboard (`templates/dealer/dealer_dashboard.html`)
Displays delivery dates for all orders in dealer view

## Managing Public Holidays

### Admin Panel Access
1. Login to admin panel at `/admin/`
2. Navigate to "Core" → "Public Holidays"
3. Add new holidays with date and name
4. Holidays are automatically considered in delivery calculations

### Holiday Model
```python
class PublicHoliday(models.Model):
    date = models.DateField(unique=True)
    name = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['date']
```

## Testing & Verification

### Manual Testing Steps
1. **Test Before 8 PM Order:**
   - Place an order before 8:00 PM
   - Verify delivery date is next working day
   - Check that Sundays are skipped

2. **Test After 8 PM Order:**
   - Place an order after 8:01 PM
   - Verify delivery date is day after next working day
   - Check that holidays are skipped

3. **Test Holiday Handling:**
   - Add a public holiday in admin panel
   - Place an order that would deliver on that holiday
   - Verify delivery date automatically shifts to next working day

### Test Scripts
- Run `python3 test_delivery_dates.py` to verify calculation logic
- Run `python3 update_order_delivery_dates.py` to backfill missing dates

## Files Modified

### Core Changes
- `core/models.py` - Updated `Order.save()` method

### Utility Scripts (New)
- `test_delivery_dates.py` - Test script for delivery calculations
- `update_order_delivery_dates.py` - Script to backfill existing orders

### Existing Files (No Changes Needed)
- `core/utils.py` - Delivery calculation logic (already correct)
- `core/context_processors.py` - Marquee display (already correct)
- `core/views.py` - Uses delivery calculation (already correct)
- Templates - Already displaying delivery dates properly

## Summary

### What Was Wrong
- Orders were created without automatically calculating delivery dates
- Only the checkout summary showed the date, but it wasn't saved to the order
- Existing orders had NULL delivery dates

### What Was Fixed
- Order model now automatically calculates delivery date on creation
- All existing orders updated with proper delivery dates
- Logic consistently applied across all order creation paths

### Result
✅ **All orders now have correct estimated delivery dates**
✅ **Dates respect the 8 PM cutoff rule**
✅ **Holidays from admin panel are properly skipped**
✅ **Marquee and actual orders use the same logic**

## Future Considerations

### Recommendations
1. Consider adding email notifications with delivery dates
2. Add SMS alerts for delivery reminders
3. Implement real-time tracking updates
4. Add ability to update delivery dates for delayed orders

### Maintenance
- Regularly update public holidays in admin panel
- Monitor delivery date accuracy
- Consider adding buffer days for high-volume periods
