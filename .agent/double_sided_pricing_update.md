# Double-Sided Pricing Configuration - Update Summary

## Overview
Successfully added double-sided pricing configuration to the fastCopy admin panel and updated the website to use these prices.

## Changes Made

### 1. **Database Model Updates** (`core/models.py`)

Added 4 new pricing fields to the `PricingConfig` model:

#### Black & White Double-Sided Pricing:
- `admin_price_per_page_double` - Double-sided B&W price for regular users (default: ₹2.50)
- `dealer_price_per_page_double` - Double-sided B&W price for dealers (default: ₹2.00)

#### Color Double-Sided Pricing:
- `color_price_addition_admin_double` - Additional charge for double-sided color pages (regular users, default: ₹8.00)
- `color_price_addition_dealer_double` - Additional charge for double-sided color pages (dealers, default: ₹6.00)

### 2. **Admin Panel Updates** (`core/admin.py`)

Updated the PricingConfig admin interface to organize pricing fields:
- **Basic Printing Prices - Single Side**: Admin & Dealer rates
- **Basic Printing Prices - Double Side**: Admin & Dealer rates
- **Color Printing Additional Charge - Single Side**: Admin & Dealer rates
- **Color Printing Additional Charge - Double Side**: Admin & Dealer rates

### 3. **Backend Logic Updates** (`core/views.py`)

#### Updated `get_user_pricing()` function:
- Added `price_per_page_double` to return dictionary
- Added `color_addition_double` to return dictionary
- These values are automatically selected based on whether the user is a dealer or regular customer

#### Updated `services_page()` function:
- Removed hardcoded double-sided price calculations
- Now uses actual configured prices from the database:
  - `price_bw_double`: Uses `config.admin_price_per_page_double`
  - `price_color_double`: Uses `config.admin_price_per_page_double + config.color_price_addition_admin_double`

#### Updated `calculate_dealer_price()` function:
- Now checks if order is single or double-sided (`order.side_type`)
- Applies appropriate pricing based on side type:
  - Single-sided: Uses `price_per_page` and `color_addition`
  - Double-sided: Uses `price_per_page_double` and `color_addition_double`

### 4. **Database Migrations**

Created and applied migrations:
- Migration `0027_merge_20251229_2050.py` - Merged conflicting migrations
- Migration `0028_pricingconfig_admin_price_per_page_double_and_more.py` - Added new pricing fields

## How to Use

### In Admin Panel:
1. Go to: http://127.0.0.1:8000/admin/
2. Navigate to: **Pricing Configuration**
3. You'll see separate sections for:
   - Single-sided B&W pricing
   - Double-sided B&W pricing
   - Single-sided color pricing
   - Double-sided color pricing
4. Update prices as needed for both Admin (regular users) and Dealer rates

### On Website:
- Prices are automatically displayed based on configuration
- When users select "Double Side" from the dropdown, the correct double-sided pricing is applied
- Calculations work for both regular users and dealers with their respective pricing

## Default Pricing Structure

| Type | Single Side (Admin) | Double Side (Admin) | Single Side (Dealer) | Double Side (Dealer) |
|------|-------------------|-------------------|---------------------|---------------------|
| **B&W** | ₹1.50/page | ₹2.50/page | ₹1.20/page | ₹2.00/page |
| **Color Addition** | +₹5.00/page | +₹8.00/page | +₹3.00/page | +₹6.00/page |

## Technical Notes

- All pricing is stored in the database and can be changed from the admin panel
- No code changes needed for future price updates
- The frontend JavaScript automatically picks up the new prices
- Dealer dashboard correctly calculates revenue based on double-sided orders
- All price calculations are centralized through the `get_user_pricing()` function

## Testing
1. Visit the services page: http://127.0.0.1:8000/services/
2. Upload a document
3. Select "Double Side" from the Sides dropdown
4. Verify that the price changes to reflect double-sided pricing
5. Test with both B&W and Color options

## Server Status
✅ Django development server is running at http://127.0.0.1:8000/
✅ All migrations have been applied successfully
✅ Changes are live and ready to use
