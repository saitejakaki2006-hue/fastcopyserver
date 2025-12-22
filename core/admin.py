from django.contrib import admin
from django.db.models import Sum, Count
from django.utils.html import format_html
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse, path
from django.template.response import TemplateResponse
from datetime import timedelta
from .models import Service, Order, UserProfile

# --- 1. ADMIN SITE GLOBAL CONFIGURATION ---
admin.site.site_header = "FastCopy | Management Command Center"
admin.site.site_title = "FastCopy Admin Portal"
admin.site.index_title = "Operational Control & Revenue Analytics"

# --- 2. ACCOUNTING VIEW & REDIRECT LOGIC ---
def get_accounting_stats(start_date, end_date):
    """Calculates business metrics for the dashboard."""
    orders = Order.objects.filter(created_at__date__range=[start_date, end_date])
    stats = orders.aggregate(
        total_orders=Count('id'),
        total_revenue=Sum('total_price'),
    )
    return {
        'total_orders': stats['total_orders'] or 0,
        'total_revenue': stats['total_revenue'] or 0,
        'delivered_count': orders.filter(status__iexact='Delivered').count(),
        'pending_count': orders.filter(status__iexact='Pending').count(),
        'start': start_date,
        'end': end_date
    }

def accounting_view(request):
    """The view logic for the Business Accounting dashboard."""
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    
    context = admin.site.each_context(request)
    context.update({
        'summary': {
            'today': get_accounting_stats(today, today),
            'yesterday': get_accounting_stats(today - timedelta(days=1), today - timedelta(days=1)),
            'this_week': get_accounting_stats(start_of_week, today),
            'this_month': get_accounting_stats(today.replace(day=1), today),
        },
        'from_date': request.GET.get('from'),
        'to_date': request.GET.get('to'),
        'title': "Business Accounting",
    })
    
    if context['from_date'] and context['to_date']:
        context['custom_stats'] = get_accounting_stats(context['from_date'], context['to_date'])
        
    return TemplateResponse(request, "admin/accounting.html", context)

# --- 3. INJECTING CUSTOM URLS INTO DEFAULT ADMIN ---
original_get_urls = admin.site.get_urls

def get_urls_with_accounting():
    urls = original_get_urls()
    custom_urls = [
        path('accounting/', admin.site.admin_view(accounting_view), name="accounting"),
    ]
    return custom_urls + urls

admin.site.get_urls = get_urls_with_accounting


# --- 4. MODEL REGISTRATIONS ---

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'mobile', 'address_short')
    search_fields = ('user__username', 'mobile', 'user__first_name')
    
    def address_short(self, obj):
        return obj.address[:30] + "..." if len(obj.address) > 30 else obj.address
    address_short.short_description = "Campus Address"

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price_display', 'description_short')
    list_display_links = ('base_price_display',)
    list_editable = ('name',)
    
    def base_price_display(self, obj):
        return format_html('<b style="color: #2563eb;">₹{}</b>', obj.base_price)
    base_price_display.short_description = "Rate / Unit"

    def description_short(self, obj):
        return obj.description[:50] + "..." if obj.description else "No description"
    description_short.short_description = "Description"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'student_info', 'service_name', 'price_tag', 'tracking_status', 'created_at')
    # Use DateFieldListFilter to enable the "Today" selection in sidebar
    list_filter = ('status', 'service_name', ('created_at', admin.DateFieldListFilter))
    search_fields = ('order_id', 'user__first_name', 'user__username', 'service_name')
    readonly_fields = ('order_id', 'created_at')
    actions = ['mark_as_delivered', 'mark_as_processing', 'mark_as_pending']

    def changelist_view(self, request, extra_context=None):
        # DEFAULT TO TODAY LOGIC:
        # If the user visits the order list and NO query parameters are set
        if request.path == reverse('admin:core_order_changelist') and not request.GET:
            today = timezone.now().date()
            url = reverse('admin:core_order_changelist')
            # Redirect with Today's parameters so the sidebar filter is selected
            return HttpResponseRedirect(f"{url}?created_at__year={today.year}&created_at__month={today.month}&created_at__day={today.day}")

        # REVENUE DASHBOARD LOGIC
        orders = Order.objects.all()
        total_rev = orders.aggregate(total=Sum('total_price'))['total'] or 0
        today_rev = orders.filter(created_at__date=timezone.now().date()).aggregate(total=Sum('total_price'))['total'] or 0

        extra_context = extra_context or {}
        extra_context['total_revenue'] = f"₹{total_rev:,.2f}"
        extra_context['today_revenue'] = f"₹{today_rev:,.2f}"
        extra_context['total_orders'] = orders.count()
        extra_context['pending_count'] = orders.filter(status='Pending').count()
        extra_context['delivered_count'] = orders.filter(status='Delivered').count()
        
        return super().changelist_view(request, extra_context=extra_context)

    def student_info(self, obj):
        return format_html("<b>{}</b><br><small style='color:gray;'>+91 {}</small>", 
                           obj.user.first_name, obj.user.username)
    student_info.short_description = "Student Details"

    def price_tag(self, obj):
        return format_html("<span style='font-weight:900;'>₹{}</span>", obj.total_price)
    price_tag.short_description = "Bill Amount"

    def tracking_status(self, obj):
        colors = {'Pending': '#be123c', 'Processing': '#ca8a04', 'Delivered': '#15803d'}
        return format_html(
            '<div style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px; '
            'font-size: 9px; font-weight: 900; text-align: center; text-transform: uppercase;">{}</div>',
            colors.get(obj.status, '#64748b'), obj.status
        )
    tracking_status.short_description = "Track Status"

    def mark_as_delivered(self, request, queryset): queryset.update(status='Delivered')
    def mark_as_processing(self, request, queryset): queryset.update(status='Processing')
    def mark_as_pending(self, request, queryset): queryset.update(status='Pending')