from django.urls import path
from . import views

urlpatterns = [
    # --- 🏠 Home & Static ---
    path('', views.home, name='home'),
    path('services/', views.services_page, name='services'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms_conditions, name='terms_conditions'),

    # --- 👤 Auth & Profile ---
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('history/', views.history_view, name='history'),

    # --- 🛒 Cart Logic ---
    path('cart/', views.cart_page, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('calculate-pages/', views.calculate_pages, name='calculate_pages'),

    # --- 🚀 Checkout & Orders ---
    path('order/now/', views.order_now, name='order_now'), # Standard Form Post
    path('order/direct/', views.process_direct_order, name='process_direct_order'), # Ajax Post
    path('order/process-all/', views.order_all, name='order_all'),
    path('checkout/summary/', views.cart_checkout_summary, name='cart_checkout_summary'),

    # --- 💳 Payments ---
    path('payment/initiate/', views.initiate_payment, name='initiate_payment'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    path('payment/bypass-test/', views.bypass_payment, name='bypass_payment'),
]