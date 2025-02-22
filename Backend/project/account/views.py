import logging
import random
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from .models import UserOTP, UserProfile
from .serializers import UserSerializer, UserOTPSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


class RegisterView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    authentication_classes = [TokenAuthentication]
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Create or retrieve token
        token, _ = Token.objects.get_or_create(user=user)

        # Automatically create a user profile
        UserProfile.objects.create(
            user=user,
            date_of_birth=request.data.get('date_of_birth'),
            gender=request.data.get('gender'),
            phone_number=request.data.get('phone_number'),
            image="profile_images/default.jpg"  # Default profile image
        )

        return Response(
            {
                'message': 'User created successfully',
                'token': token.key,
                'user': serializer.data,
                'status': status.HTTP_201_CREATED
            },
            status=status.HTTP_201_CREATED
        )
    def list(self, request, *args, **kwargs):

        token_key = self.request.headers.get('Authorization', '').replace('Token ', '')

        try:
            # Get the user associated with the token
            token = Token.objects.get(key=token_key)
            user = token.user

            # Serialize and return the user's data
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Token.DoesNotExist:
            return Response({'error': 'Invalid or missing token'}, status=status.HTTP_401_UNAUTHORIZED)

class GetUserView(generics.RetrieveDestroyAPIView):
    queryset = User.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        user = request.user

        # Ensure profile exists
        try:
            profile = user.userprofile
        except UserProfile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        # Construct the image URL
        request_host = request.build_absolute_uri('/')[:-1]
        image_url = request_host + (profile.image.url if profile.image else "/media/profile_images/default.jpg")

        # Construct the user data
        user_data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "date_of_birth": profile.date_of_birth,
            "gender": profile.gender,
            "phone_number": profile.phone_number,
            "image": image_url
        }

        return Response(user_data, status=status.HTTP_200_OK)
    def destroy(self, request, *args, **kwargs):
        token_key = request.headers.get('Authorization', '').replace('Token ', '')

        try:
            # البحث عن التوكن في قاعدة البيانات
            token = Token.objects.get(key=token_key)
            user = token.user  # المستخدم المرتبط بالتوكن

            # حذف المستخدم
            self.perform_destroy(user)
            return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

        except Token.DoesNotExist:
            return Response({'error': 'Invalid or missing token'}, status=status.HTTP_401_UNAUTHORIZED)

from rest_framework.generics import UpdateAPIView



class UpdateUserView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def update(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        # Check if the current password is provided
        current_password = data.get('current_password')
        if not current_password:
            return Response(
                {'message': 'Current password is required to update', 'status': status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify the current password
        if not user.check_password(current_password):
            return Response(
                {'message': 'Current password is incorrect', 'status': status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update user fields
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)
        user.username = data.get('email', user.username)

        if data.get('password'):
            user.set_password(data['password'])

        # Update profile fields
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.date_of_birth = data.get('date_of_birth', profile.date_of_birth)
        profile.gender = data.get('gender', profile.gender)
        profile.phone_number = data.get('phone_number', profile.phone_number)

        if 'image' in request.FILES:
            profile.image = request.FILES['image']

        # Save the updated user and profile
        user.save()
        profile.save()

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)



class ChangePasswordView(UpdateAPIView):
    queryset = User.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        # Extracting required fields
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        # Check for missing fields
        if not current_password or not new_password or not confirm_password:
            return Response(
                {'message': 'All fields are required', 'status': status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify the current password
        if not user.check_password(current_password):
            return Response(
                {'message': 'Current password is incorrect', 'status': status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if new passwords match
        if new_password != confirm_password:
            return Response(
                {'message': 'New password and confirm password do not match', 'status': status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Set the new password and save
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


from datetime import timedelta, datetime

MAX_ATTEMPTS = 3  # الحد الأقصى لعدد المحاولات
BLOCK_DURATION = timedelta(minutes=5)  # مدة حظر المحاولات (5 دقائق)

@api_view(['POST'])
def verify_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')

    if not email or not otp:
        return Response(
            {'message': 'البريد الإلكتروني ورمز التحقق مطلوبان', 'status': status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = get_object_or_404(User, email=email)
        user_otp = get_object_or_404(UserOTP, user=user)

        # التحقق من عدد المحاولات
        if user_otp.attempts >= MAX_ATTEMPTS:
            time_since_last_attempt = datetime.now() - user_otp.last_attempt_time

            # التحقق مما إذا كان الحظر لا يزال ساريًا
            if time_since_last_attempt < BLOCK_DURATION:
                return Response(
                    {'message': 'تم تجاوز عدد المحاولات المسموح به. الرجاء المحاولة لاحقًا.', 'status': status.HTTP_403_FORBIDDEN},
                    status=status.HTTP_403_FORBIDDEN
                )
            else:
                # إعادة تعيين عدد المحاولات بعد انتهاء فترة الحظر
                user_otp.attempts = 0

        # التحقق من صحة رمز التحقق
        if user_otp.otp != otp:
            user_otp.attempts += 1  # زيادة عدد المحاولات
            user_otp.save()
            return Response(
                {'message': 'رمز التحقق غير صحيح', 'status': status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST
            )

        # إذا كان رمز التحقق صحيحًا، إعادة تعيين المحاولات وحذف رمز التحقق
        user_otp.delete()
        return Response(
            {'message': 'تم التحقق من رمز التحقق بنجاح', 'status': status.HTTP_200_OK},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        logger.error(f"Error verifying OTP: {e}")
        return Response(
            {'message': 'رمز التحقق غير صحيح', 'status': status.HTTP_400_BAD_REQUEST},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
def reset_password(request):
    # Extract data from the request
    email = request.data.get('email')
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