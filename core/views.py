import io, uuid, PyPDF2, base64, json, requests, hashlib, time
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from .models import Service, Order, UserProfile, CartItem

# --- 🚀 0. CORE LOGIC ENGINES (Success/Failure/Helper) ---

def handle_failed_order(user, items_list, txn_id, reason="Payment Failed"):
    """
    DATABASE UPDATE LOGIC:
    Targets specific records by txn_id and document name to update statuses.
    Ensures 'Failed' and 'Cancelled' reflect in the database and user history.
    """
    if not txn_id:
        return None

    with transaction.atomic():
        last_order = None
        for item in items_list:
            if not item: 
                continue
                
            # Update the existing Pending record or create a new Cancelled one if not found
            last_order, created = Order.objects.update_or_create(
                transaction_id=txn_id,
                document=item.get('document_name'),
                defaults={
                    'user': user,
                    'service_name': item.get('service_name'),
                    'total_price': float(item.get('total_price', 0)),
                    'location': item.get('location'),
                    'print_mode': item.get('print_mode'),
                    'side_type': item.get('side_type'),
                    'copies': item.get('copies'),
                    'pages': item.get('pages', 1),
                    'custom_color_pages': item.get('custom_color_pages'),
                    'payment_status': "Failed", # <-- Permanent DB Status
                    'status': "Cancelled"       # <-- Permanent DB Status
                }
            )
            
            # [STRICT] Restore to DB Cart if it was a Direct Order so user doesn't lose progress
            if txn_id.startswith("DIR"):
                CartItem.objects.get_or_create(
                    user=user,
                    document_name=item.get('document_name'),
                    defaults={
                        'service_name': item.get('service_name'),
                        'total_price': item.get('total_price'),
                        'temp_path': item.get('temp_path'),
                        'temp_image_path': item.get('temp_image_path'),
                        'copies': item.get('copies'),
                        'pages': item.get('pages', 1),
                        'location': item.get('location'),
                        'print_mode': item.get('print_mode'),
                        'side_type': item.get('side_type'),
                        'custom_color_pages': item.get('custom_color_pages')
                    }
                )
        return last_order

def process_successful_order(user, items_list, txn_id):
    """
    DATABASE UPDATE LOGIC:
    Updates records to 'Success' and 'Pending' (for admin processing).
    """
    with transaction.atomic():
        for item in items_list:
            if not item: continue
                
            saved_pdf, saved_img = None, None
            path = item.get('temp_path') or item.get('temp_image_path')
            
            if path and default_storage.exists(path):
                with default_storage.open(path) as f:
                    content = ContentFile(f.read(), name=item['document_name'])
                    if item.get('temp_path'): saved_pdf = content
                    else: saved_img = content
            
            Order.objects.update_or_create(
                transaction_id=txn_id,
                document=item.get('document_name'),
                defaults={
                    'user': user,
                    'service_name': item['service_name'],
                    'total_price': float(item['total_price']),
                    'location': item['location'],
                    'print_mode': item['print_mode'],
                    'side_type': item['side_type'],
                    'copies': item['copies'],
                    'custom_color_pages': item.get('custom_color_pages', ''),
                    'payment_status': "Success",
                    'status': "Pending",
                    'document': saved_pdf,
                    'image_upload': saved_img,
                }
            )
            
            if item.get('temp_path') and default_storage.exists(item['temp_path']):
                default_storage.delete(item['temp_path'])
            if item.get('temp_image_path') and default_storage.exists(item['temp_image_path']):
                default_storage.delete(item['temp_image_path'])

# --- 👤 1. AUTHENTICATION & PROFILE ---

