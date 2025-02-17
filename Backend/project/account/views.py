import logging
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from .serializers import SignUpSerializer, UserSerializer
from .models import UserProfile, UserOTP
import random

logger = logging.getLogger(__name__)

@api_view(['POST'])
def register(request):
    data = request.data
    user = SignUpSerializer(data=data)
    
    if user.is_valid():
        if data['password'] != data['confirm_password']:
            return Response(
                {'message': 'Passwords do not match', 'status': status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=data['email']).exists():
            return Response(
                {'message': 'Email already exists', 'status': status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create(
            email=data['email'],
            password=make_password(data['password']),
            first_name=data['first_name'],
            last_name=data['last_name'],
            username=data['email']
        )

        default_image = "profile_images/default.jpg"
        UserProfile.objects.create(
            user=user,
            date_of_birth=data['date_of_birth'],
            gender=data['gender'],
            phone=data['phone'],
            image=default_image
        )

        return Response(
            {'message': 'User Created Successfully', 'status': status.HTTP_201_CREATED},
            status=status.HTTP_201_CREATED
        )
    else:
        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    user = request.user
    profile = user.userprofile

    request_host = request.build_absolute_uri('/')[:-1]
    image_url = request_host + (profile.image.url if profile.image else "/media/profile_images/default.jpg")

    user_data = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "date_of_birth": profile.date_of_birth,
        "gender": profile.gender,
        "phone": profile.phone,
        "image": image_url
    }
    return Response(user_data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request):
    user = request.user
    data = request.data
    profile = user.userprofile

    current_password = data.get('current_password')
    if not current_password:
        return Response(
            {'message': 'Current password is required to update', 'status': status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not user.check_password(current_password):
        return Response(
            {'message': 'Current password is incorrect', 'status': status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST
        )

    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.email = data.get('email', user.email)
    user.username = data.get('email', user.username)

    if data.get('password'):
        user.set_password(data['password'])

    profile.date_of_birth = data.get('date_of_birth', profile.date_of_birth)
    profile.gender = data.get('gender', profile.gender)
    profile.phone = data.get('phone', profile.phone)

    if 'image' in request.FILES:
        profile.image = request.FILES['image']

    user.save()
    profile.save()

    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    data = request.data

    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_new_password')

    if not current_password or not new_password or not confirm_password:
        return Response(
            {'message': 'All fields are required', 'status': status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not user.check_password(current_password):
        return Response(
            {'message': 'Current password is incorrect', 'status': status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST
        )

    if new_password != confirm_password:
        return Response(
            {'message': 'New password and confirm password do not match', 'status': status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST
        )

    user.set_password(new_password)
    user.save()

    return Response(
        {'message': 'Password updated successfully', 'status': status.HTTP_200_OK},
        status=status.HTTP_200_OK
    )



@api_view(['POST'])
def get_otp(request):
    email = request.data.get('email')
    if not email:
        return Response(
            {'message': 'Email is required', 'status': status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        logger.warning(f"User with email {email} does not exist")
        return Response(
            {'message': 'User with this email does not exist', 'status': status.HTTP_404_NOT_FOUND},
            status=status.HTTP_404_NOT_FOUND
        )

    otp = ''.join(random.choices('0123456789', k=5))
    UserOTP.objects.update_or_create(user=user, defaults={'otp': otp})

    try:
        send_mail(
            'Your OTP for Password Reset',
            f'Your OTP is {otp}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        return Response(
            {'message': 'OTP sent to your email', 'status': status.HTTP_200_OK},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Failed to send OTP email: {e}")
        return Response(
            {'message': 'Failed to send OTP. Please try again.', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def verify_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')

    if not email or not otp:
        return Response(
            {'message': 'Email and OTP are required', 'status': status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = get_object_or_404(User, email=email)
        user_otp = get_object_or_404(UserOTP, user=user, otp=otp)
        user_otp.delete()
        return Response(
            {'message': 'OTP verified successfully', 'status': status.HTTP_200_OK},
            status=status.HTTP_200_OK
           
        )
    except Exception as e:
        logger.error(f"Error verifying OTP: {e}")
        return Response(
            {'message': 'Invalid OTP', 'status': status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
def reset_password(request):
    # Extract data from the request
    email = request.data.get('email')
    otp = request.data.get('otp')
    new_password = request.data.get('new_password')

  
    if not new_password:
        return Response(
            {'message': 'new password is required', 'status': status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Fetch the user and OTP
        user = get_object_or_404(User, email=email)
      
        # Set the new password
        user.set_password(new_password)
        user.save()


        return Response(
            {'message': 'Password reset successfully', 'status': status.HTTP_200_OK},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Error resetting password: {e}")
        return Response(
            {'message': 'An error occurred. Please try again.', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )