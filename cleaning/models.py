# models.py

from django.db import models
from django.contrib.auth.models import User
import uuid  # Required for UUIDField
from django.db import models
from datetime import datetime
from django.utils.timezone import now
from django import forms

class ServiceRating(models.Model):
    SERVICE_CHOICES = [
        ('residential', 'Residential Cleaning'),
        ('commercial', 'Commercial Cleaning'),
        ('deep-cleaning', 'Deep Cleaning'),
        ('move-in-out', 'Move-in/Move-out Cleaning'),
        ('carpet-cleaning', 'Carpet Cleaning'),
        ('upholstery-cleaning', 'Upholstery Cleaning'),
        ('window-cleaning', 'Window Cleaning'),
        ('eco-friendly', 'Eco-friendly Green Cleaning'),
        ('anti-bacterial-mist', 'Anti-Bacterial Mist Treatment'),
        ('car-interior-detailing', 'Car Interior Detailing'),
        ('deep-dry-cleaning', 'Deep Dry Cleaning'),
        ('deep-home-cleaning', 'Deep Home Cleaning'),
        ('deep-upholstery-shampooing', 'Deep Upholstery Shampooing'),
        ('steam-sterilization', 'Superior Steam Sterilization'),
]


    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Optional: Only if ratings are user-specific
    service_name = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    rating = models.IntegerField()  # Ratings as integers, e.g., from 1 to 5
    month = models.CharField(max_length=20)  # Month as a string (e.g., 'January', 'February')

    # Optional: Add unique constraints to avoid duplicate ratings for the same service and month per user
    class Meta:
        unique_together = ('user', 'service_name', 'month')

    def __str__(self):
        return f"{self.get_service_name_display()} - {self.rating} in {self.month}"




#mao ni ang admin site sa Blog na mag upload 
class ServiceReview(models.Model):
    customer_name = models.CharField(max_length=100)
    message = models.TextField()
    photo = models.ImageField(upload_to='service_photos/')
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # Ratings from 1 to 5

    def __str__(self):
        return self.customer_name


class Booking(models.Model):
    booking_id = models.AutoField(primary_key=True, editable=False)
    
    CLEANING_CHOICES = [
    ('residential', 'Residential Cleaning'),
    ('commercial', 'Commercial Cleaning'),
    ('move-in-out', 'Move-in/Move-out Cleaning'),
    ('carpet-cleaning', 'Carpet Cleaning'),
    ('window-cleaning', 'Window Cleaning'),
    ('eco-friendly', 'Eco-friendly Green Cleaning'),
    ('anti-bacterial-mist', 'Anti-Bacterial Mist Treatment'),
    ('car-interior-detailing', 'Car Interior Detailing'),
    ('deep-dry-cleaning', 'Deep Dry Cleaning'),
    ('deep-home-cleaning', 'Deep Home Cleaning'),
    ('deep-upholstery-shampooing', 'Deep Upholstery Shampooing'),
    ('steam-sterilization', 'Superior Steam Sterilization'),
]


    PENDING = 'pending'
    APPROVED = 'approved'
    DENIED = 'denied'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (DENIED, 'Denied'),
    ]

    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cleaning_service = models.CharField(max_length=100, choices=CLEANING_CHOICES)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, default='Unknown')
    contact_number = models.CharField(max_length=15)
    address = models.TextField()
    additional_info = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    booking_date = models.DateField() 

    def __str__(self):
        return f"Booking by {self.first_name} {self.last_name} - {self.cleaning_service}"
    
class Service(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='services_images/')
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set on creation

    def __str__(self):
        return self.name

class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.name