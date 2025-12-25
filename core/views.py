import io, uuid, PyPDF2, base64, json, requests
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

from .models import Service, Order, UserProfile, CartItem

# --- 👤 1. AUTHENTICATION & PROFILE HUB ---

def register_view(request):
    if request.user.is_authenticated: return redirect('home')
    if request.method == "POST":
        full_name = request.POST.get('name', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        password = request.POST.get('password', '')
        if User.objects.filter(username=mobile).exists():
            messages.error(request, "Mobile number already registered.")
            return redirect('register')
        user = User.objects.create_user(username=mobile, password=password, first_name=full_name)
        UserProfile.objects.create(user=user, mobile=mobile)
        messages.success(request, "Account created! Please login.")
        return redirect('login')
    return render(request, 'core/register.html')

def login_view(request):
    if request.user.is_authenticated: return redirect('home')
    if request.method == "POST":
        mobile, pw = request.POST.get('mobile'), request.POST.get('password')
        user = authenticate(request, username=mobile, password=pw)
        if user:
            login(request, user)
            db_items = CartItem.objects.filter(user=user)
            request.session['cart'] = [{
                'service_name': i.service_name, 'total_price': str(i.total_price),
                'document_name': i.document_name, 'temp_path': i.temp_path,
                'temp_image_path': i.temp_image_path, 'copies': i.copies,
                'pages': i.pages, 'location': i.location, 'print_mode': i.print_mode,
                'side_type': i.side_type, 'custom_color_pages': i.custom_color_pages,
            } for i in db_items]
            request.session.modified = True
            return redirect('home')
        messages.error(request, "Invalid mobile number or password.")
    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required(login_url='login')
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    active_tracking = orders.exclude(status='Delivered').first()
    return render(request, 'core/profile.html', {'profile': profile, 'recent_bookings': orders[:5], 'tracking': active_tracking})

@login_required(login_url='login')
def edit_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        request.user.first_name = request.POST.get('name')
        request.user.save()
        profile.address = request.POST.get('address')
        profile.save()
        return redirect('profile')
    return render(request, 'core/edit_profile.html', {'profile': profile})

@login_required(login_url='login')
def history_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/history.html', {'orders': orders})

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
        page_count = int(request.POST.get('page_count', 1))
        ext = uploaded_file.name.split('.')[-1].lower()
        file_path = default_storage.save(f'temp/{uuid.uuid4()}_{uploaded_file.name}', ContentFile(uploaded_file.read()))
        item = {
            'service_name': request.POST.get('service_name'), 'total_price': request.POST.get('total_price_hidden'),
            'document_name': uploaded_file.name, 'temp_path': file_path if ext == 'pdf' else None,
            'temp_image_path': file_path if ext != 'pdf' else None, 'copies': int(request.POST.get('copies', 1)),
            'pages': page_count, 'location': request.POST.get('location'),
            'print_mode': request.POST.get('print_mode'), 'side_type': request.POST.get('side_type', 'single'),
            'custom_color_pages': request.POST.get('custom_color_pages', ''),
        }
        CartItem.objects.create(user=request.user, **item)
        cart = request.session.get('cart', []); cart.append(item); request.session['cart'] = cart; request.session.modified = True
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=401)

@login_required(login_url='login')
def cart_page(request):
    cart = request.session.get('cart', [])
    total_bill = sum(float(i.get('total_price', 0)) for i in cart)
    total_effective_pages = sum(int(i.get('pages', 0)) * int(i.get('copies', 1)) for i in cart)
    return render(request, 'core/cart.html', {
        'cart_items': cart, 'total_bill': round(total_bill, 2),
        'total_pages': total_effective_pages, 'min_required': 5,
        'remaining_pages': max(0, 5 - total_effective_pages),
    })

@login_required(login_url='login')
def remove_from_cart(request, item_id):
    cart = request.session.get('cart', [])
    if 0 <= item_id < len(cart):
        item = cart.pop(item_id)
        CartItem.objects.filter(user=request.user, document_name=item.get('document_name')).delete()
        request.session['cart'] = cart; request.session.modified = True
    return redirect('cart')

# --- 🚀 3. ORDER ENGINE ---