def register_view(request):
    if request.user.is_authenticated: return redirect('home')
    if request.method == "POST":
        full_name = request.POST.get('name', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        address = request.POST.get('address', '').strip()

        if User.objects.filter(username=mobile).exists():
            messages.error(request, "Mobile number already registered.")
            return redirect('register')

        user = User.objects.create_user(username=mobile, password=password, first_name=full_name, email=email)
        UserProfile.objects.create(user=user, mobile=mobile, address=address)
        messages.success(request, "Account created successfully! Please login.")
        return redirect('login')
    return render(request, 'core/register.html')

def login_view(request):
    if request.user.is_authenticated: return redirect('home')
    if request.method == "POST":
        mobile, pw = request.POST.get('mobile'), request.POST.get('password')
        user = authenticate(request, username=mobile, password=pw)
        if user:
            login(request, user)
            return redirect('cart') 
        messages.error(request, "Invalid login credentials.")
    return render(request, 'core/login.html')

def logout_view(request):
    logout(request); return redirect('home')

@login_required(login_url='login')
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {'profile': profile, 'user_name': request.user.first_name, 'user_email': request.user.email, 'recent_bookings': orders[:5]}
    return render(request, 'core/profile.html', context)

@login_required(login_url='login')
def edit_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        request.user.first_name = request.POST.get('name')
        request.user.email = request.POST.get('email')
        request.user.username = request.POST.get('mobile') 
        request.user.save()
        profile.mobile = request.POST.get('mobile')
        profile.address = request.POST.get('address')
        profile.save()
        messages.success(request, "Updated successfully!")
        return redirect('profile')
    return render(request, 'core/edit_profile.html', {'profile': profile})

@login_required(login_url='login')
def history_view(request):
    all_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/history.html', {'orders': all_orders})

# --- 🛒 2. CART & PDF ENGINE ---

def calculate_pages(request):
    if request.method == 'POST' and request.FILES.get('document'):
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(request.FILES['document'].read()))
            return JsonResponse({'success': True, 'pages': len(pdf_reader.pages)})
        except: return JsonResponse({'success': False})
    return JsonResponse({'success': False})

def add_to_cart(request):
    if request.method == "POST" and request.user.is_authenticated:
        uploaded_file = request.FILES.get('document')
        if not uploaded_file: return JsonResponse({'success': False})
        file_path = default_storage.save(f'temp/{uuid.uuid4()}_{uploaded_file.name}', ContentFile(uploaded_file.read()))
        service_name = request.POST.get('service_name')
        print_mode = request.POST.get('print_mode', 'B&W')
        item = {
            'service_name': service_name, 'total_price': request.POST.get('total_price_hidden'),
            'document_name': uploaded_file.name, 'temp_path': file_path if uploaded_file.name.endswith('.pdf') else None,
            'temp_image_path': file_path if not uploaded_file.name.endswith('.pdf') else None, 
            'copies': int(request.POST.get('copies', 1)), 'pages': int(request.POST.get('page_count', 1)), 
            'location': request.POST.get('location'), 'print_mode': print_mode, 
            'side_type': request.POST.get('side_type', 'single'), 'custom_color_pages': request.POST.get('custom_color_pages', ''),
        }
        CartItem.objects.create(user=request.user, **item)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=401)

@login_required(login_url='login')
def cart_page(request):
    db_items = CartItem.objects.filter(user=request.user).order_by('-created_at')
    cart_list = []
    for i in db_items:
        cart_list.append({
            'id': i.id,
            'service_name': i.service_name, 'total_price': str(i.total_price), 'document_name': i.document_name,
            'temp_path': i.temp_path, 'temp_image_path': i.temp_image_path, 'copies': i.copies, 'pages': i.pages,
            'location': i.location, 'print_mode': i.print_mode, 'side_type': i.side_type, 'custom_color_pages': i.custom_color_pages,
        })
    request.session['cart'] = cart_list
    request.session.modified = True
    total_bill = sum(float(i.total_price) for i in db_items)
    total_eff_pages = sum(int(i.pages) * int(i.copies) for i in db_items)
    context = {'cart_items': cart_list, 'total_bill': round(total_bill, 2), 'total_pages': total_eff_pages, 'min_required': 5}
    return render(request, 'core/cart.html', context)

@login_required(login_url='login')
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    name = item.service_name
    item.delete()
    messages.success(request, f"Removed '{name}' from your cart.")
    return redirect('cart')

# --- 🚀 3. ORDER & CHECKOUT FLOW ---

@login_required(login_url='login')
def order_all(request):
    cart = CartItem.objects.filter(user=request.user)
    if not cart.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart')
    if 'direct_item' in request.session: del request.session['direct_item']
    request.session['pending_batch_id'] = f"TXN_{uuid.uuid4().hex[:10].upper()}"
    request.session.modified = True
    return redirect('cart_checkout_summary')

