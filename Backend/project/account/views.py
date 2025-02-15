from django.shortcuts import render
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import status
from .serializers import SignUpSerializer,UserSerializer
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile


@api_view(['POST'])
def register(request):
    data = request.data
    user = SignUpSerializer(data=data)
    if user.is_valid():
        if data['password'] != data['confirm_password']:
            return Response({'message': 'Passwords do not match', 'status': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        if not User.objects.filter(username=data['email']).exists():
            user = User.objects.create(
                email =data['email'],
                password = make_password(data['password']),
                first_name = data['first_name'],
                last_name = data['last_name'],
                username = data['email']
            )
            UserProfile.objects.create(
                user=user,
                date_of_birth=data['date_of_birth'],
                gender=data['gender'],
                phone=data['phone']
            )

            return Response({'message': 'User Created Successfully', 'status': status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Email already exists', 'status': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(user.errors)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    user = request.user
    profile = user.userprofile
    user_data = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "date_of_birth": profile.date_of_birth,
        "gender": profile.gender,
        "phone": profile.phone
    }
    return Response(user_data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request):
    user = request.user
    data = request.data
    user.first_name = data['first_name']
    user.username = data['email']
    user.last_name = data['last_name']
    user.email = data['email']

    if data['password'] != "":
        user.password =  make_password(data['password'])

    profile = user.userprofile
    profile.date_of_birth = data['date_of_birth']
    profile.gender = data['gender']
    profile.phone = data['phone']

    user.save()
    profile.save()
    serializer = UserSerializer(user,many=False)
    return Response(serializer.data)

