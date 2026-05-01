from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid
from rest_framework_simplejwt.tokens import RefreshToken



class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number=None, email=None, first_name='', last_name='', provider=None, provider_id=None, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("The Phone Number must be set")
        email = self.normalize_email(email)
        user = self.model(
            phone_number=phone_number or '',
            email=email,
            first_name=first_name or '',
            last_name=last_name or '',
            provider=provider,
            provider_id=provider_id,
            **extra_fields
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, email=None, password=None, **extra_fields):
        
        if password is None:
            raise TypeError('Password is required')

        user = self.create_user(phone_number, email, password=password, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=250, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=250, blank=True, null=True)
    last_name = models.CharField(max_length=250, blank=True, null=True)
    phone_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    otp = models.CharField(max_length=150, blank=True, null=True)
    PROVIDER_TYPES = [
        ('apple', 'apple'),
        ('google', 'google'),
        ('facebook', 'facebook'),
    ]
    provider = models.CharField(max_length=50, choices=PROVIDER_TYPES, blank=True, null=True)
    provider_id = models.CharField(max_length=1500, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_new_user = models.BooleanField(default=False, blank=True, null=True)
    referral_code = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    def __str__(self):
        return str(self.email)
    

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh' : str(refresh),
            'access' : str(refresh.access_token)
        } 


class OtpCheck(models.Model):
    email = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    otp_code = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.phone_number} --- {self.email}"