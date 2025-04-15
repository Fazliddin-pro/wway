from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from .validators import validate_avatar_size

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Обеспечим, что суперюзер получает роль "admin"
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

USER_ROLES = [
    ('admin', 'Administrator'),
    ('teacher', 'Teacher'),
    ('student', 'Student'),
]

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
]

phone_regex = RegexValidator(
    regex=r'^\+998\d{9}$',
    message="Enter a valid phone number in the format: +998XXXXXXXXX"
)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='Email')
    phone_number = models.CharField(max_length=20, unique=True, verbose_name='Phone Number',
                                    validators=[phone_regex])
    full_name = models.CharField(max_length=255, blank=True, verbose_name='Full Name')
    age = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Age',
                                           validators=[MinValueValidator(1), MaxValueValidator(101)])
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Avatar',
                               validators=[validate_avatar_size])
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M', verbose_name='Gender')
    role = models.CharField(max_length=10, choices=USER_ROLES, default='student', verbose_name='Role')
    bio = models.TextField(blank=True, null=True, verbose_name='Biography')
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    def __str__(self):
        return f'{self.full_name} ({self.email})'
    
    def clean(self):
        super().clean()
        if self.age is not None and (self.age < 1 or self.age > 101):
            raise ValidationError({'age': 'Enter a valid age between 1 and 101.'})
    
    def save(self, *args, **kwargs):
        if not self.is_superuser:
            if self.role in ['student', 'teacher']:
                self.is_staff = False
            elif self.role == 'admin' and not self.is_staff:
                self.is_staff = True
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
