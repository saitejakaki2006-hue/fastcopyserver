from django.contrib import admin
from django.db.models import Sum, Count
from django.utils.html import format_html, mark_safe
from django.urls import reverse
from .models import Service, Order, UserProfile, CartItem

# --- 🛠️ 1. CUSTOM ADMIN SITE SETUP ---
class FastCopyAdminSite(admin.AdminSite):
    site_header = "FastCopy Admin"
    site_title = "FastCopy Portal"
    index_title = "Operations Hub"

# Create the instance that URLs will point to
admin_site = FastCopyAdminSite(name='fastcopy_admin')

# --- 🛒 2. CART ITEM ADMIN (Monitor Active/Abandoned Carts) ---
@admin.register(CartItem, site=admin_site)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'service_name', 'total_price', 'pages', 'copies', 'created_at')
    list_filter = ('service_name', 'created_at', 'location')
    search_fields = ('user__username', 'service_name', 'document_name')
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        return False  # Carts are managed by users on the frontend

# --- 📄 3. SERVICE ADMIN ---
@admin.register(Service, site=admin_site)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price')

# --- 👤 4. USER PROFILE ADMIN ---
@admin.register(UserProfile, site=admin_site)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_id_link', 'full_name', 'mobile', 'email', 'user_type', 'date_joined')
    search_fields = ('fc_user_id', 'user__username', 'mobile', 'user__email')
    list_filter = ('user__is_staff', ('user__date_joined', admin.DateFieldListFilter))
    readonly_fields = ('display_fc_id', 'user_type', 'full_name', 'mobile', 'email', 'address_display', 'date_joined')
    exclude = ('user', 'fc_user_id', 'address')
    ordering = ('-id',)

    fieldsets = (
        ('ID Info', {'fields': ('display_fc_id', 'user_type')}),
        ('Personal Info', {'fields': ('full_name', 'mobile', 'email', 'address_display')}),
        ('System Metadata', {'fields': ('date_joined',)}),
    )

    def user_id_link(self, obj):
        url = reverse('fastcopy_admin:core_userprofile_change', args=[obj.id])
        return format_html('<a href="{}" style="font-weight:bold;color:#2563eb">{}</a>', url, obj.fc_user_id or "PENDING")
    
    def display_fc_id(self, obj): return obj.fc_user_id
    def full_name(self, obj): return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
    def email(self, obj): return obj.user.email or "N/A"
    def user_type(self, obj): return "Admin User" if obj.user.is_staff else "Normal User"
    def date_joined(self, obj): return obj.user.date_joined.strftime("%d %b %Y | %I:%M %p")
    def address_display(self, obj): return obj.address or "No address provided"
    def has_add_permission(self, request): return False

# --- 🚀 5. ORDER ADMIN (View Only in Table, Edit in Detail) ---
@admin.register(Order, site=admin_site)
class OrderAdmin(admin.ModelAdmin):
    # list_editable is REMOVED to ensure data can only be updated by clicking the Order ID.
    list_display = (
        'order_id_link', 
        'user_name', 
        'mobile_number',      # Replaced Batch ID
        'service_name', 
        'display_file_thumbnail', 
        'printing_type_display', 
        'price_display', 
        'status_badge',       # Using badge for better visualization (non-editable)
        'created_at'
    )
    
    list_filter = ('status', 'payment_status', 'service_name', 'location', ('created_at', admin.DateFieldListFilter))
    search_fields = ('order_id', 'transaction_id', 'user__first_name', 'user__username')
    readonly_fields = ('order_id', 'created_at', 'user_name', 'user_email', 'mobile_number', 'display_full_file_preview', 'printing_type_display')
    
    fieldsets = (
        ('User Information', {'fields': ('user', 'location', 'user_name', 'mobile_number', 'user_email')}),
        ('Printing Specs', {'fields': ('service_name', 'print_mode', 'side_type', 'copies', 'custom_color_pages')}),
        ('File Management', {'fields': ('document', 'image_upload', 'display_full_file_preview')}),
        ('Financials', {'fields': ('total_price', 'transaction_id', 'payment_status')}),
        ('Workflow', {'fields': ('status', 'order_id', 'created_at')}),
    )

    def order_id_link(self, obj):
        url = reverse('fastcopy_admin:core_order_change', args=[obj.id])
        return format_html('<a href="{}" style="font-weight:bold;color:#2563eb">{}</a>', url, obj.order_id or f"ORD-{obj.id}")

    def display_file_thumbnail(self, obj):
        if obj.image_upload:
            return format_html('<a href="{}" target="_blank"><img src="{}" style="width:35px;height:35px;object-fit:cover;border-radius:4px;"/></a>', obj.image_upload.url, obj.image_upload.url)
        elif obj.document:
            return format_html('<a href="{}" target="_blank" style="background:#2563eb;color:#fff;padding:2px 6px;border-radius:4px;font-size:10px;text-decoration:none">📂 PDF</a>', obj.document.url)
        return mark_safe('<span style="color:#94a3b8">No File</span>')

    def display_full_file_preview(self, obj):
        html = ""
        if obj.image_upload:
            html += format_html('<div style="margin-bottom:10px;"><img src="{}" style="max-width:250px;border-radius:8px;"/></div>', obj.image_upload.url)
        if obj.document:
            html += format_html('<a href="{}" target="_blank" style="background:#1e293b;color:#fff;padding:8px 12px;border-radius:5px;text-decoration:none;display:inline-block;">Open Full PDF</a>', obj.document.url)
        return mark_safe(html) if html else "No file uploaded"

    def printing_type_display(self, obj):
        mode = str(getattr(obj, 'print_mode', 'bw')).lower()
        pages = str(getattr(obj, 'custom_color_pages', '') or '')
        if 'custom' in mode and pages:
            return format_html('<b style="color:#fd7e14">CUSTOM ({})</b>', pages)
        return mode.upper()
    printing_type_display.short_description = "Mode"

    def user_name(self, obj): return obj.user.first_name
    def user_email(self, obj): return obj.user.email
    
    def mobile_number(self, obj): 
        return obj.user.username 
    mobile_number.short_description = "Mobile"

    def price_display(self, obj): 
        return mark_safe(f'<b style="color:#2563eb">₹{float(obj.total_price or 0):,.2f}</b>')

    def status_badge(self, obj):
        colors = {
            'Pending': '#be123c', # Red
            'Ready': '#ca8a04',   # Yellow
            'Delivered': '#15803d', # Green
            'Rejected': '#64748b'  # Grey
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="background-color:{}; color:white; padding:3px 10px; border-radius:12px; font-weight:bold; font-size:10px;">{}</span>',
            color, obj.status
        )
    status_badge.short_description = "Status"

    def changelist_view(self, request, extra_context=None):
        res = super().changelist_view(request, extra_context)
        try:
            qs = res.context_data['cl'].get_queryset(request).aggregate(total=Sum('total_price'), cnt=Count('id'))
            res.context_data.update({'summary_total': float(qs['total'] or 0), 'summary_count': qs['cnt']})
        except: pass
        return res