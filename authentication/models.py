from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import RegexValidator

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('status', 'active')
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

class AllUser(AbstractBaseUser, PermissionsMixin):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancel', 'Cancel'),
        ('pending', 'Pending'),
    ]
    
    OCCUPATION_CHOICES = [
        ('investor', 'Investor'),
        ('investment_finder', 'Investment Finder'),
        ('partnership', 'Partnership'),
        ('others', 'Others'),
    ]

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    location = models.CharField(max_length=255)
    phone_number = models.CharField(
    max_length=255
)
    occupation = models.CharField(max_length=255, choices=OCCUPATION_CHOICES, default='')
    role = models.CharField(max_length=255, choices=ROLE_CHOICES, default='user')
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='pending', null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'location', 'phone_number', 'occupation']

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name.split()[0]

    @property
    def is_user_active(self):
        return self.status == 'active'

    @property
    def is_authenticated(self):
        return True

    @property 
    def is_anonymous(self):
        return False

    def get_username(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
