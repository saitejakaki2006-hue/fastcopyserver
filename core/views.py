from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Service, Profile

# 1. Home View
def home(request):
    services = Service.objects.all()
    return render(request, 'core/index.html', {'services': services})

# 2. Services View
def services_page(request):
    services = Service.objects.all()
    return render(request, 'core/services.html', {'services': services})

# 3. About Us View (Fixed the missing attribute)
def about(request):
    return render(request, 'core/about.html')

# 4. Contact View
def contact(request):
    return render(request, 'core/contact.html')

# 5. Cart View
def cart(request):
    return render(request, 'core/cart.html')

# 6. Registration Logic
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

        user = User.objects.create_user(username=mobile, email=email, password=pw, first_name=name)
        Profile.objects.create(user=user, mobile=mobile, address=address)
        
        messages.success(request, "Account created! Please login.")
        return redirect('login')
    return render(request, 'core/register.html')

# 7. Login Logic
def login_view(request):
    if request.method == "POST":
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        user = authenticate(request, username=mobile, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        messages.error(request, "Invalid mobile or password.")
    return render(request, 'core/login.html')

# 8. Profile View
def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    profile = Profile.objects.get(user=request.user)
    return render(request, 'core/profile.html', {'profile': profile})

# 9. Logout Logic
def logout_view(request):
    logout(request)
    return redirect('home')