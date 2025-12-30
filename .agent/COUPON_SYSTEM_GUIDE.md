# 🎟️ COUPON SYSTEM - COMPLETE GUIDE

## Overview
The coupon system allows you to create and manage discount coupons from the admin dashboard. Coupons provide percentage-based discounts on the total order amount.

---

## ✅ Features Implemented

### 1. **Coupon Model**
- Unique coupon codes
- Percentage-based discounts
- Validity period (start and end dates)
- Minimum order amount requirement
- Usage limits (can be unlimited)
- Active/Inactive status
- Usage tracking

### 2. **Admin Dashboard**
- Beautiful, user-friendly interface
- Create/Edit/Delete coupons
- View coupon status at a glance
- Track usage statistics
- Filter and search coupons

### 3. **Checkout Integration**
- Apply coupon codes during checkout
- Real-time validation
- Automatic discount calculation
- Visual discount display
- Remove coupon option

### 4. **Perfect Calculations**
- Original price tracking
- Discount amount calculation
- Final price after discount
- Savings display

---

## 📋 How To Use

### Creating a Coupon (Admin)

1. **Access Admin Panel**
   - Go to: http://127.0.0.1:8000/admin/
   - Login with admin credentials

2. **Navigate to Coupons**
   - Click on "Core" → "Coupons"
   - Click "Add Coupon"

3. **Fill in Coupon Details**

   **Coupon Code:**
   - Enter a unique code (e.g., `SAVE20`, `WELCOME10`)
   - Will be converted to uppercase automatically
   - Must be unique across all coupons

   **Discount Percentage:**
   - Enter the discount percentage (e.g., 10.00 for 10% off)
   - Can be decimal (e.g., 15.50 for 15.5% off)

   **Valid From / Valid Until:**
   - Set the start date and time
   - Set the expiry date and time
   - Coupon active only between these dates

   **Minimum Order Amount:**
   - Set minimum cart value required (e.g., 500.00)
   - Set to 0.00 for no minimum

   **Max Usage Count:**
   - Set maximum number of times coupon can be used
   - Set to 0 for unlimited usage
   - System automatically tracks usage

   **Is Active:**
   - Check to enable the coupon
   - Uncheck to temporarily disable

   **Description** (Optional):
   - Internal notes about the coupon
   - Not visible to customers

4. **Save**
   - Click "Save" to create the coupon
   - Coupon is now ready to use!

---

### Applying a Coupon (Customer)

1. **During Checkout**
   - Add items to cart
   - Go to checkout page
   - Look for "Have a coupon?" section

2. **Enter Coupon Code**
   - Type the coupon code
   - Click "Apply"

3. **See Savings**
   - Discount is applied instantly
   - See original price
   - See discount amount
   - See final price after discount

4. **Remove Coupon** (Optional)
   - Click "Remove" button to remove coupon
   - Price reverts to original

---

## 🎯 Coupon Validation Rules

The system automatically validates coupons based on:

### 1. **Active Status**
- ❌ Inactive coupons cannot be used
- ✅ Only active coupons work

### 2. **Validity Period**
- ❌ Coupon not yet active (before start date)
- ❌ Coupon expired (after end date)
- ✅ Current time is between start and end dates

### 3. **Usage Limit**
- ❌ Coupon reached maximum usage count
- ✅ Still has usage remaining

### 4. **Minimum Order Amount**
- ❌ Order total less than minimum required
- ✅ Order total meets or exceeds minimum

---

## 💰 Calculation Example

### Example 1: Simple Discount
```
Items Total:      ₹500.00
Delivery Charge:  ₹40.00
─────────────────────────
Subtotal:         ₹540.00

Coupon: SAVE20 (20% off)
Discount:         -₹108.00
─────────────────────────
FINAL TOTAL:      ₹432.00

You Saved: ₹108.00!
```

### Example 2: Minimum Order Requirement
```
Items Total:      ₹400.00
Delivery Charge:  ₹40.00
─────────────────────────
Subtotal:         ₹440.00

Coupon: BIG50 (50% off, min ₹500)
❌ Cannot apply: Minimum order ₹500 required
Current order: ₹440.00
```

### Example 3: Usage Limit Reached
```
Coupon: FIRST10 (10% off, max 100 uses)
Current Usage: 100/100
❌ Cannot apply: Coupon usage limit reached
```

---

## 📊 Admin Dashboard Features

### Coupon List View
Displays all coupons with:
- **Coupon Code** - Monospace font for easy reading
- **Discount Badge** - Green badge showing percentage
- **Status** - Active/Inactive/Expired/Not Yet Active
- **Usage** - Current usage / Maximum (or ∞ for unlimited)
- **Min Order** - Minimum order amount or "No minimum"
- **Valid From** - Start date and time
- **Valid Until** - End date and time

