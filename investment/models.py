from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from authentication.models import AllUser

# Create your models here.

class Property(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('rejected', 'Rejected'),
    ]

    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
    ]

    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('needs_renovation', 'Needs Renovation'),
    ]

    URGENCY_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    # Basic Information and Status
    user = models.ForeignKey(AllUser, on_delete=models.CASCADE, related_name='properties')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_public = models.BooleanField(default=False, help_text='Property becomes public when approved by admin')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Location
    country = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True, null=True)
    county = models.CharField(max_length=100, blank=True, null=True)
    parish = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    number_or_lot = models.CharField(max_length=50, blank=True, null=True)
    floor_or_apartment = models.CharField(max_length=50, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)

    # Characteristics
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    number_of_rooms = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)])
    gross_area = models.DecimalField(max_digits=10, decimal_places=2, help_text='Area in square meters')
    construction_year = models.IntegerField(blank=True, null=True)

    # Details
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    has_garage = models.BooleanField(default=False)
    has_elevator = models.BooleanField(default=False)
    has_air_conditioning = models.BooleanField(default=False)
    has_private_garden = models.BooleanField(default=False)
    has_private_pool = models.BooleanField(default=False)
    has_storage = models.BooleanField(default=False)
    has_basement = models.BooleanField(default=False)
    has_terrace = models.BooleanField(default=False)

    # Business
    urgent_sale = models.CharField(max_length=5, choices=URGENCY_CHOICES)
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, help_text='Value in euros')

    # Personal Data
    contact_name = models.CharField(max_length=100)
    contact_surname = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    observations = models.TextField(blank=True, null=True)
    how_found = models.CharField(max_length=50, choices=[
        ('facebook', 'Facebook'),
        ('google', 'Google'),
        ('friend', 'Friend'),
        ('other', 'Other'),
    ])
    marketing_consent = models.BooleanField(default=False)
    terms_accepted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Properties'

    def __str__(self):
        return f"{self.street}, {self.city}, {self.country}"
    def save(self, *args, **kwargs):
        if not self.pk:
            self.status = 'pending'
        super().save(*args, **kwargs)
    def full_address(self):
        address_parts = [
            self.street,
            self.number_or_lot,
            self.floor_or_apartment if self.floor_or_apartment else None,
            self.postal_code,
            self.city,
            self.parish,
            self.county,
            self.district,
            self.country
        ]
        return ", ".join(filter(None, address_parts))
        
class PropertyDocument(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50, default='CPU', help_text='CPU - Caderneta Predial Urbana')
    file = models.FileField(upload_to='property_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for {self.property} - {self.document_type}"

class PropertyPhoto(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='property_photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Photo {self.order} of {self.property}"
