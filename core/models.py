from django.db import models
from django.contrib.auth.models import User
import uuid

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.user.username

class Order(models.Model):
    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=100)
    total_price = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=[
        ('In Progress', 'In Progress'),
        ('Ready', 'Ready'),
        ('Delivered', 'Delivered'),
    ], default='In Progress')
    created_at = models.DateTimeField(auto_now_add=True)
class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon_class = models.CharField(max_length=50) # e.g., 'fas fa-book'
    theme_color = models.CharField(max_length=7, default='#2563eb') # e.g., '#FF5733'