from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Service, Profile, Order

def home(request):
    services = Service.objects.all()
    return render(request, 'core/index.html', {'services': services})

def services_page(request):
    services = Service.objects.all()
    return render(request, 'core/services.html', {'services': services})

def about(request): return render(request, 'core/about.html')
def contact(request): return render(request, 'core/contact.html')
def cart(request): return render(request, 'core/cart.html')

def register_view(request):
    if request.method == "POST":
        name = request.POST.get('username')
        mobile = request.POST.get('mobile')
        email = request.POST.get('email')
        pw = request.POST.get('password')
        address = request.POST.get('address')
        
        if User.objects.filter(username=mobile).exists():
            messages.error(request, "Mobile number already registered!")
            return redirect('register')
        
        # Create User and the linked Profile simultaneously
        user = User.objects.create_user(username=mobile, email=email, password=pw, first_name=name)
        Profile.objects.create(user=user, mobile=mobile, address=address)
        messages.success(request, "Registration successful! Please login.")
        return redirect('login')
    return render(request, 'core/register.html')

def login_view(request):
    if request.method == "POST":
        mobile = request.POST.get('mobile')
        pw = request.POST.get('password')
        user = authenticate(request, username=mobile, password=pw)
        if user:
            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, "Invalid credentials.")
    return render(request, 'core/login.html')

def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    profile = Profile.objects.get(user=request.user)
    # Fetch recent orders (history up to 3)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:3]
    return render(request, 'core/profile.html', {'profile': profile, 'orders': orders})

def logout_view(request):
    logout(request)
    return redirect('home')