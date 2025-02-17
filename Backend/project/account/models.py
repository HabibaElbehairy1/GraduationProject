from django.db import models
from django.contrib.auth.models import User
import random
from datetime import timedelta
from django.utils import timezone
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')])
    phone = models.CharField(max_length=15)
    image = models.ImageField(upload_to='profile_images/', default='profile_images/default.jpg', null=True, blank=True)  

    def __str__(self):
        return f"{self.user.username}'s profile"




class UserOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s OTP"