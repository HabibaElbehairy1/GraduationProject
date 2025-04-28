import logging
import random
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import UpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone


from .models import UserOTP, UserProfile
from .serializers import UserSerializer, UserOTPSerializer
from .permissions import IsAuthenticatedWithJWT

logger = logging.getLogger(__name__)
User = get_user_model()

MAX_ATTEMPTS = 3
BLOCK_DURATION = timedelta(minutes=5)


class RegisterView(generics.ListCreateAPIView):
    """Handles user registration and profile creation."""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        """Registers a new user and creates their profile."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        UserProfile.objects.create(
            user=user,
            date_of_birth=request.data.get('date_of_birth'),
            gender=request.data.get('gender'),
            phone_number=request.data.get('phone_number'),
            image="profile_images/default.jpg",
        )

        return Response({
            'message': 'User created successfully',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': serializer.data,
            'status': status.HTTP_201_CREATED
        }, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        """Returns the authenticated user's data."""
        if not request.user.is_authenticated:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LoginView(APIView):
    """Handles user login and returns JWT tokens."""
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """Authenticates a user and returns access and refresh tokens."""
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'message': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(username=user.username, password=password)
        if user is None:
            return Response({'message': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'Login successful',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            }
        }, status=status.HTTP_200_OK)


from rest_framework.generics import RetrieveDestroyAPIView

class GetUserView(RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticatedWithJWT]  # الصح هنا
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        user = request.user

        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        request_host = request.build_absolute_uri('/')[:-1]
        image_url = request_host + (profile.image.url if profile.image else "/media/profile_images/default.jpg")

        user_data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "date_of_birth": profile.date_of_birth,
            "gender": profile.gender,
            "phone_number": profile.phone_number,
            "username": user.username,
            "image": image_url
        }

        return Response(user_data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            self.perform_destroy(user)
            return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)
class UpdateUserView(UpdateAPIView):
    permission_classes = [IsAuthenticatedWithJWT]
    """Updates authenticated user's personal and profile information."""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def update(self, request, *args, **kwargs):
        """Updates user and profile fields."""
        user = request.user
        data = request.data

        current_password = data.get('current_password')
        if not current_password:
            return Response({'message': 'Current password is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(current_password):
            return Response({'message': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)
        user.username = data.get('username', user.username)
        user.gender = data.get('gender',user.gender)
        user.date_of_birth = data.get('date_of_birth',user.date_of_birth)
        user.phone_number = data.get('phone_number',user.phone_number)


        if data.get('password'):
            user.set_password(data['password'])

        user.save()

        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.gender = data.get('gender', profile.gender)
        profile.phone_number = data.get('phone_number', profile.phone_number)
        profile.date_of_birth = data.get('date_of_birth', profile.date_of_birth)

        if 'image' in request.FILES:
            profile.image = request.FILES['image']

        profile.save()

        serializer = self.get_serializer(user)
        return Response({'message': 'Data updated successfully', 'user': serializer.data}, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(instance=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ChangePasswordView(UpdateAPIView):
    permission_classes = [IsAuthenticatedWithJWT]
    """Allows authenticated users to change their password."""
    queryset = User.objects.all()

    def update(self, request, *args, **kwargs):
        """Changes user's password after validating current password."""
        user = request.user
        data = request.data

        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if not current_password or not new_password or not confirm_password:
            return Response({'message': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(current_password):
            return Response({'message': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'message': 'New password and confirm password do not match'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def get_otp(request):
    """Sends an OTP code to the user's email for password reset."""
    email = request.data.get('email')

    if not email:
        return Response({'message': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        logger.warning(f"User with email {email} does not exist")
        return Response({'message': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

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
        return Response({'message': 'OTP sent to your email'}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Failed to send OTP email: {e}")
        return Response({'message': 'Failed to send OTP. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def verify_otp(request):
    """Verifies the OTP entered by the user."""
    email = request.data.get('email')
    otp = request.data.get('otp')

    if not email or not otp:
        return Response({'message': 'Email and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = get_object_or_404(User, email=email)
        user_otp = get_object_or_404(UserOTP, user=user)

        if user_otp.attempts >= MAX_ATTEMPTS:
            if timezone.now() - user_otp.last_attempt_time < BLOCK_DURATION:
                return Response({'message': 'Maximum number of attempts exceeded. Please try again later.'}, status=status.HTTP_403_FORBIDDEN)
            else:
                user_otp.attempts = 0

        if user_otp.otp != otp:
            user_otp.attempts += 1
            user_otp.last_attempt_time = timezone.now()
            user_otp.save()
            return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

        user_otp.delete()
        return Response({'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error verifying OTP: {e}")
        return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def reset_password(request):
    """Resets the user's password after successful OTP verification."""
    email = request.data.get('email')
    new_password = request.data.get('new_password')

    if not new_password:
        return Response({'message': 'New password is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = get_object_or_404(User, email=email)
        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error resetting password: {e}")
        return Response({'message': 'An error occurred. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)