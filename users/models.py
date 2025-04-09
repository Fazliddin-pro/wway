from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Manager for users
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_teacher', False)  # Superuser is not a teacher
        return self.create_user(email, password, **extra_fields)

# Role choices
USER_ROLES = [
    ('admin', 'Administrator'),
    ('teacher', 'Teacher'),
    ('student', 'Student'),
]

# Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='Email')
    phone_number = models.CharField(max_length=20, unique=True, verbose_name='Phone Number')
    full_name = models.CharField(max_length=255, verbose_name='Full Name')
    age = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Age')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Avatar')
    gender = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')), verbose_name='Gender')
    role = models.CharField(max_length=10, choices=USER_ROLES, default='student', verbose_name='Role')
    
    # Extra fields for teachers
    is_teacher = models.BooleanField(default=False, verbose_name='Is Teacher')
    bio = models.TextField(blank=True, null=True, verbose_name='Biography')  # Info about teachers

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    def __str__(self):
        return f'{self.email} ({self.role})'

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
