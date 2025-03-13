from rest_framework import serializers
from .models import Post, Comment
from django.contrib.auth import get_user_model
from account.models import UserProfile
User = get_user_model() 

class UserSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(source='userprofile.image', read_only=True)
    class Meta:
        model = get_user_model()
        fields = ['username','image']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Nested user details
    class Meta:
        model = Comment
        fields = ['user','id','comment', 'created_at', 'updated_at']
        read_only_fields = ['user']

class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)  # Nested user details   
    class Meta:
        model = Post
        fields = ['post_name' ,'id','user', 'content', 'image', 'comments' ,'created_at', 'updated_at']
        read_only_fields = ['user']


