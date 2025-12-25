from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.admin import admin_site  # Import your custom admin instance

urlpatterns = [
    # 🛠️ Custom Admin Site
    path('admin/', admin_site.urls),
    
    # 🏠 Core App URLs
    path('', include('core.urls')),
]

# 📂 Serve Media Files (PDFs/Images) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)