### Filters Available
- **Active Status** - Filter by active/inactive
- **Valid From Date** - Filter by start date
- **Valid Until Date** - Filter by expiry date

### Search
- Search by coupon code
- Search by description

---

## 🔧 Technical Details

### Database Fields

**Coupon Model:**
```python
- code: Unique coupon code
- discount_percentage: Decimal (% off)
- valid_from: DateTime (start)
- valid_until: DateTime (expiry)
- minimum_order_amount: Decimal
- max_usage_count: Integer (0 = unlimited)
- current_usage_count: Integer (auto-tracked)
- is_active: Boolean
- description: Text (optional)
- created_at: DateTime (auto)
- updated_at: DateTime (auto)
```

**Order Model (Coupon Fields):**
```python
- coupon_code: Applied coupon code
- discount_amount: Discount in ₹
- original_price: Price before discount
- total_price:Final price after discount
```

### Workflow

1. **Customer applies coupon** → Validates against all rules
2. **Valid coupon** → Saves to session
3. **Checkout page** → Shows discount preview
4. **Payment initiation** → Applies discount to order
5. **Order created** → Stores coupon info and discount
6. **Coupon usage** → Increments usage count
7. **Session cleared** → Removes coupon from session

---

## 💡 Best Practices

### Creating Effective Coupons

1. **Clear Codes**
   - Use memorable codes (WELCOME10, SAVE20)
   - Keep them short and simple
   - Use ALL CAPS for consistency

2. **Reasonable Discounts**
   - 5-10% for regular coupons
   - 15-25% for special occasions
   - 30-50% for clearance/special events

3. **Set Minimums**
   - Encourage larger orders
   - Typical: ₹500-₹1000 minimum
   - No minimum for welcome coupons

4. **Usage Limits**
   - First-time orders: 1-time use per user
   - Promotional: 100-500 total uses
   - Referral: Unlimited but time-limited

5. **Validity Periods**
   - Weekend sales: 2-3 days
   - Monthly promotions: Whole month
   - Welcome coupons: 30-90 days

---

## 🎨 UI/UX Features

### Checkout Page
- Clean coupon input field
- "Have a coupon?" expandable section
- Apply button with validation
- Real-time error messages
- Success notification with savings
- Remove button for applied coupons
- Visual price breakdown:
  - Original total (strikethrough if discount)
  - Discount amount (in green)
  - Final total (highlighted)

---

## 🐛 Troubleshooting

### Common Issues

**Q: Coupon code not working?**
- Check if coupon is active
- Verify current date is within validity period
- Ensure order meets minimum amount
- Check if usage limit reached

**Q: Discount not applying?**
- Verify coupon code is correct (case-insensitive)
- Check all validation rules
- Try refreshing the checkout page

**Q: Usage count not incrementing?**
- Usage increments only on successful payment
- Failed/cancelled orders don't count
- Check database directly if needed

**Q: Want to reset usage count?**
- Go to admin panel
- Edit the coupon
- Manually adjust current_usage_count

---

## 📈 Analytics & Tracking

### What's Tracked
- Total coupon usage
- Revenue with coupons applied
- Most popular coupons
- Coupon expiration dates

### Viewing Analytics
1. Go to admin dashboard
2. Navigate to Coupons
3. View usage stats for each coupon
4. Filter by date range for insights

---

## 🔐 Security Features

1. **Validation** - All coupons validated server-side
2. **Session Management** - Secure session storage
3. **One-time Application** - Coupon cleared after order
4. **Usage Tracking** - Prevents over-use
5. **Admin Only** - Only admins can create/edit coupons

---

## 🚀 Example Coupon Campaigns

### Welcome Campaign
```
Code: WELCOME10
Discount: 10%
Min Order: ₹0
Max Usage: Unlimited
Valid: 30 days from today
Active: Yes
```

### Flash Sale
```
Code: FLASH50
Discount: 50%
Min Order: ₹1000
Max Usage: 50
Valid: Weekend only
Active: Yes
```

### First Order
```
Code: FIRST20
Discount: 20%
Min Order: ₹500
Max Usage: 1 per user (implement separately)
Valid: 90 days
Active: Yes
```

---

## Status: ✅ FULLY FUNCTIONAL

The coupon system is now live and ready to use!

**Next Steps:**
1. Create your first coupon
2. Test it on checkout page
3. Monitor usage and analytics
4. Create campaigns based on data

Happy discounting! 🎉