def process_successful_order(user, items_list, txn_id):
    last_order = None
    for item in items_list:
        saved_pdf, saved_img = None, None
        path = item.get('temp_path') or item.get('temp_image_path')
        if path and default_storage.exists(path):
            with default_storage.open(path) as f:
                content = ContentFile(f.read(), name=item['document_name'])
                if item.get('temp_path'): saved_pdf = content
                else: saved_img = content
        last_order = Order.objects.create(
            user=user, service_name=item['service_name'], total_price=float(item['total_price']),
            location=item['location'], print_mode=item['print_mode'], side_type=item['side_type'],
            copies=item['copies'], custom_color_pages=item['custom_color_pages'],
            transaction_id=txn_id, document=saved_pdf, image_upload=saved_img,
            payment_status="Success", status="Pending"
        )
    return last_order

@login_required(login_url='login')
def order_all(request):
    cart = request.session.get('cart', [])
    if not cart: return redirect('cart')
    total_effective = sum(int(i.get('pages', 0)) * int(i.get('copies', 1)) for i in cart)
    if total_effective < 5:
        messages.error(request, f"Minimum 5 total pages required. You have {total_effective}.")
        return redirect('cart')
    if 'direct_item' in request.session: del request.session['direct_item']
    request.session['pending_batch_id'] = f"TXN_{uuid.uuid4().hex[:10].upper()}"
    return redirect('cart_checkout_summary')

@login_required(login_url='login')
def process_direct_order(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get('document')
        if not uploaded_file: return JsonResponse({'success': False})
        ext = uploaded_file.name.split('.')[-1].lower()
        file_path = default_storage.save(f'temp/direct_{uuid.uuid4()}_{uploaded_file.name}', ContentFile(uploaded_file.read()))
        direct_item = {
            'service_name': request.POST.get('service_name'), 'total_price': request.POST.get('total_price_hidden'),
            'document_name': uploaded_file.name, 'temp_path': file_path if ext == 'pdf' else None,
            'temp_image_path': file_path if ext != 'pdf' else None, 'copies': int(request.POST.get('copies', 1)),
            'pages': int(request.POST.get('page_count', 1)), 'location': request.POST.get('location'),
            'print_mode': request.POST.get('print_mode'), 'side_type': request.POST.get('side_type', 'single'),
            'custom_color_pages': request.POST.get('custom_color_pages', ''),
        }
        request.session['direct_item'] = direct_item
        request.session['pending_batch_id'] = f"DIR_{uuid.uuid4().hex[:10].upper()}"
        request.session.modified = True
        return JsonResponse({'success': True, 'redirect_url': '/checkout/summary/'})
    return JsonResponse({'success': False})

@login_required(login_url='login')
def cart_checkout_summary(request):
    direct_item = request.session.get('direct_item')
    items = [direct_item] if direct_item else request.session.get('cart', [])
    if not items: return redirect('services')
    grand_total = sum(float(i.get('total_price', 0)) for i in items)
    return render(request, 'core/checkout.html', {'cart_items': items, 'grand_total': grand_total, 'items_count': len(items)})

@login_required(login_url='login')
def order_now(request): return redirect('services')

# --- 💳 4. PAYMENTS ---

@login_required(login_url='login')
def initiate_payment(request):
    return redirect('bypass_payment') # Bypass for testing

@login_required(login_url='login')
def bypass_payment(request):
    txn_id = request.session.get('pending_batch_id')
    direct_item = request.session.get('direct_item')
    if direct_item:
        last_o = process_successful_order(request.user, [direct_item], txn_id)
        del request.session['direct_item']
    else:
        cart = request.session.get('cart', [])
        if not cart: return redirect('cart')
        last_o = process_successful_order(request.user, cart, txn_id)
        request.session['cart'] = []; CartItem.objects.filter(user=request.user).delete()
    request.session.modified = True
    return render(request, 'core/payment_success.html', {'order': last_o})

@csrf_exempt
def payment_callback(request): return redirect('home')

# --- 🌐 5. STATIC ---
def home(request): return render(request, 'core/index.html', {'services': Service.objects.all()[:3]})
def services_page(request): return render(request, 'core/services.html', {'services': Service.objects.all()})
def about(request): return render(request, 'core/about.html')
def contact(request): return render(request, 'core/contact.html')
def privacy_policy(request): return render(request, 'core/privacy_policy.html')
def terms_conditions(request): return render(request, 'core/terms_conditions.html')