@login_required(login_url='login')
def order_now(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get('document')
        if not uploaded_file: return redirect('services')
        file_path = default_storage.save(f'temp/direct_{uuid.uuid4()}_{uploaded_file.name}', ContentFile(uploaded_file.read()))
        request.session['direct_item'] = {
            'service_name': request.POST.get('service_name'), 'total_price': request.POST.get('total_price_hidden'),
            'document_name': uploaded_file.name, 'temp_path': file_path if uploaded_file.name.endswith('.pdf') else None,
            'temp_image_path': file_path if not uploaded_file.name.endswith('.pdf') else None, 
            'copies': int(request.POST.get('copies', 1)), 'pages': int(request.POST.get('page_count', 1)), 
            'location': request.POST.get('location'), 'print_mode': request.POST.get('print_mode', 'B&W'), 
            'side_type': request.POST.get('side_type', 'single'), 'custom_color_pages': request.POST.get('custom_color_pages', ''),
        }
        request.session['pending_batch_id'] = f"DIR_{uuid.uuid4().hex[:10].upper()}"
        request.session.modified = True
        return redirect('cart_checkout_summary')
    return redirect('services')

@login_required(login_url='login')
def process_direct_order(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get('document')
        if not uploaded_file: return JsonResponse({'success': False})
        file_path = default_storage.save(f'temp/direct_{uuid.uuid4()}', ContentFile(uploaded_file.read()))
        direct_item = {
            'service_name': request.POST.get('service_name'), 'total_price': request.POST.get('total_price_hidden'),
            'document_name': uploaded_file.name, 'temp_path': file_path if uploaded_file.name.endswith('.pdf') else None,
            'temp_image_path': file_path if not uploaded_file.name.endswith('.pdf') else None, 
            'copies': int(request.POST.get('copies', 1)), 'pages': int(request.POST.get('page_count', 1)), 
            'location': request.POST.get('location'), 'print_mode': request.POST.get('print_mode', 'B&W'), 
            'side_type': request.POST.get('side_type', 'single'), 'custom_color_pages': request.POST.get('custom_color_pages', ''),
        }
        request.session['direct_item'] = direct_item
        request.session['pending_batch_id'] = f"DIR_{uuid.uuid4().hex[:10].upper()}"
        request.session.modified = True
        return JsonResponse({'success': True, 'redirect_url': '/checkout/summary/'})
    return JsonResponse({'success': False})

@login_required(login_url='login')
def cart_checkout_summary(request):
    batch_txn_id = request.session.get('pending_batch_id', '')
    if batch_txn_id.startswith("DIR"):
        items = [request.session.get('direct_item')] if request.session.get('direct_item') else []
    else:
        items = request.session.get('cart', [])
    if not items or None in items: return redirect('services')
    grand_total = sum(float(i.get('total_price', 0)) for i in items)
    return render(request, 'core/checkout.html', {'cart_items': items, 'grand_total': round(grand_total, 2), 'items_count': len(items)})

# --- 💳 4. CASHFREE GATEWAY INTEGRATION ---

@login_required(login_url='login')
def initiate_payment(request):
    batch_txn_id = request.session.get('pending_batch_id')
    direct_item = request.session.get('direct_item')
    cart_items = request.session.get('cart', [])

    if not batch_txn_id: return redirect('cart')

    if batch_txn_id.startswith("DIR"):
        items_to_process = [direct_item] if direct_item else []
    else:
        items_to_process = cart_items

    if not items_to_process: return redirect('cart')

    unique_order_id = f"{batch_txn_id}_{int(time.time())}"
    with transaction.atomic():
        for item in items_to_process:
            Order.objects.update_or_create(
                transaction_id=unique_order_id, document=item.get('document_name'),
                defaults={'user': request.user, 'service_name': item.get('service_name'), 'total_price': float(item.get('total_price', 0)), 
                          'location': item.get('location'), 'print_mode': item.get('print_mode'), 'side_type': item.get('side_type'),
                          'copies': item.get('copies'), 'pages': item.get('pages', 1), 'custom_color_pages': item.get('custom_color_pages', ''), 
                          'payment_status': "Pending", 'status': "Pending"}
            )

    grand_total = sum(float(i.get('total_price', 0)) for i in items_to_process)
    callback_url = f"{request.scheme}://{request.get_host()}/payment/callback/"
    user_mobile = request.user.profile.mobile if hasattr(request.user, 'profile') else "9999999999"
    if not user_mobile.startswith('91'): user_mobile = f"91{user_mobile}"

    payload = {
        "order_id": unique_order_id, "order_amount": float(grand_total), "order_currency": "INR",
        "customer_details": {"customer_id": f"CUST_{request.user.id}", "customer_name": request.user.username, "customer_email": request.user.email or "test@fastcopy.in", "customer_phone": user_mobile},
        "order_meta": {"return_url": callback_url, "notify_url": callback_url}
    }
    headers = {"Content-Type": "application/json", "x-api-version": settings.CASHFREE_API_VERSION, "x-client-id": settings.CASHFREE_APP_ID, "x-client-secret": settings.CASHFREE_SECRET_KEY}
    
    try:
        response = requests.post(f"{settings.CASHFREE_API_URL}/orders", json=payload, headers=headers)
        res_json = response.json()
        if response.status_code == 200 and res_json.get('payment_session_id'):
            request.session['cashfree_payment_session_id'] = res_json.get('payment_session_id')
            request.session['cashfree_order_id'] = unique_order_id
            request.session.modified = True
            return redirect('cashfree_checkout')
        return redirect('cart')
    except: return redirect('cart')

@csrf_exempt
def payment_callback(request):
    """STRICT CALLBACK: Updates DB to Success or Failed/Cancelled."""
    order_id = (request.GET.get('order_id') or 
                request.GET.get('orderId') or 
                request.session.get('cashfree_order_id'))

    if not order_id:
        messages.error(request, "Payment session not found. Returning to cart.")
        return redirect('cart')
    
    txn_id = order_id
    is_direct = txn_id.startswith("DIR")
    direct_item = request.session.get('direct_item')
    items_involved = [direct_item] if is_direct else request.session.get('cart', [])

    headers = {"Content-Type": "application/json", "x-api-version": settings.CASHFREE_API_VERSION, "x-client-id": settings.CASHFREE_APP_ID, "x-client-secret": settings.CASHFREE_SECRET_KEY}
    
    try:
        response = requests.get(f"{settings.CASHFREE_API_URL}/orders/{order_id}", headers=headers)
        order_status = response.json().get('order_status', 'FAILED')
    except: order_status = 'FAILED'

    if order_status == 'PAID':
        process_successful_order(request.user, items_involved, txn_id)
        if is_direct: 
            CartItem.objects.filter(user=request.user, document_name=direct_item.get('document_name')).delete()
            if 'direct_item' in request.session: del request.session['direct_item']
        else: 
            CartItem.objects.filter(user=request.user).delete()
            request.session['cart'] = []
        messages.success(request, "Payment successful! Order placed.")
        return redirect('history')
    else:
        # LOG FAILED PAYMENT TO DATABASE
        handle_failed_order(request.user, items_involved, txn_id)
        
        # Restore session context for retry
        if is_direct and direct_item:
            db_cart = CartItem.objects.filter(user=request.user)
            request.session['cart'] = [{'id': i.id, 'service_name': i.service_name, 'total_price': str(i.total_price), 'document_name': i.document_name} for i in db_cart]
            if 'direct_item' in request.session: del request.session['direct_item']

        messages.warning(request, "Payment was canceled or failed. Items are safe in your cart.")
        return redirect('cart')

@login_required(login_url='login')
def cashfree_checkout(request):
    context = {'payment_session_id': request.session.get('cashfree_payment_session_id'), 'cashfree_env': 'sandbox'}
    return render(request, 'core/cashfree_checkout.html', context)

# --- 🌐 5. STATIC PAGES ---
def home(request): return render(request, 'core/index.html', {'services': Service.objects.all()[:3]})
def services_page(request): return render(request, 'core/services.html', {'services': Service.objects.all()})
def about(request): return render(request, 'core/about.html')
def contact(request): return render(request, 'core/contact.html')
def privacy_policy(request): return render(request, 'core/privacy_policy.html')
def terms_conditions(request): return render(request, 'core/terms_conditions.html')