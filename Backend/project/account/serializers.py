
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserOTP


from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model() 

class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = [
            'first_name', 'last_name', 'date_of_birth',
            'username', 'email', 'password', 'confirm_password',
            'phone_number', 'gender'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'date_of_birth': {'required': True},
            'phone_number': {'required': True},
            'gender': {'required': True},

        }

    def validate(self, data):
        # التحقق من تطابق كلمات المرور
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        
        # التحقق من صحة كلمة المرور باستخدام validators الافتراضية
        try:
            validate_password(data['password'])
        except ValidationError as e:
            raise serializers.ValidationError({'password': e.messages})
        
        # التحقق من أن البريد الإلكتروني فريد
        if get_user_model().objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already exists.")
        
        # التحقق من أن رقم الهاتف فريد
        if get_user_model().objects.filter(phone_number=data['phone_number']).exists():
            raise serializers.ValidationError("Phone number already exists.")
        
        return data

    def create(self, validated_data):
        # إزالة حقل confirm_password لأنه غير مطلوب في النموذج
        validated_data.pop('confirm_password')
        
        # إنشاء المستخدم
        user = get_user_model().objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            date_of_birth=validated_data.get('date_of_birth'),
            phone_number=validated_data['phone_number'],
            gender=validated_data.get('gender')
        )
        return user


class UserOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserOTP
        fields = ['user', 'otp', 'created_at']