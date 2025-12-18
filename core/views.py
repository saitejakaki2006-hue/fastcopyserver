from django.shortcuts import render
from .models import Service

def home(request):
    services = Service.objects.all()
    return render(request, 'core/index.html', {'services': services})

def services_page(request):
    services = Service.objects.all()
    return render(request, 'core/services.html', {'services': services})