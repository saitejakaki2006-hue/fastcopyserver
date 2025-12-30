# Pricing Auto-Update  Testing Guide

## Testing Steps

### 1. Clear Browser Cache (IMPORTANT!)

The browser may be caching the old JavaScript file. To ensure you see the latest prices:

**Option A - Hard Refresh:**
- **Chrome/Edge**: Press `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
- **Firefox**: Press `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)
- **Safari**: Press `Cmd+Option+E` then `Cmd+R`

**Option B - Clear Cache:**
- Open browser DevTools (F12)
- Right-click the refresh button
- Select "Empty Cache and Hard Reload"

### 2. Check Console Logs

1. Open the services page: http://127.0.0.1:8000/services/
2. Open Browser DevTools (Press F12)
3. Go to the "Console" tab
4. You should see: `FastCopy Pricing Loaded:` with all current prices
5. Verify these match your PricingConfig in admin

### 3. Update Prices in Admin

1. Go to: http://127.0.0.1:8000/admin/
2. Login with: **admin1** / **admin123**
3. Click on **Pricing Configuration**
4. Click on the pricing config entry
5. Try changing:
   - **B&W Single Side** (currently ₹1.50)
   - **B&W Double Side** (currently ₹2.50)
   - **Color Addition Single** (currently ₹5.00)
   - **Color Addition Double** (currently ₹8.00)
6. Click **Save**

### 4. Verify Changes on Website

1. Go back to services page: http://127.0.0.1:8000/services/
2. Do a **Hard Refresh** (Ctrl+Shift+R or Cmd+Shift+R)
3. Check the console log again - prices should be updated
4. Check the displayed prices in the "Rates Summary" section
5. Upload a test PDF and verify the price calculation is correct

## Current Pricing Structure

### Configured Prices (Default Values):

**Black & White:**
- Single Side: ₹1.50/page (admin), ₹1.20/page (dealer)
- Double Side: ₹2.50/page (admin), ₹2.00/page (dealer)

**Color Addition:**
- Single Side: +₹5.00/page (admin), +₹3.00/page (dealer)
- Double Side: +₹8.00/page (admin), +₹6.00/page (dealer)

**Spiral Binding Tiers:**
- Tier 1 (1-40 pages): ₹20.00 (admin/dealer)
- Tier 2 (41-60 pages): ₹25.00 (admin/dealer)
- Tier 3 (61-90 pages): ₹30.00 (admin/dealer)
- Extra (per 20 pages above 90): +₹5.00 (admin/dealer)

**Soft Binding:**
- ₹30.00 (admin), ₹25.00 (dealer)

**Custom Layouts:**
- 1/4 Layout: ₹2.00/sheet (admin), ₹1.50/sheet (dealer)
- 1/8 Layout: ₹4.00/sheet (admin), ₹3.00/sheet (dealer)
- 1/9 Layout: ₹4.00/sheet (admin), ₹3.00/sheet (dealer)

**Delivery:**
- ₹40.00 (admin), ₹30.00 (dealer)

## Price Calculation Logic Applied

### For Regular Printing:

**Single-Sided B&W:**
```
Total = Pages × Copies × admin_price_per_page
```

**Double-Sided B&W:**
```
Total = ceil(Pages / 2) × Copies × admin_price_per_page_double
```

**Single-Sided Color:**
```
Total = Pages × Copies × (admin_price_per_page + color_price_addition_admin)
```

**Double-Sided Color:**
```
Total = Pages × Copies × (admin_price_per_page_double + color_price_addition_admin_double)
```

### For Spiral Binding:

```
Printing Cost = (Pages × Copies × price_per_page)

If Pages <= 40: Binding = spiral_tier1_price_admin
Else If Pages <= 60: Binding = spiral_tier2_price_admin
Else If Pages <= 90: Binding = spiral_tier3_price_admin
Else: Binding = spiral_tier3_price_admin + ceil((Pages-90)/20) × spiral_extra_price_admin

Total = Printing Cost + (Binding × Copies)
```

### For Custom Layouts:

**1/4 Layout:**
```
Sheets = ceil(Pages / 4)
Total = Sheets × Copies × custom_1_4_price_admin
```

**1/8 Layout:**
```
Sheets = ceil(Pages / 8)
Total = Sheets × Copies × custom_1_8_price_admin
```

**1/9 Layout:**
```
Sheets = ceil(Pages / 9)
Total = Sheets × Copies × custom_1_9_price_admin
```

## Troubleshooting

### If prices are not updating:

1. **Check server is running**: Look for "Watching for file changes with StatReloader"
2. **Clear browser cache**: Use hard refresh (Ctrl+Shift+R)
3. **Check console for errors**: Open DevTools Console tab
4. **Verify pricing in admin**: Make sure changes were saved
5. **Try incognito/private browsing**: This ensures no cache

### If calculations seem wrong:

1. Check the console log output to verify prices are loaded correctly
2. Upload a simple 10-page PDF and manually calculate:
   - B&W Single: 10 × 1 × ₹1.50 = ₹15.00
   - B&W Double: ceil(10/2) × 1 × ₹2.50 = ₹12.50
3. Compare with what the website shows

## Files Modified

1. `/Users/saitejakaki/Desktop/fastCopy/core/models.py` - Added double-sided price fields
2. `/Users/saitejakaki/Desktop/fastCopy/core/admin.py` - Updated admin interface
3. `/Users/saitejakaki/Desktop/fastCopy/core/views.py` - Added all pricing to context
4. `/Users/saitejakaki/Desktop/fastCopy/templates/core/services.html` - Updated JavaScript to use dynamic prices

All prices now come from the database - NO hardcoded values remain!
