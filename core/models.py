from django.db import models
from django.contrib.auth.models import User

# --- 1. USER PROFILE MODEL ---
class UserProfile(models.Model):
    """
    Extends the base Django User. 
    Stores custom User ID in format: FC_USER_0000
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Custom Formatted ID Field
    fc_user_id = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False, 
        null=True, 
        blank=True
    )
    
    mobile = models.CharField(max_length=15)
    address = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Initial save to get the primary key ID
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        # Generate FC_USER_0000 format after ID is available
        if is_new and not self.fc_user_id:
            self.fc_user_id = f"FC_USER_{self.id:04d}"
            # Use update to save specifically the fc_user_id without re-triggering save()
            UserProfile.objects.filter(pk=self.pk).update(fc_user_id=self.fc_user_id)

    def __str__(self): 
        return f"{self.fc_user_id} | {self.user.username}"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


# --- 2. SERVICE MODEL ---
class Service(models.Model):
    """
    Stores types of services offered (e.g., Printing, Binding).
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self): 
        return self.name

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"


# --- 3. ORDER MODEL (MASTER ENGINE) ---
class Order(models.Model):
    """
    Order ID format: FC_ORDER_0000000000
    Stores transaction details and printing configurations.
    """
    
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    payment_status = models.CharField(
        max_length=20, 
        choices=[('Pending', 'Pending'), ('Success', 'Success'), ('Failed', 'Failed')],
        default='Pending'
    )
    
    # Formatted Order ID
    order_id = models.CharField(max_length=30, unique=True, editable=False, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    
    service_name = models.CharField(max_length=100)
    
    # Dual-purpose file support
    document = models.FileField(upload_to='orders/documents/', null=True, blank=True)
    image_upload = models.ImageField(upload_to='orders/images/', null=True, blank=True)
    
    # Printing Mode Logic (bw, color, or custom(pages))
    print_mode = models.CharField(max_length=100, default='bw')
    custom_color_pages = models.CharField(
        max_length=255, 
        null=True, 
        blank=True, 
        help_text="Stores raw page numbers before formatting"
    )
    
    side_type = models.CharField(max_length=50, default='single')
    copies = models.IntegerField(default=1)
    location = models.CharField(max_length=100, null=True, blank=True)
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Ready', 'Ready'),
        ('Delivered', 'Delivered'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # 1. Logic for Custom print_mode format
        if self.print_mode == 'custom_split' and self.custom_color_pages:
            self.print_mode = f"custom({self.custom_color_pages})"
        elif self.print_mode and "(" not in self.print_mode:
            self.print_mode = self.print_mode.lower()

        # 2. Initial Save to get ID
        is_new = self._state.adding
        super().save(*args, **kwargs)

        # 3. Update order_id with the 10-digit format
        if is_new and not self.order_id:
            self.order_id = f"FC_ORDER_{self.id:010d}"
            Order.objects.filter(pk=self.pk).update(order_id=self.order_id)

    def __str__(self):
        return str(self.order_id if self.order_id else f"Temp_{self.id}")

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']


# --- 4. CART MODEL ---
class CartItem(models.Model):
    """
    Persistence model to ensure cart items survive user logouts.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=255)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    document_name = models.CharField(max_length=255, null=True, blank=True)
    temp_path = models.CharField(max_length=500, null=True, blank=True)
    temp_image_path = models.CharField(max_length=500, null=True, blank=True)
    copies = models.IntegerField(default=1)
    pages = models.IntegerField(default=0)
    location = models.CharField(max_length=255, null=True, blank=True)
    print_mode = models.CharField(max_length=50, null=True, blank=True)
    side_type = models.CharField(max_length=50, default='single')
    custom_color_pages = models.TextField(null=True, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.service_name}"