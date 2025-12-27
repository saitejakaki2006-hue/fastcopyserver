from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.admin import admin_site # Your custom admin site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('core.urls')),
]

# This is what allows the 'Open File' button to work on your local machine
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)