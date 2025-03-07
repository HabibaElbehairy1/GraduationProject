from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator ,MaxLengthValidator
from django.conf import settings
# from project import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, MaxLengthValidator
import uuid
class User(AbstractUser):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(
        max_length=12, 
        unique=True,
        null=False,
        blank=False,
        validators=[MinLengthValidator(11), MaxLengthValidator(12)],
        help_text="Phone number must be exactly 11 or 12 characters long."
    )
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('E', 'Engineer'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    
    def __str__(self):
        return self.username
class UserProfile(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='userprofile')
    image = models.ImageField(upload_to='profile_images/', default='profile_images/default.jpg', null=True, blank=True)
    bio = models.TextField(null=True, blank=True) 
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(
        max_length= 12,
        unique=True,
        null=False,
        blank=False,
        validators=[MinLengthValidator(11), MaxLengthValidator(12)],
        help_text="Phone number must be exactly 11 or 12 characters long."
    )
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Engineer', 'Engineer'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
     # مثال لحقل إضافي

    def __str__(self):
        return f"{self.user.username}'s profile"

from django.utils import timezone
from datetime import timedelta

class UserOTP(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='otp')
    otp = models.CharField(max_length=6)  # زيادة طول OTP إلى 6 أحرف
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)  # إضافة حقل للتحقق من صحة OTP
    attempts = models.IntegerField(default=0)  # عدد المحاولات
    last_attempt_time = models.DateTimeField(auto_now=True) 

    def is_expired(self):
        # انتهاء صلاحية OTP بعد 5 دقائق
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def __str__(self):
        return f"{self.user.username}'s OTP"