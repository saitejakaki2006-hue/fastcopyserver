import PyPDF2
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service, Order, UserProfile

# --- NAVIGATION ---
def home(request):
    services = Service.objects.all()[:3]
    return render(request, 'core/index.html', {'services': services})

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    return render(request, 'core/contact.html')

def services_page(request):
    services = Service.objects.all()
    first_service = services.first()
    return render(request, 'core/services.html', {
        'services': services, 
        'first_service': first_service
    })
    
# --- AUTHENTICATION ---
def register_view(request):
    if request.method == "POST":
        mobile = request.POST.get('mobile')
        pw = request.POST.get('password')
        if User.objects.filter(username=mobile).exists():
            messages.error(request, "Mobile already registered!")
            return redirect('register')
        user = User.objects.create_user(username=mobile, password=pw, first_name=request.POST.get('name'))
        UserProfile.objects.create(user=user, mobile=mobile, address=request.POST.get('address'))
        return redirect('login')
    return render(request, 'core/register.html')

def login_view(request):
    if request.method == "POST":
        mobile = request.POST.get('mobile')
        pw = request.POST.get('password')
        user = authenticate(request, username=mobile, password=pw)
        if user:
            login(request, user)
            return redirect('home')
        messages.error(request, "Invalid Credentials")
    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

# --- PROFILE & HISTORY ---
@login_required(login_url='login')
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'mobile': request.user.username, 'address': 'Update address'}
    )
    all_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/profile.html', {
        'profile': profile,
        'recent_bookings': all_orders[:3],
        'tracking': all_orders.exclude(status='Delivered').first(),
    })

@login_required(login_url='login')
def edit_profile(request):
    if request.method == "POST":
        user = request.user
        profile = user.userprofile
        user.first_name = request.POST.get('name')
        user.save()
        profile.mobile = request.POST.get('mobile')
        profile.address = request.POST.get('address')
        profile.save()
        messages.success(request, "Profile updated!")
    return redirect('profile')

@login_required(login_url='login')
def history_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'core/history.html', {'orders': orders, 'profile': profile})

# --- CART & ORDERING ---
@login_required(login_url='login')
def cart_page(request):
    # Fetching items from session (assuming cart is stored in session)
    cart_items = request.session.get('cart', [])
    
    # THE FIX: Use float() instead of int() to handle strings like '525.00'
    total_bill = sum(float(item.get('total_price', 0)) for item in cart_items)
    
    # Optional: If you want the total_bill to be an integer at the end
    # total_bill = int(total_bill) 

    context = {
        'cart_items': cart_items,
        'total_bill': total_bill,
    }
    return render(request, 'core/cart.html', context)
def remove_from_cart(request, item_id):
    cart_list = request.session.get('cart', [])
    if 0 <= item_id < len(cart_list):
        cart_list.pop(item_id)
        request.session['cart'] = cart_list
        request.session.modified = True
    return redirect('cart')

def add_to_cart(request):
    if request.method == "POST":
        item = {'service_name': request.POST.get('service_name'), 'total_price': request.POST.get('total_price_hidden')}
        
        cart = request.session.get('cart', [])
        cart.append(item)
        request.session['cart'] = cart
        request.session.modified = True
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})



@login_required
def order_now(request):
    if request.method == "POST":
        # ... your existing logic to handle the order creation ...
        # Ensure total_price is converted to int to match database expectation
        total_price = int(request.POST.get('total_price_hidden', 0))
        
        # ... logic to save order ...
        
        # FINAL REDIRECT TO HOME PAGE
        return redirect('home') 
    return redirect('services')


@login_required(login_url='login')
def order_all(request):
    if request.method == "POST":
        cart_items = request.session.get('cart', [])
        
        if not cart_items:
            return redirect('cart')

        for item in cart_items:
            # The conversion to float fixes the ValueError
            price_as_number = float(item.get('total_price', 0))
            
            Order.objects.create(
                user=request.user,
                service_name=item.get('service_name', 'Printing Service'),
                total_price=price_as_number,
                status='Pending'
            )

        # Clear the cart after orders are created
        request.session['cart'] = []
        return redirect('home') # Or a success page
        
    return redirect('cart')

def calculate_pages(request):
    if request.method == 'POST' and request.FILES.get('document'):
        try:
            pdf = PyPDF2.PdfReader(request.FILES['document'])
            return JsonResponse({'success': True, 'pages': len(pdf.pages)})
        except:
            return JsonResponse({'success': False})
    return JsonResponse({'success': False})