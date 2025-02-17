
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserOTP


class SignUpSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    date_of_birth = serializers.DateField(required=True)
    gender = serializers.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')])
    phone = serializers.CharField(max_length=15)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'confirm_password', 'date_of_birth', 'gender', 'phone')
        extra_kwargs = {
            'first_name':  {'required': True,'allow_blank': False},
            'last_name': {'required': True,'allow_blank': False},
            'email': {'required': True,'allow_blank': False},
            'password': {'required': True,'allow_blank': False,'min_length':8},
        }

class UserSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(source='userprofile.image', required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'image']




class UserOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserOTP
        fields = ['user', 'otp', 'created_at']