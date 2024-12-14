from django.shortcuts import render
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import status
from .serializers import SignUpSerializer
from rest_framework.permissions import IsAuthenticated



# Create your views here.
@api_view(['POST'])

def register(request):
    data = request.data
    user = SignUpSerializer(data=data)
    if user.is_valid():
        if not User.objects.filter(username=data['email']).exists():
            user = User.objects.create(
                email =data['email'],
                password = make_password(data['password']),
                first_name = data['first_name'],
                last_name = data['last_name'],
                username = data['email']
                

            )
            return Response({'message': 'User Created Successfully', 'status': status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Email already exists', 'status': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(user.errors)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    user = SignUpSerializer(request.user)
    return Response(user.data)
