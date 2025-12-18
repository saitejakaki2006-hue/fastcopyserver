from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=100)
    icon_class = models.CharField(max_length=50, help_text="Example: fa-print, fa-book")
    short_description = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name